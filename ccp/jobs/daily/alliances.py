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
        alliance_rows = list()

        try:
            for a in api.eve.AllianceList().alliances:
                alliance_ids.add( a.allianceID )
                alliance_rows.append(a)
        except Exception, e:
            if str(e) == 'EVE backend database temporarily disabled':
                self.log.warn('EVE API taken offline by CCP.')
            else:
                self.log.error('Error refreshing alliances: %s', e)
            return

        for row in alliance_rows:
            try:
                self.update_alliance(row)
            except Exception, e:
                self.log.error('Unhandled exception in alliance refresh: %s', e)

        # And now, remove all of the dead alliances.
        for id in [x[0] for x in Alliance.objects.values_list('pk')]:
            if id not in alliance_ids:
                a = Alliance.objects.get(id=id)
                self.log.info('Removing defunct alliance: %s', a)
                a.delete()

        self.log.debug("Elapsed: %s", datetime.utcnow() - start_time)

    def corp_gor(self, id):
        '''gor stands for Get_or_refresh'''
        try:
            corp = Corporation.objects.get(id=id)
        except Corporation.DoesNotExist:
            self.log.debug('Adding new corp: %d', id)
            corp = Corporation(id=id)
            messages =  corp.refresh()
            corp.messages = messages
            self.log.debug('Corp messgaes: %s', messages)
        return corp

    def update_alliance(self, a):
        self.log.debug('Updating alliance: %s', a.name)

        try:
            alliance = Alliance.objects.get(id=a.allianceID)
        except Alliance.DoesNotExist:
            alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)

        # Check the executor corp, creating if needed.
        corp = self.corp_gor(a.executorCorpID)
        if corp.refresh_failed is True:
            return False

        alliance.executor = corp
        alliance.member_count = a.memberCount
        alliance.save()

        # Refresh all the member corps too. (This includes the exec.)
        members = set()
        for c in a.memberCorporations:
            members.add(c.corporationID)
            corp = self.corp_gor(c.corporationID)
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