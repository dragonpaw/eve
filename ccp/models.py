'''
All of the CCP-provided objects, plus a few minor addons like the Alliance
object and extensions to the Corporation
'''
from decimal import Decimal
import os

from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete, pre_save

from eve.lib import eveapi, evelogo, null_fields
from eve.lib.alliance_graphics import alliance_graphics
from eve.lib.cachehandler import MyCacheHandler
from eve.lib.decorators import cachedmethod
from eve.lib.formatting import unique_slug
from eve.lib.jfilters import filter_comma as comma, filter_time as time
from eve import settings

evelogo.resourcePath = os.path.join(settings.MEDIA_ROOT, 'ccp-icons', 'corplogos')

TRUE_FALSE = (
    ('true', 'Yes'),
    ('false', 'No'),
)
API = eveapi.get_api()

NULL_GRAPHIC = '/static/1px.gif'

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)

class Base(models.Model):
    '''Default Base model for all Widget models.

    Use EveBase for non-deleteable objects.
    '''
    # This appeases the code intellegence functions of Komodo.
    objects = models.Manager()

    def get_icon(self, size):
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

    def __unicode__(self):
        if hasattr(self, 'displayname') and self.displayname is not None:
            return self.displayname
        elif hasattr(self, 'name'):
            return self.name
        else:
            return u'Undefined __unicode__'

    class Meta:
        abstract = True
        ordering = ('name',)

class EveBase(Base):
    '''Base class for objects that must not be deleted or created.'''

    def delete(self):
        raise NotImplementedError('Tried to remove an immutable.')

    def really_delete(self):
        super(Base, self).delete()

    class Meta(Base.Meta):
        abstract = True
        managed = False

#class CachedGet(object):
#    """A mixin to cause the entire table to be loaded into memory the first time
#    that the class is accessed. A restart of the web server will be necessary
#    to reload any changed data within the table.
#
#    Unfortunately, seems to only work when called with Class.objects.get
#    """
#    def get(self, *args, **kwargs):
#        log = settings.logging.getLogger('CachedGet')
#        log.debug('Called!')
#        pk_name = self.model._meta.pk.name
#        if not hasattr(self, '_cache'):
#            log.info('Caching entire table in memory: %s' % self.__class__.__name__)
#            self._cache = dict((obj._get_pk_val(), obj) for obj in self.all())
#        value = len(kwargs) == 1 and kwargs.keys()[0] in ('pk', pk_name, '%s__exact' % pk_name) and self._cache.get(kwargs.values()[0], False)
#        if value:
#            log.debug('Returning cached value: %s', value)
#            return value
#        else:
#            log.debug('Failed to get value, falling back to super().')
#            super(CachedGet, self).get(*args, **kwargs)

class Agent(EveBase):
    id = null_fields.Int(primary_key=True, db_column='agentID')
    division = null_fields.Key('CorporationDivision', db_column='divisionID')
    corporation = null_fields.Key('Corporation', db_column='corporationID')
    station = null_fields.Key('Station', db_column='stationID')
    level = null_fields.Small()
    quality = null_fields.Small()
    agenttype = null_fields.Key('AgentType', db_column='agentTypeID')

    class Meta(EveBase.Meta):
        ordering = ('id',)
        db_table = 'agtAgents'

    @property
    @cachedmethod(60*4)
    def name(self):
        return Name.objects.get(pk=self.id).name


class AgentType(EveBase):
    id = null_fields.Small(primary_key=True, db_column='agentTypeID')
    agenttype = null_fields.Char(max_length=50, db_column='agentType')

    class Meta(EveBase.Meta):
        ordering = ('id',)
        db_table = 'agtAgentTypes'

    def __unicode__(self):
        return self.agenttype


class Alliance(Base):
    name = models.CharField(max_length=100)
    executor = models.ForeignKey('Corporation', related_name='executors')
    ticker = models.CharField(max_length=10)
    member_count = models.IntegerField(default=0)
    slug = models.SlugField(max_length=100, db_index=True)

    def get_icon(self, size):
        if alliance_graphics.has_key(self.id):
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, alliance_graphics[self.id])
        else:
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, '01_01')

    def save(self, force_insert=False, force_update=False):
        #print 'Alliance pre-save.'
        if not self.slug:
            self.slug = unique_slug(self)
        super(Alliance, self).save(force_insert, force_update)

    def delete(self):
        print "Breaking all links for alliance '%s'." % self.name
        #self.executor = None
        self.corporations.clear()
        self.solarsystems_lost.clear()
        self.solarsystems.clear()
        self.constellations.clear()
        self.save()
        super(Alliance, self).delete()

class Attribute(EveBase):
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
    id = null_fields.Small(primary_key=True, db_column='attributeID')
    attributename = null_fields.Char('Attribute Name', max_length=100, db_column='attributeName')
    description = null_fields.Char(max_length=1000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    defaultvalue = null_fields.Float('Default Value', db_column='defaultValue')
    published = models.NullBooleanField('Published?')
    displayname = null_fields.Char('Display Name', max_length=100, db_column='displayName')
    unit = null_fields.Key('Unit', db_column='unitID')
    stackable = models.NullBooleanField('Stackable?')
    highisgood = models.NullBooleanField('High is Good?', db_column='highIsGood')
    category = null_fields.Key('AttributeCategory', db_column='categoryID')

    class Meta(EveBase.Meta):
        ordering = ('attributename', )
        db_table = 'dgmAttributeTypes'

    def __unicode__(self):
        return "%d: %s" % (self.id, self.name)

    def get_icon(self, size):
        return self.graphic.get_icon(size)

    # Used when joining with Item.
    #valueint = None
    #valuefloat = None
    #def get_value(self):
    #    if self.valueint is not None:
    #        return self.valueint
    #    else:
    #        return self.valuefloat
    #value = property(get_value, None, None, None)

    # There are two name fields, but they are not always filled in.
    @property
    def name(self):
        if self.displayname:
            return self.displayname
        else:
            return self.attributename

class AttributeCategory(EveBase):
    id = null_fields.Small(primary_key=True, db_column='categoryID',)
    name = null_fields.Char(max_length=50, db_column='categoryName')
    description = null_fields.Char(max_length=200, db_column='categoryDescription')

    class Meta(EveBase.Meta):
        verbose_name_plural = "Attribute catagories"
        db_table = 'dgmAttributeCategories'


class BlueprintDetail(Base):
    # Using the proper foreign key relationship here causes a fatal django error.
    # (Only using the admin interface.)
    id = null_fields.Small(primary_key=True, db_column='blueprintTypeID')
    parent = null_fields.Key('BlueprintDetail', db_column='parentBlueprintTypeID', related_name='child_blueprints')
    makes = null_fields.Key('Item', db_column='productTypeID',
                              related_name='blueprint_madeby_qs',
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
    productiontime = null_fields.Int(db_column='productionTime')
    techlevel = null_fields.Small(db_column='techLevel')
    researchproductivitytime = null_fields.Int(db_column='researchProductivityTime')
    researchmaterialtime = null_fields.Int(db_column='researchMaterialTime')
    researchcopytime = null_fields.Int(db_column='researchCopyTime')
    researchtechtime = null_fields.Int(db_column='researchTechTime')
    productivitymodifier = null_fields.Int(db_column='productivityModifier')
    materialmodifier = null_fields.Small(db_column='materialModifier')
    wastefactor = null_fields.Small(db_column='wasteFactor')
    maxproductionlimit = null_fields.Int(db_column='maxProductionLimit')

    def item(self):
        return Item.objects.get(pk=self.id)

    class Meta(Base.Meta):
        ordering = ('id',)
        db_table = 'invBlueprintTypes'

class Category(EveBase):
    """This table contains the most basic groupings in game:

    Sample:
        Asteroid
        Charge
        Ship"""
    id = null_fields.Small(primary_key=True, db_column='categoryID')
    name = null_fields.Char(max_length=100, db_column='categoryName')
    description = null_fields.Char(max_length=3000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    published = models.NullBooleanField()

    class Meta(EveBase.Meta):
        verbose_name_plural = "Categories"
        db_table = 'invCategories'


class CharacterAncestry(EveBase):
    id = null_fields.Small(primary_key=True, db_column='ancestryID')
    name = null_fields.Char(max_length=100, db_column='ancestryName')
    bloodline = null_fields.Key('ccp.CharacterBloodline', db_column='bloodlineID')
    description = null_fields.Char(max_length=1000)
    perception = null_fields.Small()
    willpower = null_fields.Small()
    charisma = null_fields.Small()
    memory = null_fields.Small()
    intelligence = null_fields.Small()
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')

    class Meta(EveBase.Meta):
        verbose_name_plural = "Character ancestries"
        db_table = 'chrAncestries'


class CharacterAttribute(EveBase):
    id = null_fields.Small(primary_key=True, db_column='attributeID')
    name = null_fields.Char(max_length=100, db_column='attributeName')
    description = null_fields.Char(max_length=1000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')
    notes = null_fields.Char(max_length=500)

    class Meta(EveBase.Meta):
        db_table = 'chrAttributes'

class CharacterBloodline(EveBase):
    id = null_fields.Small(primary_key=True, db_column='bloodlineID')
    name = null_fields.Char(max_length=100, db_column='bloodlineName')
    race = null_fields.Key('Race', db_column='raceID')
    description = null_fields.Char(max_length=1000)
    maledescription = null_fields.Char(max_length=1000, db_column='maleDescription')
    femaledescription = null_fields.Char(max_length=1000, db_column='femaleDescription')
    ship = null_fields.Key('Item', related_name='bloodline_ship', db_column='shipTypeID')
    corporation = null_fields.Key('Corporation', db_column='corporationID')
    perception = null_fields.Small()
    willpower = null_fields.Small()
    charisma = null_fields.Small()
    memory = null_fields.Small()
    intelligence = null_fields.Small()
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')
    shortmaledescription = null_fields.Char(max_length=500, db_column='shortMaleDescription')
    shortfemaledescription = null_fields.Char(max_length=500, db_column='shortFemaleDescription')

    class Meta(EveBase.Meta):
        db_table = 'chrBloodlines'


class CharacterCareer(EveBase):
    race = null_fields.Key('Race', db_column='raceID')
    id = null_fields.Small(primary_key=True, db_column='careerID')
    name = null_fields.Char(max_length=100, db_column='careerName')
    description = null_fields.Char(max_length=2000)
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    school = null_fields.Key('School', related_name='careers', db_column='schoolID')

    class Meta(EveBase.Meta):
        db_table = 'chrCareers'


class CharacterCareerSpeciality(EveBase):
    id = null_fields.Small(primary_key=True, db_column='specialityID')
    career = null_fields.Key('CharacterCareer', db_column='careerID')
    name = null_fields.Char(max_length=100, db_column='specialityName')
    description = null_fields.Char(max_length=2000)
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')
    graphic = null_fields.Key('Graphic', db_column='graphicID')

    class Meta(EveBase.Meta):
        verbose_name_plural = "Character career specialities"
        db_table = 'chrCareerSpecialities'


class Constellation(EveBase):
    region = null_fields.Key('Region', db_column='regionID', related_name='constellations')
    id = models.IntegerField(primary_key=True, db_column='constellationID', )
    name = null_fields.Char(max_length=100, db_column='constellationName')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    xmin = null_fields.Float(db_column='xMin')
    xmax = null_fields.Float(db_column='xMax')
    ymin = null_fields.Float(db_column='yMin')
    ymax = null_fields.Float(db_column='yMax')
    zmin = null_fields.Float(db_column='zMin')
    zmax = null_fields.Float(db_column='zMax')
    faction = null_fields.Key('Faction', db_column='factionID')
    radius = null_fields.Float()
    sov_time = models.DateTimeField(db_column='sovereigntyDateTime', null=True)
    grace_date_time = models.DateTimeField(db_column='graceDateTime', null=True)
    alliance = null_fields.Key('Alliance', related_name='constellations')

    class Meta(EveBase.Meta):
        db_table = 'mapConstellations'

    def get_absolute_url(self):
        return "/constellation/%s/" % self.name

    def moons(self):
        return self.map.filter(type__name='Moon')

    def get_icon(self, size):
        if self.alliance:
            return self.alliance.get_icon(size)
        elif self.faction:
            return self.faction.get_icon(size)
        elif self.region.faction:
            return self.region.faction.get_icon(size)
        else:
            return None

    @property
    def note(self):
        return self.owner()

    def owner(self):
        if self.faction:
            return self.faction
        else:
            alliance = self.alliance
            if alliance:
                return alliance
            else:
                return None

#
#class ContrabandType(EveBase):
#    factionid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='typeID')
#    standingloss = models.FloatField()
#    confiscateminsec = models.FloatField()
#    finebyvalue = models.FloatField()
#    attackminsec = models.FloatField()
#
#    class Meta(EveBase.Meta):
#        ordering = ('id',)
#        db_table = 'invContrabandTypes'


class Corporation(EveBase):
    id = models.IntegerField(primary_key=True, db_column='corporationID')
    #mainactivity = null_fields.Key('CorporationActivity',
    #                                 db_column='mainactivityID',
    #                                 related_name='corp_activity_1')
    #secondaryactivity = null_fields.Key('CorporationActivity',
    #                                      db_column='secondaryactivityID',
    #                                      related_name='corp_activity_2',
    #                                      null=True, blank=True)
    size = null_fields.Char(max_length=1)
    extent = null_fields.Char(max_length=1)
    solarsystem = null_fields.Key('SolarSystem', db_column='solarSystemID')
    investorid1 = null_fields.Int(db_column='investorID1')
    investorshares1 = null_fields.Small(db_column='investorShares1')
    investorid2 = null_fields.Int(db_column='investorID2')
    investorshares2 = null_fields.Small(db_column='investorShares2')
    investorid3 = null_fields.Int(db_column='investorID3')
    investorshares3 = null_fields.Small(db_column='investorShares3')
    investorid4 = null_fields.Int(db_column='investorID4')
    investorshares4 = null_fields.Small(db_column='investorShares4')
    friend = null_fields.Key('Name', db_column='friendID', related_name='friends')
    enemy = null_fields.Key('Name', db_column='enemyID', related_name='enemies')
    publicshares = null_fields.Int(db_column='publicShares')
    initialprice = null_fields.Int(db_column='initialPrice')
    minsecurity = null_fields.Float(db_column='minSecurity')
    scattered = models.NullBooleanField()
    fringe = null_fields.Small()
    corridor = null_fields.Small()
    hub = null_fields.Small()
    border = null_fields.Small()
    faction = null_fields.Key('Faction', db_column='factionID', related_name='corporations')
    sizefactor = null_fields.Float(db_column='sizeFactor')
    stationcount = null_fields.Small(db_column='stationCount')
    stationsystemcount = null_fields.Small(db_column='stationSystemCount')
    description = null_fields.Char(max_length=4000)
    alliance = null_fields.Key('Alliance', related_name='corporations')
    last_updated = models.DateTimeField(null=True)
    cached_until = models.DateTimeField(null=True)

    refresh_failed = None

    class Meta(EveBase.Meta):
        ordering = ('id',)
        db_table = 'crpNPCCorporations'

    @property
    @cachedmethod(60)
    def name(self):
        return Name.objects.get(pk=self.id).name

    def get_icon(self, size):
        if self.is_player_corp:
            return '/static/corplogos/%d_%d/%s.png' % (size, size, self.id)
        else:
            return '/static/ccp-icons/corporation/%d/c_%s.jpg' % (size, self.id)

    @property
    def is_player_corp(self):
        return self.faction == None

    def directors(self):
        return self.characters.filter(is_director=True)

    def logofile(self):
        return os.path.join(settings.MEDIA_ROOT, 'corplogos', '32_32', (str(self.id) + '.png'))

    def updatelogo(self, record=None):
        path = self.logofile()
        if os.path.exists(path):
            return('No logo generation required.')
        try:
            dir, file = os.path.split(path)
            if not os.path.exists(dir):
                os.makedirs(dir)
            if record is None:
                record = API.corp.CorporationSheet(corporationID=self.id)
            logo = evelogo.CorporationLogo(record.logo, size=32)
            logo.save(path, 'png')
            return('Logo created.')
        except Exception, e:
            return('Failed to make corp icon for: %s. [%s]' % (self.id, str(e)))

    def refresh(self, character=None, name=None):
        messages = []
        self.refresh_failed = False

        if self.is_player_corp is False:
            messages.append('No refresh needed for NPC corps.')
            return messages

        i = Item.objects.get(name='Corporation')

        record = None
        try:
            if character:
                api = character.api_corporation()
                record = api.CorporationSheet() # Adding corpid triggers an API bug.
            else:
                api = API
                record = api.corp.CorporationSheet(corporationID=self.id)
            name = record.corporationName
        except eveapi.Error, e:
            messages.append("EVE API ERROR on corp (%s) refresh: %s" % (self.id, e))
            self.refresh_failed = True
            return messages

        if name == None:
            messages.append("Unable to refresh corporation '%s', no name available." % self.id)
            self.refresh_failed = True
            return messages

        try:
            name = Name.objects.get(id=self.id)
        except Name.DoesNotExist:
            name = Name(id=self.id, name=name, type=i, group=i.group, category=i.group.category)
            name.save()
            messages.append("Added: %s to name database. [%d]" % (name.name, name.id))

        if record.allianceID:
            try:
                self.alliance = Alliance.objects.get(pk=record.allianceID)
            except Alliance.DoesNotExist:
                # Happens when we first create the alliance. The corp will
                # be added later.
                messages.append('Alliance unavailable: %s' % record.allianceID)

        messages.append('Corp refreshed: %s(%s)' % (name.name, self.id))
        self.save()

        self.updatelogo()

        return messages

#class CorporationActivity(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='activityID')
#    name = null_fields.Char(max_length=100, db_column='activityname')
#    description = models.TextField()
#
#    class Meta(EveBase.Meta):
#        verbose_name_plural = "Corporation activities"
#        db_table = 'crpActivities'
#

class CorporationDivision(EveBase):
    id = null_fields.Small(primary_key=True, db_column='divisionID')
    name = null_fields.Char(max_length=100, db_column='divisionName')
    description = null_fields.Char(max_length=1000)
    leadertype = null_fields.Char(max_length=100, db_column='leaderType')

    class Meta(EveBase.Meta):
        db_table = 'crpNPCDivisions'

class Effect(EveBase):
    id = null_fields.Small(primary_key=True, db_column='effectID')
    name = null_fields.Char(max_length=400, db_column='effectName')
    effectcategory = null_fields.Small(db_column='effectCategory')
    preexpression = null_fields.Int(db_column='preExpression')
    postexpression = null_fields.Int(db_column='postExpression')
    description = null_fields.Char(max_length=1000)
    guid = null_fields.Char(max_length=60)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    isoffensive = models.NullBooleanField(db_column='isOffensive')
    isassistance = models.NullBooleanField(db_column='isAssistance')
    durationattributeid = null_fields.Small(db_column='durationAttributeID')
    trackingspeedattributeid = null_fields.Small(db_column='trackingSpeedAttributeID')
    dischargeattributeid = null_fields.Small(db_column='dischargeAttributeID')
    rangeattributeid = null_fields.Small(db_column='rangeAttributeID')
    falloffattributeid = null_fields.Small(db_column='falloffAttributeID')
    disallowautorepeat = models.NullBooleanField(db_column='disallowAutoRepeat')
    published = models.NullBooleanField()
    displayname = null_fields.Char(max_length=100, db_column='displayName')
    iswarpsafe = models.NullBooleanField(db_column='isWarpSafe')
    rangechance = models.NullBooleanField(db_column='rangeChance')
    electronicchance = models.NullBooleanField(db_column='electronicChance')
    propulsionchance = models.NullBooleanField(db_column='propulsionChance')
    distribution = null_fields.Small()
    sfxname = null_fields.Char(max_length=20, db_column='sfxName')
    npcusagechanceattributeid = null_fields.Small(db_column='npcUsageChanceAttributeID')
    npcactivationchanceattributeid = null_fields.Small(db_column='npcActivationChanceAttributeID')
    fittingusagechanceattributeid = null_fields.Small(db_column='fittingUsageChanceAttributeID')

    class Meta(EveBase.Meta):
        db_table = 'dgmEffects'

class Faction(EveBase):
    """Table describes the major factions in game:

    Amaar Empire
    CONCORD Assembly
    ...
    Thukker Tribe"""
    id = null_fields.Int(primary_key=True, db_column='factionID')
    name = null_fields.Char(max_length=100, db_column='factionName')
    description = null_fields.Char(max_length=1000)
    raceids = null_fields.Int(db_column='raceIDs')
    solarsystem = null_fields.Key('SolarSystem', db_column='solarSystemID', related_name='home_system')
    corporation = null_fields.Key('Corporation', db_column='corporationID', related_name='base_coporation')
    sizefactor = null_fields.Float(db_column='sizeFactor')
    stationcount = null_fields.Small(db_column='stationCount')
    stationsystemcount = null_fields.Small(db_column='stationSystemCount')
    militia_corporation = null_fields.Key('Corporation', db_column='militiaCorporationID', related_name='faction2')

    class Meta(EveBase.Meta):
        db_table = 'chrFactions'

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
               'The Blood Raider Covenant':'blood-raiders',
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


class Group(EveBase):
    """This table describes goups like: Ammo and Advanced Torpedo.

    It also contains non-item groups like 'Alliance' and
    'Asteroid Angel Cartel Officer'."""
    id = null_fields.Small(primary_key=True, db_column='groupID')
    category = null_fields.Key('Category', db_column='categoryID', related_name='groups')
    name = null_fields.Char(max_length=100, db_column='groupName')
    description = null_fields.Char(max_length=3000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    usebaseprice = models.NullBooleanField(db_column='useBasePrice')
    allowmanufacture = models.NullBooleanField("Manafacturable?", db_column='allowManufacture')
    allowrecycler = models.NullBooleanField(db_column='allowRecycler')
    anchored = models.NullBooleanField()
    anchorable = models.NullBooleanField()
    fittablenonsingleton = models.NullBooleanField(db_column='fittableNonSingleton')
    published = models.NullBooleanField()
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta(EveBase.Meta):
        db_table = 'invGroups'

    @cachedmethod(60*24)
    def get_icon(self, size):
        if self.is_npc():
            try:
                x = self.items.all()[0]
            except IndexError:
                return get_graphic(None)
            return x.get_icon(size)
        else:
            return self.graphic.get_icon(size)

    def get_absolute_url(self):
        if self.is_npc():
            return u'/npc/%s' % self.slug
        else:
            return 'x'

    def is_npc(self):
        return self.category.name == 'Entity'


class Graphic(EveBase):
    id = null_fields.Small(primary_key=True, db_column='graphicID')
    url3d = null_fields.Char(max_length=100, db_column='url3D')
    urlweb = null_fields.Char(max_length=100, db_column='urlWeb')
    description = null_fields.Char(max_length=1000)
    published = models.NullBooleanField()
    obsolete = models.NullBooleanField()
    icon = null_fields.Char(max_length=100)
    urlsound = null_fields.Char(max_length=100, db_column='urlSound')
    explosionid = null_fields.Small(db_column='explosionID')

    color = 'white'
    dir = '/static/ccp-icons'

    class Meta(EveBase.Meta):
        ordering = ('id',)
        db_table = 'eveGraphics'

    def __unicode__(self):
        return "%s: %s (%s)" % (self.id, self.urlweb, self.icon)

    #-------------------------------------------------------------------------
    # All things iconic.

    def get_icon(self, size):
        d = {
                'dir'    : self.dir,
                'size'   : size,
                'color'  : self.color,
                'icon'   : self.icon,
            }
        icon = "%(dir)s/icons/%(size)d_%(size)d/icon%(icon)s.png" % d
        return icon

    def save(self, *args, **kwargs):
        """Custom save handler to set a good and safe id on new objects."""
        if self.id is None:
            if not self.description:
                self.description = 'Automatically added by Django'
            min_id = 10000 # We enter new ID's on demand, but not below this value.
            max_id = Graphic.objects.all().order_by('-id')[0].id
            max_id = max(max_id, min_id)
            self.id=max_id+1

        super(Graphic, self).save(*args, **kwargs)

class NullGraphic(object):
    """
    Fake Graphic object that will appease the needed parts of the Widget,
    but only gives out a static 1px transparent image.
    """
    def get_icon(self, size):
        return NULL_GRAPHIC


def get_graphic(icon):
    """Helper utility that will find one icon or make it for you.
    Used in NavigationElement and elsewhere.
    Useful because icons are often non-unique, but I don't care in my app."""
    # Special key for the blank icon.
    if icon is None:
        return NullGraphic()
    elif isinstance(icon, type('')):
        g = Graphic.objects.filter(icon=icon)
        if g.count() == 0:
            graphic = Graphic.objects.create(icon=icon)
        else:
            graphic = g[0]
        return graphic
    else:
        return icon


class InventoryMetaGroup(EveBase):
    """
    The categories of items:
      Tech I
      Tech II
      Storyline
      Faction
      Officer
      ...

    """
    id = null_fields.Small(primary_key=True, db_column='metaGroupID')
    name = null_fields.Char(max_length=100, db_column='metaGroupName')
    description = null_fields.Char(max_length=1000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')

    class Meta(EveBase.Meta):
        db_table = 'invMetaGroups'

class InventoryMetaType(EveBase):
    """
    Gives all of the items that are the same base item.

    e.g. item.meta.parent.meta_children.all() is all items of the same type.
    Group by metagroup for the category (T1, T2, Faction, etc...)

    """
    item = null_fields.Key('Item', db_column='typeID', related_name='meta', primary_key=True)
    parent = null_fields.Key('Item', db_column='parentTypeID', related_name='meta_children')
    metagroup = null_fields.Key('InventoryMetaGroup', db_column='metaGroupID')

    class Meta(EveBase.Meta):
        ordering = ('item',)
        db_table = 'invMetaTypes'


class ItemSkillManager(models.Manager):
    def get_query_set(self):
        return super(ItemSkillManager, self).get_query_set().filter(
            group__category__name__exact = 'Skill',
            published = True,
        )

class Item(EveBase):
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
    id = null_fields.Small(primary_key=True, db_column='typeID')
    group = null_fields.Key('Group', db_column='groupID', related_name='items')
    name = null_fields.Char(max_length=100, db_column='typeName')
    real_description = null_fields.Char(max_length=3000, db_column='description')
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    radius = null_fields.Float()
    mass = null_fields.Float()
    volume = null_fields.Float()
    capacity = null_fields.Float()
    portionsize = null_fields.Int(db_column='portionSize')
    race = null_fields.Key('Race', db_column='raceID')
    baseprice = null_fields.Float(db_column='basePrice')
    published = models.NullBooleanField()
    marketgroup = null_fields.Key('MarketGroup', db_column='marketGroupID')
    chanceofduplicating = null_fields.Float(db_column='chanceOfDuplicating')
    slug = models.SlugField(max_length=100, db_index=True, default='')

    # If I don't have both managers, it gets weird.
    objects = models.Manager()
    # Allows for a search for just skills.
    skill_objects = ItemSkillManager()

    class Meta(EveBase.Meta):
        # If I use 'name' instead of 'typename', then the BlueprintDetails model dies
        # in the admin list view. Like this, the list works, but not the detail.
        #ordering = ('name', )
        db_table = 'invTypes'

    @property
    @cachedmethod(60*6)
    def category(self):
        return self.group.category

    def get_absolute_url(self):
        return "/item/%s/" % self.slug

    @property
    def parent(self):
        return self.marketgroup

    @property
    def description(self):
        if self.is_blueprint:
            return self.blueprint_makes.real_description
        else:
            return self.real_description

    # All things iconic.

    @cachedmethod(60*6)
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
        cats = (
            'Blueprint', 'Drone', 'Ship', 'Station',
            'Structure', 'Deployable', 'Entity'
        )
        cat = self.category.name
        if cat in cats:
            d = {
                'cat':     cat.lower(),
                'dir':     Graphic.dir,
                'size':    size,
                'color':   Graphic.color,
                'item_id': self.id,
            }
            if cat == 'Entity' and self.marketgroup is None:
                d['cat'] = 'npc'
                d['item_id'] = self.graphic_id
            icon = "%(dir)s/%(cat)s/%(size)d_%(size)d/%(item_id)d.png" % d
        else:
            icon = self.graphic.get_icon(size)
        return icon

    @cachedmethod(60)
    def attributes_by_name(self):
        return dict([(a.attribute.attributename, a)
            for a in self.attributes.select_related('attributes').all()])

    @cachedmethod(60)
    def attribute_by_name(self, name):
        return self.attributes.get(attribute__attributename=name)

    @property
    def meta_level(self):
        return int(self.attribute_by_name('metaLevel').value)

    @property
    def tech_level(self):
        return int(self.attribute_by_name('techLevel').value)

    @cachedmethod(60)
    def dps(self):
        d = self.attributes_by_name()
        if 'speed' not in d:
            return dict()
        rate = max(d['speed'].value, 1.0)
        # Convert to seconds.
        if rate > 100.0:
                rate = rate / 1000.0

        if 'damageMultiplier' in d:
            mult = d['damageMultiplier'].value
        else:
            mult = 1.00

        dps = dict()
        if 'emDamage' in d:
            dps['em'] = d['emDamage'].value * mult / rate
        if 'explosiveDamage' in d:
            dps['explosive'] = d['explosiveDamage'].value * mult / rate
        if 'kineticDamage' in d:
            dps['kinetic'] = d['kineticDamage'].value * mult / rate
        if 'thermalDamage' in d:
            dps['thermal'] = d['thermalDamage'].value * mult / rate

        # Does it have missles?
        if 'entityMissileTypeID' in d and 'missileLaunchDuration' in d:
            if 'missileDamageMultiplier' in d:
                mult = d['missileDamageMultiplier'].value
            else:
                mult = 1.00
            rate = d['missileLaunchDuration'].value
            # Sometimes the rate really IS in seconds.
            if rate > 100.0:
                rate = rate / 1000.0
            try:
                type = Item.objects.get(id=d['entityMissileTypeID'].value)
                dps['missile_type'] = type
                attributes = type.attributes_by_name()
                if 'emDamage' in attributes:
                    dps['missile_em'] = attributes['emDamage'].value * mult / rate
                if 'explosiveDamage' in attributes:
                    dps['missile_explosive'] = attributes['explosiveDamage'].value * mult / rate
                if 'kineticDamage' in attributes:
                    dps['missile_kinetic'] = attributes['kineticDamage'].value * mult / rate
                if 'thermalDamage' in attributes:
                    dps['missile_thermal'] = attributes['thermalDamage'].value * mult / rate
            except Item.DoesNotExist:
                pass

        for type in ('em', 'explosive', 'kinetic', 'thermal'):
            if type in dps:
                total = dps[type]
            else:
                total = 0
            if 'missile_' + type in dps:
                total = total + dps['missile_'+type]
            dps['total_' + type] = total

        return dps

    @cachedmethod(60)
    def effects(self):
        set = Effect.objects.extra(
            tables=['dgmtypeeffects'],
            where=[
                'dgmtypeeffects.effectid = dgmeffects.effectID',
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
        if self.category.name == 'Skill':
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

    # Construction-orientated methods
    @property
    def is_blueprint(self):
        if self.category.name == 'Blueprint':
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
        if self.is_blueprint:
            return BlueprintDetail.objects.get(pk=self.pk)
        else:
            return BlueprintDetail.objects.get(pk=self.blueprint.pk)

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
        if hasattr(self, '_blueprint'):
            return self._blueprint
        elif self.is_blueprint:
            blueprint = self
        elif self.blueprint_madeby_qs.count() > 0:
            #assert(self.blueprint_madeby_qs.count() == 1)
            blueprint = self.blueprint_madeby_qs.all()[0].item()
            if not blueprint.published:
                blueprint = None
        else:
            blueprint = None
        self._blueprint = blueprint
        return blueprint

    @property
    def blueprint_makes(self):
        if self.blueprint is None:
            return None
        else:
            return self.blueprint_details.makes

    def materials(self, activity=None):
        """
        >>> myrm = Item.objects.get(name='Myrmidon Blueprint')
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

        # We no longer show materials for the blueprint automatically.
        filter = filter & Q(item=self)

        return Material.objects.filter(filter).select_related('material__group__category', 'material__graphic', 'activity')

    def refines(self):
        return self.materials(activity='Refining')


class ItemAttribute(EveBase):
    item = null_fields.Key('Item', db_column='typeID', related_name='attributes')
    attribute = null_fields.Key('Attribute', db_column='attributeID', related_name='items')
    valueint = null_fields.Int(db_column='valueInt')
    valuefloat = null_fields.Float(db_column='valueFloat')

    class Meta(EveBase.Meta):
        db_table = u'dgmTypeAttributes'
        ordering = ('item',)

    def __unicode__(self):
        return '%s = %s' % (str(self.attribute), self.value)

    @property
    def name(self):
        return self.attribute.name

    @cachedmethod(60*4)
    def get_icon(self, size):
        g = None
        name = self.attribute.attributename

        if name.startswith('chargeGroup') or name == 'launcherGroup':
            g = Group.objects.get(pk = int(self.value) )
        # There are no default icons on required skills. :(
        elif name == 'requiredSkill1':
            g = get_graphic('50_13')
        elif name == 'requiredSkill2':
            g = get_graphic('50_11')
        elif name == 'requiredSkill3':
            g = get_graphic('50_14')
        elif name == 'reprocessingSkillType':
            g = get_graphic('17_01')
        elif name in ('primaryAttribute','secondaryAttribute'):
            g = Attribute.objects.get(pk=int(self.value)).graphic
        elif self.attribute.graphic:
            g = self.attribute.graphic
        else:
            g = Graphic.objects.get(icon='07_15')
        return g.get_icon(size)

    @property
    def value(self):
        if self.valuefloat is not None:
            return self.valuefloat
        else:
            return self.valueint

    @property
    def display_value(self):
        if self.attribute.unit is None:
            return self.value

        # Big lookup....
        unit = self.attribute.unit.name
        if unit == 'Modifier Percent':
            value = "%.0f %%" % ((self.value - 1.0) * 100)
        elif unit == 'Sizeclass':
            value = {
                1: 'Small',
                2: 'Medium',
                3: 'Large',
                4: 'X-Large'
            }[int(self.value)] # Sometimes it's a float. Don't ask me why.
        elif self.attribute.attributename.startswith('requiredSkill'):
            try:
                level = int( self.item.attribute_by_name('%sLevel' % self.attribute.attributename).value )
            except ItemAttribute.DoesNotExist:
                level = 1
            value = "%s %s" % (
                Item.objects.get(pk=int(self.value)),
                level,
            )
        elif unit == 'groupID':
            value = Group.objects.get(pk=int(self.value))
        elif unit == 'Milliseconds' and self.value > 1000:
            value = time(self.value/1000.0)
        elif unit == 'typeID':
            value = Item.objects.get(pk=int(self.value)).name
        elif unit == 'attributeID':
            value = Attribute.objects.get(pk=int(self.value)).name
        elif unit == 'Inverse Absolute Percent':
            value = "%d %%" % int((1 - self.value) * 100)
        else:
            value = str(comma(self.value)) + " " + self.attribute.unit.displayname
        return value

class MapDenormalize(EveBase):
    id = models.IntegerField(primary_key=True, db_column='itemID')
    type = null_fields.Key('Item', db_column='typeID')
    group = null_fields.Key('Group', db_column='groupID')
    solarsystem = null_fields.Key('SolarSystem', db_column='solarSystemID', related_name='map')
    constellation = null_fields.Key('Constellation', db_column='constellationID', related_name='map')
    region = null_fields.Key('Region', db_column='regionID', related_name='map')
    orbits = null_fields.Key('MapDenormalize', db_column='orbitID')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    radius = null_fields.Float()
    name = null_fields.Char(max_length=100, db_column='itemName')
    security = null_fields.Float()
    celestialindex = null_fields.Small(db_column='celestialIndex')
    orbitindex = null_fields.Small(db_column='orbitIndex')

    class Meta(EveBase.Meta):
        db_table = 'mapDenormalize'

#class MapLandmark(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='landmarkID')
#    name = models.TextField(db_column='landmarkname')
#    description = models.TextField()
#    locationid = null_fields.Int()
#    x = models.FloatField()
#    y = models.FloatField()
#    z = models.FloatField()
#    radius = models.FloatField()
#    graphic = null_fields.Key('Graphic', db_column='graphicID')
#    importance = models.IntegerField()
#    url2d = models.TextField()
#
#    class Meta(EveBase.Meta):
#        db_table = 'mapLandmarks'

class MarketGroup(EveBase):
    '''This is the list of the groups as seen in the market type browser.
    (Which is more detailed than the normal group table.)

    Items here have a self-referential parent, which is used to create heirarchy
    within this table.'''

    id = null_fields.Small(primary_key=True, db_column='marketGroupID')
    parent = null_fields.Key('MarketGroup', db_column='parentGroupID')
    name = null_fields.Char(max_length=100, db_column='marketGroupName')
    description = null_fields.Char(max_length=3000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    hastypes = models.NullBooleanField(db_column='hasTypes')
    slug = models.SlugField(max_length=100, db_index=True)

    class Meta(EveBase.Meta):
        db_table = 'invMarketGroups'


    def get_absolute_url(self):
        return "/items/%s/" % self.slug

    @cachedmethod(60*4)
    def get_icon(self, size):
        if self.graphic:
            return self.graphic.get_icon(size)
        else:
            return None


class MaterialPublishedManager(models.Manager):
    def get_query_set(self):
        return super(MaterialPublishedManager, self).get_query_set().select_related().filter(item__published=True,
                                                                                             activity__published=True)

class Material(EveBase):
    """
    All the 'stuff' to make other 'stuff'.
    """
    item = null_fields.Key('Item', db_column='typeID')
    activity = null_fields.Key('RamActivity', db_column='activityID')
    material = null_fields.Key('Item', db_column='requiredTypeID', related_name='helps_make')
    quantity = null_fields.Int()
    damageperjob = null_fields.Float(db_column='damagePerJob')
    recycle = models.NullBooleanField()
    objects = MaterialPublishedManager()

    class Meta(EveBase.Meta):
        ordering = ('id',)
        db_table = 'typeActivityMaterials'


    def __unicode__(self):
        return "%s: %d" % (self.name, self.quantity)

    @property
    def name(self):
        return self.material.name

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


class Name(EveBase):
    """This table contains the names of planets, stars, systems and corporations."""
    id = models.IntegerField(primary_key=True, db_column='itemID')
    name = null_fields.Char(max_length=100, db_column='itemName')
    category = null_fields.Key('Category', db_column='categoryID', related_name='names')
    group = null_fields.Key('Group', db_column='groupID', related_name='names')
    type = null_fields.Key('Item', db_column='typeID', related_name='names')

    class Meta(EveBase.Meta):
        db_table = 'eveNames'


class Race(EveBase):
    """Table contains the basic races in the game:

    Amaar
    Gallente
    Jove"""
    id = null_fields.Small(primary_key=True, db_column='raceID')
    name = null_fields.Char(max_length=100, db_column='raceName')
    description = null_fields.Char(max_length=1000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    shortdescription = null_fields.Char(max_length=500, db_column='shortDescription')

    class Meta(EveBase.Meta):
        db_table = 'chrRaces'


class Reaction(EveBase):
    reaction = null_fields.Key('Item', db_column='reactionTypeID', related_name='reactions')
    input = models.NullBooleanField()
    item = null_fields.Key('Item', db_column='typeID', related_name='reacts')
    quantity = null_fields.Small()

    def __unicode__(self):
        arrow = '=>'
        if self.input == 1:
            arrow = '<-'
        return "%s %s %s[%d]" % (self.reaction, arrow, self.item, self.quantity)

    class Meta(EveBase.Meta):
        db_table = 'invTypeReactions'
        ordering = ('reaction',)


class RamActivity(EveBase):
    """
    mysql> desc ccp_ramactivity;
    +--------------+----------+------+-----+---------+-------+
    | Field        | Type     | Null | Key | Default | Extra |
    +--------------+----------+------+-----+---------+-------+
    | activityID   | int(11)  | NO   | PRI | NULL    |       |
    | activityName | tinytext | NO   |     | NULL    |       |
    | iconNo       | tinytext | YES  |     | NULL    |       |
    | description  | text     | NO   |     | NULL    |       |
    | published    | int(11)  | NO   |     | NULL    |       |
    +--------------+----------+------+-----+---------+-------+
    5 rows in set (0.00 sec)
    """
    id = null_fields.Small(primary_key=True, db_column='activityID')
    name = null_fields.Char(max_length=100, db_column='activityName')
    iconNo = null_fields.Char(max_length=5)
    description = null_fields.Char(max_length=1000)
    published = models.NullBooleanField()

    class Meta(EveBase.Meta):
        db_table = 'ramActivities'


class Region(EveBase):
    id = null_fields.Int(primary_key=True, db_column='regionID')
    name = null_fields.Char(max_length=100, db_column='regionName')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    xmin = null_fields.Float(db_column='xMin')
    xmax = null_fields.Float(db_column='xMax')
    ymin = null_fields.Float(db_column='yMin')
    ymax = null_fields.Float(db_column='yMax')
    zmin = null_fields.Float(db_column='zMin')
    zmax = null_fields.Float(db_column='zMax')
    faction = null_fields.Key('Faction', db_column='factionID')
    radius = null_fields.Float()
    slug = models.SlugField(db_index=True)

    class Meta(EveBase.Meta):
        db_table = 'mapRegions'

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

    @property
    def note(self):
        return self.owner()

    def alliance(self):
        qs = self.constellations.select_related('alliance').filter(alliance__isnull=False)
        alliance = None
        for i in qs:
            if alliance is None:
                alliance = i.alliance
            if alliance != i.alliance:
                return None
        return alliance

    @cachedmethod(60*6)
    def get_icon(self, size):
        owner = self.owner()

        if owner is None:
            return NULL_GRAPHIC
        else:
            return owner.get_icon(size)


class School(EveBase):
    race = null_fields.Key('Race', db_column='raceID')
    id = null_fields.Small(primary_key=True, db_column='schoolID')
    name = null_fields.Char(max_length=100, db_column='schoolName')
    description = null_fields.Char(max_length=1000)
    graphic = null_fields.Key('Graphic', db_column='graphicID')
    corporation = null_fields.Key('Corporation', db_column='corporationID')
    agent = null_fields.Key('Agent', db_column='newAgentID')
    career = null_fields.Key('CharacterCareer', related_name='schools', db_column='careerID')

    class Meta(EveBase.Meta):
        db_table = 'chrSchools'


class SolarSystem(EveBase):
    region = null_fields.Key('Region', db_column='regionID', related_name='solarsystems')
    constellation = null_fields.Key('Constellation', db_column='constellationID', related_name='solarsystems')
    id = null_fields.Int(primary_key=True, db_column='solarSystemID')
    name = null_fields.Char(max_length=100, db_column='solarSystemName')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    xmin = null_fields.Float(db_column='xMin')
    xmax = null_fields.Float(db_column='xMax')
    ymin = null_fields.Float(db_column='yMin')
    ymax = null_fields.Float(db_column='yMax')
    zmin = null_fields.Float(db_column='zMin')
    zmax = null_fields.Float(db_column='zMax')
    luminosity = null_fields.Float()
    border = models.NullBooleanField()
    fringe = models.NullBooleanField()
    corridor = models.NullBooleanField()
    hub = models.NullBooleanField()
    international = models.NullBooleanField()
    regional = models.NullBooleanField()
    constellation2 = models.NullBooleanField(db_column='constellation')
    security = null_fields.Float()
    faction = null_fields.Key('Faction', db_column='factionID', related_name='solarsystems')
    radius = null_fields.Float()
    suntypeid = null_fields.Small(db_column='sunTypeID')
    securityclass = null_fields.Char(max_length=2, db_column='securityClass')
    alliance = null_fields.Key('Alliance', related_name='solarsystems')
    sov = null_fields.Int(db_column='sovereigntyLevel')
    sov_time = models.DateTimeField(db_column='sovereigntyDate', null=True)
    alliance_old = null_fields.Key('Alliance', related_name='solarsystems_lost')

    class Meta(EveBase.Meta):
        db_table = 'mapSolarSystems'

    def moons(self):
        return self.map.filter(type__name='Moon')

    def belts(self):
        return self.map.filter(type__name='Asteroid Belt')

    def get_absolute_url(self):
        return "/solarsystem/%s/" % self.name

    def get_icon(self, size):
        return self.alliance.get_icon(size)

    @property
    def note(self):
        return self.owner()

    def owner(self):
        if self.faction:
            return self.faction
        else:
            alliance = self.alliance
            if alliance:
                return alliance
            else:
                return None


class Station(EveBase):
    id = models.IntegerField(primary_key=True, db_column='stationID')
    security = null_fields.Small()
    dockingcostpervolume = null_fields.Float('Docking', db_column='dockingCostPerVolume')
    maxshipvolumedockable = null_fields.Float('Max Dockable', db_column='maxShipVolumeDockable')
    officerentalcost = null_fields.Int('Office Rental', db_column='officeRentalCost')
    operationid = null_fields.Small(db_column='operationID')
    type = null_fields.Key('Item', db_column='stationTypeID', related_name='staitons')
    corporation = null_fields.Key('Corporation', db_column='corporationID')
    solarsystem = null_fields.Key('SolarSystem', db_column='solarSystemID',related_name='stations')
    constellation = null_fields.Key('Constellation', db_column='constellationID',related_name='stations')
    region = null_fields.Key('Region', db_column='regionID', related_name='stations')
    name = null_fields.Char(max_length=100, db_column='stationName')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    reprocessingefficiency = null_fields.Float('%', default=0, db_column='reprocessingEfficiency')
    reprocessingstationstake = null_fields.Float('Take', default=0, db_column='reprocessingStationsTake')
    reprocessinghangarflag = null_fields.Small('Hangar?', db_column='reprocessingHangarFlag')
    capital_station = null_fields.Int('Made Capital', db_column='capitalStation')
    ownership_date = models.DateTimeField('Ownership Date', db_column='ownershipDateTime', null=True)
    upgrade_level = null_fields.Int(db_column='upgradeLevel')
    custom_service_mask = null_fields.Int('Service Mask', db_column='customServiceMask')

    class Meta(EveBase.Meta):
        db_table = 'staStations'

    def get_icon(self, size):
        return self.corporation.get_icon(size)

class PosFuel(EveBase):
    q = Q(group__name='Control Tower') & Q(published=True)

    tower = null_fields.Key('Item', limit_choices_to = q, db_column = 'controlTowerTypeID', related_name='fuel')
    type = null_fields.Key('Item', db_column='resourceTypeID', related_name='fuel_for')
    purpose = null_fields.Key('PosFuelPurpose', db_column='purpose')
    quantity = null_fields.Int()
    minsecuritylevel = null_fields.Float(db_column='minSecurityLevel')
    faction = null_fields.Key('Faction', db_column='factionID')

    def __unicode__(self):
        return "%s (%d)" % (self.type, self.quantity)

    class Meta(EveBase.Meta):
        ordering = ('tower', 'purpose', 'type')
        db_table = 'invControlTowerResources'

class PosFuelPurpose(EveBase):
    id = null_fields.Small(primary_key=True, db_column='purpose')
    name = null_fields.Char(max_length=100, db_column='purposeText')

    class Meta(EveBase.Meta):
        db_table = 'invControlTowerResourcePurposes'


class Unit(EveBase):
    id = null_fields.Small(primary_key=True, db_column='unitID')
    name = null_fields.Char(max_length=100, db_column='unitName')
    displayname = null_fields.Char(max_length=20, db_column='displayName')
    description = null_fields.Char(max_length=1000)

    class Meta(EveBase.Meta):
        db_table = 'eveUnits'


class Universe(EveBase):
    id = models.IntegerField(primary_key=True, db_column='universeID')
    name = null_fields.Char(max_length=100, db_column='universeName')
    x = null_fields.Float()
    y = null_fields.Float()
    z = null_fields.Float()
    xmin = null_fields.Float(db_column='xMin')
    xmax = null_fields.Float(db_column='xMax')
    ymin = null_fields.Float(db_column='yMin')
    ymax = null_fields.Float(db_column='yMax')
    zmin = null_fields.Float(db_column='zMin')
    zmax = null_fields.Float(db_column='zMax')
    radius = null_fields.Float()

    class Meta(EveBase.Meta):
        db_table = 'mapUniverse'

#class MapClestialStatistics(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='celestialID')
#    temperature = models.FloatField()
#    spectralclass = null_fields.Char(max_length=30)
#    luminosity = models.FloatField()
#    age = models.FloatField()
#    life = models.FloatField()
#    orbitradius = models.FloatField()
#    eccentricity = models.FloatField()
#    massdust = models.FloatField()
#    massgas = models.FloatField()
#    fragmented = null_fields.Char(max_length=15)
#    density = models.FloatField()
#    surfacegravity = models.FloatField()
#    escapevelocity = models.FloatField()
#    orbitperiod = models.FloatField()
#    rotationrate = models.FloatField()
#    locked = null_fields.Char(max_length=15)
#    pressure = models.FloatField()
#    radius = models.FloatField()
#    mass = models.FloatField()


# class Agent_config(EveBase):
#     id = models.IntegerField(primary_key=True, db_column='agentID')
#     k = null_fields.Char(max_length=150)
#     v = models.TextField()
#     class Meta:
#         db_table = u'agtconfig'


# class Character_careerskills(EveBase):
#     careerid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerskills'


# class Character_careerspecialityskills(EveBase):
#     specialityid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerspecialityskills'


# class Character_raceskills(EveBase):
#     race = null_fields.Key('Race', db_column='raceID')
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrraceskills'


# class Character_schoolagents(EveBase):
#     schoolid = null_fields.Int()
#     agentindex = null_fields.Int()
#     agentid = null_fields.Int()
#     class Meta:
#         db_table = u'chrschoolagents'


# class Crpnpccorporationdivisions(EveBase):
#     corporationid = models.IntegerField()
#     divisionid = models.IntegerField()
#     divisionnumber = models.IntegerField()
#     size = null_fields.Int()
#     leaderid = null_fields.Int()
#     class Meta:
#         db_table = u'crpnpccorporationdivisions'


# class Crpnpccorporationresearchfields(EveBase):
#     skillid = models.IntegerField()
#     corporationid = models.IntegerField()
#     suppliertype = models.IntegerField()
#     class Meta:
#         db_table = u'crpnpccorporationresearchfields'

# This table cannot be used within Django, as it's a multi-multi table with ID's
# That Django doesn't like. I've emulated it in class Item below.
# class Dgmtypeeffects(EveBase):
#     typeid = models.IntegerField()
#     effectid = models.IntegerField()
#     isdefault = null_fields.Char(max_length=15)
#     class Meta:
#         db_table = u'dgmtypeeffects'

# class InventoryFlags(EveBase):
#     id = models.IntegerField(primary_key=True, db_column='flagID')
#     flagname = null_fields.Char(max_length=300)
#     flagtext = models.TextField()
#     flagtype = models.TextField()
#     orderid = null_fields.Int()
#     class Meta:
#         db_table = u'invflags'


# class Mapconstellationjumps(EveBase):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapconstellationjumps'


# class Mapjumps(EveBase):
#     stargateid = models.IntegerField()
#     celestialid = models.IntegerField()
#     class Meta:
#         db_table = u'mapjumps'


# class Mapregionjumps(EveBase):
#     fromregionid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapregionjumps'


# Empty table in dump
# class Mapsecurityratings(EveBase):
#     fromsolarsystemid = models.IntegerField()
#     fromvalue = models.FloatField()
#     tosolarsystemid = models.IntegerField()
#     tovalue = models.FloatField()
#     class Meta:
#         db_table = u'mapsecurityratings'


# class Mapsolarsystemjumps(EveBase):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     fromsolarsystemid = models.IntegerField()
#     tosolarsystemid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapsolarsystemjumps'


#class RamAssemblyLines(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='assemblylineID')
#    assemblylinetypeid = models.IntegerField()
#    containerid = null_fields.Int()
#    nextfreetime = null_fields.Char(max_length=60)
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
#    ownerid = null_fields.Int()
#    oldcontainerid = null_fields.Int()
#    oldownerid = null_fields.Int()
#    activityid = null_fields.Int()


#class RamAssemblyLineStationCostLogs(EveBase):
#    stationid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeID')
#    logdatetime = null_fields.Char(max_length=60)
#    _usage = models.FloatField()
#    costperhour = models.FloatField()


# class Ramassemblylinestations(EveBase):
#     stationid = models.IntegerField()
#     assemblylinetypeid = models.IntegerField()
#     quantity = models.IntegerField()
#     stationtypeid = models.IntegerField()
#     ownerid = models.IntegerField()
#     solarsystemid = models.IntegerField()
#     regionid = models.IntegerField()
#     class Meta:
#         db_table = u'ramassemblylinestations'


# class Ramassemblylinetypedetailpercategory(EveBase):
#     assemblylinetypeid = models.IntegerField()
#     categoryid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpercategory'


# class Ramassemblylinetypedetailpergroup(EveBase):
#     assemblylinetypeid = models.IntegerField()
#     groupid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpergroup'


#class RamAssemblylineTypes(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeID')
#    assemblylinetypename = null_fields.Char(max_length=300)
#    description = models.TextField()
#    basetimemultiplier = models.FloatField()
#    basematerialmultiplier = models.FloatField()
#    volume = models.FloatField()
#    activityid = models.IntegerField()
#    mincostperhour = null_fields.Float()


#class RamCompletedStatuses(EveBase):
#    completedstatus = models.IntegerField(primary_key=True)
#    completedstatustext = null_fields.Char(max_length=300)
#    description = models.TextField()


#class RamInstallationTypeDefaultContents(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='installationtypeID')
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


#class StationOperation(EveBase):
#    activityid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='operationID')
#    operationname = null_fields.Char(max_length=300)
#    description = models.TextField()
#    fringe = models.IntegerField()
#    corridor = models.IntegerField()
#    hub = models.IntegerField()
#    border = models.IntegerField()
#    ratio = models.IntegerField()
#    caldaristationtypeid = null_fields.Int()
#    minmatarstationtypeid = null_fields.Int()
#    amarrstationtypeid = null_fields.Int()
#    gallentestationtypeid = null_fields.Int()
#    jovestationtypeid = null_fields.Int()


# class Staoperationservices(EveBase):
#     operationid = models.IntegerField()
#     serviceid = models.IntegerField()
#     class Meta:
#         db_table = u'staoperationservices'


#class StationService(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='serviceID')
#    servicename = null_fields.Char(max_length=300)
#    description = models.TextField()


#class StationType(EveBase):
#    id = models.IntegerField(primary_key=True, db_column='stationtypeID')
#    dockingbaygraphicid = null_fields.Int()
#    hangargraphicid = null_fields.Int()
#    dockentryx = models.FloatField()
#    dockentryy = models.FloatField()
#    dockentryz = models.FloatField()
#    dockorientationx = models.FloatField()
#    dockorientationy = models.FloatField()
#    dockorientationz = models.FloatField()
#    operationid = null_fields.Int()
#    officeslots = null_fields.Int()
#    reprocessingefficiency = null_fields.Float()
#    conquerable = null_fields.Char(max_length=15)
#    class Meta:
