from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
#from django import newforms as forms
from django.http import HttpResponseRedirect, Http404
from django.db.models.query import Q, QNot

from datetime import datetime

from eve.pos.models import PlayerStation
from eve.user.models import Character
from eve.lib.formatting import make_nav

pos_nav = make_nav("Player-Owned Structures", "/pos/", '40_14', 
                   note='Fuel status for all of your POSes.')
pos_consumption_nav = make_nav('Consumption', '/pos/consumption/', '10_07', 
                               'Consumption and shopping list for all of your POSes')
pos_profit_nav = make_nav('Profits', '/pos/profit/', '06_03', 
                          'Profits and costs for all of your POSes')
pos_monkey_nav = make_nav('POS Helpers', '/pos/helpers/','02_16',
                          'Allow others to see POS status.')

def get_poses(request):
    corps = {}
    for c in request.user.get_profile().characters.all():
        poses = []
        for pos in c.corporation.pos.all():
            if not(c.is_director or c.is_pos_monkey
                   or pos.delegates.filter(character=c).count() ):
                continue
            if not corps.has_key(c.corporation.name):
                corps[c.corporation.name] = {
                                          'name':c.corporation.name,
                                          'pos':poses,
                                        }
            # This works, because the object is already in the dict.
            poses.append(pos)
            
        if len(poses) > 0:
            poses.sort(key=lambda x:"%s/%s/%s" % (x.solarsystem.name, 
                                                  x.moon.celestialindex, 
                                                  x.moon.orbitindex))
    
    return corps.values()

def check_rights(request, pos):
    for c in request.user.get_profile().characters.all():
        if pos.corporation_id == c.corporation_id:
            if c.is_director:
                return True
            elif c.is_pos_monkey:
                return True
        if pos.delegates.filter(character=c).count() > 0:
            return True
        
    # Guess not.
    raise Http404

@login_required
def list(request):
    d = {}
    d['nav'] = [pos_nav]
    
    d['poses'] = get_poses(request) 
    d['inline_nav'] = [ pos_consumption_nav, pos_profit_nav, pos_monkey_nav ]
    
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
    
    # Build of the nav options for the POS.
    refuel_nav = make_nav('Update Fuel Quantities', '/pos/%d/refuel/' % pos.id, '10_07',
                               'The EVE Widget automatically refreshes all POS data every 6 hours. '
                               + 'Click here to update quantities if you have just refueled the tower and do not wish '
                               + 'to wait.')
    delegate_nav = make_nav('Delegate access to this POS', '/pos/%s/delegations/' % pos.id, '02_16',
                                 'Allow other people to see this specific POS. Used for personal POSes usually.'
                                 )
    d['inline_nav'] = [refuel_nav]
    if is_director_of(request.user, pos):
        d['inline_nav'].append(delegate_nav)
    
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

@login_required
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
        d['fuel'] = [x for x in pos.fuel.all()]
        d['fuel'].sort(key=lambda x:x.type.name)
        d['days'] = days
        return render_to_response('pos_refuel.html', d,
                                  context_instance=RequestContext(request))    
    
@login_required
def monkey_list(request):
    d = {}
    d['nav'] = [pos_nav, pos_monkey_nav]
    
    corporations = []
    d['corporations'] = corporations
    
    profile = request.user.get_profile()
    for character in profile.characters.all():
        if not character.is_director:
            continue
        corporations.append(character.corporation)
        
    
    return render_to_response('pos_helpers.html', d,
                                  context_instance=RequestContext(request))

def is_director_of(me, you):
    '''Security check to make sure that profile 'me' has a director role that would allow
    them to alter user 'you'. The 'you' involved may be a charcter, or a pos. (Or anything
    with a corporation_id really.)'''
    
    profile = me.get_profile()
    
    for c in profile.characters.all():
        if c.is_director and you.corporation_id == c.corporation_id:
            return True
        
    return False
    
def is_director_of_or_404(me, you):
    if is_director_of(me, you):
        return True
    else:
        raise Http404

@login_required
def monkey_grant(request, grant=None, revoke=None):
    if grant:
        char = grant
        monkey = True
    elif revoke:
        char = revoke
        monkey = False
    
    char = get_object_or_404(Character, name=char)
    is_director_of_or_404(request.user, char)
    char.is_pos_monkey = monkey
    char.save()
    return HttpResponseRedirect( pos_monkey_nav['get_absolute_url'] )

@login_required
def delegate_add(request, station_id, character_name):
    pos = get_object_or_404(PlayerStation, id=station_id)
    character = get_object_or_404(Character, name=character_name)
    check_rights(request, pos)
    is_director_of_or_404(request.user, character)
    pos.delegates.get_or_create(character=character, station=pos)
    return HttpResponseRedirect( '/pos/%s/delegations/' % pos.id )

@login_required
def delegate_delete(request, station_id, character_name):
    pos = get_object_or_404(PlayerStation, id=station_id)
    character = get_object_or_404(Character, name=character_name)
    check_rights(request, pos)
    is_director_of_or_404(request.user, character)
    pos.delegates.filter(character=character).delete()
    return HttpResponseRedirect( '/pos/%s/delegations/' % pos.id )

@login_required
def delegate_list(request, station_id):
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos)
    
    delegates = {}
    for d in pos.delegates.all():
        delegates[d.character.id] = 1
    
    d = {}
    d['pos'] = pos
    d['characters'] = [{'character':c,
                         'director':c.is_director,
                         'monkey':c.is_pos_monkey,
                         'delegate':delegates.has_key(c.id)} for c in pos.corporation.characters.all() ]
     
     
    d['nav'] = [pos_nav, pos, {'name':'Delegate'}]
    return render_to_response('pos_delegate.html', d,
                              context_instance=RequestContext(request))