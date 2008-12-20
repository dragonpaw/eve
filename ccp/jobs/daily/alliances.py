from django_extensions.management.jobs import DailyJob

from eve.lib import eveapi
from eve.ccp.models import Alliance, Corporation

from datetime import datetime

#from Queue import Queue
import workerpool

class Job(DailyJob):
    help = "Reload all of the alliances and member corporations."

    def execute(self):
        update_alliances()

def check_link(alliance, corp_id):
    messages = []
    corp = None
    try:
        corp = Corporation.objects.get(id=corp_id)
        corp.failed = False # This counts as a sucessful refresh.
        if corp.alliance != alliance:
            old = corp.alliance
            corp.alliance = alliance
            corp.save()
            messages.append('Updated alliance link on %s: %s -> %s' % (corp.name, old, alliance))
    except Corporation.DoesNotExist:
        messages.append('Refreshing new corp: %s' % corp_id)
        corp = Corporation(id=corp_id)
        messages.extend( corp.refresh() )
    return corp, messages

def update_alliance(a):
    messages = ['Updating alliance: %s' % a.name]
    worked = False

    try:
        alliance = Alliance.objects.get(id=a.allianceID)
    except Alliance.DoesNotExist:
        alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)
    alliance.member_count = a.memberCount
    alliance.save()

    members = [ a.executorCorpID ]

    # Check the executor corp.
    corp, msg = check_link(alliance, a.executorCorpID)
    messages.extend(msg)

    # Have to set executor and re-save it here to work around constraints.
    # Can't add an alliance unless the exec corp exists first. Can't add a
    # Corp unless the alliance it belongs to exists.
    # So dance is: Make alliance without exec, add corp, set exec.
    if corp.failed is True:
        messages.append('Alliance refresh failed. Will be deleted.')
        return (alliance.id, worked, messages)

    alliance.executor = corp
    alliance.save()
    worked = True
    # Refresh all the member corps too.
    for c in a.memberCorporations:
        id = c.corporationID
        members.append(id)
        messages.extend( check_link(alliance, id) )

    for c in Corporation.objects.filter(alliance=alliance):
        if c.id not in members:
            c.alliance = None
            c.save()
            messages.append('Removed from alliance %s: %s' % (alliance.name, c.name))

    return (alliance.id, worked, messages)


def update_alliances():
    api = eveapi.get_api()
    print("Starting alliance list...")
    start_time = datetime.utcnow()

    #output = Queue()
    pool = workerpool.WorkerPool(size=20)

    #for a in api.eve.AllianceList().alliances:
    #    job = SimpleJob(output, update_alliance, a)
    #    pool.put(job)

    alliance_ids = []

    results = pool.map(update_alliance, api.eve.AllianceList().alliances)
    for id, worked, messages in results:
        if worked:
            alliance_ids.append(id)
        else:
            print "Failed: %s" % id
            for m in messages:
                print m

    pool.shutdown()
    pool.wait()

    # Force immediate evaluation to protect from odd interaction with the cursor
    # while deleting rows.
    delete_me = []
    for a in Alliance.objects.all():
        if a.id in alliance_ids:
            # It still exists.
            continue
        delete_me.append(a)
    for a in delete_me:
        print('Removing defunct alliance: %s' % a.name)
        a.delete()

    print "Elapsed: %s" % (datetime.utcnow() - start_time)
