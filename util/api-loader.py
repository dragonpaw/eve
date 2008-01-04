from eve.ccp.models import *
from eve.user.models import *
from eve.trade.models import *
from eve.pos.models import *
from sys import exit

from cachehandler import MyCacheHandler

from datetime import datetime
import eveapi
import time
import pprint

import os
os.environ['TZ'] = 'UTC'

sp = [0, 250, 1414, 8000, 45255, 256000]
debug = False

skills = Item.skill_objects.all()
api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True))

def auth(d_account):
    auth = api.auth(userID=d_account.id, apiKey=d_account.api_key)
    return auth

def auth_corp(d_character):
    d_account = d_character.account
    auth_o = auth(d_account)
    me = auth_o.corporation(d_character.id)
    return me

def auth_character(d_character):
    d_account = d_character.account
    auth_o = auth(d_account)
    me = auth_o.character(d_character.id)
    return me
    
def update_account(d_account):
    assert( isinstance(d_account, Account) )
    print "Starting Account: %s (%d)" % (d_account.user.username, d_account.id)
    
    auth = api.auth(userID=d_account.id, apiKey=d_account.api_key)
    result = auth.account.Characters()

    for c in result.characters:
        update_character(d_account, c)
        
    d_account.last_refreshed = datetime.now()
    d_account.save()
    
    
    
def update_character(d_account, character):
    assert( isinstance(d_account, Account) )
    assert( isinstance(character, eveapi.Row) )
    print "Starting Character: %s (%d)" % (character.name, character.characterID)
    
    # Django create/lookup.
    try:
        d_character = Character.objects.get(id = character.characterID)
        d_character.account = d_account
        d_character.name = character.name
    except Character.DoesNotExist:
        d_character = Character(id = character.characterID,
                                name = character.name,
                                account = d_account)
    corp = update_corporation(character.corporationID, character.corporationName)
    d_character.corporation = corp
    d_character.user = d_account.user
    d_character.save()
    update_character_wallet(d_character)
    update_character_skills(d_character)
    update_character_transactions(d_character)
    update_pos(d_character, corp)

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
        print "Training: %s, End Time: %s" % (training.skillInTraining,
                                              training.trainingEndTime)
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
            if debug:
                print "- %s Rank(%d) - SP: %d/%d - Level: %d" %\
                (d_skill.name, d_skill.skill_rank, trained.skillpoints, (d_skill.skill_rank * sp[trained.level]), trained.level)
                
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
    
    wallet = me.WalletTransactions()
    last_id = 0
    stopping_time = time.time() - (60*60*24*7)
    for t in wallet.transactions:
        update_character_transactions_single(d_character, t)
        last_id = t.transactionID
        last_time = t.transactionDateTime
    qty = len(wallet.transactions)
    try:
        while len(wallet.transactions) == 1000 and last_time > stopping_time:
            wallet = me.WalletTransactions(beforeTransID=last_id)
            qty = qty + len(wallet.transactions)
            for t in wallet.transactions:
                update_character_transactions_single(d_character, t)
                last_id = t.transactionID
                last_time = t.transactionDateTime
    except eveapi.Error, e:
        print "Oops! eveapi returned the following error:"
        print "code:", e.code
        print "message:", e.message
    print "last ID: %s, qty: %d" % (last_id, qty)    

def update_character_transactions_single(d_character, t):
    try:
        obj = Transaction.objects.get(character = d_character,
                                      transaction_id = t.transactionID)
    except Transaction.DoesNotExist:
        if t.transactionType == 'buy':
            sold = False
        else:
            sold = True

        if debug:
            print "%s sales yielded %.2f ISK since %s" %\
            (t.typeName, t.quantity, time.asctime(time.gmtime(t.transactionDateTime)))
                    
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

def update_corporation(id, name):
    # http://api.eve-online.com/eve/AllianceList.xml.aspx
    # http://api.eve-online.com/corp/CorporationSheet.xml.aspx?version=2&corporationID=XXXXXXXXX
    #try:
    #    r = api.corp.CorporationSheet(corporationID=id)
    #except eveapi.Error, e:
    #    pass
    i = Item.objects.get(name='Corporation')
    # Fuckall if I can find where it is in the DB.
    # ticker = r.ticker 
    try:
        corp = Corporation.objects.get(pk=id)
    except Corporation.DoesNotExist:
        name = Name(id=id, name=name, type=i, group=i.group, category=i.group.category)
        name.save()
        print "Added: %s to name database. [%d]" % (name.name, name.id)
        corp = Corporation(name=name, id=id)
        corp.save()
        print "Added: %s to corp database. [%d]" % (name.name, id)
    #print "%s [%s]" % (corp.name, corp.id)
    #corp.shares = r.shares
    
    #corp.save()
    return corp
    
def update_stations():
    # http://api.eve-online.com//eve/ConquerableStationList.xml.aspx
    # <rowset name="outposts" key="stationID" columns="stationID,stationName,stationTypeID,solarSystemID,corporationID,corporationName">
    # <row stationID="60014926" stationName="The Alamo" stationTypeID="12295" solarSystemID="30004712" corporationID="844498619" corporationName="Tin Foil"/>

    for s in api.eve.ConquerableStationList().outposts:
        print "%s: %s (%s)" % (s.solarSystemID, s.stationName, s.corporationID)
        
        corporation = update_corporation(s.corporationID, s.corporationName)
        try:
            station = Station.objects.get(id=s.stationID)
        except Station.DoesNotExist:
            solarsystem = SolarSystem.objects.get(id=s.solarSystemID)
            station = Station(id=s.stationID, name=s.stationName, solarsystem=solarsystem, 
                              region=solarsystem.region, constellation=solarsystem.constellation)
            station.save()
            print "Added station '%s' to DB. [%d]" % (station.name, station.id)

def update_pos(character, corp):
    assert( isinstance(character, Character) )
    
    auth = auth_corp(character)
    
    try:
        for s in auth.StarbaseList().starbases:
            detail = auth.StarbaseDetail(itemID=s.itemID)
            update_pos_detail(s, detail, corp)
        character.is_director = True
        character.save()
    except eveapi.Error, e:
        if e.message == 'Character must be a Director or CEO':
            character.is_director = False
            character.save()
            print "Not Director."
            return;
        
def update_pos_detail(api, detail, corp):
    print "POS: %d=%d at %s[%s] Online:%s" % (api.itemID, api.typeID, api.locationID, 
                                              api.moonID, api.onlineTimestamp)
    try:
        station = PlayerStation.objects.get(pk=api.itemID)
    except PlayerStation.DoesNotExist:
        station = PlayerStation(id=api.itemID)
        station.depot = ""

    station.tower = Item.objects.get(pk=api.typeID)
    station.corporation = corp
    station.moon = MapDenormalize.objects.get(id=api.moonID)
    station.solarsystem = SolarSystem.objects.get(id=api.locationID)
    station.constellation = station.moon.constellation        
    station.region = station.moon.region
    
    station.state = api.state
    station.online_time = datetime(*time.gmtime(api.onlineTimestamp)[0:5])
    station.state_time = datetime(*time.gmtime(api.stateTimestamp)[0:5])
    
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

    station.save()
    
    #print dir(api)
    
    # Now, the fuel.
    PlayerStationFuelSupply.objects.filter(station=station).delete()
    for fuel in detail.fuel:
        type = Item.objects.get(id=fuel.typeID)
        fuel = PlayerStationFuelSupply(type=type, station=station, quantity=fuel.quantity)
        fuel.solarsystem = SolarSystem.objects.get(id=api.locationID)
        fuel.constellation = station.moon.constellation        
        fuel.region = station.moon.region
        fuel.corporation = corp
        fuel.save()
        
update_stations()
for d_account in Account.objects.all():
    update_account(d_account)
        
