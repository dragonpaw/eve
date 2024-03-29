# Create your views here.
#from django.http import HttpResponseRedirect
from datetime import datetime, timedelta
from decimal import Decimal
from collections import defaultdict
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.db.models import Q, Count
from django.views.decorators.cache import cache_page

from eve.ccp.models import SolarSystem, Constellation, Region, MarketGroup, Item, Attribute, Category, Group, get_graphic, Graphic, AttributeCategory, ItemAttribute
from eve.lib.formatting import NavigationElement
from eve.lib.jinja import render_to_response
from eve.pos.models import PlayerStation
from eve.settings import logging
from eve.trade.models import BlueprintOwned, get_buy_price, get_sell_price

item_nav = NavigationElement(
    "Items", "/items/", '24_05', note='All items in the game.'
)
region_nav = NavigationElement(
    "Regions", "/regions/", '17_03', note='The universe, and everything in it.'
)
sov_nav = NavigationElement(
    'Sovereignty Changes', '/sov/changes/', '70_11',
    note='Who lost and gained systems.'
)
npc_nav = NavigationElement(
    'NPCs', '/npc/', '07_07',
    note='All the things to blow up, or be blown up by.'
)

uses_nav = NavigationElement(
    'Uses', None, None
)

NPC_ICONS = {
    'shield': get_graphic('02_01'),
    'armor': get_graphic('01_10'),
    'dps_em': get_graphic('22_12'),
    'dps_ex': get_graphic('22_11'),
    'dps_ki': get_graphic('22_09'),
    'dps_th': get_graphic('22_10'),
    'tank_em': get_graphic('22_20'),
    'tank_ex': get_graphic('22_19'),
    'tank_ki': get_graphic('22_17'),
    'tank_th': get_graphic('22_18'),
    'ewar_scramble': get_graphic('04_09'),
    'ewar_web': get_graphic('12_06'),
    'ewar_tracking': get_graphic('05_07'),
    'ewar_jam': get_graphic('04_12'),
    'ewar_damp': get_graphic('04_11'),
    'ewar_neut': get_graphic('01_03'),
    'ewar_paint': get_graphic('56_01'),
}

VOLUME = Attribute.objects.get(attributename='volume')
CAPACITY = Attribute.objects.get(attributename='capacity')
try:
    PORTIONSIZE = Attribute.objects.get(attributename='portionSize')
except:
    PORTIONSIZE = Attribute(
        id = 5000,
        description = 'Portion Size (Automatically added by Widget)',
        attributename = 'portionSize',
        defaultvalue = 1.0,
        published = True,
        category = AttributeCategory.objects.get(name='Structure'),
        displayname = 'Portion Size',
        graphic = get_graphic('07_16'),
    ).save()

USES_FILTER  = ~Q(activity__name__contains='Not in game')
USES_FILTER &=  Q(quantity__gt=0)
USES_FILTER &= ~Q(activity__name='Refining')

def generate_navigation(object):
    """Build up a heiracy of objects"""
    # IS it an NPC?
    if isinstance(object, Item) and object.group.category.name == 'Entity':
        nav = (npc_nav, object.group, object)
    else:
        nav = [object]
        current = object
        while current.parent is not None:
            nav.append(current.parent)
            current = current.parent
        nav.append( item_nav )
        nav.reverse()
    return nav

def solarsystem(request, name):
    item = get_object_or_404(SolarSystem, name=name)

    if request.user.is_authenticated():
        log = logging.getLogger('eve.ccp.views.solarsystem')
        profile = request.user.get_profile()
        log.debug('Adding POSes for user: %s' % profile)
        query = profile.characters.filter(corporation__alliance__isnull=False)
        ids = set([x.corporation.alliance_id for x in query])
        log.debug('Allowed to see alliances with ID of: %s' % str(ids))
        poses = PlayerStation.objects.filter(corporation__alliance__in=ids,
                                             solarsystem=item)
        poses = dict([(pos.moon, pos) for pos in poses])
        log.debug('Total number of POS vieable: %d' % len(poses))
    else:
        poses = dict()

    return render_to_response('solarsystem.html', {
        'poses': poses,
        'item' : item,
        'nav'  : (region_nav, item.region, item.constellation, item),
    }, request)

@cache_page(60 * 60 * 2)
def constellation(request, name):
    item = get_object_or_404(Constellation, name=name)

    return render_to_response('constellation.html', {
        'nav': (region_nav, item.region, item),
        'item': item,
        'title': 'test',
    }, request)

@cache_page(60 * 60 * 2)
def region(request, slug):
    item = get_object_or_404(Region, slug=slug)

    return render_to_response('region.html', {
        'item': item,
        'nav': (region_nav, item),
    }, request)

#@cache_page(60 * 60 * 2)
def region_list(request):
    q = ( Q(faction__isnull=True) | ~Q(faction__name='Jove Empire') ) & ~Q(slug__startswith='unknown')
    regions = Region.objects.select_related('constellation').filter(q)

    return render_to_response('regions.html', {
        'nav': ( {'name':"Regions",'get_absolute_url':"/regions/"}, ),
        'inline_nav': regions,
    }, request)

@cache_page(60 * 60 * 2)
def group_index(request):
    root_objects = MarketGroup.objects.filter(parent__isnull=True)
    #output = ', '.join([m.name for m in root_objects])
    d = {}
    d['nav'] = [ item_nav ]
    d['objects'] = [{'item':x} for x in root_objects]

    return render_to_response('item_list.html', d,
                              request)

# Cannot cache as it depends on user prices.
def group(request, slug):
    group = get_object_or_404(MarketGroup, slug=slug)
    profile = None
    if request.user.is_anonymous() == False:
        profile = request.user.get_profile()

    d = {}

    d['nav'] = generate_navigation(group)
    d['title'] = "Market Group: %s" % group.name

    groups = [ {'item': x } for x in MarketGroup.objects.filter(parent=group)]
    items  = [{'item':x,
               'buy':get_buy_price(profile, x),
               'sell':get_sell_price(profile, x)} for x in group.item_set.all()]
    d['objects'] = groups + items

    d['objects'].sort(key=lambda x:x['item'].name)
    return render_to_response('item_list.html', d,
                              request)

# Cannot cache as it depends on user prices.
def item(request, slug, days=30):
    log = logging.getLogger('eve.ccp.views.item')
    item = get_object_or_404(Item, slug=slug)
    d = dict()
    d['time_span'] = '%d days' % days
    d['item'] = item

    d['title']     = "Item: %s" % item.name
    d['nav']       = generate_navigation(item)

    profile = None
    if request.user.is_authenticated():
        profile = request.user.get_profile()
        values, best_values = profile.trade_history(item=item, days=days)

        d['values'] = values
        d['best_values'] = best_values

    max_pe = None
    if request.user.is_authenticated():
        max_pe = profile.max_skill_level('Production Efficiency')

    my_blueprint = None
    if profile:
        try:
            my_blueprint = BlueprintOwned.objects.get(
                blueprint=item.blueprint, user=profile
            )
        except BlueprintOwned.DoesNotExist:
            pass

    mats = {
        'titles':{},
        'materials': defaultdict(dict),
        'isk': {}
    }

    #-------------------------------------------------------------------------
    # Can it be manufactured?
    for mat in item.materials():
        name = mat.activity.name
        mats['titles'][name] = name
        # If we own the blueprint, show our manufacture quantity instead.
        if my_blueprint and name == 'Manufacturing':
            pass
        else:
            mats['materials'][mat.material][name] = mat.quantity

    #-------------------------------------------------------------------------
    # If we own this blueprint...
    if my_blueprint:
        # Add in the blueprint itself as a material.
        mats['materials'][my_blueprint.blueprint] = {
            'Personal': 1,
            'material':my_blueprint.blueprint,
            'buy_price':my_blueprint.cost_per_run,
            'input':'Blueprint run cost',
        }
        mats['titles']['Personal'] = "Your Blueprint: PE%s/ME%d" % (max_pe, my_blueprint.me)
        for mat in my_blueprint.blueprint.materials(activity='Manufacturing'):
            mats['materials'][mat.material]['Personal'] = my_blueprint.mineral(
                mat.quantity, max_pe
            )

    #-------------------------------------------------------------------------
    # We don't want isk prices on where things refine -from-
    if item.group.name in ('Mineral','Ice Product'):
        mats['titles']['Refined From'] = 'Refined From'
        for mat in item.helps_make.filter(activity=50):
            mats['materials'][mat.item] = {
                'material' : mat.item,
                'Refined From' : mat.quantity_per_unit(),
            }

    #-------------------------------------------------------------------------
    # This triggers on materials that CAN react.
    if item.reacts.count():
        for mat in item.reacts.all():
            if mat.input:
                mats['titles']['Reaction-in'] = 'Reactions Needing'
                for r in mat.reaction.reactions.filter(input=False):
                    mats['materials'][r.item] = {
                        'material': r.item,
                        'input':'Needed',
                        'Reaction-in': mat.quantity,
                    }
            else:
                mats['titles']['Reaction-out'] = 'Materials to React'
                for r in mat.reaction.reactions.filter(input=True):
                    mats['materials'][r.item] = {
                        'material': r.item,
                        'input':'Used',
                        'Reaction-out': r.quantity,
                    }

    #-------------------------------------------------------------------------
    # This triggers on reaction blueprints
    if item.reactions.count():
        mats['titles']['Reaction'] = 'POS Reaction'
        for mat in item.reactions.select_related('item__group__category'):
            buy_price = sell_price = 0
            if mat.input == True:
                input = "Input"
            else:
                input = "Output"
                sell_price = get_sell_price(profile, mat.item)
            mats['materials'][mat.item] = {
                'material' : mat.item,
                'input': input,
                'sell_price': sell_price,
                'Reaction' : mat.quantity
            }

    #-------------------------------------------------------------------------
    # Lookup prices for all materials.
    log.debug('Materials: %s', mats)
    for m, v in mats['materials'].items():
        if m.is_skill:
            v['buy_price'] = Decimal(0)
        else:
            # Don't overwrite a value.
            if 'buy_price' not in v:
                v['buy_price'] = get_buy_price(m, profile)
        log.debug('Value for %s: %s', m, v['buy_price'])

    #-------------------------------------------------------------------------
    # Calculate total prices for all actions.
    for activity in mats['titles']:
        cost = Decimal(0)
        for m in mats['materials']:
            v = mats['materials'][m]
            v['material'] = m # Used by the template later.
            if activity in v and v['buy_price'] and activity != 'Refined From':
                assert isinstance(v['buy_price'], Decimal), \
                    "Buy price is: %s" % type(v['buy_price'])
                assert isinstance(v[activity], (Decimal, int, long)), \
                    "Activity is: %s" % type(v[activity])
                cost += (v['buy_price'] * v[activity])
        if item.is_blueprint:
            portion = item.blueprint_makes.portionsize
        else:
            portion = item.portionsize
        cost = cost / portion
        mats['isk'][activity] = cost

    #-------------------------------------------------------------------------
    if ('Personal' in mats['isk'] and 'sell' in best_values
        and best_values['sell'] and best_values['sell']['sell_price'] > 0
        and mats['isk']['Personal'] > 0):
        best_values['manufacturing_profit_isk'] =  (
            best_values['sell']['sell_price'] - mats['isk']['Personal']
        )
        best_values['manufacturing_profit_pct'] = (
            best_values['manufacturing_profit_isk'] / mats['isk']['Personal']
        ) * 100

    #-------------------------------------------------------------------------
    # Display order, and filter out actions we cannot perform.
    mats['materials'] = mats['materials'].values()
    mats['materials'].sort(key=lambda x:"%s-%s" % (x['material'].is_blueprint, x['material'].name))
    mats['order'] = ['Manufacturing', 'Personal', 'Research Mineral Production',
                          'Research Time Production', 'Copying', 'Inventing', 'Refining',
                          'Refined From', 'Reaction', 'Reaction-in', 'Reaction-out']
    mats['order'] = [x for x in mats['order'] if mats['titles'].has_key(x)]

    d['materials'] = mats
    log.debug('Materials2: %s', mats)

    if not (item.marketgroup and item.marketgroup.name == 'Minerals'):
        d['other_uses'] = item.helps_make.filter(USES_FILTER).count()

    #-------------------------------------------------------------------------
    # Setup the attributes of an item.
    d['VOLUME'] = VOLUME # Fake attribute
    d['PORTIONSIZE'] = PORTIONSIZE # Fake attribute
    d['CAPACITY'] = CAPACITY
    d['attributes'] = []
    temp = defaultdict(list)
    for a in item.attributes.select_related('attribute__category', 'attribute__unit', 'attribute__graphic'):
        if a.value == 0 or a.value == 0.0 or a.attribute.category is None:
            continue
        if not a.attribute.published:
            continue
        temp[a.attribute.category].append(a)
    for c in temp.keys():
        temp[c].sort(key=lambda x:x.attribute.id)
        d['attributes'].append([c, temp[c]])
    d['attributes'].sort(key=lambda x:x[0].id)

    #-------------------------------------------------------------------------
    # Setup the price indexes of an item.
    q = Q(index__user__isnull=True) | Q(index__user=profile)
    d['indexes'] = list(item.indexes.filter(q))
    d['indexes'].sort(key=lambda x:x.index.priority, reverse=True)

    d['blueprint'] = my_blueprint

    return render_to_response('item.html', d, request)

def item_uses(request, slug):
    item = get_object_or_404(Item, slug=slug)
    d = dict()
    d['nav'] = generate_navigation(item)
    d['nav'].append(uses_nav)
    d['inline_nav'] = (item,)
    d['item'] = item

    # Un-seeded items have no group.
    if not (item.marketgroup and item.marketgroup.name == 'Minerals'):
        d['makes'] = item.helps_make.filter(USES_FILTER).order_by('item__name')
        #d['makes'].sort(key=lambda x:x.item.name)
        # FIXME: Make this return an order_by instead.

    return render_to_response('item_uses.html', d, request)

@cache_page(60 * 60 * 4)
def sov_changes(request, days=14):
    """Show all of the changes in system sov since the last update."""
    old_date = datetime.utcnow() - timedelta(days)
    d = {}
    d['objects'] = SolarSystem.objects.filter(sov_time__gt=old_date).order_by('-sov_time')
    d['nav'] = [ sov_nav ]

    return render_to_response('sov_changes.html', d,
                              request)

@cache_page(60 * 60 * 4)
def npc_groups(request):
    """Show all of the available groups of NPCs out there."""
    #groups = Category.objects.get(name='Entity').groups.extra(
    #    select = {'item_count': 'SELECT COUNT(*) item_count from ccp_item where ccp_item.groupID = ccp_group.groupID'},
    #).select_related()

    groups = Category.objects.get(name='Entity').groups.annotate(Count('items')).select_related()
    # Template needs the objects as dicts.
    objects = [{'item': x } for x in groups if x.items__count > 0]

    return render_to_response('item_list.html', {
        'nav': (npc_nav, ),
        'objects': objects,
    }, request)

@cache_page(60 * 60 * 4)
def npc_group(request, slug):
    """Show all the members of a single group"""
    group = Group.objects.get(slug=slug)
    objects = list( group.items.all() )

    resist_map = {
        'armor_resist_em': 'armorEmDamageResonance',
        'armor_resist_thermal': 'armorThermalDamageResonance',
        'armor_resist_kinetic': 'armorKineticDamageResonance',
        'armor_resist_explosive': 'armorExplosiveDamageResonance',
        'shield_resist_em': 'shieldEmDamageResonance',
        'shield_resist_thermal': 'shieldThermalDamageResonance',
        'shield_resist_kinetic': 'shieldKineticDamageResonance',
        'shield_resist_explosive': 'shieldExplosiveDamageResonance',
    }
    # Scramble is missing, as it uses two attributes.
    ewar_map = {
        'jam': 'entityTargetJamMaxRange',
        'web': 'modifyTargetSpeedRange',
        'damp': 'entitySensorDampenMaxRange',
        'tracking': 'entityTrackingDisruptMaxRange',
        'neut': 'entityCapacitorDrainMaxRange',
        'paint': 'entityTargetPaintMaxRange',
    }

    # Stick the attributes where the template can find them easily.
    for o in objects:
        o.a = o.attributes_by_name()
        o.dps = o.dps()
        if 'gfxTurretID' in o.a:
            o.gun_icon = Graphic.objects.get(id=o.a['gfxTurretID'].value)
        else:
            o.gun_icon = None
        if 'missile_type' in o.dps:
            o.missile_icon = o.dps['missile_type'].graphic
        else:
            o.missile_icon = None

        for key, value in resist_map.items():
            if value in o.a:
                o.dps[key] = (1.0 - o.a[value].value) * 100
            else:
                o.dps[key] = 0

        o.ewar = dict()
        # The Insurance Teaching drone has one, but not the other? WTF?
        if 'warpScrambleStrength' in o.a and 'warpScrambleRange' in o.a:
            o.ewar['scramble'] = "%s (%s pt)" % (o.a['warpScrambleRange'].value, o.a['warpScrambleStrength'].value)
        for key, value in ewar_map.items():
            if value in o.a:
                o.ewar[key] = "%.0f km" % (int(o.a[value].value)/1000)

        if 'entityKillBounty' in o.a:
            o.bounty = o.a['entityKillBounty'].value

        if 'shieldCapacity' in o.a:
            o.shield_hp = o.a['shieldCapacity'].value
        else:
            o.shield_hp = 0

        if 'armorHP' in o.a:
            o.armor_hp = o.a['armorHP'].value
        else:
            o.armor_hp = 0

    return render_to_response('npc_group.html', {
        'nav': (npc_nav, group),
        'objects': objects,
        'icon': NPC_ICONS,
    }, request)
