from django_extensions.management.jobs import DailyJob

from eve.ccp.models import SolarSystem, Faction

import os
os.environ['TZ'] = 'UTC'

from eve.lib import eveapi

from datetime import datetime, timedelta

class Job(DailyJob):
    help = "Load map soverignity."

    def execute(self):
        update_map()

def update_map():
    print 'Starting galaxy map...'
    api = eveapi.get_api()

    for s in api.map.Sovereignty().solarSystems:
        system = SolarSystem.objects.get(pk=s.solarSystemID)
        faction = None
        if s.factionID != 0:
            faction = Faction.objects.get(pk=s.factionID)

        alliance = None
        if s.allianceID != 0:
            alliance = s.allianceID

        # Data cleanup.
        if system.alliance_id == 0:
            system.alliance = None

        constellation_sov = None
        if s.constellationSovereignty != 0:
            constellation_sov = s.constellationSovereignty

        old = datetime.utcnow() - timedelta(days=7)
        old = old.date()

        if system.alliance_id != alliance:
            print("Differing: %s Old: %s, current: %s, new: %s" %
                            (system.name, system.alliance_old_id,
                             system.alliance_id, alliance))
            if alliance != None and system.alliance == None:
                # Don't overwrite old sovereignty data with null.
                pass
            else:
                system.alliance_old = system.alliance
            system.alliance_id = alliance
            system.sov_time = datetime.utcnow()
        elif system.sov_time == None:
            # Set a default time of 2 weeks ago when we have no data.
            # This only should occur when we reload the DB from CCP.
            system.sov_time = datetime.utcnow() - timedelta(days=15)
        elif system.sov_time < old and system.alliance_old != None:
            # You only get a certain time to reclaim it.
            system.alliance_old = None


        system.sov = s.sovereigntyLevel
        system.faction = faction

        constellation = system.constellation
        if constellation.alliance_id != constellation_sov:
            if constellation.sov_time == None:
                constellation.sov_time = datetime.utcnow() - timedelta(days=15)
            else:
                constellation.sov_time = datetime.utcnow()
            constellation.alliance_id = constellation_sov
            constellation.save()

        #print "Saving: %s" % system.name
        system.save()
