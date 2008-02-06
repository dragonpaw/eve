from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
#from django import newforms as forms
from django.http import HttpResponseRedirect, Http404

from datetime import datetime

from eve.pos.models import PlayerStation
from eve.util.formatting import make_nav

pos_nav = make_nav("Player-Owned Structures", "/pos/", '40_14', 
                   note='Fuel status for all of your POSes.')
pos_consumption_nav = make_nav('Consumption', '/pos/consumption/', '10_07', 
                               'Consumption and shopping list for all of your POSes')
pos_profit_nav = make_nav('Profits', '/pos/profit/', '06_03', 
                               'Profits and costs for all of your POSes')

def get_poses(request):
    corps = {}
    for c in request.user.get_profile().characters.filter(is_director=True):
        poses = c.corporation.pos.select_related().order_by('ccp_mapdenormalize.itemName', 
                                                            'ccp_mapdenormalize.celestialindex',
                                                            'ccp_mapdenormalize.orbitindex',
                                                            )
        corps[c.corporation.name] = {
                                        'name':c.corporation.name,
                                        'pos':poses,
                                    }
    return corps.values()

def check_rights(request, pos):
    for c in request.user.get_profile().characters.filter(is_director=True):
        if pos.corporation_id == c.corporation_id:
            return
        
    # Guess not.
    raise Http404

@login_required
def list(request):
    d = {}
    d['nav'] = [pos_nav]
    
    d['poses'] = get_poses(request) 
    d['inline_nav'] = [ pos_consumption_nav, pos_profit_nav ]
    
    return render_to_response('pos_list.html', d, context_instance=RequestContext(request))


@login_required
def detail(request, station_id, days=14):
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos)
    profile = request.user.get_profile()
    
    d = {}
    d['nav'] = [pos_nav, pos]
    d['pos'] = pos
    d['days'] = days
    d['refuel_nav'] = make_nav('Manually Refuel', '/pos/%d/refuel/' % pos.id, '10_07',
                               'Manually update the fuel quantites within this tower.')
    cost = 0
    fuels = []
    for f in pos.fuel.all():
        if f.purpose == 'Reinforce':
            continue
                
        price = profile.get_buy_price(f.type)
        weekly = f.consumption * 24 * 7
        weekly_cost = price * weekly
        cost += weekly_cost
        fuels.append({'price':price,'weekly':weekly,'weekly_cost':weekly_cost,'type':f.type,'fuel':f})
        
    fuels.sort(key=lambda x:x['type'].name)
    d['weekly_cost'] = cost
    d['fuels'] = fuels
    
    return render_to_response('pos_detail.html', d, context_instance=RequestContext(request))

@login_required
def consumption(request, days=14):
    d = {}
    d['nav'] = [pos_nav, pos_consumption_nav]
    
    hours = days * 24 # Hours.
    profile = request.user.get_profile()
    
    corps = []
    poses = get_poses(request)
    for pos_list in poses:
        corp_name = pos_list['name']
        needs = {}
        cost_weekly = 0
        cost_total = 0
        pos_costs = []
        for pos in pos_list['pos']:
            for fuel in pos.fuel.all():
                if fuel.purpose == 'Reinforce':
                    continue
                
                if not needs.has_key(fuel.type.id):
                    needs[fuel.type.id] = {
                                           'purpose':fuel.purpose,
                                           'quantity':0,
                                           'ideal_quantity':0,
                                           'consumption':0,
                                           'weekly':0,
                                           'needed':0,
                                           'type':fuel.type,
                                           'buy_price':profile.get_buy_price(fuel.type)
                                          }
                
                f = needs[fuel.type.id]
                f['quantity'] += fuel.quantity
                f['consumption'] += fuel.consumption
                f['ideal_quantity'] += fuel.consumption * hours
                f['weekly'] += fuel.consumption * 24 * 7
                f['needed'] += fuel.need(days=days)
          
        fuels = needs.values()
        for f in fuels:
            f['cost'] = f['needed'] * f['buy_price']
            f['cost_weekly'] = f['weekly'] * f['buy_price']
            f['cost_needed'] = f['needed'] * f['buy_price']
            cost_total += f['cost_needed']
            cost_weekly += f['cost_weekly']
                        
        fuels.sort(key=lambda x:x['type'].name)
        corps.append({'name':corp_name,
                      'fuel':fuels,
                      'cost_total':cost_total,
                      'cost_weekly':cost_weekly,
                      'poses':pos_costs,
                      })
        
    d['fuels'] = corps
    d['days'] = days
    return render_to_response('pos_consumption.html', d, context_instance=RequestContext(request))

@login_required
def profit(request):
    d = {}
    d['nav'] = [pos_nav, pos_profit_nav]
    
    profile = request.user.get_profile()
    
    corps = []
    poses = get_poses(request)
    for pos_list in poses:
        corp_name = pos_list['name']
        prices = {}
        cost_weekly = 0
        pos_costs = []
        for pos in pos_list['pos']:
            pos_weekly_cost = 0
            for fuel in pos.fuel.all():
                if fuel.purpose == 'Reinforce':
                    continue
                if not prices.has_key(fuel.type.id):
                    buy_price = profile.get_buy_price(fuel.type)
                    prices[fuel.type.id] = buy_price

                
                pos_weekly_cost += fuel.consumption * 24 * 7 * prices[fuel.type.id]
            pos_costs.append({'pos':pos, 'cost':pos_weekly_cost})
            cost_weekly += pos_weekly_cost
        corps.append({'name':corp_name,
                      'cost_weekly':cost_weekly,
                      'poses':pos_costs,
                      })
        
    d['fuels'] = corps
    return render_to_response('pos_profits.html', d, context_instance=RequestContext(request))


def refuel(request, station_id, days=14):
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos)
    if request.method == 'POST':
        for fuel in pos.fuel.all():
            id = str(fuel.type.id)
            print "id: %s" % id
            if id in request.POST:
                fuel.quantity = int(request.POST[id])
                print "new qty: %d" % fuel.quantity
                fuel.save()
        pos.state_time = datetime.utcnow()
        pos.save()
        return HttpResponseRedirect( pos.get_absolute_url() )
    else:
        d = {}
        d['nav'] = [pos_nav, pos, {'name':'Manual Refueling'}]
        d['pos'] = pos
        d['days'] = days
        return render_to_response('pos_refuel.html', d,
                                  context_instance=RequestContext(request))    
    