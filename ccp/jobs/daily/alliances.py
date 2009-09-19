from django_extensions.management.jobs import DailyJob

from eve.lib import eveapi
from eve.ccp.models import Alliance, Corporation

from datetime import datetime

#from Queue import Queue
#import threading
import workerpool

class Job(DailyJob):
    help = "Reload all of the alliances and member corporations."

    def execute(self):
        update_alliances()

def update_alliance(a):
    try:
        return _update_alliance(a)
    except Exception as e:
        return a.allianceID, False, (str(e),)

def _update_alliance(a):
    messages = ['Updating alliance: %s' % a.name]
    print messages[0]

    try:
        alliance = Alliance.objects.get(id=a.allianceID)
    except Alliance.DoesNotExist:
        alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)

    # Check the executor corp, creating if needed.
    corp_id = a.executorCorpID
    try:
        corp = Corporation.objects.get(id=corp_id)
    except Corporation.DoesNotExist:
        messages.append('Refreshing new corp: %d' % corp_id)
        corp = Corporation(id=corp_id)
        messages.extend( corp.refresh() )
        if corp.refresh_failed is True:
            return (alliance.id, False, messages)

    alliance.executor = corp
    alliance.member_count = a.memberCount
    alliance.save()

    # Refresh all the member corps too. (This includes the exec.)
    members = list()
    for c in a.memberCorporations:
        corp_id = c.corporationID
        members.append(corp_id)
        try:
            corp = Corporation.objects.get(id=corp_id)
        except Corporation.DoesNotExist:
            messages.append('Refreshing new corp: %d' % corp_id)
            corp = Corporation(id=corp_id)
            messages.extend( corp.refresh() )
        if corp.alliance != alliance:
            corp.alliance = alliance
            corp.save()

    for c in alliance.corporations.all():
        if c.id not in members:
            c.alliance = None
            c.save()
            messages.append('Removed from alliance %s: %s' % (alliance.name, c.name))

    return (alliance.id, True, messages)


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

    try:
        results = pool.map(update_alliance, api.eve.AllianceList().alliances)
        for id, worked, messages in results:
            if worked:
                alliance_ids.append(id)
            else:
                print "Failed: %s" % id
                for m in messages:
                    print m
    except Exception, e:
        print str(e)

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
