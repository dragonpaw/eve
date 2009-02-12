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
from django.core.cache import cache
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from eve.settings import DEBUG, logging
from eve.lib import eveapi, evelogo
from eve.lib.alliance_graphics import alliance_graphics
from eve.lib.formatting import comma, time, unique_slug
from eve.lib.cachehandler import MyCacheHandler
from eve import settings
from eve.lib.decorators import cachedmethod

import os

evelogo.resourcePath = os.path.join(settings.STATIC_DIR, 'ccp-icons', 'corplogos')

TRUE_FALSE = (
    ('true', 'Yes'),
    ('false', 'No'),
)
API = eveapi.get_api()

class PublishedManager(models.Manager):
    def get_query_set(self):
        return super(PublishedManager, self).get_query_set().filter(published=True)


class Base(models.Model):
    deleteable = False

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

    def delete(self):
        if self.deleteable:
            super(Base, self).delete()
        else:
            raise NotImplementedError('Tried to remove an immutable.')

    class Meta:
        abstract = True
        ordering = ('name',)

class CachedGet(object):
    """A mixin to cause the entire table to be loaded into memory the first time
    that the class is accessed. A restart of the web server will be necessary
    to reload any changed data within the table."""
    def get(self, *args, **kwargs):
        log = logging.getLogger('CachedGet')
        log.info('Caching entire table in memory: %s' % self.__class__.__name__)
        pk_name = self.model._meta.pk.name
        if not hasattr(self, '_cache'):
            self._cache = dict((obj._get_pk_val(), obj) for obj in self.all())
        value = len(kwargs) == 1 and kwargs.keys()[0] in ('pk', pk_name, '%s__exact' % pk_name) and self._cache.get(kwargs.values()[0], False)
        if value:
            return value
        else:
            super(CachedGet, self).get(*args, **kwargs)

class Agent(Base):
    id = models.IntegerField(primary_key=True, db_column='agentid')
    division = models.ForeignKey('CorporationDivision', null=True, blank=True, db_column='divisionid')
    corporation = models.ForeignKey('Corporation', null=True, blank=True, db_column='corporationid')
    station = models.ForeignKey('Station', null=True, blank=True, db_column='stationid')
    level = models.IntegerField(null=True, blank=True)
    quality = models.IntegerField(null=True, blank=True)
    agenttype = models.ForeignKey('AgentType', db_column='agenttypeid')

    _name = None

    class Meta:
        ordering = ('id',)

    @property
    def name(self):
        if not self._name:
            self._name = Name.objects.get(pk=self.id).name
        return self._name


class AgentType(Base):
    id = models.IntegerField(primary_key=True, db_column='agenttypeid')
    agenttype = models.CharField(max_length=150)

    class Meta:
        ordering = ('id',)

    def __unicode__(self):
        return self.agenttype


class Alliance(Base):
    name = models.CharField(max_length=100)
    executor = models.ForeignKey('Corporation', blank=True, null=True, related_name='executors')
    ticker = models.CharField(max_length=10)
    member_count = models.IntegerField()
    slug = models.SlugField(max_length=100)
    objects = models.Manager()

    deleteable = True

    def get_icon(self, size):
        if alliance_graphics.has_key(self.id):
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, alliance_graphics[self.id])
        else:
            return "/static/ccp-icons/alliances/%d_%d/icon%s.png" % (size, size, '01_01')

    def save(self, *args, **kwargs):
        self.slug = unique_slug(self)
        super(Alliance, self).save(*args, **kwargs)

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



class Attribute(CachedGet, Base):
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
    description = models.TextField()
    attributename = models.CharField(max_length=100)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    defaultvalue = models.FloatField()
    published = models.BooleanField()
    displayname = models.CharField(max_length=100, blank=True)
    unit = models.ForeignKey('Unit', null=True, blank=True, db_column='unitid')
    stackable = models.BooleanField()
    highisgood = models.BooleanField()
    category = models.ForeignKey('AttributeCategory', db_column='categoryID')

    class Meta:
        ordering = ['category', 'displayname' ]

    def __unicode__(self):
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
        elif self.attributename.startswith('requiredSkill'):
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

    @cachedmethod(60*4)
    def get_icon(self, size):
        if self.displayname == 'Used with (chargegroup)':
            return Group.objects.get(pk=self.get_value()).get_icon(size)
        elif self.graphic:
            return self.graphic.get_icon(size)
        else:
            return Graphic.objects.get(icon='07_15').get_icon(size)


class AttributeCategory(Base):
    id = models.IntegerField(primary_key=True, db_column='categoryID')
    name = models.CharField(max_length=50, db_column='categoryName')
    description = models.CharField(max_length=200, db_column='categoryDescription')

    class Meta(Base.Meta):
        verbose_name_plural = "Attribute catagories"



class BlueprintDetail(Base):
    # Using the proper foreign key relationship here causes a fatal django error.
    # (Only using the admin interface.)
    id = models.ForeignKey('Item', primary_key=True,
                           db_column='blueprinttypeid',
                           related_name='blueprint_details_qs',
                           limit_choices_to = {'group__category__name__exact': 'Blueprint'})
    parent = models.IntegerField(db_column='parentBlueprintTypeID', null=True)
    makes = models.ForeignKey('Item', db_column='producttypeid',
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

class Category(Base):
    """This table contains the most basic groupings in game:

    Sample:
        Asteroid
        Charge
        Ship"""
    id = models.IntegerField(primary_key=True, db_column='categoryid')
    name = models.CharField(max_length=100, db_column='categoryName')
    description = models.TextField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    published = models.BooleanField(null=True, blank=True, default=False)

    class Meta(Base.Meta):
        verbose_name_plural = "Categories"


class CharacterAncestry(Base):
    id = models.IntegerField(primary_key=True, db_column='ancestryid')
    name = models.CharField(max_length=100, db_column='ancestryname')
    bloodline = models.ForeignKey('CharacterBloodline', db_column='bloodlineid')
    description = models.TextField()
    perception = models.IntegerField()
    willpower = models.IntegerField()
    charisma = models.IntegerField()
    memory = models.IntegerField()
    intelligence = models.IntegerField()
    skill_1 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='ca_s1',
                               db_column='skilltypeid1')
    skill_2 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='ca_s2',
                               db_column='skilltypeid2')
    item_1 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='ca_i1',
                               db_column='typeid')
    item_2 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='ca_i2',
                               db_column='typeid2')
    item_quantity_1 = models.IntegerField(null=True, blank=True, db_column='typequantity')
    item_quantity_2 = models.IntegerField(null=True, blank=True, db_column='typequantity2')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid',)
    shortdescription = models.TextField()

    class Meta(Base.Meta):
        verbose_name_plural = "Character ancestries"

class CharacterAttribute(Base):
    id = models.IntegerField(primary_key=True, db_column='attributeid')
    name = models.CharField(max_length=100, db_column='attributename')
    description = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    shortdescription = models.TextField()
    notes = models.TextField()


class CharacterBloodline(Base):
    id = models.IntegerField(primary_key=True, db_column='bloodlineid')
    name = models.CharField(max_length=100, db_column='bloodlinename')
    race = models.ForeignKey('Race', db_column='raceid')
    description = models.TextField()
    maledescription = models.TextField()
    femaledescription = models.TextField()
    ship = models.ForeignKey('Item', null=True, blank=True,
                               related_name='bloodline_ship',
                               db_column='shiptypeid')
    corporation = models.ForeignKey('Corporation', db_column='corporationid')
    perception = models.IntegerField()
    willpower = models.IntegerField()
    charisma = models.IntegerField()
    memory = models.IntegerField()
    intelligence = models.IntegerField()
    bonus = models.ForeignKey('Item', null=True, blank=True,
                               related_name='bloodline_bonus',
                               db_column='bonustypeid')
    skill_1 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='bloodline_skill1',
                               db_column='skilltypeid1')
    skill_2 = models.ForeignKey('Item', null=True, blank=True,
                               related_name='bloodline_skill2',
                               db_column='skilltypeid2')
    graphic = models.ForeignKey('Graphic', null=True, blank=True,
                                  db_column='graphicid')
    shortdescription = models.TextField()
    shortmaledescription = models.TextField()
    shortfemaledescription = models.TextField()


class CharacterCareer(Base):
    id = models.IntegerField(primary_key=True, db_column='careerid')
    race = models.ForeignKey('Race', db_column='raceid')
    name = models.CharField(max_length=100, db_column='careername')
    description = models.TextField()
    shortdescription = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True,
                                  db_column='graphicid',)
    school = models.ForeignKey('School', null=True, blank=True, related_name='careers',
                               db_column='schoolid')



class CharacterCareerSpeciality(Base):
    id = models.IntegerField(primary_key=True, db_column='specialityid')
    career = models.ForeignKey('CharacterCareer', db_column='careerid')
    name = models.CharField(max_length=100, db_column='specialityname')
    description = models.TextField()
    shortdescription = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True,
                                  db_column='graphicid' )
    departmentid = models.IntegerField(null=True, blank=True)

    class Meta(Base.Meta):
        verbose_name_plural = "Character career specialities"


class Constellation(Base):
    region = models.ForeignKey('Region', db_column='regionid',
                               related_name='constellations')
    id = models.IntegerField(primary_key=True, db_column='constellationid')
    name = models.CharField(max_length=100, db_column='constellationname')
    x = models.FloatField(null=True)
    y = models.FloatField(null=True)
    z = models.FloatField(null=True)
    xmin = models.FloatField(null=True)
    xmax = models.FloatField(null=True)
    ymin = models.FloatField(null=True)
    ymax = models.FloatField(null=True)
    zmin = models.FloatField(null=True)
    zmax = models.FloatField(null=True)
    faction = models.ForeignKey('Faction', null=True, blank=True,
                                db_column='factionid')
    radius = models.FloatField(null=True)
    sov_time = models.DateTimeField(null=True, blank=True,
                                    db_column='sovereigntyDateTime')
    alliance = models.ForeignKey('Alliance', null=True, blank=True,
                                 related_name='constellations')
    grace_date_time = models.DateTimeField(null=True, db_column='graceDateTime')

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


class ContrabandType(Base):
    factionid = models.IntegerField()
    id = models.IntegerField(primary_key=True, db_column='typeid')
    standingloss = models.FloatField()
    confiscateminsec = models.FloatField()
    finebyvalue = models.FloatField()
    attackminsec = models.FloatField()

    class Meta:
        ordering = ('id',)


class Corporation(Base):
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
    #                                db_column='solarsystemid', )
#    investorid1 = models.IntegerField(null=True, blank=True)
#    investorshares1 = models.IntegerField()
#    investorid2 = models.IntegerField(null=True, blank=True)
#    investorshares2 = models.IntegerField()
#    investorid3 = models.IntegerField(null=True, blank=True)
#    investorshares3 = models.IntegerField()
#    investorid4 = models.IntegerField(null=True, blank=True)
#    investorshares4 = models.IntegerField()
#    friend = models.ForeignKey('Name', null=True, blank=True,
#                               db_column='friendid', related_name='friends')
#    enemy = models.ForeignKey('Name', null=True, blank=True,
#                              db_column='enemyid', related_name='enemies')
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
    alliance = models.ForeignKey('Alliance', null=True, related_name='corporations')
    last_updated = models.DateTimeField(blank=True, null=True)
    cached_until = models.DateTimeField(blank=True, null=True)

    _name = None
    deleteable = True

    class Meta:
        ordering = ('id',)

    @property
    def name(self):
        if not self._name:
            self._name = Name.objects.get(pk=self.id).name
        return self._name

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
        return os.path.join(settings.STATIC_DIR, 'corplogos', '32_32', (str(self.id) + '.png'))

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
        self.failed = False

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
            self.failed = True
            return messages

        if name == None:
            messages.append("Unable to refresh corporation '%s', no name available." % self.id)
            self.failed = True
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
        messages.append('Corp refreshed: %s(%s)' % (name.name, self.id))
        self.save()

        self.updatelogo()

        return messages


class CorporationActivity(Base):
    id = models.IntegerField(primary_key=True, db_column='activityid')
    name = models.CharField(max_length=100, db_column='activityname')
    description = models.TextField()

    class Meta(Base.Meta):
        verbose_name_plural = "Corporation activities"


class CorporationDivision(Base):
    id = models.IntegerField(primary_key=True, db_column='divisionid')
    name = models.CharField(max_length=100, db_column='divisionname')
    description = models.TextField()
    leadertype = models.CharField(max_length=100)


class Effect(Base):
    id = models.IntegerField(primary_key=True, db_column='effectid')
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    name = models.TextField(db_column='effectname')
    displayname = models.CharField(max_length=100)
    effectcategory = models.IntegerField(null=True, blank=True)
    preexpression = models.IntegerField(null=True, blank=True)
    postexpression = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    guid = models.CharField(null=True, blank=True, max_length=60)
    isoffensive = models.IntegerField(null=True, blank=True)
    isassistance = models.IntegerField(null=True, blank=True)
    durationattributeid = models.IntegerField(null=True, blank=True)
    trackingspeedattributeid = models.IntegerField(null=True, blank=True)
    dischargeattributeid = models.IntegerField(null=True, blank=True)
    rangeattributeid = models.IntegerField(null=True, blank=True)
    falloffattributeid = models.IntegerField(null=True, blank=True)
    disallowautorepeat = models.IntegerField(null=True, blank=True)
    published = models.BooleanField(null=True, blank=True)
    iswarpsafe = models.IntegerField(null=True, blank=True)
    rangechance = models.IntegerField(null=True, blank=True)
    electronicchance = models.IntegerField(null=True, blank=True)
    propulsionchance = models.IntegerField(null=True, blank=True)
    distribution = models.IntegerField(null=True, blank=True)
    sfxname = models.CharField(blank=True, max_length=20)
    npcusagechanceattributeid = models.IntegerField(null=True, blank=True)
    npcactivationchanceattributeid = models.IntegerField(null=True, blank=True)
    fittingusagechanceattributeid = models.IntegerField(null=True, blank=True)



class Faction(CachedGet, Base):
    """Table describes the major factions in game:

    Amaar Empire
    CONCORD Assembly
    ...
    Thukker Tribe"""
    id = models.IntegerField(primary_key=True, db_column='factionid')
    name = models.CharField(max_length=100, db_column='factionname')
    description = models.TextField(null=True)
    raceids = models.IntegerField(null=True, blank=True)
    solarsystem = models.ForeignKey('SolarSystem', null=True, blank=True,
                                    db_column='solarsystemid', related_name='home_system')
    corporation = models.ForeignKey('Corporation', null=True, blank=True,
                                    db_column='corporationid', related_name='corporations')
    sizefactor = models.FloatField(null=True, blank=True)
    stationcount = models.IntegerField(null=True, blank=True)
    stationsystemcount = models.IntegerField(null=True, blank=True)

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



class Group(Base):
    """This table describes goups like: Ammo and Advanced Torpedo.

    It also contains non-item groups like 'Alliance' and
    'Asteroid Angel Cartel Officer'."""
    id = models.IntegerField(primary_key=True, db_column='groupid')
    category = models.ForeignKey('Category', db_column='categoryid', related_name='groups')
    name = models.CharField(max_length=100, db_column='groupname')
    description = models.TextField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    usebaseprice = models.IntegerField(max_length=15, choices=TRUE_FALSE)
    allowmanufacture = models.BooleanField("Manafacturable?", choices=TRUE_FALSE)
    allowrecycler = models.BooleanField(null=True, blank=True)
    anchored = models.BooleanField(null=True, blank=True)
    anchorable = models.BooleanField(null=True, blank=True)
    fittablenonsingleton = models.BooleanField(null=True, blank=True)
    published = models.BooleanField(default=True, null=True)
    slug = models.SlugField()

    @cachedmethod(60*24)
    def get_icon(self, size):
        return self.graphic.get_icon(size)

    def get_absolute_url(self):
        if self.category.name == 'Entity':
            # I am an NPC.
            return u'/npc/%s' % self.slug
        else:
            return 'x'


class Graphic(CachedGet, Base):
    id = models.IntegerField(primary_key=True, db_column='graphicid')
    url3d = models.CharField(max_length=100, null=True, blank=True)
    urlweb = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True, default='Automatically added by Django')
    published = models.BooleanField(default=False, null=True)
    obsolete = models.BooleanField(default=False, null=True)
    icon = models.CharField(max_length=100)
    urlsound = models.CharField(max_length=100, null=True, blank=True)
    explosionid = models.IntegerField(null=True, blank=True)

    color = 'white'
    dir = '/static/ccp-icons'

    class Meta:
        ordering = ('id',)

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

    def save(self, *args, **kwargs):
        """Custom save handler to set a good and safe id on new objects."""
        if self.id is None:
            min_id = 10000 # We enter new id's on demand, but not below this value.
            max_id = Graphic.objects.all().order_by('-id')[0].id
            max_id = max(max_id, min_id)
            self.id=max_id+1

        super(Graphic, self).save(*args, **kwargs)

def get_graphic(icon):
    """Helper utility that will find one icon or make it for you. Used in make_nav and elsewhere.
    Useful because icons are often non-unique, but I don't care in my app."""
    if isinstance(icon, type('')):
        g = Graphic.objects.filter(icon=icon)
        if g.count() == 0:
            graphic = Graphic.objects.create(icon=icon)
        else:
            graphic = g[0]
        return graphic
    else:
        return icon


class InventoryMetaGroup(Base):
    id = models.IntegerField(primary_key=True, db_column='metagroupid')
    name = models.CharField(blank=True, max_length=100, db_column='metagroupname')
    description = models.TextField(blank=True, null=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')


class InventoryMetaType(Base):
    item = models.ForeignKey('Item', null=True, blank=True,
                           db_column='typeid',
                           related_name='metatype')
    parent = models.ForeignKey('Item', null=True, blank=True,
                               db_column='parenttypeid',
                               related_name='metatype_children')
    metagroup = models.ForeignKey('InventoryMetaGroup', null=True, blank=True,
                                    db_column='metagroupid')

    class Meta:
        ordering = ('item',)


class ItemSkillManager(models.Manager):
    def get_query_set(self):
        return super(ItemSkillManager, self).get_query_set().filter(
            group__category__name__exact = 'Skill',
            published = True,
        )

class Item(Base):
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
    name = models.CharField(max_length=100)
    real_description = models.TextField(db_column='description')
    graphic = models.ForeignKey('Graphic', null=True, blank=True,
                                db_column='graphicid')
    radius = models.FloatField()
    mass = models.FloatField()
    volume = models.FloatField()
    capacity = models.FloatField()
    portionsize = models.IntegerField()
    race = models.ForeignKey('Race', null=True, blank=True, db_column='raceid')
    baseprice = models.FloatField()
    published = models.BooleanField()
    marketgroup = models.ForeignKey('MarketGroup', null=True, blank=True,
                                    db_column='marketgroupid')
    chanceofduplicating = models.FloatField()
    slug = models.SlugField(max_length=100)
    objects = models.Manager()

    object_cache = {}

    #def __init__(self, *args, **kwargs):
    #    super(Item, self).__init__(*args, **kwargs)
    #    self.icon_cache = {}

    #class Meta:
        #pass
        # If I use 'name' instead of 'typename', then the BlueprintDetails model dies
        # in the admin list view. Like this, the list works, but not the detail.
        #ordering = ['name', ]

    @property
    @cachedmethod(60*6, '%(id)d')
    def category(self):
        return self.group.category.name

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

    #@cachedmethod(60*6)
    def get_icon(self, size):
        from django.core.cache import cache
        key = 'eve.ccp.models.Item.get_icon(%d,%d)' % (self.id, size)
        value = cache.get(key)
        if value:
            return value

        #if size in self.icon_cache:
        #    return self.icon_cache[size]

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
        cat = self.category
        if cat in cats:
            d = {
                'cat':     cat.lower(),
                'dir':     Graphic.dir,
                'size':    size,
                'color':   Graphic.color,
                'item_id': self.id,
            }
            icon = "%(dir)s/%(cat)s/%(size)d_%(size)d/%(item_id)d.png" % d
        else:
            icon = self.graphic.get_icon(size)

        cache.set(key, icon, 60*60*6)
        return icon


    # Fancy way to get the attributes and their values.
    @cachedmethod(60, '%(id)d')
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
        ).select_related()
        for s in set:
            try:
                if s.attributename == 'requiredSkill1':
                    s.graphic = get_graphic('50_13')
                    s.valuefloat = set.filter(attributename='requiredSkill1Level')[0].valueint
                if s.attributename == 'requiredSkill2':
                    s.graphic = get_graphic('50_11')
                    s.valuefloat = set.filter(attributename='requiredSkill2Level')[0].valueint
                if s.attributename == 'requiredSkill3':
                    s.graphic = get_graphic('50_14')
                    s.valuefloat = set.filter(attributename='requiredSkill3Level')[0].valueint
            except IndexError:
                s.valuefloat = 1

        # Limit to the published attributes.
        # (If done in Attribute, then we don't get the skill levels above.)
        #set = [x for x in set if x.published]
        return set

    @cachedmethod(60, '%(id)d')
    def attributes_by_name(self):
        return dict([(a.attributename, a) for a in self.attributes()])

    def attribute_by_name(self, name):
        d = self.attributes_by_name()
        if name in d:
            return d[name]
        else:
            return None
        #set = Attribute.objects.extra(
        #    select={
        #        'valueint':'ccp_typeattribute.valueint',
        #        'valuefloat':'ccp_typeattribute.valuefloat',
        #    },
        #    tables=['ccp_typeattribute'],
        #    where=[
        #        'ccp_typeattribute.attributeid = ccp_attribute.attributeid',
        #        'ccp_typeattribute.typeid = %s',
        #        'ccp_attribute.attributeName = %s',
        #    ],
        #    params=[self.id, name]
        #)
        #if set.count() > 0:
        #    return set[0]
        #else:
        #    return None

    @cachedmethod(60, '%(id)d')
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

            type = Item.objects.get(id=d['entityMissileTypeID'].value)
            attributes = type.attributes_by_name()
            if 'emDamage' in attributes:
                dps['missile_em'] = attributes['emDamage'].value * mult / rate
            if 'explosiveDamage' in attributes:
                dps['missile_explosive'] = attributes['explosiveDamage'].value * mult / rate
            if 'kineticDamage' in attributes:
                dps['missile_kinetic'] = attributes['kineticDamage'].value * mult / rate
            if 'thermalDamage' in attributes:
                dps['missile_thermal'] = attributes['thermalDamage'].value * mult / rate

        for type in ('em', 'explosive', 'kinetic', 'thermal'):
            if type in dps:
                total = dps[type]
            else:
                total = 0
            if 'missile_' + type in dps:
                total = total + dps['missile_'+type]
            dps['total_' + type] = total

        return dps

    @cachedmethod(60, '%(id)d')
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
        #assert(item.blueprint_details_qs.count() == 1)
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
        if hasattr(self, '_blueprint'):
            return self._blueprint
        elif self.is_blueprint:
            blueprint = self
        elif self.blueprint_madeby_qs.count() > 0:
            #assert(self.blueprint_madeby_qs.count() == 1)
            blueprint = self.blueprint_madeby_qs.all()[0].id
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


class MapDenormalize(Base):
    id = models.IntegerField(primary_key=True, db_column='itemid')
    type = models.ForeignKey('Item', db_column='typeid')
    group = models.ForeignKey('Group', db_column='groupid')
    solarsystem = models.ForeignKey('SolarSystem', db_column='solarsystemid', null=True, blank=True,
                                    related_name='map')
    constellation = models.ForeignKey('Constellation', db_column='constellationid', null=True, blank=True,
                                      related_name='map')
    region = models.ForeignKey('Region', db_column='regionid', null=True, blank=True,
                               related_name='map')
    orbits = models.ForeignKey('MapDenormalize', db_column='orbitid', null=True, blank=True)
    x = models.FloatField(null=True, blank=True)
    y = models.FloatField(null=True, blank=True)
    z = models.FloatField(null=True, blank=True)
    radius = models.FloatField(null=True, blank=True)
    name = models.CharField(blank=True, max_length=100, db_column='itemname')
    security = models.FloatField(null=True, blank=True)
    celestialindex = models.IntegerField(null=True, blank=True)
    orbitindex = models.IntegerField(null=True, blank=True)


class MapLandmark(Base):
    id = models.IntegerField(primary_key=True, db_column='landmarkid')
    name = models.TextField(null=True, blank=True, db_column='landmarkname')
    description = models.TextField()
    locationid = models.IntegerField(null=True, blank=True)
    x = models.FloatField()
    y = models.FloatField()
    z = models.FloatField()
    radius = models.FloatField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    importance = models.IntegerField()
    url2d = models.TextField()

    class Meta(Base.Meta):
        db_table = u'ccp_maplandmarks'


class MapUniverse(Base):
    id = models.IntegerField(primary_key=True, db_column='universeid')
    name = models.CharField(max_length=100, db_column='universename')
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


class MarketGroup(Base):
    '''This is the list of the groups as seen in the market type browser.
    (Which is more detailed than the normal group table.)

    Items here have a self-referential parent, which is used to create heirarchy
    within this table.'''

    id = models.IntegerField(primary_key=True, db_column='marketgroupid')
    parent = models.ForeignKey('MarketGroup', null=True, blank=True, db_column='parentgroupid')
    name = models.CharField(max_length=100, db_column='marketgroupname')
    description = models.TextField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    hastypes = models.BooleanField(null=True, blank=True)
    slug = models.SlugField(max_length=100)

    def get_absolute_url(self):
        return "/items/%s/" % self.slug

    def get_icon(self, size):
        from django.core.cache import cache
        key = 'eve.ccp.models.MarketGroup.get_icon(%d,%d)' % (self.id, size)
        value = cache.get(key)
        if value:
            return value

        value = self.graphic.get_icon(size)
        cache.set(key, value)
        return value


class MaterialPublishedManager(models.Manager):
    def get_query_set(self):
        return super(MaterialPublishedManager, self).get_query_set().select_related().filter(item__published=True,
                                                                                             activity__published=True)

class Material(Base):
    """
    All the 'stuff' to make other 'stuff'.
    """
    item = models.ForeignKey('Item', db_column='typeid')
    activity = models.ForeignKey('RamActivity', db_column='activityID')
    material = models.ForeignKey('Item',
                                 db_column='requiredtypeid',
                                 related_name='helps_make' )
    quantity = models.IntegerField()
    damageperjob = models.FloatField(default=1)
    id = models.IntegerField(primary_key=True)
    objects = MaterialPublishedManager()

    class Meta:
        ordering = ('id',)

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


class Name(Base):
    """This table contains the names of planets, stars, systems and corporations."""
    id = models.IntegerField(primary_key=True, db_column='itemid')
    name = models.CharField(max_length=100, db_column='itemname')
    category = models.ForeignKey('Category', db_column='categoryid', related_name='names')
    group = models.ForeignKey('Group', db_column='groupid', related_name='names')
    type = models.ForeignKey('Item', db_column='typeid', related_name='names',)


class Race(Base):
    """Table contains the basic races in the game:

    Amaar
    Gallente
    Jove"""
    id = models.IntegerField(primary_key=True, db_column='raceid')
    name = models.CharField(max_length=100, db_column='racename')
    description = models.TextField()
    skilltypeid1 = models.IntegerField(null=True, blank=True)
    typeid = models.IntegerField(null=True, blank=True)
    typequantity = models.IntegerField(null=True, blank=True)
    graphic = models.ForeignKey('Graphic', null=True, blank=True, db_column='graphicid')
    shortdescription = models.TextField()


class Reaction(Base):
    reaction = models.ForeignKey('Item', db_column='reactiontypeid', related_name='reactions')
    input = models.BooleanField()
    item = models.ForeignKey('Item', db_column='typeid', related_name='reacts')
    quantity = models.IntegerField()

    def __unicode__(self):
        arrow = '=>'
        if self.input == 1:
            arrow = '<-'
        return "%s %s %s[%d]" % (self.reaction, arrow, self.item, self.quantity)

    class Meta:
        ordering = ('reaction',)



class RamActivity(Base):
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
    id = models.IntegerField(primary_key=True, db_column='activityid')
    name = models.CharField(max_length=100, db_column='activityname')
    description = models.TextField(default="")
    iconNo = models.CharField(max_length=5, blank=True, null=True, default="")
    published = models.BooleanField(default=False)


class Region(Base):
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
    faction = models.ForeignKey('Faction', null=True, blank=True, db_column='factionid')
    radius = models.FloatField(null=True)
    slug = models.SlugField(max_length=50)

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
            return owner.get_icon(size)


class School(Base):
    id = models.IntegerField(primary_key=True, db_column='schoolid')
    race = models.ForeignKey('Race', null=True, blank=True, db_column='raceid')
    name = models.CharField(max_length=100, db_column='schoolname')
    description = models.TextField()
    graphic = models.ForeignKey('Graphic', null=True, blank=True,
                                db_column='graphicid',)
    corporation = models.ForeignKey('Corporation', null=True, blank=True,
                                    db_column='corporationid',)
    agent = models.ForeignKey('Agent', null=True, blank=True,
                              db_column='agentid',)
    newagent = models.ForeignKey('Agent', null=True, blank=True,
                                 db_column='newagentid',
                                 related_name='charactershool_new_set', )
    career = models.ForeignKey('CharacterCareer', null=True, blank=True, related_name='schools',
                                db_column='careerid')


class SolarSystem(Base):
    region = models.ForeignKey('Region', db_column='regionid', related_name='solarsystems')
    constellation = models.ForeignKey('Constellation', db_column='constellationid',
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
    faction = models.ForeignKey('Faction', null=True, blank=True,
                                db_column='factionid',
                                related_name='solarsystems')
    radius = models.FloatField(default=0.0)
    suntypeid = models.IntegerField(null=True, blank=True)
    securityclass = models.CharField(blank=True, max_length=2, null=True)
    alliance = models.ForeignKey('Alliance', null=True, blank=True, related_name='solarsystems')
    sov = models.IntegerField(null=True, blank=True, db_column='sovereigntyLevel')
    sov_time = models.DateTimeField(null=True, blank=True, db_column='sovereigntyDate')
    alliance_old = models.ForeignKey('Alliance', null=True, blank=True, related_name='solarsystems_lost')


    def moons(self):
        return self.map.filter(type__name='Moon')

    def belts(self):
        return self.map.filter(type__name='Asteroid Belt')

    def get_absolute_url(self):
        return "/solarsystem/%s/" % self.name

    def get_icon(self, size):
        return self.alliance.get_icon(size)


class Station(Base):
    id = models.IntegerField(primary_key=True, db_column='stationid')
    security = models.IntegerField(null=True)
    dockingcostpervolume = models.FloatField('Docking', default=0)
    maxshipvolumedockable = models.FloatField('Max Dockable', default=0)
    officerentalcost = models.IntegerField('Office Rental', default=0)
    operationid = models.IntegerField(null=True, default=0)
    type = models.ForeignKey('Item', null=True, blank=True,
                             db_column='stationtypeid', related_name='staitons')
    corporation = models.ForeignKey('Corporation', null=True, blank=True, db_column='corporationid')
    solarsystem = models.ForeignKey('SolarSystem', null=True, blank=True, db_column='solarsystemid',
                                    related_name='stations')
    constellation = models.ForeignKey('Constellation', null=True, blank=True, db_column='constellationid',
                                       related_name='stations')
    region = models.ForeignKey('Region', null=True, blank=True, db_column='regionid', related_name='stations')
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

    def get_icon(self, size):
        return self.corporation.get_icon(size)
        #icon = self.corporation.get_icon(size)
        #if icon:
        #    return icon
        #else:
        #    return self.type.get_icon(size)



class StationResource(Base):
    q = Q(group__name='Control Tower') & Q(published=True)

    tower = models.ForeignKey('Item', limit_choices_to = q, db_column = 'controlTowerTypeID', related_name='fuel')
    type = models.ForeignKey('Item', db_column='resourcetypeid', related_name='fuel_for')
    purpose = models.ForeignKey('StationResourcePurpose', db_column='purpose')
    quantity = models.IntegerField()
    minsecuritylevel = models.FloatField(null=True, blank=True)
    faction = models.ForeignKey('Faction', null=True, blank=True, db_column='factionID')

    def __unicode__(self):
        return "%s (%d)" % (self.type, self.quantity)

    class Meta:
        ordering = ('tower', 'purpose', 'type')

class StationResourcePurpose(Base):
    id = models.IntegerField(primary_key=True, db_column='purpose')
    name = models.CharField(max_length=100, db_column='purposetext')

class Unit(CachedGet, Base):
    id = models.IntegerField(primary_key=True, db_column='unitid')
    name = models.CharField(null=True, blank=True, max_length=100, db_column='unitname')
    displayname = models.CharField(null=True, blank=True, max_length=20)
    description = models.TextField(null=True, blank=True)

#class MapcClestialStatistics(Base):
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


# class Agent_config(Base):
#     id = models.IntegerField(primary_key=True, db_column='agentid')
#     k = models.CharField(max_length=150)
#     v = models.TextField()
#     class Meta:
#         db_table = u'agtconfig'


# class Character_careerskills(Base):
#     careerid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerskills'


# class Character_careerspecialityskills(Base):
#     specialityid = models.IntegerField()
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrcareerspecialityskills'


# class Character_raceskills(Base):
#     race = models.ForeignKey('Race', null=True, blank=True, db_column='raceid')
#     skilltypeid = models.IntegerField()
#     levels = models.IntegerField()
#     class Meta:
#         db_table = u'chrraceskills'


# class Character_schoolagents(Base):
#     schoolid = models.IntegerField(null=True, blank=True)
#     agentindex = models.IntegerField(null=True, blank=True)
#     agentid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'chrschoolagents'


# class Crpnpccorporationdivisions(Base):
#     corporationid = models.IntegerField()
#     divisionid = models.IntegerField()
#     divisionnumber = models.IntegerField()
#     size = models.IntegerField(null=True, blank=True)
#     leaderid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'crpnpccorporationdivisions'


# class Crpnpccorporationresearchfields(Base):
#     skillid = models.IntegerField()
#     corporationid = models.IntegerField()
#     suppliertype = models.IntegerField()
#     class Meta:
#         db_table = u'crpnpccorporationresearchfields'


# This table cannot be used within Django, as it's a multi-multi table with id's
# That Django doesn't like. I've emulated it in class Item below.
# class Dgmtypeattributes(Base):
#     typeid = models.IntegerField()
#     attributeid = models.IntegerField()
#     valueint = models.IntegerField(null=True, blank=True)
#     valuefloat = models.FloatField(null=True, blank=True)
#     class Meta:
#         db_table = u'dgmtypeattributes'


# This table cannot be used within Django, as it's a multi-multi table with id's
# That Django doesn't like. I've emulated it in class Item below.
# class Dgmtypeeffects(Base):
#     typeid = models.IntegerField()
#     effectid = models.IntegerField()
#     isdefault = models.CharField(max_length=15)
#     class Meta:
#         db_table = u'dgmtypeeffects'

# class InventoryFlags(Base):
#     id = models.IntegerField(primary_key=True, db_column='flagid')
#     flagname = models.CharField(blank=True, max_length=300)
#     flagtext = models.TextField(blank=True)
#     flagtype = models.TextField(blank=True)
#     orderid = models.IntegerField(null=True, blank=True)
#     class Meta:
#         db_table = u'invflags'


# class Mapconstellationjumps(Base):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapconstellationjumps'


# class Mapjumps(Base):
#     stargateid = models.IntegerField()
#     celestialid = models.IntegerField()
#     class Meta:
#         db_table = u'mapjumps'


# class Mapregionjumps(Base):
#     fromregionid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapregionjumps'


# Empty table in dump
# class Mapsecurityratings(Base):
#     fromsolarsystemid = models.IntegerField()
#     fromvalue = models.FloatField()
#     tosolarsystemid = models.IntegerField()
#     tovalue = models.FloatField()
#     class Meta:
#         db_table = u'mapsecurityratings'


# class Mapsolarsystemjumps(Base):
#     fromregionid = models.IntegerField()
#     fromconstellationid = models.IntegerField()
#     fromsolarsystemid = models.IntegerField()
#     tosolarsystemid = models.IntegerField()
#     toconstellationid = models.IntegerField()
#     toregionid = models.IntegerField()
#     class Meta:
#         db_table = u'mapsolarsystemjumps'


#class RamAssemblyLines(Base):
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


#class RamAssemblyLineStationCostLogs(Base):
#    stationid = models.IntegerField()
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeid')
#    logdatetime = models.CharField(max_length=60)
#    _usage = models.FloatField()
#    costperhour = models.FloatField()


# class Ramassemblylinestations(Base):
#     stationid = models.IntegerField()
#     assemblylinetypeid = models.IntegerField()
#     quantity = models.IntegerField()
#     stationtypeid = models.IntegerField()
#     ownerid = models.IntegerField()
#     solarsystemid = models.IntegerField()
#     regionid = models.IntegerField()
#     class Meta:
#         db_table = u'ramassemblylinestations'


# class Ramassemblylinetypedetailpercategory(Base):
#     assemblylinetypeid = models.IntegerField()
#     categoryid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpercategory'


# class Ramassemblylinetypedetailpergroup(Base):
#     assemblylinetypeid = models.IntegerField()
#     groupid = models.IntegerField()
#     timemultiplier = models.FloatField()
#     materialmultiplier = models.FloatField()
#     class Meta:
#         db_table = u'ramassemblylinetypedetailpergroup'


#class RamAssemblylineTypes(Base):
#    id = models.IntegerField(primary_key=True, db_column='assemblylinetypeid')
#    assemblylinetypename = models.CharField(max_length=300)
#    description = models.TextField()
#    basetimemultiplier = models.FloatField()
#    basematerialmultiplier = models.FloatField()
#    volume = models.FloatField()
#    activityid = models.IntegerField()
#    mincostperhour = models.FloatField(null=True, blank=True)


#class RamCompletedStatuses(Base):
#    completedstatus = models.IntegerField(primary_key=True)
#    completedstatustext = models.CharField(max_length=300)
#    description = models.TextField()


#class RamInstallationTypeDefaultContents(Base):
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


#class StationOperation(Base):
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


# class Staoperationservices(Base):
#     operationid = models.IntegerField()
#     serviceid = models.IntegerField()
#     class Meta:
#         db_table = u'staoperationservices'


#class StationService(Base):
#    id = models.IntegerField(primary_key=True, db_column='serviceid')
#    servicename = models.CharField(max_length=300)
#    description = models.TextField()


#class StationType(Base):
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
