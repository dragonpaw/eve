# Create your views here.
#from django import newforms as forms
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.ccp.models import SolarSystem, Constellation, Region, MarketGroup, Item, Attribute
from eve.trade.models import BlueprintOwned
from eve.util.formatting import make_nav
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models.query import Q, QNot

item_nav = make_nav("Items", "/group/", '24_05')
region_nav = make_nav("Regions", "/regions/", '17_03')
sov_nav = make_nav('Sovereignty Changes', '/sov/changes/', '70_11')

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
    
    return render_to_response('solarsystem.html', d,
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

    
    return render_to_response('constellation.html', d,
                              context_instance=RequestContext(request))
    
def region(request, name):
    item = get_object_or_404(Region, name=name)
    #item = Constellation.objects.get(name=name)

    d = {}
    
    d['nav'] = [
                {'name':"Regions",'get_absolute_url':"/regions/"},
                item
               ]
    d['title'] = "Region: %s" % item.name
    d['item'] = item

    
    return render_to_response('region.html', d,
                              context_instance=RequestContext(request))
    
def region_list(request):
    
    d = {}
    d['objects'] = Region.objects.all()
    d['title'] = "Region List"
    d['nav'] = [ {'name':"Regions",'get_absolute_url':"/regions/"} ]
    
    return render_to_response('regions.html', d,
                              context_instance=RequestContext(request))
    
def group_index(request):
    root_objects = MarketGroup.objects.filter(parent__isnull=True)
    #output = ', '.join([m.name for m in root_objects])
    return render_to_response('generic_menu.html', {
                              'objects': root_objects,
                              'title': "Market Groups",
                              'nav': [ item_nav ],
                              },
                              context_instance=RequestContext(request))

def group(request, group_id):
    group = get_object_or_404(MarketGroup, id=group_id)
    d = {}
    
    d['nav'] = generate_navigation(group)
    d['title'] = "Market Group: %s" % group.name

    d['objects'] = list(MarketGroup.objects.filter(parent=group)) + list(group.item_set.all())

    d['objects'].sort(key=lambda x:x.name)
    return render_to_response('item_list.html', d,
                              context_instance=RequestContext(request))

    
    
def item(request, item_id, days=14):
    item = get_object_or_404(Item, id=item_id)
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
            
    try:
        d['blueprint'] = BlueprintOwned.objects.filter(blueprint=item.blueprint, user=request.user)[0]
    except IndexError:
        d['blueprint'] = None
   
   
    materials = {'titles':{},
                 'materials':{},
                 'isk': {} }
        
    # Can it be manufactured?
    for mat in item.materials():
        name = mat.activity.name
        materials['titles'][name] = name
        if not materials['materials'].has_key(mat.material.id):
            materials['materials'][mat.material.id] = {'material': mat.material,
                                                       'index': mat.material.index}
        materials['materials'][mat.material.id][name] = mat.quantity
        
        # Then, if we own the blueprint, the manufacture quantity.
        if d['blueprint'] and name == 'Manufacturing':
            perfect = materials['materials'][mat.material.id]['Manufacturing']
            materials['materials'][mat.material.id]['Personal'] = d['blueprint'].mineral(perfect, max_pe)
            
    if d['blueprint']:
        materials['titles']['Personal'] = "Your Blueprint: PE%s/ME%d" % (max_pe, d['blueprint'].me)
        del materials['titles']['Manufacturing']

    for key, value in materials['titles'].items():
        cost = Decimal(0)
        for m in materials['materials'].values():
            if m.has_key(key) and m['index']:
                cost += Decimal(str(m['index'].value)) * m[key]
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
            materials['materials'][mat.item.id] = {'material' : mat.item,
                                                       'index'    : mat.item.index,
                                                       'Refined From' : value}

    # Display order, and filter out actions we cannot perform.
    materials['materials'] = [materials['materials'][key] for key in materials['materials'].keys()]
    materials['materials'].sort(key=lambda x:x['material'].name)
    materials['order'] = ['Manufacturing', 'Personal', 'Research Mineral Production',
                          'Research Time Production', 'Copying', 'Inventing', 'Refining', 'Refined From']
    materials['order'] = [x for x in materials['order'] if materials['titles'].has_key(x)]

    d['materials'] = materials
    
    # Un-seeded items have no group.
    if item.marketgroup and item.marketgroup.name != 'Minerals':
        #filter = QNot(Q(item__group__category__name='Blueprint')) & Q(item__published=True)
        filter = Q(item__published=True) & QNot(Q(activity__name__contains='Not in game'))
        d['makes'] = list(item.helps_make.filter(filter))
        d['makes'].sort(key=lambda x:x.item.name)
        # FIXME: Make this return an order_by instead.
        
    d['attributes'] = list(item.attributes())
    if item.volume:
        volume = Attribute.objects.get(attributename='volume')
        volume.valuefloat = item.volume
        d['attributes'].append(volume)
    if item.portionsize > 1:
        portion = Attribute.objects.get(attributename='portionsize')
        portion.valueint = item.portionsize
        d['attributes'].append(portion)
        # FIXME: Make this return an order_by instead.
    d['attributes'].sort(lambda a, b: cmp(a.attributecategory,
                                          b.attributecategory)
                         or cmp (a.id, b.id))
    
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
    