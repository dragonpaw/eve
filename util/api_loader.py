#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'
os.environ['TZ'] = 'UTC'

from eve.lib.cachehandler import MyCacheHandler
from datetime import datetime, timedelta
from exceptions import Exception
from eve.lib import eveapi
import time
import pprint
import sys
import traceback

from eve.ccp.models import Alliance, Station, Corporation, Item, SolarSystem, Faction
from eve.user.models import Account
from eve.settings import DEBUG

character_security_timeout = timedelta(hours=12)

def get_api(debug=DEBUG):
    api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=debug, throw=False)).context(version=2)
    return api

# Depricated
def exit():
    output("Runtime: %s" % (datetime.utcnow() - start_time))
    if exit_code != 0 and not options.verbose:
        print message
    sys.exit(exit_code)

def update_alliances():
    messages = []
    api = get_api()
    messages.append("Starting alliance list...")

    alliance_ids = []

    for a in api.eve.AllianceList().alliances:
        try:
            alliance = Alliance.objects.get(id=a.allianceID)
        except Alliance.DoesNotExist:
            alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)
        alliance.member_count = a.memberCount
        alliance.save()

        # Create the executor corp.
        corp = Corporation(id=a.executorCorpID)
        messages.extend( corp.refresh(name=a.name) )

        # Refresh all the member corps too.
        for c in a.memberCorporations:
            id = c.corporationID
            corp = Corporation(id=id)
            messages.extend( corp.refresh(name=a.name) )


        # Have to set executor and re-save it here to work around constraints.
        # Can't add an alliance unless the exec corp exists first. Can't add a
        # Corp unless the alliance it belongs to exists.
        # So dance is: Make alliance without exec, add corp, set exec.
        if corp.failed is False:
            alliance.executor = corp
            alliance.save()
            alliance_ids.append(alliance.id)
        else:
            messages.append('Alliance refresh failed. Will be deleted.')

    # Force immediate evaluation to protect from odd interaction with the cursor
    # while deleting rows.
    delete_me = []
    for a in Alliance.objects.all():
        if a.id in alliance_ids:
            # It still exists.
            continue
        delete_me.append(a)
    for a in delete_me:
        messages.append('Removing defunct alliance: %s' % a.name)
        a.delete()

    return messages


def update_map():
    messages = ['Starting galaxy map...']
    api = get_api()

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
            messages.append("Differing: %s Old: %s, current: %s, new: %s" %
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

        system.save()
        return messages

def update_stations():
    messages = ['Starting outposts...']
    api = get_api()

    for s in api.eve.ConquerableStationList().outposts:
        corp_id = s.corporationID
        corp_name = s.corporationName
        try:
            corporation = Corporation.objects.get(id=corp_id)
        except Corporation.DoesNotExist:
            corporation = Corporation(id=corp_id)
        messages.extend( corporation.refresh(name=corp_name) )
        try:
            station = Station.objects.get(id=s.stationID)
        except Station.DoesNotExist:
            messages.append("Added station %s in system: %s" % (s.stationID, s.solarSystemID))
            solarsystem = SolarSystem.objects.get(id=s.solarSystemID)
            station = Station(id=s.stationID, solarsystem=solarsystem,
                              region=solarsystem.region, constellation=solarsystem.constellation)
        station.name = s.stationName
        station.corporation = corporation
        station.save()
    return messages

def update_users(user=None, force=False):
    messages = ['Starting user refresh...']
    api = get_api()

    if user:
        messages.append("Only loading characters for: %s" % user)
        accounts = Account.objects.filter(user__user__username=user)
    else:
        accounts = Account.objects.all()

    if force:
        messages.append("Forcing reload, cache times will be ignored.")

    for account in accounts:
        messages.append("Account: %s(%s)" % (account.user, account.id))
        error = False
        m = []
        try:
            messages.extend( account.refresh(force=force) )
        except Exception, e:
            m.append(traceback.format_exc())
            if DEBUG:
                raise

if __name__ == '__main__':
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
    parser.add_option('-d', '--debug', action='store_true', default=DEBUG,
                      help='Be really chatty.')

    (options, args) = parser.parse_args()

    # Debug is also verbose.
    if options.debug:
        DEBUG = True

    # After this long, we purge a character giving a security error. (So people don't change key
    # before leaving a corp to still see data.)

    if options.alliances:
        try:
            for m in update_alliances():
                print
        except Exception, e:
            output ("Failed! [%s]" % e)
            exit_code = 1
            if DEBUG:
                raise

    if options.map:
        try:
            for m in update_map():
                print m
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

    update_users(user=options.user, force=option.force)
