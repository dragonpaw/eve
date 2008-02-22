#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'
os.environ['TZ'] = 'UTC'

from cachehandler import MyCacheHandler
from datetime import datetime, timedelta
from exceptions import Exception
import eveapi
import time
import pprint
import sys

from eve.ccp.models import Alliance, Station, Corporation, Item, SolarSystem
from eve.user.models import Account
from eve.settings import DEBUG

exit_code = 0
message = ''
start_time = datetime.utcnow()

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-m', '--map', action='store_true',  default=False,
                   help='Load the soverignty map.')
parser.add_option('-a', '--alliances', action='store_true', default=False,
                   help='Load the list of alliances.')
parser.add_option('-s', '--stations', action='store_true', default=False,
                  help='Load the list of conquerable stations/outposts.')
parser.add_option('-u', '--user', 
                  help='Username to load accounts for.')
parser.add_option('-f', '--force', action='store_true', default=False,
                  help='Force reload of cached data.')
parser.add_option('-v', '--verbose', action='store_true', default=False,
                  help='Be a little bit chatty.')
parser.add_option('-d', '--debug', action='store_true', default=DEBUG,
                  help='Be really chatty.')

(options, args) = parser.parse_args()

sp = [0, 250, 1414, 8000, 45255, 256000]

skills = Item.skill_objects.all()
api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=options.debug, throw=False)).context(version=2)

# After this long, we purge a character giving a security error. (So people don't change key
# before leaving a corp to still see data.)
character_security_timeout = timedelta(hours=12) 

def output(msg):
    global message
    message += msg + '\n'
    if options.debug or options.verbose:
        print msg
    
def exit():
    output("Runtime: %s" % (datetime.utcnow() - start_time))
    if exit_code != 0 and not (options.debug or options.verbose):
        print message
    sys.exit(exit_code)
    
def update_alliances():
    output ("Starting alliance list...")
    
    alliance_ids = []
    
    for a in api.eve.AllianceList().alliances:
        try:
            alliance = Alliance.objects.get(id=a.allianceID)
        except Alliance.DoesNotExist:
            alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)
        alliance.member_count = a.memberCount
        alliance.executor_id = a.executorCorpID
        alliance.save()

        alliance_ids.append(alliance.id)
            
        # Cannot use get_or_create, as we cannot immediately save it.
        try:
            corp = Corporation.objects.get(id=a.executorCorpID)
        except Corporation.DoesNotExist:
            corp = Corporation(id=a.executorCorpID)
        messages = corp.refresh(name=a.name)
        
        for m in messages:
            output(m)
        
    # Force immediate evaluation to protect from odd interaction with the cursor
    # while deleting rows.
    delete_me = []
    for a in Alliance.objects.all():
        if a.id in alliance_ids:
            # It still exists.
            continue
        delete_me.append(a)
    for a in delete_me:
        output('Removing defunct alliance: %s' % a.name)
        a.delete()
            
def update_map():
    output ("Starting galaxy map...")
    for s in api.map.Sovereignty().solarSystems:
        system = SolarSystem.objects.get(pk=s.solarSystemID)
        #output ("System: %s" % s.solarSystemName)
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
                
        if system.alliance_id != alliance:
            output ("Differing: %s Old: %s, current: %s, new: %s" % (system.name, system.alliance_old_id,
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
        
        system.save()
    
def update_stations():
    # http://api.eve-online.com//eve/ConquerableStationList.xml.aspx
    # <rowset name="outposts" key="stationID" columns="stationID,stationName,stationTypeID,solarSystemID,corporationID,corporationName">
    # <row stationID="60014926" stationName="The Alamo" stationTypeID="12295" solarSystemID="30004712" corporationID="844498619" corporationName="Tin Foil"/>
    output ('Starting outposts...')
    for s in api.eve.ConquerableStationList().outposts:
        #output ("%s: %s (%s)" % (s.solarSystemID, s.stationName, s.corporationID))
        
        corp_id = s.corporationID
        corp_name = s.corporationName
        try:
            corporation = Corporation.objects.get(id=corp_id)
        except Corporation.DoesNotExist:
            corporation = Corporation(id=corp_id)
        messages = corporation.refresh(name=corp_name)
        for m in messages:
            output(m)
        try:
            station = Station.objects.get(id=s.stationID)
        except Station.DoesNotExist:
            solarsystem = SolarSystem.objects.get(id=s.solarSystemID)
            station = Station(id=s.stationID, solarsystem=solarsystem, 
                              region=solarsystem.region, constellation=solarsystem.constellation)
        station.name = s.stationName
        station.corporation = corporation
        station.save()

if options.alliances:
    try:
        update_alliances()
    except Exception, e:
        output ("Failed! [%s]" % e)
        exit_code = 1
        if DEBUG:
            raise
    
if options.map:
    try:
        update_map()
    except Exception, e:
        output ("Failed! [%s]" % e)
        exit_code = 1
        if DEBUG:
            raise

if options.stations:
    try:
        update_stations()
    except Exception, e:
        output ("Failed! [%s]" % e)
        exit_code = 1
        if DEBUG:
            raise

if options.stations or options.map or options.alliances:
    # We do not load users if we're loading other things.
    exit()


if options.user:
    output ("Only loading characters for: %s" % options.user)
    accounts = Account.objects.filter(user__user__username=options.user)
else:
    accounts = Account.objects.all()
    
for account in accounts:
    try:
        print "-" * 78
        print "Starting: %s(%s)" % (account.user, account.id)
        messages = account.refresh(force=options.force)
        for x in messages:
            output("-- %s" % x['name'])
            output("  " +("\n  ".join(x['messages'])))
    except Exception, e:
        output ("Failed! [%s]" % e)
        if DEBUG:
            raise
        exit_code = 1
   
exit()
