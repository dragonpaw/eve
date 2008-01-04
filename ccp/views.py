# Create your views here.
#from django import newforms as forms
#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.ccp.models import *
from eve.trade.models import BlueprintOwned
from eve.util.formatting import make_nav
import re

item_nav = make_nav("Items", "/group/", '24_05')
region_nav = make_nav("Regions", "/regions/", '17_03')

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

    d['objects'].sort(lambda a,b: cmp(a.name, b.name))
    return render_to_response('generic_menu.html', d,
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
        d['blueprint'] = BlueprintOwned.objects.filter(blueprint=item.blueprint)[0]
    except IndexError:
        d['blueprint'] = None
   
   
    materials = {'titles':[],
                 'materials':[],
                 'isk': [],
                 'isk_by_name': {} }
        
    # Can it be manufactured?
    if item.blueprint:
        # First, the perfect manufacture/recycle values.
        materials['titles'] = ['Perfect',]
        for material, qty in item.materials():
            try:
                index = material.index_values.order_by('-date')[0]
            except IndexError:
                index = None
            materials['materials'].append({'material': material, 'index': index, 'values':[qty]})

        # Then, if we own the blueprint, the manufacture values.
        if d['blueprint']:
            materials['titles'].append( "PE%s/ME%d" % (max_pe, d['blueprint'].me) )
            for m in materials['materials']:
                qty = m['values'][0]
                qty = d['blueprint'].mineral(qty, max_pe)
                m['values'].append(qty)
                            
        materials['titles'].append('Reprocess')
        for m in materials['materials']:
            # TODO: Recycle values.
            m['values'].append(None) 
            
    refines = item.material_set.filter(activity=50)
    if refines.count():
        assert(len(materials['materials']) == 0) # Nothing manufactured can be also refined as such.
        
        materials['titles'].append('Refined')
        for m in refines:
            try:
                index = m.material.index_values.order_by('-date')[0]
            except IndexError:
                index = None
            materials['materials'].append({'material': m.material, 'index': index, 'values':[m.quantity]})

    re_manufacture = re.compile(r'^PE\d/ME\d+$')
    for i in range(len(materials['titles'])):
        cost = Decimal(0)
        for m in materials['materials']:
            material = m['material']
                
            if material.group.name in ('Mineral',) and m['values'][i] and m['index']:
                cost += Decimal(str(m['index'].value)) * m['values'][i]
        cost = cost / item.portionsize
        materials['isk'].append(cost)
        materials['isk_by_name'][materials['titles'][i]] = cost
        if re_manufacture.match(materials['titles'][i]):
            materials['isk_by_name']['manufacture'] = cost

    if len(materials['materials']):
        materials['titles'].append('Index')
        for m in materials['materials']:
            if m['index']:
                m['values'].append("%0.2f" % m['index'].value)
            else:
                m['values'].append("None")
        materials['isk'].append(" ") # Avoids a 'N/a' cell.
        materials['materials'].sort(lambda a,b: cmp(a['material'].name, b['material'].name))

    if (materials['isk_by_name'].has_key('manufacture') and best_values.has_key('sell') 
        and best_values['sell'] and best_values['sell']['sell_price'] > 0
        and materials['isk_by_name']['manufacture'] > 0):
        best_values['manufacturing_profit_isk'] =  ( best_values['sell']['sell_price'] 
                                                    - materials['isk_by_name']['manufacture'])
        best_values['manufacturing_profit_pct'] = (best_values['manufacturing_profit_isk'] 
                                                    / materials['isk_by_name']['manufacture']) * 100   

    # We don't want isk prices on where things refine -from-
    if item.group.name in ('Mineral','Ice Product'):
        assert(len(materials['materials']) == 0) # Nothing manufactured can be also refined as such.
        materials['titles'].append('Per Unit')
        temp = list(item.helps_make.filter(activity=50))
        temp.sort(lambda a,b: cmp(a.quantity_per_unit(), b.quantity_per_unit()))
        temp.reverse()
        for m in temp:
            value = "%0.2f" % m.quantity_per_unit()
            materials['materials'].append({'material': m.item,'values':[value]})

    d['materials'] = materials

            
    # FIXME: Make this return an order_by instead.
    d['invention'] = item.materials(activity=8)
    if d['invention']:
        d['invention'].sort(lambda a, b: cmp(a[0].name, b[0].name))

    # Un-seeded items have no group.
    if item.marketgroup and item.marketgroup.name != 'Minerals':
        d['makes'] = list(item.helps_make.filter(activity=1))
        d['makes'].sort(lambda a, b: cmp(a.item.name, b.item.name))
        # FIXME: Make this return an order_by instead.
    
    d['invents'] = list(item.helps_make.filter(activity=8))
    d['invents'].sort(lambda a, b: cmp(a.item.name, b.item.name))
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
    
    return render_to_response('trade_item.html', d,
                              context_instance=RequestContext(request))
                   