#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.ccp.models import *
from eve.user.models import *
from eve.trade.models import *
from eve.pos.models import *
from eve.settings import DEBUG
import sys

from cachehandler import MyCacheHandler

from datetime import datetime, timedelta
import eveapi
import time
import pprint

import os
os.environ['TZ'] = 'UTC'

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
parser.add_option('-d', '--debug', action='store_true', default=False,
                  help='Be really chatty.')

(options, args) = parser.parse_args()

sp = [0, 250, 1414, 8000, 45255, 256000]

skills = Item.skill_objects.all()
api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=options.debug, throw=False)).context(version=2)

character_cache_time = timedelta(hours=1)
transaction_cutoff = datetime.utcnow() - timedelta(days=30)

# After this long, we purge a character giving a security error. (So people don't change key
# before leaving a corp to still see data.)
character_security_timeout = timedelta(hours=12) 

exit_code = 0

def exit():
    print "Runtime: %s" % (datetime.utcnow() - start_time)
    sys.exit(exit_code)

def auth(d_account):
    """Login as a EVE account."""
    auth = api.auth(userID=d_account.id, apiKey=d_account.api_key)
    return auth

def auth_corp(d_character):
    """Login as a specific character and setup to access the corporation pages."""
    d_account = d_character.account
    auth_o = auth(d_account)
    me = auth_o.corporation(d_character.id)
    return me

def auth_character(d_character):
    """Login as a specific character and setup to access the user's data"""
    d_account = d_character.account
    auth_o = auth(d_account)
    me = auth_o.character(d_character.id)
    return me
    
def update_alliances():
    print "Starting alliance list..."
    corp_to_alliance = {}
    for a in api.eve.AllianceList().alliances:
        try:
            alliance = Alliance.objects.get(id=a.allianceID)
        except Alliance.DoesNotExist:
            alliance = Alliance(id=a.allianceID, name=a.name, ticker=a.shortName)
        alliance.member_count = a.memberCount
        # Save twice so that the update_corporation call below has an alliance to find.
        alliance.save()

            
        try:
            alliance.executor = update_corporation(a.executorCorpID)
        except eveapi.Error, e:
            print "WTF?! Corp %d is executor of alliance '%s' [%d], but not in an alliance?! [%s]" % (
                    a.executorCorpID, a.name, a.allianceID, e)
        alliance.save()
        
    
def update_map():
    print "Starting galaxy map..."
    for s in api.map.Sovereignty().solarSystems:
        system = SolarSystem.objects.get(pk=s.solarSystemID)
        #print "System: %s" % s.solarSystemName
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
            print "Differing: %s Old: %s, current: %s, new: %s" % (system.name, system.alliance_old_id,
                                                                 system.alliance_id, alliance)
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
    
def update_account(d_account):
    assert( isinstance(d_account, Account) )
    print "Account: %s (%d)" % (d_account.user.username, d_account.id)
    
    auth = api.auth(userID=d_account.id, apiKey=d_account.api_key)
    result = auth.account.Characters()

    ids = []
    for c in result.characters:
        ids.append(c.characterID)
        character, created = Character.objects.get_or_create(id = c.characterID,
                                        defaults={'name':c.name,
                                                  'account':d_account,
                                                  'user':d_account.user,
                                                  'last_updated':datetime.utcnow(),
                                                  'cached_until':datetime.utcnow(),
                                                  'corporation_id':c.corporationID})
        character.account = d_account
        character.save()
    
    # Look for deleted characters.
    for character in Character.objects.filter(account__id=d_account.id).exclude(id__in=ids):
        print "Lost character: %s will be purged." % character.name
        character.delete()
    
    d_account.last_refreshed = datetime.now()
    d_account.save()
    
def update_character(character):
    assert( isinstance(character, Character) )

    
    if not options.force and character.cached_until and character.cached_until > datetime.utcnow():
        if options.debug:
            print "Character: %s (%d): Still cached." % (character.name, character.id)
        return
        
    print "Starting Character: %s (%d)" % (character.name, character.id)
    api_data = auth_character(character).CharacterSheet()
    corp = update_corporation(api_data.corporationID, name=api_data.corporationName)
    try:
        auth = auth_corp(character)
        auth.StarbaseList()
        character.is_director = True
    except eveapi.Error, e:
        if e.message == 'Character must be a Director or CEO':
            character.is_director = False
            print "Not Director."

    character.name = api_data.name
    character.corporation = corp
    # We set the account earlier in update_account. Now just make sure it matches.
    # USernames can change, or a character might move between accounts.
    character.user = character.account.user
    character.last_updated = datetime.utcnow()
    character.cached_until = datetime.utcnow() + character_cache_time
    character.save()
    
    update_character_wallet(character)
    update_character_skills(character)
    update_character_transactions(character)

def update_character_wallet(d_character):
    assert( isinstance(d_character, Character) )
    
    me = auth_character(d_character)
    
    wallet = me.AccountBalance()
    d_character.isk = wallet.accounts[0].balance
    d_character.save()

def update_character_skills(d_character):
    assert( isinstance(d_character, Character) )
    
    me = auth_character(d_character)
    
    training = me.SkillInTraining()
    if training.skillInTraining:
        t = datetime.fromtimestamp(training.trainingEndTime) 
        skill = Item.objects.get(pk=training.trainingTypeID)
        
        d_character.training_skill = skill
        d_character.training_level = training.trainingToLevel
        d_character.training_completion = t
    else:
        d_character.training_skill = None
        d_character.training_level = None
        d_character.training_completion = None
    d_character.save()
        
    sheet = me.CharacterSheet()
    for d_skill in skills:
        trained = sheet.skills.Get(d_skill.id, False)
        if trained:
#            if DEBUG:
#                print "- %s Rank(%d) - SP: %d/%d - Level: %d" %\
#                (d_skill.name, d_skill.skill_rank, trained.skillpoints, (d_skill.skill_rank * sp[trained.level]), trained.level)
#                
            try:
                obj = SkillLevel.objects.get(character = d_character, skill = d_skill)
                obj.points = trained.skillpoints
                obj.level = trained.level
            except SkillLevel.DoesNotExist:
                obj = SkillLevel(character = d_character, skill = d_skill,
                                 level = trained.level, points = trained.skillpoints)
            obj.save()
                    
def update_character_transactions(d_character):
    assert( isinstance(d_character, Character) )
    
    me = auth_character(d_character)
    
    last_id = 0
    stopping_time = time.time() - (60*60*24*7)
    qty = 0
    while qty==0 or (len(wallet.transactions) == 1000 and last_time > stopping_time):
        if last_id == 0:
            print "Loading first wallet."
            wallet = me.WalletTransactions()
        else:
            print "Loading wallet before %d" % last_id
            wallet = me.WalletTransactions(beforeTransID=last_id)
        for t in wallet.transactions:
            try:
                Transaction.objects.get(character = d_character, transaction_id = t.transactionID)
                print "Loaded %d new transactions." % qty
                return
            except Transaction.DoesNotExist:
                pass
        
            update_character_transactions_single(d_character, t)
            last_id = t.transactionID
            last_time = t.transactionDateTime
            qty+=1
        if last_id == 0:
            print "No transactions to load."
            return

def update_character_transactions_single(d_character, t):
    if t.transactionType == 'buy':
        sold = False
    else:
        sold = True

#    if DEBUG:
#        print "%s sales yielded %.2f ISK since %s" %\
#        (t.typeName, t.quantity, time.asctime(time.gmtime(t.transactionDateTime)))
                    
    item = Item.objects.get(pk=t.typeID)
    station = Station.objects.get(id=t.stationID)
            
    obj = Transaction(character = d_character,
                      transaction_id = t.transactionID,
                      sold = sold,
                      item = item,
                      price = t.price,
                      quantity = t.quantity,
                      station =  station,
                      region = station.region,
                      time = datetime(*time.gmtime(t.transactionDateTime)[0:5]),
                      client = t.clientName,
                      )
    obj.save()

def update_corporation(id, name=None):
    # http://api.eve-online.com/eve/AllianceList.xml.aspx
    # http://api.eve-online.com/corp/CorporationSheet.xml.aspx?version=2&corporationID=483314419
    #try:
    #    r = api.corp.CorporationSheet(corporationID=id)
    #except eveapi.Error, e:
    #    pass
    i = Item.objects.get(name='Corporation')
    # Fuckall if I can find where it is in the DB.
    # ticker = r.ticker
    api_corp = None 
    try:
        api_corp = api.corp.CorporationSheet(corporationID=id)
        name = api_corp.corporationName
    except eveapi.Error:
        pass
            
    try:
        corp = Corporation.objects.get(pk=id)
    except Corporation.DoesNotExist:
        if name == None:
            print "Unable to add %s to corp DB, no name available." % id
            return
            
        name = Name(id=id, name=name, type=i, group=i.group, category=i.group.category)
        name.save()
        print "Added: %s to name database. [%d]" % (name.name, name.id)
        corp = Corporation(name=name, id=id)
        print "Added: %s to corp database. [%d]" % (name.name, id)

    if api_corp:
        corp.alliance = Alliance.objects.get(pk=api_corp.allianceID) 
    
    corp.save()
    #print "%s [%s]" % (corp.name, corp.id)
    #corp.shares = r.shares
    
    #corp.save()
    return corp
    
def update_stations():
    # http://api.eve-online.com//eve/ConquerableStationList.xml.aspx
    # <rowset name="outposts" key="stationID" columns="stationID,stationName,stationTypeID,solarSystemID,corporationID,corporationName">
    # <row stationID="60014926" stationName="The Alamo" stationTypeID="12295" solarSystemID="30004712" corporationID="844498619" corporationName="Tin Foil"/>
    print 'Starting outposts...'
    for s in api.eve.ConquerableStationList().outposts:
        #print "%s: %s (%s)" % (s.solarSystemID, s.stationName, s.corporationID)
        
        corporation = update_corporation(s.corporationID, name=s.corporationName)

        try:
            station = Station.objects.get(id=s.stationID)
        except Station.DoesNotExist:
            solarsystem = SolarSystem.objects.get(id=s.solarSystemID)
            station = Station(id=s.stationID, solarsystem=solarsystem, 
                              region=solarsystem.region, constellation=solarsystem.constellation)
        station.name = s.stationName
        station.corporation = corporation
        station.save()

def update_poses(character):
    assert( isinstance(character, Character) )
    
    auth = auth_corp(character)
    corp = character.corporation
    
    ids = []
    for s in auth.StarbaseList().starbases:
        ids.append(s.itemID)
        update_pos_detail(auth, s, corp)
    character.is_director = True
    character.save()
    
    # Look for POSes that got taken down.
    for pos in PlayerStation.objects.filter(corporation=corp).exclude(id__in=ids):
        print "Removed POS: %s will be purged." % pos.moon
        pos.delete()

        
def update_pos_detail(auth, api, corp):
    try:
        station = PlayerStation.objects.get(pk=api.itemID)
    except PlayerStation.DoesNotExist:
        station = PlayerStation(id=api.itemID)
        station.depot = ""

    moon = MapDenormalize.objects.get(id=api.moonID)
    tower = Item.objects.get(pk=api.typeID)

    if not options.force and station.cached_until and station.cached_until > datetime.utcnow():
        if options.debug:
            print "POS: %s at %s: Still cached." % (tower, moon)
        return

    
    print "POS: %s at %s" % (tower, moon)

    detail = auth.StarbaseDetail(itemID=api.itemID)

    station.tower = tower
    station.corporation = corp
    station.moon = moon
    station.solarsystem = SolarSystem.objects.get(id=api.locationID)
    station.constellation = station.moon.constellation        
    station.region = station.moon.region
    
    state_time = datetime(*time.gmtime(api.stateTimestamp)[0:5])
    online_time = datetime(*time.gmtime(api.onlineTimestamp)[0:5])
    hours_since_update = state_time - station.state_time
    hours_since_update = hours_since_update.seconds / 60**2
    
    station.state = api.state
    station.online_time = online_time
    station.state_time = state_time
    
    station.corporation_use = detail.generalSettings.allowCorporationMembers == 1
    station.alliance_use = detail.generalSettings.allowAllianceMembers == 1
    station.claim = detail.generalSettings.claimSovereignty == 1
    station.usage_flags = detail.generalSettings.usageFlags
    station.deploy_flags = detail.generalSettings.deployFlags
    
    station.attack_aggression = detail.combatSettings.onAggression.enabled == 1
    station.attack_atwar= detail.combatSettings.onCorporationWar.enabled == 1
    station.attack_secstatus_flag = detail.combatSettings.onStatusDrop.enabled == 1
    station.attack_secstatus_value = detail.combatSettings.onStatusDrop.standing / 100.0
    station.attack_standing_flag = detail.combatSettings.onStandingDrop.enabled == 1
    station.attack_standing_value = detail.combatSettings.onStandingDrop.standing / 100.0

    station.cached_until = datetime.utcfromtimestamp(detail._meta.cachedUntil)
    station.last_updated = datetime.utcnow()

    station.save()
    station.setup_fuel_supply()
    
    # Now, the fuel.
    for fuel_type in detail.fuel:
        type = Item.objects.get(id=fuel_type.typeID)
        fuel = PlayerStationFuelSupply.objects.get(type=type, station=station)
        
        purpose = fuel.purpose
        consumed = (fuel.quantity - fuel_type.quantity)
        max = Decimal(fuel.max_consumption)
        if options.debug:
            print "P: '%s'; H: %s; C: %s, Max: %s/hr" % (purpose, hours_since_update, consumed, max) 
        if (purpose == 'CPU' or purpose == 'Power') and hours_since_update > 0:
            consumed /= hours_since_update
            if consumed > 0 and consumed < max:
                if purpose == 'CPU':
                    station.cpu_utilization = consumed / max
                    print "CPU Utilization: %s" % station.cpu_utilization
                else:
                    station.power_utilization = consumed / max
                    print "Power Utilization: %s" % station.power_utilization
                station.save()
        
        
        fuel.quantity=fuel_type.quantity
        fuel.save()

start_time = datetime.utcnow()
if options.alliances:
    try:
        update_alliances()
    except eveapi.Error, e:
        print "Failed! [%s]" % e
        exit_code = 1
    
if options.map:
    try:
        update_map()
    except eveapi.Error, e:
        print "Failed! [%s]" % e
        exit_code = 1

if options.stations:
    try:
        update_stations()
    except eveapi.Error, e:
        print "Failed! [%s]" % e
        exit_code = 1

if options.stations or options.map or options.alliances:
    # We do not load users if we're loading other things.
    exit()


if options.user:
    print "Only loading characters for: %s" % options.user
    accounts = Account.objects.filter(user__user__username=options.user)
else:
    accounts = Account.objects.all()
    
for account in accounts:
    try:
        update_account(account)
    except eveapi.Error, e:
        if (e.message == 'Authentication failure' 
            and account.last_refreshed + character_security_timeout < datetime.utcnow() ):
            print "This account has had an invalid API key for too long. Deleting..."
            account.delete()
             
        print "Failed! [%s]" % e
        exit_code = 1

# Now, the characters.
if options.user:
    characters = Character.objects.filter(user__user__username=options.user)
else:
    characters = Character.objects.all()
    
for character in characters:
    try:
        update_character(character)
    except eveapi.Error, e:
        print "Failed! [%s]" % e
        exit_code = 1

old = Transaction.objects.filter(time__lt=transaction_cutoff)
print "Purging %d old transactions..." % old.count()
old.delete()

if options.user:
    profiles = [ UserProfile.objects.get(name=options.user) ]
else:
    profiles = UserProfile.objects.all()
    
for profile in profiles:
    print "Updating personal index: %s" % profile
    profile.update_personal_index()    


if options.user:
    directors = []
    for c in Character.objects.filter(user__user__username=options.user):
        if c.is_director:
            directors.append(c)
else:
    directors = Character.objects.filter(is_director=True)

for character in directors:
    try:
        update_poses(character)
    except eveapi.Error, e:
        print "Failed! [%s]" % e
        exit_code = 1
        
exit()