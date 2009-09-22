from eve.lib import eveapi
from eve.lib.log import BaseJob
from eve.ccp.models import Alliance, Corporation

from datetime import datetime

class Job(BaseJob):
    help = "Reload all of the alliances and member corporations."
    when = 'daily'

    def execute(self):
        api = eveapi.get_api()
        self.log = self.logger()

        self.log.debug("Starting alliance list...")
        start_time = datetime.utcnow()

        alliance_ids = set()

        try:
            for id in api.eve.AllianceList().alliances:
                alliance_ids.add( id )
        except Exception, e:
            if str(e) == 'EVE backend database temporarily disabled':
                self.log.warn('EVE API taken offline by CCP.')
            else:
                self.log.error('Error refreshing alliances: %s', e)
            return

        for id in alliance_ids:
            try:
                self.update_alliance(id)
            except Exception, e:
                self.log.error('Unhandled exception in alliance refresh: %s', e)

        # And now, remove all of the dead alliances.
        for id in [x[0] for x in Alliance.objects.values_list('pk')]:
            if id not in alliance_ids:
                self.log.info('Removing defunct alliance: %s', a)
                Alliance.objects.filter(pk=id).delete()

        self.log.debug("Elapsed: %s", datetime.utcnow() - start_time)


    def update_alliance(self, a):
        self.log.debug('Updating alliance: %s', a.name)

        try:
            alliance = Alliance.objects.get(id=a.allianceID)
        except Alliance.DoesNotExist:
            alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)

        # Check the executor corp, creating if needed.
        corp_id = a.executorCorpID
        try:
            corp = Corporation.objects.get(id=corp_id)
        except Corporation.DoesNotExist:
            self.log.debug('Adding new corp: %d', corp_id)
            corp = Corporation(id=corp_id)
            messages =  corp.refresh()
            log.debug('Corp messgaes: %s', messages)
            if corp.refresh_failed is True:
                return False

        alliance.executor = corp
        alliance.member_count = a.memberCount
        alliance.save()

        # Refresh all the member corps too. (This includes the exec.)
        members = set()
        for c in a.memberCorporations:
            corp_id = c.corporationID
            members.add(corp_id)
            try:
                corp = Corporation.objects.get(id=corp_id)
            except Corporation.DoesNotExist:
                messages.append('Refreshing new corp: %d' % corp_id)
                corp = Corporation(id=corp_id)
                messages.extend( corp.refresh() )
            if corp.alliance != alliance:
                corp.alliance = alliance
                corp.save()

        for id in [x[0] for x in alliance.corporations.values_list('pk')]:
            if id not in members:
                c = Corporation.objects.get(pk=id)
                c.alliance = None
                c.save()
                self.log.debug('Removed from alliance %s: %s', alliance.name, c.name)

        return True