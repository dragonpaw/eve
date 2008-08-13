'''
# Copy all data from production DB.
>>> from django.db import connection
>>> cursor = connection.cursor()
>>> _ = cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
>>> _ = cursor.execute("INSERT ccp_race SELECT * FROM eve.ccp_race")
>>> _ = cursor.execute("INSERT ccp_graphic SELECT * FROM eve.ccp_graphic")
>>> _ = cursor.execute("INSERT ccp_category SELECT * FROM eve.ccp_category")
>>> _ = cursor.execute("INSERT ccp_group SELECT * FROM eve.ccp_group")
>>> _ = cursor.execute("INSERT ccp_marketgroup SELECT * FROM eve.ccp_marketgroup")
>>> _ = cursor.execute("INSERT ccp_item SELECT * FROM eve.ccp_item")
>>> _ = cursor.execute("INSERT ccp_attribute SELECT * FROM eve.ccp_attribute")
>>> _ = cursor.execute("INSERT ccp_material SELECT * FROM eve.ccp_material")
>>> _ = cursor.execute("INSERT ccp_blueprintdetail SELECT * FROM eve.ccp_blueprintdetail")
>>> _ = cursor.execute("INSERT ccp_station SELECT * FROM eve.ccp_station")
>>> _ = cursor.execute("INSERT ccp_region SELECT * FROM eve.ccp_region")
>>> _ = cursor.execute("INSERT ccp_solarsystem SELECT * FROM eve.ccp_solarsystem")
>>> _ = cursor.execute("INSERT ccp_constellation SELECT * FROM eve.ccp_constellation")
>>> _ = cursor.execute("INSERT ccp_faction SELECT * FROM eve.ccp_faction")
>>> _ = cursor.execute("CREATE TABLE ccp_typeattribute SELECT * FROM eve.ccp_typeattribute")
>>> _ = cursor.execute("INSERT trade_journalentrytype SELECT * FROM eve.trade_journalentrytype")

>>> _ = cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
>>> _ = cursor.execute("COMMIT")
'''

from decimal import Decimal
from django.db import models
from django.db.models.query import Q, QNot
from django.template.defaultfilters import slugify
from eve.settings import DEBUG
from eve.lib import eveapi
from eve.lib.alliance_graphics import alliance_graphics
from eve.lib.formatting import comma, time, unique_slug
from eve.lib.cachehandler import MyCacheHandler

TRUE_FALSE = (
    ('true', 'Yes'), 
    ('false', 'No'), 
)
API = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=DEBUG, throw=False)).context(version=2)

class Agent(models.Model):
    id = models.IntegerField(primary_key=True, db_column='agentid')
    division = models.ForeignKey('CorporationDivision', null=True, blank=True, 
                                 db_column='divisionid')
    corporation = models.ForeignKey('Corporation', null=True, blank=True, 
                                    raw_id_admin=True, db_column='corporationid')
    station = models.ForeignKey('Station', null=True, blank=True, 
                                db_column='stationid', raw_id_admin=True)
    level = models.IntegerField(null=True, blank=True)
    quality = models.IntegerField(null=True, blank=True)
    agenttype = models.ForeignKey('AgentType', db_column='agenttypeid')
    class Meta:

        ordering = ('id',)

    class Admin:
        search_fields = ('id',)
        list_display = ('id', 'name', 'corporation', 'division', 'station')

    def get_name(self):
        obj = Name.objects.get(pk=self.id)
        return obj.name
    name = property(get_name)
    
    def __str__(self):
        return self.name
        
class AgentType(models.Model):
    id = models.IntegerField(primary_key=True, db_column='agenttypeid')
    agenttype = models.CharField(max_length=150)
    class Meta:

        ordering = ('id',)

    class Admin:
        search_fields = ('id',)
        list_display = ('id', 'agenttype')
 
    def __str__(self):
        return self.agenttype
    
class Alliance(models.Model):
    name = models.CharField(max_length=100)
    executor = models.ForeignKey('Corporation', blank=True, null=True, related_name='executors')
    ticker = models.CharField(max_length=10)
    member_count = models.IntegerField()
    slug = models.SlugField(max_length=100)
    objects = models.Manager()
    
    class Admin:
        search_fields = ('name', 'ticker')
        list_display = ('name', 'executor', 'ticker', 'member_count')
    
    class Meta:
        ordering = ('name',)
    
    def __str__(self):
        return self.name

    @property
    def icon16(self):
        return self.get_icon(16)

    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def icon64(self):
        return self.get_icon(64)

    @property
    def icon128(self):
        return self.get_icon(128)

    def get_icon(self, size):
        if alliance_graphics.has_key(self.id):
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, alliance_graphics[self.id])
        else:
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, '01_01')
    
    def save(self):
        self.slug = unique_slug(self)
        super(Alliance, self).save()
        
    def delete(self):
        # Break the links to the alliance, so they are clean, and don't 
        # get cascade deleted.
        print "Braking all links for alliance '%s'." % self.name
        print "Unlinking executor corp."
        self.executor = None
        self.save()
        for c in self.corporations.all():
            print "Breaking link to corp '%s'" % c.name
            c.alliance = None
            c.save()
        for s in self.solarsystems_lost.all():
            print "Removing alliance from old sov in: %s" % s
            s.alliance_old = None
            s.save()
        for s in self.solarsystems.all():
            print "Removing alliance from new sov in: %s" % s
            s.alliance = None
            s.save()
        for c in self.constellations.all():
            print "Removing alliance from sov in constellation: %s" % c
            c.alliance = None
            c.save()
        super(Alliance, self).delete()
    
# class Agent_config(models.Model):
#     id = models.IntegerField(primary_key=True, db_column='agentid')
#     k = models.CharField(max_length=150)
#     v = models.TextField()
#     class Meta:
#         db_table = u'agtconfig'

class CharacterAncestry(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ancestryid')
    name = models.CharField(max_length=300, db_column='ancestryname')
    bloodline = models.ForeignKey('CharacterBloodline', db_column='bloodlineid')
    description = models.TextField()
    perception = models.IntegerField()
    willpower = models.IntegerField()
    charisma = models.IntegerField()
    memory = models.IntegerField()
    intelligence = models.IntegerField()
    skill_1 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, related_name='ca_s1', 
                               db_column='skilltypeid1')
    skill_2 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, related_name='ca_s2', 
                               db_column='skilltypeid2')
    item_1 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, related_name='ca_i1', 
                               db_column='typeid')
    item_2 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, related_name='ca_i2', 
                               db_column='typeid2')
    item_quantity_1 = models.IntegerField(null=True, blank=True, db_column='typequantity')
    item_quantity_2 = models.IntegerField(null=True, blank=True, db_column='typequantity2')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    shortdescription = models.TextField()
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'description')
 
    def __str__(self):
        return self.name

class CharacterAttribute(models.Model):
    id = models.IntegerField(primary_key=True, db_column='attributeid')
    name = models.CharField(max_length=300, db_column='attributename')
    description = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    shortdescription = models.TextField()
    notes = models.TextField()
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'description')
 
    def __str__(self):
        return self.name

class CharacterBloodline(models.Model):
    id = models.IntegerField(primary_key=True, db_column='bloodlineid')
    name = models.CharField(max_length=300, db_column='bloodlinename')
    race = models.ForeignKey('Race', db_column='raceid')
    description = models.TextField()
    maledescription = models.TextField()
    femaledescription = models.TextField()
    ship = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, related_name='bloodline_ship', 
                               db_column='shiptypeid')
    corporation = models.ForeignKey('Corporation', raw_id_admin=True, 
                                    db_column='corporationid')
    perception = models.IntegerField()
    willpower = models.IntegerField()
    charisma = models.IntegerField()
    memory = models.IntegerField()
    intelligence = models.IntegerField()
    bonus = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, 
                               related_name='bloodline_bonus', 
                               db_column='bonustypeid')
    skill_1 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, 
                               related_name='bloodline_skill1', 
                               db_column='skilltypeid1')
    skill_2 = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, 
                               related_name='bloodline_skill2', 
                               db_column='skilltypeid2')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    shortdescription = models.TextField()
    shortmaledescription = models.TextField()
    shortfemaledescription = models.TextField()
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'description')
 
    def __str__(self):
        return self.name

class CharacterCareer(models.Model):
    id = models.IntegerField(primary_key=True, db_column='careerid')
    race = models.ForeignKey('Race', db_column='raceid')
    name = models.CharField(max_length=300, db_column='careername')
    description = models.TextField()
    shortdescription = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    school = models.ForeignKey('School', null=True, blank=True, related_name='careers', 
                               raw_id_admin=True, db_column='schoolid')
    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'school', 'description')
 
    def __str__(self):
        return self.name

# class Character_careerskills(models.Model):
#     careerid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerskills'

class CharacterCareerSpeciality(models.Model):
    id = models.IntegerField(primary_key=True, db_column='specialityid')
    career = models.ForeignKey('CharacterCareer', db_column='careerid')
    name = models.CharField(max_length=300, db_column='specialityname')
    description = models.TextField()
    shortdescription = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    departmentid = models.IntegerField(null=True, blank=True)
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'career', 'description')
 
    def __str__(self):
        return self.name

# class Character_careerspecialityskills(models.Model):
#     specialityid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerspecialityskills'

class Faction(models.Model):
    """Table describes the major factions in game: 
        
    Amaar Empire
    CONCORD Assembly
    ...
    Thukker Tribe"""
    id = models.IntegerField(primary_key=True, db_column='factionid')
    name = models.CharField(max_length=100, db_column='factionname')
    description = models.CharField(max_length=1000, null=True)
    raceids = models.IntegerField(null=True, blank=True)
    solarsystem = models.ForeignKey('SolarSystem', null=True, blank=True, 
                                    db_column='solarsystemid', related_name='home_system')
    corporation = models.ForeignKey('Corporation', null=True, blank=True, 
                                    db_column='corporationid', related_name='corporations')
    sizefactor = models.FloatField(null=True, blank=True)
    stationcount = models.IntegerField(null=True, blank=True)
    stationsystemcount = models.IntegerField(null=True, blank=True)
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name', 'id')
        list_display = ('name', 'description') 
        
    def __str__(self):
        return self.name
    
    def iconid(self):
        ids = {
               'Caldari State':'caldari', 
               'Minmatar Republic':'minmatar', 
               'Gallente Federation':'gallente', 
               'Amarr Empire':'amarr', 
               'Khanid Kingdom':'khanid-kingdom', 
               'CONCORD Assembly':'concord', 
               'Ammatar Mandate':'ammatar', 
               'Jove Empire':'jovian-directorate', 
               'The Syndicate':'intaki-syndicate', 
               'Guristas Pirates':'guristas', 
               'Angel Cartel':'angel-cartel', 
               'The Blood Raider Covenant':'', 
               'The InterBus':'interbus', 
               'ORE':'ore', 
               'Thukker Tribe':'thukker-tribe', 
               'The Servant Sisters of EVE':'soe', 
               'The Society':'society-of-conscious', 
               "Mordu's Legion Command":"mordus-legion", 
               "Sansha's Nation":'sanshas-nation', 
               'Serpentis':'serpentis', 
        }
        
        if ids.has_key(self.name):
            return ids[self.name]
        else:
            return None

    def get_icon(self, size):
        id = self.iconid()
        if id is None:
            return None
        else:
            return "/static/ccp-icons/corporation/%s-%s.jpg" % (id, size)
        
    @property
    def icon32(self):
        return self.get_icon(32)

class Race(models.Model):
    """Table contains the basic races in the game:
        
    Amaar
    Gallente
    Jove"""
    id = models.IntegerField(primary_key=True, db_column='raceid')
    name = models.CharField(max_length=300, db_column='racename')
    description = models.TextField()
    skilltypeid1 = models.IntegerField(null=True, blank=True)
    typeid = models.IntegerField(null=True, blank=True)
    typequantity = models.IntegerField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid', raw_id_admin=True)
    shortdescription = models.TextField()
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name', 'id')
        list_display = ('name', 'description') 
        
    def __str__(self):
        return self.name

    def delete(self):
        raise 'ERROR: Tried to remove an immutable.'

# class Character_raceskills(models.Model):
#     race = models.ForeignKey(Race, null=True, blank=True, db_column='raceid')
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrraceskills'
# 
# class Character_schoolagents(models.Model):
#     schoolid = models.IntegerField(null=True, blank=True)
#     agentindex = models.IntegerField(null=True, blank=True)
#     agentid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'chrschoolagents'

class School(models.Model):
    id = models.IntegerField(primary_key=True, db_column='schoolid')
    race = models.ForeignKey(Race, null=True, blank=True, db_column='raceid')
    name = models.CharField(max_length=300, db_column='schoolname')
    description = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                db_column='graphicid', raw_id_admin=True)
    corporation = models.ForeignKey('Corporation', null=True, blank=True, 
                                    db_column='corporationid', raw_id_admin=True)
    agent = models.ForeignKey('Agent', null=True, blank=True, 
                              db_column='agentid', raw_id_admin=True)
    newagent = models.ForeignKey('Agent', null=True, blank=True, 
                                 db_column='newagentid', 
                                 related_name='charactershool_new_set', 
                                 raw_id_admin=True)
    career = models.ForeignKey('CharacterCareer', null=True, blank=True, related_name='schools', 
                                db_column='careerid')
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name') 
        
    def __str__(self):
        return self.name
        
class CorporationActivity(models.Model):
    id = models.IntegerField(primary_key=True, db_column='activityid')
    name = models.CharField(max_length=300, db_column='activityname')
    description = models.TextField()
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name')
        
    def __str__(self):
        return self.name
        
# class Crpnpccorporationdivisions(models.Model):
#     corporationid = models.IntegerField()
#     divisionid = models.IntegerField()
#     divisionnumber = models.IntegerField()
#     size = models.IntegerField(null=True, blank=True)
#     leaderid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'crpnpccorporationdivisions'

# class Crpnpccorporationresearchfields(models.Model):
#     skillid = models.IntegerField()
#     corporationid = models.IntegerField()
#     suppliertype = models.IntegerField()
#     class Meta:
#         db_table = u'crpnpccorporationresearchfields'

class Corporation(models.Model):
    id = models.IntegerField(primary_key=True, db_column='corporationid')
    #mainactivity = models.ForeignKey('CorporationActivity',
    #                                 db_column='mainactivityid',
    #                                 related_name='corp_activity_1')
    #secondaryactivity = models.ForeignKey('CorporationActivity',
    #                                      db_column='secondaryactivityid',
    #                                      related_name='corp_activity_2',
    #                                      null=True, blank=True)
    #size = models.CharField(max_length=3)
    #extent = models.CharField(max_length=3)
    #solarsystem = models.ForeignKey('SolarSystem', null=True, blank=True,
    #                                db_column='solarsystemid', raw_id_admin=True)
#    investorid1 = models.IntegerField(null=True, blank=True)
#    investorshares1 = models.IntegerField()
#    investorid2 = models.IntegerField(null=True, blank=True)
#    investorshares2 = models.IntegerField()
#    investorid3 = models.IntegerField(null=True, blank=True)
#    investorshares3 = models.IntegerField()
#    investorid4 = models.IntegerField(null=True, blank=True)
#    investorshares4 = models.IntegerField()
#    friend = models.ForeignKey('Name', null=True, blank=True,
#                               db_column='friendid', related_name='friends',
#                               raw_id_admin=True)
#    enemy = models.ForeignKey('Name', null=True, blank=True,
#                              db_column='enemyid', related_name='enemies',
#                              raw_id_admin=True)
    publicshares = models.IntegerField(default=0)
    #initialprice = models.IntegerField()
    #minsecurity = models.FloatField()
    #scattered = models.CharField(max_length=15)
    #fringe = models.IntegerField()
    #corridor = models.IntegerField()
    #hub = models.IntegerField()
    #border = models.IntegerField()
    faction = models.ForeignKey('Faction', db_column='factionid', 
                                related_name='corporations', null=True)
    #sizefactor = models.FloatField()
    #stationcount = models.IntegerField()
    #stationsystemcount = models.IntegerField()
    alliance = models.ForeignKey(Alliance, null=True, related_name='corporations')
    last_updated = models.DateTimeField(blank=True, null=True)
    cached_until = models.DateTimeField(blank=True, null=True)
    
    class Meta:

        ordering = ('id',)
        
    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'is_player_corp')

    @property
    def name(self):
        obj = Name.objects.get(pk=self.id)
        return obj.name
    
    def __str__(self):
        return self.name

    @property
    def is_player_corp(self):
        return self.faction == None
    
    def directors(self):
        return self.characters.filter(is_director=True)

    def refresh(self, character=None, name=None):
        messages = []
        
        if self.is_player_corp is False:
            messages.append('No refresh needed for NPC corps.')
            return messages
        
        i = Item.objects.get(name='Corporation')
                
        record = None        
        try:
            if character:
                api = character.api_corporation()
                record = api.CorporationSheet(corporationID=self.id)
            else:
                api = API
                record = api.corp.CorporationSheet(corporationID=self.id)
            name = record.corporationName
        except eveapi.Error, e:
            messages.append("EVE API ERROR on corp refresh: %s" % e)
            return messages
                
        if name == None:
            messages.append("Unable to refresh corporation '%s', no name available." % self.id)
            return messages
        
        try:
            name = Name.objects.get(id=self.id)
        except Name.DoesNotExist:
            name = Name(id=self.id, name=name, type=i, group=i.group, category=i.group.category)
            name.save()
            messages.append("Added: %s to name database. [%d]" % (name.name, name.id))

        if record:
            if record.allianceID:
                self.alliance = Alliance.objects.get(pk=record.allianceID)
            else:
                self.alliance = None 
        messages.append('Corp refreshed: %s(%s)' % (name, self.id))
        self.save()
        return messages

class CorporationDivision(models.Model):
    id = models.IntegerField(primary_key=True, db_column='divisionid')
    name = models.CharField(max_length=300, db_column='divisionname')
    description = models.TextField()
    leadertype = models.CharField(max_length=300)
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('id', 'name')
        list_display = ('id', 'name', 'description',) 
            
    def __str__(self):
        return self.name

class Attribute(models.Model):
    """This table seems to contain the various attributes of an Item that can
    have numeric values associated with them.
    
    For example, for the T2 laser crystal 'Scorch M' Item(id=12818): 
    Attribute: 613: baseArmorDamage
    Attribute: 612: baseShieldDamage
    Attribute: 317: capNeedBonus
    Attribute: 128: chargeSize
    Attribute: 786: crystalsGetDamaged
    Attribute: 783: crystalVolatilityChance
    Attribute: 784: crystalVolatilityDamage
    Attribute: 114: emDamage
    Attribute: 779: entityFlyRangeMultiplier
    Attribute: 116: explosiveDamage
    Attribute: 9: hp
    Attribute: 117: kineticDamage
    Attribute: 137: launcherGroup
    Attribute: 124: mainColor
    Attribute: 182: requiredSkill1
    Attribute: 277: requiredSkill1Level
    Attribute: 204: speedMultiplier
    Attribute: 422: techLevel
    Attribute: 118: thermalDamage
    Attribute: 244: trackingSpeedMultiplier
    Attribute: 120: weaponRangeMultiplier
    """
    id = models.IntegerField(primary_key=True, db_column='attributeid')
    attributename = models.CharField(max_length=100)
    attributecategory = models.IntegerField()
    description = models.CharField(max_length=1000)
    maxattributeid = models.IntegerField(null=True, blank=True)
    attributeidx = models.IntegerField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    chargerechargetimeid = models.IntegerField(null=True, blank=True)
    defaultvalue = models.FloatField()
    published = models.BooleanField()
    displayname = models.CharField(max_length=300, blank=True)
    unit = models.ForeignKey('Unit', null=True, blank=True, db_column='unitid')
    stackable = models.BooleanField()
    highisgood = models.BooleanField()
    
    class Meta:
        ordering = ('attributename',)

    class Admin:
        search_fields = ('attributename', 'displayname', 'id')
        list_display = ('id', 'attributename', 'displayname', 'description',) 
        
    def __str__(self):
        if self.valueint is not None:
            return "%d: %s (I:%d)" % (self.id, self.name, self.valueint)
        elif self.valuefloat is not None:
            return "%d: %s (F:%f)" % (self.id, self.name, self.valuefloat)
        else:
            return "%d: %s (?)" % (self.id, self.name)
     

    # Used when joining with Item.
    valueint = None
    valuefloat = None
    def get_value(self):
        if self.valueint is not None:
            return self.valueint
        else:
            return self.valuefloat
    value = property(get_value, None, None, None)

    @property
    def display_value(self):
        value = self.get_value()
        if self.unit is None:
            return value
            
        # Big lookup....
        name = self.unit.name
        if name == 'Modifier Percent':
            value = "%.0f %%" % ((value - 1.0) * 100)
        elif name == 'Sizeclass':
            if value == 1:
                value = 'Small'
            elif value == 2:
                value = 'Medium'
            elif value == 3:
                value = 'Large'
            elif value == 4:
                value = 'X-Large'
        elif self.attributename == 'requiredSkill1':
            value = "%s %s" % (Item.objects.get(pk=self.valueint).name, self.valuefloat)
        elif self.attributename == 'requiredSkill2':
            value = "%s %s" % (Item.objects.get(pk=self.valueint).name, self.valuefloat)
        elif self.attributename == 'requiredSkill3':
            value = "%s %s" % (Item.objects.get(pk=self.valueint).name, self.valuefloat)                                      
        elif name == 'groupID':
            value = Group.objects.get(pk=value)
        elif name == 'Milliseconds' and value > 1000:
            value = time(value/1000)
        elif name == 'typeID':
            value = Item.objects.get(pk=value)
        elif name == 'attributeID':
            value = CharacterAttribute.objects.get(pk=value)
        elif name == 'Inverse Absolute Percent':
            value = "%d %%" % int((1 - value) * 100)
        else:
            value = str(comma(value)) + " " + self.unit.displayname
        return value
        
    
    # There are two name fields, but they are not always filled in.
    @property
    def name(self):
        if self.displayname:
            return self.displayname
        else:
            return self.attributename
            
    def get_icon(self, size):
        if self.displayname == 'Used with (chargegroup)':
            return Group.objects.get(pk=self.get_value()).get_icon(size)
        elif self.graphic:
            return self.graphic.get_icon(size)
        else:
            return Graphic.objects.get(icon='07_15').get_icon(size)
            
    @property
    def icon16(self):
        return self.get_icon(16)
        
    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def icon64(self):
        return self.get_icon(64)

    @property
    def icon128(self):
        return self.get_icon(128)
            
class Effect(models.Model):
    id = models.IntegerField(primary_key=True, db_column='effectid')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    name = models.TextField(db_column='effectname')
    displayname = models.CharField(max_length=300)
    effectcategory = models.IntegerField()
    preexpression = models.IntegerField(null=True, blank=True)
    postexpression = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    guid = models.CharField(blank=True, max_length=180)
    isoffensive = models.CharField(max_length=15)
    isassistance = models.CharField(max_length=15)
    durationattributeid = models.IntegerField(null=True, blank=True)
    trackingspeedattributeid = models.IntegerField(null=True, blank=True)
    dischargeattributeid = models.IntegerField(null=True, blank=True)
    rangeattributeid = models.IntegerField(null=True, blank=True)
    falloffattributeid = models.IntegerField(null=True, blank=True)
    disallowautorepeat = models.CharField(max_length=15)
    published = models.CharField(max_length=15)
    iswarpsafe = models.CharField(max_length=15)
    rangechance = models.CharField(max_length=15)
    electronicchance = models.CharField(max_length=15)
    propulsionchance = models.CharField(max_length=15)
    distribution = models.IntegerField(null=True, blank=True)
    sfxname = models.CharField(blank=True, max_length=60)
    npcusagechanceattributeid = models.IntegerField(null=True, blank=True)
    npcactivationchanceattributeid = models.IntegerField(null=True, blank=True)
    fittingusagechanceattributeid = models.IntegerField(null=True, blank=True)
    
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('name', 'displayname', 'id')
        list_display = ('id', 'name', 'displayname', 'description',) 
        
    def __str__(self):
        if self.displayname is not None:
            return self.displayname
        else:
            return self.name
          
# This table cannot be used within Django, as it's a multi-multi table with id's
# That Django doesn't like. I've emulated it in class Item below.
# class Dgmtypeattributes(models.Model):
#     typeid = models.IntegerField()
#     attributeid = models.IntegerField()
#     valueint = models.IntegerField(null=True, blank=True)
#     valuefloat = models.FloatField(null=True, blank=True)
#     class Meta:
#         db_table = u'dgmtypeattributes'
# 
# This table cannot be used within Django, as it's a multi-multi table with id's
# That Django doesn't like. I've emulated it in class Item below.
# class Dgmtypeeffects(models.Model):
#     typeid = models.IntegerField()
#     effectid = models.IntegerField()
#     isdefault = models.CharField(max_length=15)
#     class Meta:
#         db_table = u'dgmtypeeffects'

class Graphic(models.Model):
    id = models.IntegerField(primary_key=True, db_column='graphicid')
    url3d = models.CharField(max_length=300, null=True, blank=True)
    urlweb = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default='Automatically added by Django')
    published = models.BooleanField(default=False, null=True)
    obsolete = models.BooleanField(default=False, null=True)
    icon = models.CharField(max_length=300)
    urlsound = models.CharField(max_length=300, null=True, blank=True)
    explosionid = models.IntegerField(null=True, blank=True)
    class Meta:
        ordering = ('id',)

    class Admin:
        search_fields = ('id', 'icon', 'description')
        list_display = ('id', 'icon', 'url3d', 'urlweb', 'description') 
        
    def __str__(self):
        return "%s: %s (%s)" % (self.id, self.urlweb, self.icon)

    #-------------------------------------------------------------------------
    # All things iconic.
    def get_icon(self, size, item=None):
        d = {
                'dir'    : "/static/ccp-icons" , 
                'size'   : size, 
                'color'  : 'white', 
                'icon'   : self.icon, 
            }
        if item is not None:
            d['item_id'] = item.id
            
        if item is None:
            return "%(dir)s/%(color)s/%(size)d_%(size)d/icon%(icon)s.png" % d
        elif item.category == 'Blueprint':
            return "%(dir)s/blueprints/%(size)d_%(size)d/%(item_id)d.png" % d
        elif item.category == 'Drone':
            return "%(dir)s/dronetypes/%(size)d_%(size)d/%(item_id)d.png" % d
        elif item.category == 'Ship':
            return "%(dir)s/shiptypes/%(size)d_%(size)d/%(item_id)d.png" % d
        elif item.category == 'Station':
            return "%(dir)s/stationtypes/%(size)d_%(size)d/%(item_id)d.png" % d
        elif item.category == 'Structure':
            return "%(dir)s/structuretypes/%(size)d_%(size)d/%(item_id)d.png" % d
        else:
            return "%(dir)s/%(color)s/%(size)d_%(size)d/icon%(icon)s.png" % d
          
    @property
    def icon16(self, item=None):
        return self.get_icon(16, item)
        
    @property
    def icon32(self, item=None):
        return self.get_icon(32, item)

    @property
    def icon64(self, item=None):
        return self.get_icon(64, item)

    @property
    def icon128(self, item=None):
        return self.get_icon(128, item)

    def save(self):
        """Custom save handler to set a good and safe id on new objects."""
        if self.id is None:
            min_id = 10000 # We enter new id's on demand, but not below this value.
            max_id = Graphic.objects.all().order_by('-id')[0].id
            max_id = max(max_id, min_id)
            self.id=max_id+1
            
        super(Graphic, self).save()

def get_graphic(icon):
    """Helper utility that will find one icon or make it for you. Used in make_nav and elsewhere.
    Useful because icons are often non-unique, but I don't care in my app."""
    g = Graphic.objects.filter(icon=icon)
    if g.count() == 0:
        graphic = Graphic.objects.create(icon=icon)
    else:
        graphic = g[0]
    return graphic

class Unit(models.Model):
    id = models.IntegerField(primary_key=True, db_column='unitid')
    name = models.CharField(blank=True, max_length=60, db_column='unitname')
    displayname = models.CharField(blank=True, max_length=60)
    description = models.CharField(blank=True, max_length=300)
    class Meta:
        ordering = ('id',)

    class Admin:
        search_fields = ('id',)
        list_display = ('id', 'name', 'description') 
        
    def __str__(self):
        return self.displayname
              
class ContrabandType(models.Model):
    factionid = models.IntegerField()
    id = models.IntegerField(primary_key=True, db_column='typeid')
    standingloss = models.FloatField()
    confiscateminsec = models.FloatField()
    finebyvalue = models.FloatField()
    attackminsec = models.FloatField()

# class InventoryFlags(models.Model):
#     id = models.IntegerField(primary_key=True, db_column='flagid')
#     flagname = models.CharField(blank=True, max_length=300)
#     flagtext = models.TextField(blank=True)
#     flagtype = models.TextField(blank=True)
#     orderid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'invflags'

class Category(models.Model):
    """This table contains the most basic groupings in game:
        
    Sample:
        Asteroid
        Charge
        Ship"""
    id = models.IntegerField(primary_key=True, db_column='categoryid')
    name = models.CharField(max_length=300, db_column='categoryName')
    description = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    published = models.BooleanField()
    
    class Meta:

        ordering = ('name',)
        verbose_name_plural = "Categories"

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'description',) 
        
    def __str__(self):
        return self.name

class Group(models.Model):
    """This table describes goups like: Ammo and Advanced Torpedo.
    
    It also contains non-item groups like 'Alliance'."""
    id = models.IntegerField(primary_key=True, db_column='groupid')
    category = models.ForeignKey(Category, db_column='categoryid', related_name='groups')
    name = models.CharField(max_length=100, db_column='groupname')
    description = models.CharField(max_length=3000, null=True)
    graphic = models.ForeignKey(Graphic, null=True, blank=True, db_column='graphicid')
    usebaseprice = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    allowmanufacture = models.CharField("Manafacturable?", max_length=15, choices=TRUE_FALSE, radio_admin=True)
    allowrecycler = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    anchored = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    anchorable = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    fittablenonsingleton = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    published = models.BooleanField(default=True, null=True)
    
    class Meta:

        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'category', 'graphic', 'description',) 
        fields = (
            (None, {
                'fields': ('id', 'name', 'category', 'description', 'graphic'), 
            }), 
            ('Flags', {
                'fields': ('usebaseprice', 'allowmanufacture', 'allowrecycler', 
                           'anchored', 'anchorable'), 
            })
        )
        
    def __str__(self):
        return self.name
    
    def get_icon(self, size):
        return self.graphic.get_icon(size)

class BlueprintDetail(models.Model):
    # Using the proper foreign key relationship here causes a fatal django error.
    # (Only using the admin interface.)
    id = models.ForeignKey('Item', primary_key=True, 
                           db_column='blueprinttypeid', 
                           related_name='blueprint_details_qs', 
                           raw_id_admin=True, 
                           limit_choices_to = {'group__category__name__exact': 'Blueprint'})
    parent = models.IntegerField(db_column='parentBlueprintTypeID', null=True)
    # blueprint = models.IntegerField(db_column='blueprinttypeid', primary_key=True)
    makes = models.ForeignKey('Item', db_column='producttypeid', 
                              related_name='blueprint_madeby_qs', 
                              raw_id_admin=True, 
                              limit_choices_to = {
                                  'group__category__name__in': [
                                      'Celestial', 
                                      'Material', 
                                      'Accessories', 
                                      'Ship', 
                                      'Module', 
                                      'Charge', 
                                      'Commodity', 
                                      'Drone', 
                                      'Implant', 
                                      'Deployable', 
                                  ]
                              })
    productiontime = models.IntegerField()
    techlevel = models.IntegerField()
    researchproductivitytime = models.IntegerField()
    researchmaterialtime = models.IntegerField()
    researchcopytime = models.IntegerField()
    researchtechtime = models.IntegerField()
    productivitymodifier = models.IntegerField()
    materialmodifier = models.IntegerField()
    wastefactor = models.IntegerField()
    chanceofreverseengineering = models.FloatField()
    maxproductionlimit = models.IntegerField()
    
    class Meta:
        ordering = ('id',)

    class Admin:
        search_fields = ('makes__name',)
        list_display = ('id', 'makes',) 
        
    #def __str__(self):
    #    return self.id.name
        
class Material(models.Model):
    """
    All the 'stuff' to make other 'stuff'.
    """
    item = models.ForeignKey('Item', 
                             null=True, 
                             blank=True, 
                             db_column='typeid', 
                             raw_id_admin=True)
    activity = models.ForeignKey('RamActivity', 
                                 #null=True,
                                 #blank=True,
                                 db_column='activity')
    material = models.ForeignKey('Item', 
                                 null=True, 
                                 blank=True, 
                                 db_column='requiredtypeid', 
                                 related_name='helps_make', 
                                 raw_id_admin=True)
    quantity = models.IntegerField(null=True, blank=True)
    damageperjob = models.FloatField(null=True, blank=True)
    id = models.IntegerField(primary_key=True)

    class Meta:
        pass
        # Django erros if you uncomment this, as it tries and failes to follow the 
        # relationship.
        #ordering = ( 'item',)

    class Admin:
        search_fields = ('item',)
        list_display = ('item', 'activity', 'material', 'quantity',) 
        
    def __str__(self):
        return "%s: %d" % (self.name, self.quantity)

    def get_name(self):
        return self.material.name
    name = property(get_name)
    
    def quantity_per_unit(self):
        return float(self.quantity) / float(self.item.portionsize)    
    
    @property
    def volume(self):
        return Decimal(self.material.volume) * self.quantity 
  
    @property
    def value(self):
        if self.material.value:
            return self.material.value * self.quantity
        else:
            return None
  
class ItemSkillManager(models.Manager):
    def get_query_set(self):
        return super(ItemSkillManager, self).get_query_set().filter(group__category__name__exact='Skill')

class Item(models.Model):
    """This table contains information about each item that you can aquire in
    EVE. Weapons, Ammo, etc...
    
    # Find some objects.
    >>> scorch = Item.objects.get(name='Scorch M')
    >>> myrm = Item.objects.get(name='Myrmidon')
    >>> dcm = Item.objects.get(name='Deep Core Mining')
    
    >>> scorch.group.name
    u'Advanced Pulse Laser Crystal'
    
    >>> scorch.graphic.id
    1141L
    
    """
    
    # DON'T REORDER!!! (Breaks the test copy above.)
    id = models.IntegerField(primary_key=True, db_column='typeid')
    group = models.ForeignKey('Group', db_column='groupid', related_name='items')
    name = models.CharField(max_length=300)
    real_description = models.TextField(db_column='description')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                raw_id_admin=True, 
                                db_column='graphicid')
    radius = models.FloatField()
    mass = models.FloatField()
    volume = models.FloatField()
    capacity = models.FloatField()
    portionsize = models.IntegerField()
    race = models.ForeignKey(Race, null=True, blank=True, db_column='raceid')
    baseprice = models.FloatField()
    published = models.BooleanField()
    marketgroup = models.ForeignKey('MarketGroup', null=True, blank=True, 
                                    db_column='marketgroupid')
    chanceofduplicating = models.FloatField()
    slug = models.SlugField(max_length=100)
    objects = models.Manager()
    
    class Meta:
        pass
        # If I use 'name' instead of 'typename', then the BlueprintDetails model dies
        # in the admin list view. Like this, the list works, but not the detail.
        ordering = ['name', ]

    class Admin:
        search_fields = ('name', 'id')
        list_display = ('name', 'id', 'group', 'category', 'graphic') 
        fields = (
            (None, {
                'fields': ('id', 'name', 'group', 'marketgroup', 'real_description', 
                           'graphic', 'race'), 
            }), 
            ('Physics', {
                'fields': ('mass', 'volume', 'radius', 'portionsize')
            }), 
            ('Misc', {
                'fields': ('published', 'baseprice', 'chanceofduplicating'), 
            })
        )
        list_filter = ('group',)
        
    def __str__(self):
        return self.name
        
    @property
    def category(self):
        return self.group.category.name
        
    def get_absolute_url(self):
        return "/item/%s/" % self.slug

    def get_parent(self):
        return self.marketgroup
    parent = property(get_parent)

    @property
    def description(self):
        if self.is_blueprint:
            return self.blueprint_makes.real_description
        else:
            return self.real_description

    # All things iconic.
    def get_icon(self, size):
        '''
        Get icons for all of the items.
        # Find some objects.
        >>> Item.objects.get(name='Myrmidon').icon32
        '/static/ccp-icons/shiptypes/32_32/24700.png'
        
        >>> Item.objects.get(name='Scorch M').icon16
        u'/static/ccp-icons/white/16_16/icon08_04.png'
        
        >>> Item.objects.get(name='Deep Core Mining').icon128
        u'/static/ccp-icons/white/128_128/icon50_11.png'
        '''
        return self.graphic.get_icon(size, item=self)

    @property
    def icon16(self):
        return self.get_icon(16)
        
    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def icon64(self):
        return self.get_icon(64)

    @property
    def icon128(self):
        return self.get_icon(128)

    # Fancy way to get the attributes and their values.    
    def attributes(self):
        set = Attribute.objects.extra(
            select={
                'valueint':'ccp_typeattribute.valueint', 
                'valuefloat':'ccp_typeattribute.valuefloat', 
            }, 
            tables=['ccp_typeattribute'], 
            where=[
                'ccp_typeattribute.attributeid = ccp_attribute.attributeid', 
                'ccp_typeattribute.typeid = %s', 
            ], 
            params=[self.id]
        )
        for s in set:
            try:
                if s.attributename == 'requiredSkill1':
                    s.graphic = get_graphic('50_13')
                    s.valuefloat = set.filter(attributename='requiredSkill1Level')[0].valueint
                if s.attributename == 'requiredSkill2':
                    s.graphic = get_graphic('50_11')
                    s.valuefloat = set.filter(attributename='requiredSkill2Level')[0].valueint
                if s.attributename == 'requiredSkill3':
                    s.graphic = get_graphic(icon='50_14')
                    s.valuefloat = set.filter(attributename='requiredSkill3Level')[0].valueint
            except IndexError:
                s.valuefloat = 1
        return set
    
    def attribute_by_name(self, name):
        set = Attribute.objects.extra(
            select={
                'valueint':'ccp_typeattribute.valueint', 
                'valuefloat':'ccp_typeattribute.valuefloat', 
            }, 
            tables=['ccp_typeattribute'], 
            where=[
                'ccp_typeattribute.attributeid = ccp_attribute.attributeid', 
                'ccp_typeattribute.typeid = %s',
                'ccp_attribute.attributeName = %s',
            ], 
            params=[self.id, name]
        )
        if set.count() > 0:
            return set[0]
        else:
            return None
    
    def effects(self):
        set = Effect.objects.extra(
            tables=['dgmtypeeffects'], 
            where=[
                'dgmtypeeffects.effectid = dgmeffects.effectid', 
                'dgmtypeeffects.typeid = %s'
            ], 
            params=[self.id]
        )
        return set
        
    # Skill-orientated methods
    @property
    def is_skill(self):
        '''
        Is the goven object a skill?
        
        >>> dcm.is_skill
        True
    
        >>> myrm.is_skill
        False
        '''
        if self.category == 'Skill':
            return True
        else:
            return False
    
    @property
    def skill_rank(self):
        '''
        Return int of the skill rank for a skill. (Training time multiplier.)
        
        >>> dcm.skill_rank
        6
        
        >>> myrm.skill_rank
        None
        '''
        if self.is_skill is False:
            return None
        else:
            rank = self.attribute_by_name('skillTimeConstant')
            return int(rank.value)
    
    # Allows for a search for just skills.
    skill_objects = ItemSkillManager()

    # Construction-orientated methods
    @property
    def is_blueprint(self):
        if self.category == 'Blueprint':
            return True
        else:
            return False

    @property
    def blueprint_details(self):
        '''
        The record of the details of a blueprint.
        Returns a BlueprintDetail instance.
        
        >>> myrm.blueprint.blueprint_details.techlevel
        1L
        '''
        item = self
        if self.is_blueprint is False:
            item = self.blueprint
        assert(item.blueprint_details_qs.count() == 1)
        return item.blueprint_details_qs.all()[0]
    
    @property
    def blueprint(self):
        '''
        Returns the Item of the published blueprint for self if one exists.
        Returns None otherwise.
        
        >>> myrm.blueprint.name
        u'Myrmidon Blueprint'
        
        >>> myrm.blueprint.id
        24701L
        
        >>> dcm.blueprint
        None
        
        '''
        if self.is_blueprint:
            return self
        elif self.blueprint_madeby_qs.count() > 0:
            assert(self.blueprint_madeby_qs.count() == 1)
            blueprint = self.blueprint_madeby_qs.all()[0].id
            if blueprint.published:
                return blueprint
            else:
                return None
        else:
            return None
    
    @property
    def blueprint_makes(self):
        if self.blueprint is None:
            return None
        else:
            return self.blueprint_details.makes
    
    def materials(self, activity=None):
        """
        >>> myrm = Item.objects.get(name='Myrmidon')
        >>> for m in myrm.materials():
        ...     print "%s: %s" % (m.material, m.quantity)
        Tritanium: 2885176
        Pyerite: 642378
        Mexallon: 215466
        Nocxium: 13483
        Zydrine: 2523
        Megacyte: 1236
        """

        # If it can't be made, then it has no mats.
        filter = Q(quantity__gt=0)
        if activity:
            filter = filter & Q(activity__name=activity)

        if self.blueprint:
            # filter = filter & (Q(item=self) | Q(item=self.blueprint))
            filter = filter & (Q(item=self.blueprint))
        else:
            filter = filter & Q(item=self)
            
        return Material.objects.filter(filter)
       
    def refines(self):
        return self.materials(activity='Refining') 

class Name(models.Model):
    """This table contains the names of planets, stars, systems and corporations."""
    id = models.IntegerField(primary_key=True, db_column='itemid')
    name = models.CharField(max_length=300, db_column='itemname')
    category = models.ForeignKey(Category, db_column='categoryid', related_name='namexxxx')
    group = models.ForeignKey(Group, db_column='groupid', related_name='namexxxxx')
    type = models.ForeignKey(Item, db_column='typeid', related_name='namexxx', raw_id_admin=True)
    class Meta:
        #pass
        ordering = ('name',)

    class Admin:
        search_fields = ('name', 'id')
        # Don't ask why, but adding type or group makes the admin list show
        # no rows at all.
        list_display = ('name', 'category', 'group') 
        list_filter = ('group',)
        
    def __str__(self):
        return self.name
        

class MarketGroup(models.Model):
    '''This is the list of the groups as seen in the market type browser.
    (Which is more detailed than the normal group table.)
    
    Items here have a self-referential parent, which is used to create heirarchy
    within this table.'''
    
    id = models.IntegerField(primary_key=True, db_column='marketgroupid')
    parent = models.ForeignKey('MarketGroup', null=True, blank=True, db_column='parentgroupid')
    name = models.CharField(max_length=100, db_column='marketgroupname')
    description = models.CharField(max_length=3000, null=True)
    graphic = models.ForeignKey(Graphic, null=True, blank=True, db_column='graphicid')
    hastypes = models.CharField(max_length=15, choices=TRUE_FALSE, radio_admin=True)
    slug = models.SlugField(max_length=50)
    objects = models.Manager()
    
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'slug', 'description', 'graphic') 
        
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/items/%s/" % self.slug

    #-------------------------------------------------------------------------
    # All things iconic.
    def get_icon16(self):
        return self.graphic.get_icon(16)
    icon16 = property(get_icon16)
        
    def get_icon32(self):
        return self.graphic.get_icon(32)
    icon32 = property(get_icon32)

    def get_icon64(self):
        return self.graphic.get_icon(64)
    icon64 = property(get_icon64)

    def get_icon128(self):
        return self.graphic.get_icon(128)
    icon128 = property(get_icon128)

        
class InventoryMetaGroup(models.Model):
    id = models.IntegerField(primary_key=True, db_column='metagroupid')
    name = models.CharField(blank=True, max_length=300, db_column='metagroupname')
    description = models.CharField(blank=True, max_length=300)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    class Meta:
        pass
        #ordering = ( 'id',)

    class Admin:
        search_fields = ('name', 'id')
        list_display = ('id', 'name', 'description')
        list_select_related = True
        
    def __str__(self):
        return self.name
        
class InventoryMetaType(models.Model):
    item = models.ForeignKey('Item', null=True, blank=True, 
                           raw_id_admin=True, 
                           db_column='typeid', 
                           related_name='metatype')
    parent = models.ForeignKey('Item', null=True, blank=True, 
                               raw_id_admin=True, 
                               db_column='parenttypeid', 
                               related_name='metatype_children')
    metagroup = models.ForeignKey('InventoryMetaGroup', null=True, blank=True, 
                                    db_column='metagroupid')
    class Meta:
        pass
        #ordering = ( 'item__typeid',)

    class Admin:
        search_fields = ('id', 'metagroup__name', 'parent__name')
        list_display = ('item', 'metagroup', 'parent')
        list_select_related = True
        
class Reaction(models.Model):
    reaction = models.ForeignKey(Item, db_column='reactiontypeid', related_name='reactions')
    input = models.BooleanField()
    item = models.ForeignKey(Item, db_column='typeid', related_name='reacts')
    quantity = models.IntegerField()
    
    class Admin:
        pass
    
    #class Meta:
        #ordering = ['reaction', 'input']

    def __str__(self):
        arrow = '=>'
        if self.input == 1:
            arrow = '<-'
        return "%s %s %s[%d]" % (self.reaction, arrow, self.item, self.quantity)

#class MapcClestialStatistics(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='celestialid')
#    temperature = models.FloatField()
#    spectralclass = models.CharField(max_length=30)
#    luminosity = models.FloatField()
#    age = models.FloatField()
#    life = models.FloatField()
#    orbitradius = models.FloatField()
#    eccentricity = models.FloatField()
#    massdust = models.FloatField()
#    massgas = models.FloatField()
#    fragmented = models.CharField(max_length=15)
#    density = models.FloatField()
#    surfacegravity = models.FloatField()
#    escapevelocity = models.FloatField()
#    orbitperiod = models.FloatField()
#    rotationrate = models.FloatField()
#    locked = models.CharField(max_length=15)
#    pressure = models.FloatField()
#    radius = models.FloatField()
#    mass = models.FloatField()

# 
# class Mapconstellationjumps(models.Model):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapconstellationjumps'
        
class Region(models.Model):
    id = models.IntegerField(primary_key=True, db_column='regionid')
    name = models.CharField(max_length=100, db_column='regionname')
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    xmin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    zmin = models.FloatField(null=True)
    zmax = models.FloatField(null=True)
    faction = models.ForeignKey(Faction, null=True, blank=True, db_column='factionid')
    radius = models.FloatField(null=True)
    slug = models.SlugField(max_length=50)
    
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'faction') 
        fields = (
            (None, {
                'fields': ('id', 'name', 'faction')
            }), 
            ('Location', {
                'fields': ('radius', 'x', 'y', 'z', 'xmin', 'ymin', 'zmin', 
                           'xmax', 'ymax', 'zmax'), 
            }), 
        )
    def __str__(self):
        return self.name
        
    def get_absolute_url(self):
        return "/region/%s/" % self.slug
    
    def owner(self):
        if self.faction:
            return self.faction
        else:
            alliance = self.alliance()
            if alliance:
                return alliance
            else:
                return None
    
    def note(self):
        return self.owner()
    
    def alliance(self):
        alliances= {}
        for x in self.constellations.all():
            if x.alliance:
                alliances[x.alliance_id] = x.alliance
        if len(alliances) == 1:
            return alliances.values()[0]
        else:
            return None
        
    def get_icon(self, size):
        owner = self.owner()
        
        if owner is None:
            return None
        else:
            return owner.get_icon(32)
    
    @property
    def icon32(self):
        return self.get_icon(32)

    def delete(self):
        raise 'ERROR: Tried to remove an immutable.'

class Constellation(models.Model):
    region = models.ForeignKey(Region, db_column='regionid', 
                               edit_inline=models.TABULAR,
                               related_name='constellations')
    id = models.IntegerField(primary_key=True, db_column='constellationid')
    name = models.CharField(max_length=300, db_column='constellationname', 
                            core=True)
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    xmin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    zmin = models.FloatField(null=True)
    zmax = models.FloatField(null=True)
    faction = models.ForeignKey(Faction, null=True, blank=True, 
                                db_column='factionid')
    radius = models.FloatField(null=True)
    sov_time = models.DateTimeField(null=True, blank=True, 
                                    db_column='sovereigntyDateTime')
    alliance = models.ForeignKey(Alliance, null=True, blank=True,
                                 db_column='allianceID',
                                 related_name='constellations')
    grace_date_time = models.DateTimeField(null=True, db_column='graceDateTime')
    
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'faction') 
        fields = (
            (None, {
                'fields': ('id', 'name', 'region', 'faction')
            }), 
            ('Location', {
                'classes': 'collapse', 
                'fields': ('radius', 'x', 'y', 'z', 'xmin', 'ymin', 'zmin', 
                           'xmax', 'ymax', 'zmax'), 
            }), 
        )
#        list_filter = ('region')
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/constellation/%s/" % self.name
    
    def moons(self):
        return self.map.filter(type__name='Moon')

    def get_icon(self, size):
        if self.alliance:
            return self.alliance.get_icon(size)
        else:
            return None

    @property
    def icon16(self):
        return self.get_icon(16)
    
    @property
    def icon32(self):
        return self.get_icon(32)

    @property
    def icon64(self):
        return self.get_icon(64)
    
    @property
    def icon128(self):
        return self.get_icon(128)
    
    def delete(self):
        raise 'ERROR: Tried to remove an immutable.'    
    
class SolarSystem(models.Model):
    region = models.ForeignKey(Region, db_column='regionid', related_name='solarsystems')
    constellation = models.ForeignKey(Constellation, db_column='constellationid', raw_id_admin=True, 
                                      related_name='solarsystems')
    id = models.IntegerField(primary_key=True, db_column='solarsystemid')
    name = models.CharField(max_length=100, db_column='solarsystemname')
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    xmin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    zmin = models.FloatField(null=True)
    zmax = models.FloatField(null=True)
    luminosity = models.FloatField(null=True)
    border = models.IntegerField(null=True)
    fringe = models.IntegerField(null=True)
    corridor = models.IntegerField(null=True)
    hub = models.IntegerField(null=True)
    international = models.IntegerField(null=True)
    regional = models.IntegerField(null=True)
    constellation2 = models.IntegerField(null=True, db_column='constellation')
    security = models.FloatField(null=True)
    faction = models.ForeignKey(Faction, null=True, blank=True,
                                db_column='factionid', 
                                related_name='solarsystems')
    radius = models.FloatField(default=0.0)
    suntypeid = models.IntegerField(null=True, blank=True)
    securityclass = models.CharField(blank=True, max_length=2, null=True)
    alliance = models.ForeignKey(Alliance, null=True, blank=True, 
                                 db_column='allianceid',
                                  related_name='solarsystems')
    sov = models.IntegerField(null=True, blank=True, db_column='sovereigntyLevel')
    sov_time = models.DateTimeField(null=True, blank=True, db_column='sovereigntyDateTime')
    alliance_old = models.ForeignKey(Alliance, null=True, blank=True, 
                                     related_name='solarsystems_lost')
    
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'region', 'constellation', 'security',) 
        
    def __str__(self):
        return self.name
    
    def delete(self):
        raise 'ERROR: Tried to remove an immutable.'
    
    def moons(self):
        return self.map.filter(type__name='Moon')
    
    def belts(self):
        return self.map.filter(type__name='Asteroid Belt')
    
    def get_absolute_url(self):
        return "/solarsystem/%s/" % self.name
    
    @property
    def icon16(self):
        return self.alliance.icon16
    
    @property
    def icon32(self):
        return self.alliance.icon32

    @property
    def icon64(self):
        return self.alliance.icon64
    
    @property
    def icon128(self):
        return self.alliance.icon128
    
class MapDenormalize(models.Model):
    id = models.IntegerField(primary_key=True, db_column='itemid')
    type = models.ForeignKey(Item, db_column='typeid')
    group = models.ForeignKey(Group, db_column='groupid')
    solarsystem = models.ForeignKey('SolarSystem', db_column='solarsystemid', null=True, blank=True, 
                                    related_name='map')
    constellation = models.ForeignKey(Constellation, db_column='constellationid', null=True, blank=True, 
                                      related_name='map')
    region = models.ForeignKey('Region', db_column='regionid', null=True, blank=True, 
                               related_name='map')
    orbits = models.ForeignKey('MapDenormalize', db_column='orbitid', null=True, blank=True, raw_id_admin=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    name = models.CharField(blank=True, max_length=300, db_column='itemname')
    security = models.FloatField(null=True, blank=True)
    celestialindex = models.IntegerField(null=True, blank=True)
    orbitindex = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name    

# class Mapjumps(models.Model):
#     stargateid = models.IntegerField()
#     celestialid = models.IntegerField()
#     class Meta:
#         db_table = u'mapjumps'

class MapLandmarks(models.Model):
    id = models.IntegerField(primary_key=True, db_column='landmarkid')
    landmarkname = models.CharField(max_length=300)
    description = models.TextField()
    locationid = models.IntegerField(null=True, blank=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    radius = models.FloatField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, 
                                  db_column='graphicid', 
                                  raw_id_admin=True,)
    importance = models.IntegerField()
    url2d = models.CharField(blank=True, max_length=765)

# 
# class Mapregionjumps(models.Model):
#     fromregionid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapregionjumps'

# Empty table in dump
# class Mapsecurityratings(models.Model):
#     fromsolarsystemid = models.IntegerField()
#     fromvalue = models.FloatField()
#     tosolarsystemid = models.IntegerField()
#     tovalue = models.FloatField()
#     class Meta:
#         db_table = u'mapsecurityratings'
# 
# class Mapsolarsystemjumps(models.Model):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     fromsolarsystemid = models.IntegerField()
#     tosolarsystemid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapsolarsystemjumps'

class MapUniverse(models.Model):
    id = models.IntegerField(primary_key=True, db_column='universeid')
    universename = models.CharField(max_length=300)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    xmin = models.FloatField()
    xmax = models.FloatField()
    ymin = models.FloatField()
    ymax = models.FloatField()
    zmin = models.FloatField()
    zmax = models.FloatField()
    radius = models.FloatField()


class RamActivity(models.Model):
    id = models.IntegerField(primary_key=True, db_column='activityid')
    name = models.CharField(max_length=300, db_column='activityname')

    class Admin:
        pass
    
    def __str__(self):
        return self.name
#        
#        
#class RamAssemblyLines(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='assemblylineid')
#    assemblylinetypeid = models.IntegerField()
#    containerid = models.IntegerField(null=True, blank=True)
#    nextfreetime = models.CharField(blank=True, max_length=60)
#    uigroupingid = models.IntegerField()
#    costinstall = models.FloatField()
#    costperhour = models.FloatField()
#    restrictionmask = models.IntegerField()
#    discountpergoodstandingpoint = models.FloatField()
#    surchargeperbadstandingpoint = models.FloatField()
#    minimumstanding = models.FloatField()
#    minimumcharsecurity = models.FloatField()
#    minimumcorpsecurity = models.FloatField()
#    maximumcharsecurity = models.FloatField()
#    maximumcorpsecurity = models.FloatField()
#    ownerid = models.IntegerField(null=True, blank=True)
#    oldcontainerid = models.IntegerField(null=True, blank=True)
#    oldownerid = models.IntegerField(null=True, blank=True)
#    activityid = models.IntegerField(null=True, blank=True)
#
#
#class RamAssemblyLineStationCostLogs(models.Model):
#    stationid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeid')
#    logdatetime = models.CharField(max_length=60)
#    _usage = models.FloatField()
#    costperhour = models.FloatField()

# 
# class Ramassemblylinestations(models.Model):
#     stationid = models.IntegerField()
#     assemblylinetypeid = models.IntegerField()
#     quantity = models.IntegerField()
#     stationtypeid = models.IntegerField()
#     ownerid = models.IntegerField()
#     solarsystemid = models.IntegerField()
#     regionid = models.IntegerField()
#     class Meta:
#         db_table = u'ramassemblylinestations'
# 
# class Ramassemblylinetypedetailpercategory(models.Model):
#     assemblylinetypeid = models.IntegerField()
#     categoryid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpercategory'
# 
# class Ramassemblylinetypedetailpergroup(models.Model):
#     assemblylinetypeid = models.IntegerField()
#     groupid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpergroup'

#class RamAssemblylineTypes(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeid')
#    assemblylinetypename = models.CharField(max_length=300)
#    description = models.TextField()
#    basetimemultiplier = models.FloatField()
#    basematerialmultiplier = models.FloatField()
#    volume = models.FloatField()
#    activityid = models.IntegerField()
#    mincostperhour = models.FloatField(null=True, blank=True)
#
#class RamCompletedStatuses(models.Model):
#    completedstatus = models.IntegerField(primary_key=True)
#    completedstatustext = models.CharField(max_length=300)
#    description = models.TextField()
#
#class RamInstallationTypeDefaultContents(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='installationtypeid')
#    assemblylinetypeid = models.IntegerField()
#    uigroupingid = models.IntegerField()
#    quantity = models.IntegerField()
#    costinstall = models.FloatField()
#    costperhour = models.FloatField()
#    restrictionmask = models.IntegerField()
#    discountpergoodstandingpoint = models.FloatField()
#    surchargeperbadstandingpoint = models.FloatField()
#    minimumstanding = models.FloatField()
#    minimumcharsecurity = models.FloatField()
#    minimumcorpsecurity = models.FloatField()
#    maximumcharsecurity = models.FloatField()
#    maximumcorpsecurity = models.FloatField()
#
#class StationOperation(models.Model):
#    activityid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='operationid')
#    operationname = models.CharField(max_length=300)
#    description = models.TextField()
#    fringe = models.IntegerField()
#    corridor = models.IntegerField()
#    hub = models.IntegerField()
#    border = models.IntegerField()
#    ratio = models.IntegerField()
#    caldaristationtypeid = models.IntegerField(null=True, blank=True)
#    minmatarstationtypeid = models.IntegerField(null=True, blank=True)
#    amarrstationtypeid = models.IntegerField(null=True, blank=True)
#    gallentestationtypeid = models.IntegerField(null=True, blank=True)
#    jovestationtypeid = models.IntegerField(null=True, blank=True)

# class Staoperationservices(models.Model):
#     operationid = models.IntegerField()
#     serviceid = models.IntegerField()
#     class Meta:
#         db_table = u'staoperationservices'

#class StationService(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='serviceid')
#    servicename = models.CharField(max_length=300)
#    description = models.TextField()

class Station(models.Model):
    id = models.IntegerField(primary_key=True, db_column='stationid')
    security = models.IntegerField(null=True)
    dockingcostpervolume = models.FloatField('Docking', default=0)
    maxshipvolumedockable = models.FloatField('Max Dockable', default=0)
    officerentalcost = models.IntegerField('Office Rental', default=0)
    operationid = models.IntegerField(null=True, default=0)
    type = models.ForeignKey(Item, null=True, blank=True, 
                             db_column='stationtypeid', related_name='staitons')
    corporation = models.ForeignKey(Corporation, null=True, blank=True, db_column='corporationid')
    solarsystem = models.ForeignKey(SolarSystem, null=True, blank=True, db_column='solarsystemid', 
                                    related_name='stations', raw_id_admin=True)
    constellation = models.ForeignKey(Constellation, null=True, blank=True, db_column='constellationid', 
                                       related_name='stations', 
                                       raw_id_admin=True)
    region = models.ForeignKey(Region, null=True, blank=True, db_column='regionid', related_name='stations')
    name = models.CharField(max_length=100, db_column='stationname')
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    z = models.FloatField(default=0)
    reprocessingefficiency = models.FloatField('%', default=0)
    reprocessingstationstake = models.FloatField('Take', default=0)
    reprocessinghangarflag = models.IntegerField('Hangar?', default=0)
    capital_station = models.DateTimeField('Made Capital', null=True,
                                           db_column='capitalStation')
    ownership_date = models.DateTimeField('Ownership Date', null=True,
                                           db_column='ownershipDateTime')
    upgrade_level = models.IntegerField(null=True, db_column='upgradeLevel')
    custom_service_mask = models.IntegerField('Service Mask', null=True,
                                               db_column='customServiceMask')
    
    class Meta:
        ordering = ('name',)

    class Admin:
        search_fields = ('name',)
        list_display = ('name', 'region', 'constellation', 'corporation') 
        fields = (
            (None, {
                'fields': ('id', 'name', 'corporation', 'security')
            }), 
            ('Corp', {
             'fields': ('dockingcostpervolume', 'maxshipvolumedockable', 
                        'officerentalcost'), 
             }), 
            ('Reprocessing', {
             'fields': ('reprocessingefficiency', 'reprocessingstationstake', 
                        'reprocessinghangarflag'), 
             }), 
            ('Location', {
                'fields': ('region', 'constellation', 'solarsystem', 'x', 'y', 'z',), 
            }), 
        )
        list_filter = ('region',)
        
    def __str__(self):
        return self.name
    
    def icon32(self):
        if self.corporation.alliance:
            return self.corporation.alliance.icon32
        else:
            return self.type.icon32
    
    def delete(self):
        raise 'ERROR: Tried to remove an immutable.'    
    
class StationResourcePurpose(models.Model):
    id = models.IntegerField(primary_key=True, db_column='purpose')
    text = models.CharField(max_length=300, db_column='purposetext')
     
    class Admin:
        pass
    
    def __str__(self):
        return self.text
     
class StationResource(models.Model):
    q = Q(group__name='Control Tower') & Q(published=True)
    
    tower = models.ForeignKey(Item, limit_choices_to = q, db_column = 'controlTowerTypeID', 
                              related_name='fuel')
    type = models.ForeignKey(Item, db_column='resourcetypeid', raw_id_admin=True, 
                             related_name='fuel_for')
    purpose_id = models.ForeignKey(StationResourcePurpose, db_column='purpose')
    quantity = models.IntegerField()
    minsecuritylevel = models.FloatField(null=True, blank=True)
    faction = models.ForeignKey(Faction, null=True, blank=True, db_column='factionID')
    
    class Admin:
        pass
    
    def __str__(self):
        return "%s (%d)" % (self.type, self.quantity)
        
    @property
    def purpose(self):
        return self.purpose_id.text
        
#class StationType(models.Model):
#    id = models.IntegerField(primary_key=True, db_column='stationtypeid')
#    dockingbaygraphicid = models.IntegerField(null=True, blank=True)
#    hangargraphicid = models.IntegerField(null=True, blank=True)
#    dockentryx = models.FloatField()
#    dockentryy = models.FloatField()
#    dockentryz = models.FloatField()
#    dockorientationx = models.FloatField()
#    dockorientationy = models.FloatField()
#    dockorientationz = models.FloatField()
#    operationid = models.IntegerField(null=True, blank=True)
#    officeslots = models.IntegerField(null=True, blank=True)
#    reprocessingefficiency = models.FloatField(null=True, blank=True)
#    conquerable = models.CharField(max_length=15)
#    class Meta:


