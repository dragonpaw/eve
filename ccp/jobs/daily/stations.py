from django_extensions.management.jobs import DailyJob

from eve.ccp.models import Station, Corporation, SolarSystem, Item

from eve.lib import eveapi

class Job(DailyJob):
    help = "Load conquerable stations."

    def execute(self):
        update_stations()

def update_stations():
    print 'Starting outposts...'
    api = eveapi.get_api()

    for s in api.eve.ConquerableStationList().outposts:
        corp_id = s.corporationID
        corp_name = s.corporationName
        try:
            corporation = Corporation.objects.get(id=corp_id)
        except Corporation.DoesNotExist:
            corporation = Corporation(id=corp_id)
            for m in corporation.refresh(name=corp_name):
                print m
        try:
            station = Station.objects.get(id=s.stationID)
        except Station.DoesNotExist:
            print("Added station %s in system: %s" % (s.stationID, s.solarSystemID))
            solarsystem = SolarSystem.objects.get(id=s.solarSystemID)
            station = Station(id=s.stationID, solarsystem=solarsystem,
                              region=solarsystem.region, constellation=solarsystem.constellation)
        station.type = Item.objects.get(id=s.stationTypeID)
        station.name = s.stationName
        station.corporation = corporation
        station.save()
