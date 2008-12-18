# Create your views here.
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.db.models import Q

from eve.ccp.models import SolarSystem, Constellation, Region, MarketGroup, Item, Attribute
from eve.trade.models import BlueprintOwned
from eve.lib.formatting import make_nav

from datetime import datetime, timedelta
from decimal import Decimal

item_nav = make_nav("Items", "/items/", '24_05', note='All items in the game.')
region_nav = make_nav("Regions", "/regions/", '17_03', note='The universe, and everything in it.')
sov_nav = make_nav('Sovereignty Changes', '/sov/changes/', '70_11', note='Who lost and gained systems.')

def generate_navigation(object):
    """Build up a heiracy of objects"""
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

    d = {}

    d['nav'] = [
                {'name':"Regions",'get_absolute_url':"/regions/"},
                item.region,
                item.constellation,
                item
               ]
    d['title'] = "Solar System: %s" % item.name
    d['item'] = item

    return render_to_response('ccp_solarsystem.html', d,
                              context_instance=RequestContext(request))


def constellation(request, name):
    item = get_object_or_404(Constellation, name=name)
    #item = Constellation.objects.get(name=name)

    d = {}

    d['nav'] = [
                {'name':"Regions",'get_absolute_url':"/regions/"},
                item.region,
                item
               ]
    d['title'] = "Constellation: %s" % item.name
    d['item'] = item


    return render_to_response('ccp_constellation.html', d,
                              context_instance=RequestContext(request))

def region(request, slug):
    item = get_object_or_404(Region, slug=slug)
    #item = Constellation.objects.get(name=name)

    d = {}

    d['nav'] = [
                {'name':"Regions",'get_absolute_url':"/regions/"},
                item
               ]
    d['title'] = "Region: %s" % item.name
    d['item'] = item


    return render_to_response('ccp_region.html', d,
                              context_instance=RequestContext(request))

def region_list(request):
    d = {}
    d['nav'] = [ {'name':"Regions",'get_absolute_url':"/regions/"} ]

    #q1 = Q(faction__isnull=True)
    #q2 = ~Q(faction__name='Jove Empire')

    #regions = list(Region.objects.filter(q1)) + list(Region.objects.filter(q2))
    #regions.sort(key=lambda x:x.name)

    q = Q(faction__isnull=True) | ~Q(faction__name='Jove Empire')
    regions = Region.objects.filter(q)

    d['inline_nav'] = regions

    return render_to_response('ccp_regions.html', d,
                              context_instance=RequestContext(request))

def group_index(request):
    root_objects = MarketGroup.objects.filter(parent__isnull=True)
    #output = ', '.join([m.name for m in root_objects])
    d = {}
    d['nav'] = [ item_nav ]
    d['objects'] = [{'item':x} for x in root_objects]

    return render_to_response('ccp_item_list.html', d,
                              context_instance=RequestContext(request))

def group(request, slug):
    group = get_object_or_404(MarketGroup, slug=slug)
    profile = None
    if request.user.is_anonymous() == False:
        profile = request.user.get_profile()

    d = {}

    d['nav'] = generate_navigation(group)
    d['title'] = "Market Group: %s" % group.name

    objects = list(MarketGroup.objects.filter(parent=group)) + list(group.item_set.all())
    d['objects'] = [{'item':x,
                     'buy':get_buy_price(profile, x),
                     'sell':get_sell_price(profile, x)} for x in objects]

    d['objects'].sort(key=lambda x:x['item'].name)
    return render_to_response('ccp_item_list.html', d,
                              context_instance=RequestContext(request))


def get_index_price(profile, item, type=None):
    # I'm lazy in group above, and call this for market groups as well as items.
    if not isinstance(item, Item):
        return None

    temp = list( item.index_values.all() )
    if len(temp) == 0:
        return None
    temp.sort(key=lambda x:x.index.priority, reverse=True)
    for k in temp:
        if type == 'buy' and k.buy:
            return k.buy
        if type == 'sell' and k.sell:
            return k.sell

    return None

def get_sell_price(profile, item):
    if profile is not None:
        return profile.get_sell_price(item)

    return get_index_price(profile, item, type='sell')

def get_buy_price(profile, item):
    if profile is not None:
        return profile.get_buy_price(item)

    return get_index_price(profile, item, type='buy')

def item(request, slug, days=30):
    item = get_object_or_404(Item, slug=slug)
    d = {}
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
            my_blueprint = BlueprintOwned.objects.filter(blueprint=item.blueprint, user=profile)[0]
        except IndexError:
            pass


    materials = {'titles':{},
                 'materials':{},
                 'isk': {} }

    # Can it be manufactured?
    for mat in item.materials():
        if mat.quantity <= 0:
            continue

        name = mat.activity.name
        materials['titles'][name] = name
        if not materials['materials'].has_key(mat.material.id):
            price = get_buy_price(profile, mat.material)
            materials['materials'][mat.material.id] = {'material': mat.material,
                                                       'buy_price': price}
        materials['materials'][mat.material.id][name] = mat.quantity

        # Then, if we own the blueprint, the manufacture quantity.
        if my_blueprint and name == 'Manufacturing':
            perfect = materials['materials'][mat.material.id]['Manufacturing']
            materials['materials'][mat.material.id]['Personal'] = my_blueprint.mineral(perfect, max_pe)

    # If we own this blueprint...
    if my_blueprint:
        # Add in the Blueprint itself.
        materials['materials'][my_blueprint.blueprint.id] = {'Personal': 1,
                                                             'material':my_blueprint.blueprint,
                                                             'buy_price':my_blueprint.cost_per_run,
                                                             'input':'Blueprint run cost',
                                                             }
        materials['titles']['Personal'] = "Your Blueprint: PE%s/ME%d" % (max_pe, my_blueprint.me)
        # We only show our manufacturing if we have the blueprint.
        del materials['titles']['Manufacturing']

    for key, value in materials['titles'].items():
        cost = Decimal(0)
        for m in materials['materials'].values():
            if m.has_key(key) and m['buy_price'] and not m['material'].is_skill:
                cost += Decimal(str(m['buy_price'])) * m[key]
        if item.is_blueprint:
            portion = item.blueprint_makes.portionsize
        else:
            portion = item.portionsize
        cost = cost / portion
        materials['isk'][key] = cost

    if (materials['isk'].has_key('Personal') and best_values.has_key('sell')
        and best_values['sell'] and best_values['sell']['sell_price'] > 0
        and materials['isk']['Personal'] > 0):
        best_values['manufacturing_profit_isk'] =  ( best_values['sell']['sell_price']
                                                    - materials['isk']['Personal'])
        best_values['manufacturing_profit_pct'] = (best_values['manufacturing_profit_isk']
                                                    / materials['isk']['Personal']) * 100

    # We don't want isk prices on where things refine -from-
    if item.group.name in ('Mineral','Ice Product'):
        materials['titles']['Refined From'] = "Refined From"
        for mat in item.helps_make.filter(activity=50):
            value = "%0.2f" % mat.quantity_per_unit()
            price = get_buy_price(profile, mat.item)
            materials['materials'][mat.item.id] = {'material' : mat.item,
                                                   'buy_price'    : price,
                                                   'Refined From' : value}

    # This triggers on materials that CAN react.
    if item.reacts.count():
        for mat in item.reacts.all():
            price = get_buy_price(profile, mat.reaction)
            reaction = mat.reaction
            if mat.input:
                materials['titles']['Reaction-in'] = 'Reactions Needing'
                for r in reaction.reactions.filter(input=False):
                    materials['materials'][r.item.id] = {'material': r.item,
                                                         'buy_price': price,
                                                         'input':'Needed',
                                                         'Reaction-in': mat.quantity
                                                         }
            else:
                materials['titles']['Reaction-out'] = 'Materials to React'
                for r in reaction.reactions.filter(input=True):
                    materials['materials'][r.item.id] = {'material': r.item,
                                                         'buy_price': price,
                                                         'input':'Used',
                                                         'Reaction-out': r.quantity
                                                         }

    # This triggers on reaction blueprints
    if item.reactions.count():
        materials['titles']['Reaction'] = 'POS Reaction'
        for mat in item.reactions.all():
            buy_price = sell_price = 0
            if mat.input == True:
                input = "Input"
                buy_price = get_buy_price(profile, mat.item)
            else:
                input = "Output"
                sell_price = get_sell_price(profile, mat.item)
            materials['materials'][mat.item.id] = {'material' : mat.item,
                                                   'buy_price': buy_price,
                                                   'input': input,
                                                   'sell_price': sell_price,
                                                   'Reaction' : mat.quantity}
    # Display order, and filter out actions we cannot perform.
    materials['materials'] = [materials['materials'][key] for key in materials['materials'].keys()]
    materials['materials'].sort(key=lambda x:"%s-%s" % (x['material'].is_blueprint, x['material'].name))
    materials['order'] = ['Manufacturing', 'Personal', 'Research Mineral Production',
                          'Research Time Production', 'Copying', 'Inventing', 'Refining',
                          'Refined From', 'Reaction', 'Reaction-in', 'Reaction-out']
    materials['order'] = [x for x in materials['order'] if materials['titles'].has_key(x)]

    d['materials'] = materials

    # Un-seeded items have no group.
    if item.marketgroup and item.marketgroup.name != 'Minerals':
        filter = ~Q(activity__name__contains='Not in game')
        filter &= Q(quantity__gt=0)
        filter &= ~Q(activity__name='Refining')

        d['makes'] = list(item.helps_make.filter(filter))
        d['makes'].sort(key=lambda x:x.item.name)
        # FIXME: Make this return an order_by instead.

    attributes = list(item.attributes())
    if item.volume:
        volume = Attribute.objects.get(attributename='volume')
        volume.valuefloat = item.volume
        attributes.append(volume)
    if item.portionsize > 1:
        portion = Attribute.objects.get(attributename='portionsize')
        portion.valueint = item.portionsize
        attributes.append(portion)
        # FIXME: Make this return an order_by instead.

    # Setup the attributes of an item.
    d['attributes'] = []
    temp = {}
    attributes.sort(lambda a, b: cmp(a.id,  b.id))
    for a in attributes:
        if a.value == 0 or a.value == 0.0 or a.category is None:
            continue
        if not temp.has_key(a.category):
            temp[a.category] = []
        temp[a.category].append(a)
    for c in temp.keys():
        d['attributes'].append([c, temp[c]])
    d['attributes'].sort(key=lambda x:x[0].id)

    # Setup the price indexes of an item.
    q = Q(index__user__isnull=True) | Q(index__user=profile)
    d['indexes'] = list(item.index_values.filter(q))
    d['indexes'].sort(key=lambda x:x.index.priority, reverse=True)

    d['blueprint'] = my_blueprint

    return render_to_response('ccp_item.html', d,
                              context_instance=RequestContext(request))


def sov_changes(request, days=14):
    """Show all of the changes in system sov since the last update."""
    old_date = datetime.utcnow() - timedelta(days)
    d = {}
    d['objects'] = SolarSystem.objects.filter(sov_time__gt=old_date).order_by('-sov_time')
    d['nav'] = [ sov_nav ]

    return render_to_response('sov_changes.html', d,
                              context_instance=RequestContext(request))
