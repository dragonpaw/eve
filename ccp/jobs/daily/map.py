from eve.lib.log import BaseJob

from eve.ccp.models import SolarSystem, Faction, Alliance

import os
os.environ['TZ'] = 'UTC'

from eve.lib import eveapi

from datetime import datetime, timedelta

class Job(BaseJob):
    help = "Load map soverignity."
    when = 'daily'

    def execute(self):
        log = self.logger()
        log.info('Starting galaxy map...')
        api = eveapi.get_api()
        old = datetime.utcnow() - timedelta(days=7)

        for s in api.map.Sovereignty().solarSystems:
            system = SolarSystem.objects.get(pk=s.solarSystemID)
            faction = None
            if s.factionID != 0:
                faction = Faction.objects.get(pk=s.factionID)

            if s.allianceID != 0:
                try:
                    alliance = Alliance.objects.get(id=s.allianceID)
                except Alliance.DoesNotExist:
                    log.error('Unable to lookup alliance #%s for map update.', s.allianceID)
                    continue
            else:
                alliance = None

            # Query and cache the alliance.
            try:
                system.alliance
            except Alliance.DoesNotExist:
                log.error('%s: Unable to find existing alliance: %s', system, system.alliance_id)
                system.alliance = None

            # Data cleanup.
            if system.alliance_id == 0:
                log.info('%s: Clearing old system alliance from 0 to None', system)
                system.alliance = None

            #if s.constellationSovereignty != 0:
            #    constellation_sov = s.constellationSovereignty
            #else:
            #    constellation_sov = None

            if system.alliance != alliance:
                log.info("%s: Differing: Old: %s, current: %s, new: %s",
                         system, system.alliance_old_id,
                         system.alliance_id, alliance)
                # Sov is lost in stages. It goes -> None, then to -> New.
                # So if it changed, and there was a current alliance, save
                # them, so we may report on them later.
                if system.alliance:
                    system.alliance_old = system.alliance
                system.alliance = alliance
                system.sov_time = datetime.utcnow()

            if system.sov_time == None:
                log.debug('%s: Setting default time for system.', system)
                # Set a default time of 2 weeks ago when we have no data.
                # This only should occur when we reload the DB from CCP.
                system.sov_time = datetime.utcnow() - timedelta(days=15)

            # Check for a system with an old alliance older than the max.
            if system.sov_time < old and system.alliance_old:
                log.debug('%s: Removing old alliance history.', system)
                # You only get a certain time to reclaim it.
                system.alliance_old = None

            #system.sov = s.sovereigntyLevel
            system.faction = faction

            #constellation = system.constellation
            #if constellation.alliance_id != constellation_sov:
            #    if constellation.sov_time == None:
            #        constellation.sov_time = datetime.utcnow() - timedelta(days=15)
            #
            #    else:
            #        constellation.sov_time = datetime.utcnow()
            #    constellation.alliance_id = constellation_sov
            #    constellation.save()

            system.save()
