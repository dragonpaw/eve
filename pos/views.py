from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django import forms
from django.http import HttpResponseRedirect, Http404
from django.db.models import Q

from datetime import datetime

from eve.ccp.models import Item, Corporation
from eve.pos.models import PlayerStation
from eve.user.models import Character
from eve.lib.formatting import make_nav, NavigationElement

pos_nav = make_nav("Player-Owned Structures", "/pos/", '40_14',
                   note='Fuel status for all of your POSes.')
pos_profit_nav = make_nav('Profits', '/pos/profit/', '06_03',
                          'Profits and consumption for all of your POSes')
pos_monkey_nav = make_nav('POS Helpers', '/pos/helpers/','02_16',
                          'Check who is able to see POS status.')
REFUEL_NAV = make_nav('Update Fuel Quantities', '/pos/%d/refuel/', '10_07',
                      'The EVE Widget automatically refreshes all POS data every 6 hours. '
                      + 'Click here to update quantities if you have just refueled the tower and do not wish '
                      + 'to wait.')
REACTION_NAV = make_nav('Configure Reactions', '/pos/%d/reactions/', '50_04',
                        'Update what mining/reactions this POS is running.')

DEFAULT_DAYS = 30

def get_poses(profile):
    corps = set()
    characters = set()

    for c in profile.characters.all():
        if c.is_pos_monkey or c.is_director:
            corps.add(c.corporation)
        else:
            characters.add(c)

    query = Q(corporation__in=corps) | Q(owner__in=characters)
    sorting = ['corporation','owner', 'solarsystem__name', 'moon__celestialindex', 'moon__orbitindex']

    poses = PlayerStation.objects.filter(query).order_by(*sorting).select_related()

    return poses

def pos_allowed(profile, pos):
    for character in profile.characters.all():
        if pos.corporation_id == character.corporation_id:
            if character.is_director:
                return True
            elif character.is_pos_monkey:
                return True
            elif pos.owner == character:
                return True
    raise Http404

@login_required
def pos_list(request):
    d = {}
    d['nav'] = [pos_nav]
    profile = request.user.get_profile()



    d['poses'] = get_poses(profile)
    d['inline_nav'] = [ pos_profit_nav, pos_monkey_nav ]

    return render_to_response('list.html', d, context_instance=RequestContext(request))

#
#@login_required
#def fuel_detail(request, station_id, days=DEFAULT_DAYS):
#    pos = get_object_or_404(PlayerStation, id=station_id)
#    profile = request.user.get_profile()
#    pos_allowed(profile, pos)
#
#    d = {}
#    d['nav'] = [pos_nav, pos]
#    d['pos'] = pos
#    d['days'] = days
#    d['id'] = pos.id # Used by the inline nav function.
#    fuels = []
#    for f in pos.fuel.all():
#        fuels.append({'need':f.need(days=days),
#                      'run_time':f.time_remaining,
#                      'type':f.type,
#                      'fuel':f})
#
#    fuels.sort(key=lambda x:x['type'].name)
#    d['fuels'] = fuels
#
#
#    nav = []
#    # Build of the nav options for the POS.
#    for x in (REFUEL_NAV, REACTION_NAV, PROFIT_NAV):
#        x.id = pos.id
#        nav.append(x)
#
#    if pos.owner:
#        owner = NavigationElement (
#            'Owner: %s' % pos.owner.name,
#            '/pos/%d/owner' % pos.id,
#            pos.owner,
#            "Set the 'owner' of this POS."
#        )
#    else:
#        owner = NavigationElement (
#            'Corporation Use',
#            '/pos/%d/owner' % pos.id,
#            pos.corporation,
#            "Set the 'owner' of this POS."
#        )
#    nav.append(owner)
#
#    d['inline_nav'] = nav
#
#    return render_to_response('pos_fuel_detail.html', d,
#                              context_instance=RequestContext(request))

#@login_required
#def profit_detail(request, station_id):
#    profile = request.user.get_profile()
#    pos = get_object_or_404(PlayerStation, id=station_id)
#    pos_allowed(profile, pos)
#
#    d = {}
#    d['nav'] = [pos_nav, pos_profit_nav, pos]
#    d['pos'] = pos
#    cost = 0
#    fuels = []
#    for f in pos.fuel.all():
#        price = profile.get_buy_price(f.type)
#
#        weekly = 0
#        if f.purpose != 'Reinforce':
#            weekly = f.consumption * 24 * 7
#            weekly_cost = price * weekly
#            cost += weekly_cost
#
#        fuels.append({'price':price,
#                      'weekly':weekly,
#                      'weekly_cost':weekly_cost,
#                      'type':f.type,
#                      'fuel':f})
#
#    fuels.sort(key=lambda x:x['type'].name)
#    d['weekly_cost'] = cost
#    d['fuels'] = fuels
#    d['reactions'] = list( pos.reactions.all() )
#    d['reactions'].sort(key=lambda x:'%d-%s' % (x.is_reaction, x.type.name))
#
#    reaction_values = []
#    weekly_value = 0
#    for type, quantity in pos.reacted_quantities():
#        r = {}
#        r['weekly'] = 24 * 7 * quantity
#        r['sell'] = profile.get_sell_price(type)
#        r['weekly_value'] = r['sell'] * r['weekly']
#        r['type'] = type
#        reaction_values.append(r)
#        weekly_value += r['weekly_value']
#    reaction_values.sort(key=lambda x:x['type'].id)
#    d['reaction_values'] = reaction_values
#    d['weekly_value'] = weekly_value
#    d['weekly_total'] = abs(weekly_value - cost)
#    d['profitable'] = d['weekly_total'] > 0
#    nav = []
#    # Build of the nav options for the POS.
#    for x in (REACTION_NAV,):
#        x.id = pos.id
#        nav.append(x)
#    d['inline_nav'] = nav
#
#    return render_to_response('pos_profit_detail.html', d,
#                              context_instance=RequestContext(request))


@login_required
def detail(request, station_id, days=DEFAULT_DAYS):
    profile = request.user.get_profile()
    pos = get_object_or_404(PlayerStation, id=station_id)
    # Doesn't actually seem faster.
    #try:
    #    pos = PlayerStation.objects.get(id=station_id).select_related()
    #except PlayerStation.DoesNotExist:
    #    raise Http404
    pos_allowed(profile, pos)

    # Build of the nav options for the POS.
    nav = []
    for x in (REFUEL_NAV, REACTION_NAV):
        x.id = pos.id
        nav.append(x)
    if pos.owner:
        owner = NavigationElement (
            'Owner: %s' % pos.owner.name,
            '/pos/%d/owner' % pos.id,
            pos.owner,
            "Set the 'owner' of this POS."
        )
    else:
        owner = NavigationElement (
            'Corporation Use',
            '/pos/%d/owner' % pos.id,
            pos.corporation,
            "Set the 'owner' of this POS."
        )
    nav.append(owner)

    # Fuel use and costs.
    fuels = []
    cost = 0
    for f in pos.fuel.select_related():
        price = profile.get_buy_price(f.type)

        weekly = 0
        if f.purpose != 'Reinforce':
            weekly = f.consumption * 24 * 7
            weekly_cost = price * weekly
            cost += weekly_cost

        fuels.append({
            'need':f.need(days=days),
            'run_time':f.time_remaining,
            'type':f.type,
            'fuel':f,
            'price':price,
            'weekly':weekly,
            'weekly_cost':weekly_cost,
        })

    fuels.sort(key=lambda x:x['type'].name)

    # Figure out reactions and their value
    reactions = list( pos.reactions.select_related() )
    reactions.sort(key=lambda x:'%d-%s' % (x.is_reaction, x.type.name))
    reaction_values = []
    weekly_value = 0
    for type, quantity in pos.reacted_quantities():
        r = {}
        r['weekly'] = 24 * 7 * quantity
        r['sell'] = profile.get_sell_price(type)
        r['weekly_value'] = r['sell'] * r['weekly']
        r['type'] = type
        reaction_values.append(r)
        weekly_value += r['weekly_value']
    reaction_values.sort(key=lambda x:x['type'].id)
    weekly_total = weekly_value - cost

    # Shove it all into the stash.
    d = {
        'nav': (pos_nav, pos),
        'pos': pos,
        'days': days,
        'id': pos.id, # Used by the inline nav function.
        'inline_nav': nav,
        'weekly_cost': cost,
        'fuels': fuels,
        'reactions': reactions,
        'reaction_values': reaction_values,
        'weekly_value':  weekly_value,
        'weekly_total': abs(weekly_total),
        'profitable': weekly_total > 0,
    }

    return render_to_response('detail.html', d,
                              context_instance=RequestContext(request))

@login_required
def profits(request, days=DEFAULT_DAYS):
    d = {}
    d['nav'] = (pos_nav,)

    profile = request.user.get_profile()
    poses = get_poses(profile=profile)

    corps = {}
    price_cache = {}
    purpose_cache = {} # Cached to avoid a lot of redundant lookups.
    type_cache = {}

    for pos in poses:
        corp_id = pos.corporation_id
        if corp_id not in corps:
            corps[corp_id] = {
                'weekly_cost': 0,
                'weekly_value': 0,
                'value': 0,
                'total': 0,
                'fuels': {},
                'reactions': {},
                'corp':  pos.corporation,
            }

        pos.cost = 0
        pos.value = 0
        pos.m3_needed = 0.0

        for fuel in pos.fuel.all():
            type_id = fuel.type_id

            # HACK!!!!
            # This caches the tower informtion on the fuel.
            # Really, Django should be doing this.
            fuel.station = pos

            # Data for this type must be cached.
            if type_id not in price_cache:
                #print('looked up price/purpose of: %s' % type)
                type = fuel.type
                price_cache[type_id] = profile.get_buy_price(type)
                purpose_cache[type_id] = fuel.purpose
                type_cache[type_id] = type

            type = type_cache[type_id]
            price = price_cache[type_id]
            purpose = purpose_cache[type_id]

            # Record for tracking how much of this fuel a corp uses.
            if type.id not in corps[corp_id]['fuels']:
                corps[corp_id]['fuels'][type_id] = {
                    'consumption': 0,
                    'needed': 0,
                    'type': type,
                }

            consumption = fuel.consumption
            need = fuel.need(days=days)
            pos.m3_needed += need * type.volume
            corps[corp_id]['fuels'][type_id]['needed'] += need

            if purpose != 'Reinforce':
                pos.cost += (consumption * price)
                corps[corp_id]['fuels'][type_id]['consumption'] += consumption

        for reaction in pos.reactions.select_related('type'):
            reactions = [['input', item_id, qty] for item_id, qty in reaction.inputs()]
            reactions.extend([['output', item_id, qty] for item_id, qty in reaction.output()])
            for inout, type_id, quantity in reactions:

                if type_id not in price_cache:
                    type = Item.objects.get(id=type_id)
                    price_cache[type_id] = profile.get_sell_price(type)
                price = price_cache[type_id]

                if type_id not in corps[corp_id]['reactions']:
                    corps[corp_id]['reactions'][type_id] = {
                        'quantity': 0,
                        'type': type,
                    }

                if inout == 'input':
                    corps[corp_id]['reactions'][type_id]['quantity'] -= quantity
                    pos.value -= (quantity * price)
                else:
                    corps[corp_id]['reactions'][type_id]['quantity'] += quantity
                    pos.value += (quantity * price)

        # Cost needs to be weekly.
        pos.weekly_cost = pos.cost * 24 * 7
        pos.weekly_value = pos.value * 24 * 7
        pos.is_profitable = pos.value > pos.cost
        pos.weekly_net = pos.weekly_value - pos.weekly_cost
        corps[corp_id]['weekly_cost'] += pos.weekly_cost
        corps[corp_id]['weekly_value'] += pos.weekly_value
        #print ('Finished POS: %s' % pos.id)

    for c in corps.values():
        c['profitable'] = c['weekly_value'] > c['weekly_cost']
        c['weekly_net'] = abs(c['weekly_value'] - c['weekly_cost'])
        for f in c['fuels'].values():
            f['weekly_consumption'] = f['consumption'] * 24 * 7

    d['poses'] = poses
    d['fuels'] = corps
    d['days'] = days
    return render_to_response('profits.html', d, context_instance=RequestContext(request))

#@login_required
#def profit_list(request):
#    d = {}
#    d['nav'] = [pos_nav, pos_profit_nav]
#
#    profile = request.user.get_profile()
#
#    corps = {}
#    price_cache = {}
#    poses = get_poses(profile)
#
#    for pos_list in poses:
#        corp_name = pos_list['name']
#        prices = {}
#        cost_weekly = 0
#        income_weekly = 0
#        m3_weekly = 0
#        poses = []
#        for pos in pos_list['pos']:
#            pos_weekly_cost = 0
#            pos_weekly_value = 0
#            m3 = 0
#            for fuel in pos.fuel.all():
#                if fuel.purpose == 'Reinforce':
#                    continue
#                if not prices.has_key(fuel.type.id):
#                    prices[fuel.type.id] = profile.get_buy_price(fuel.type)
#                pos_weekly_cost += fuel.consumption * 24 * 7 * prices[fuel.type.id]
#
#            for type, quantity in pos.reacted_quantities():
#                if not prices.has_key(type.id):
#                    prices[type.id] = profile.get_sell_price(type)
#                pos_weekly_value += prices[type.id] * 24 * 7 * quantity
#                m3 += type.volume * 24 * 7 * quantity
#            profit = pos_weekly_value - pos_weekly_cost
#            poses.append({'pos':pos,
#                          'cost':pos_weekly_cost,
#                          'value':pos_weekly_value,
#                          'profit':profit,
#                          'm3':m3,
#                          'is_profitable': profit > 0,
#                          })
#            cost_weekly += pos_weekly_cost
#            income_weekly += pos_weekly_value
#            m3_weekly += m3
#        corps.append({'name':corp_name,
#                      'cost_weekly':cost_weekly,
#                      'income_weekly':income_weekly,
#                      'profit_weekly': abs(income_weekly - cost_weekly),
#                      'm3_weekly':m3_weekly,
#                      'poses':poses,
#                      'profitable': (income_weekly > cost_weekly),
#                      })
#
#    d['fuels'] = corps
#    return render_to_response('pos_profits.html', d, context_instance=RequestContext(request))

class ReactionForm(forms.Form):
    q = Q(group__name__in=['Moon Materials', 'Intermediate Materials',
                           'Composite'])
    q = q & Q(published=True)
    reactions = [('', 'None')] + [(x.slug, x.name) for x in Item.objects.filter(q)]
    reactions.sort(key=lambda x:x[0])

    r1 = forms.ChoiceField(label='1', choices=reactions, required=False)
    r2 = forms.ChoiceField(label='2', choices=reactions, required=False)
    r3 = forms.ChoiceField(label='3', choices=reactions, required=False)
    r4 = forms.ChoiceField(label='4', choices=reactions, required=False)
    r5 = forms.ChoiceField(label='5', choices=reactions, required=False)
    r6 = forms.ChoiceField(label='6', choices=reactions, required=False)
    r7 = forms.ChoiceField(label='7', choices=reactions, required=False)
    r8 = forms.ChoiceField(label='8', choices=reactions, required=False)
    r9 = forms.ChoiceField(label='9', choices=reactions, required=False)
    r10 = forms.ChoiceField(label='10', choices=reactions, required=False)

@login_required
def setup_reactions(request, station_id):
    pos = get_object_or_404(PlayerStation, id=station_id)
    profile = request.user.get_profile()
    pos_allowed(profile, pos)

    d = {}
    d['pos'] = pos
    d['nav'] = [pos_nav, pos_profit_nav, pos]

    if request.method == 'POST':
        form = ReactionForm(request.POST)
        if not form.is_valid():
            render_to_response(template, d,
                              context_instance=RequestContext(request))
        else:
            pos.reactions.all().delete()
            for slug in form.cleaned_data.values():
                if slug == '':
                    continue
                type = Item.objects.get(slug=slug)
                pos.reactions.create(station=pos, type=type).save()
            return HttpResponseRedirect( pos.get_absolute_url() )
    else:
        index = 1
        reactions = {}
        for r in pos.reactions.all():
            key = "r%d" % index
            reactions[key] = r.type.slug
            index += 1

        d['form'] = ReactionForm(reactions)
        return render_to_response('edit_reactions.html', d,
                                  context_instance=RequestContext(request))


@login_required
def refuel(request, station_id, days=DEFAULT_DAYS):
    pos = get_object_or_404(PlayerStation, id=station_id)
    profile = request.user.get_profile()
    pos_allowed(profile, pos)
    if request.method == 'POST':
        for fuel in pos.fuel.all():
            id = str(fuel.type.id)
            print "id: %s" % id
            if id in request.POST:
                fuel.quantity = int(request.POST[id])
                print "new qty: %d" % fuel.quantity
                fuel.save()
        pos.state_time = datetime.utcnow()
        pos.update_fueled_until()
        pos.save()
        return HttpResponseRedirect( pos.get_absolute_url() )
    else:
        d = {}
        d['nav'] = [pos_nav, pos, {'name':'Manual Refueling'}]
        d['pos'] = pos
        d['fuel'] = [x for x in pos.fuel.all()]
        d['fuel'].sort(key=lambda x:x.type.name)
        d['days'] = days
        return render_to_response('refuel.html', d,
                                  context_instance=RequestContext(request))

@login_required
def monkey_list(request):
    d = {}
    d['nav'] = [pos_nav, pos_monkey_nav]

    corporations = []
    d['corporations'] = corporations

    profile = request.user.get_profile()
    for character in profile.characters.all():
        if not (character.is_director or character.is_pos_monkey):
            continue
        corporations.append(character.corporation)


    return render_to_response('roles.html', d,
                                  context_instance=RequestContext(request))

def is_director_of(me, you):
    '''Security check to make sure that profile 'me' has a director role that would allow
    them to alter user 'you'. The 'you' involved may be a character, or a pos. (Or anything
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
def owner_set(request, station_id, character_id):
    pos = get_object_or_404(PlayerStation, id=station_id)
    profile = request.user.get_profile()
    pos_allowed(request, pos)
    if character_id == '0':
        pos.owner = None
    else:
        character = get_object_or_404(Character, id=character_id)
        #is_director_of_or_404(request.user, character)
        if character.corporation != pos.corporation:
            raise Http404
        pos.owner = character
    pos.save()
    return HttpResponseRedirect( '/pos/%s/fuel/' % pos.id )

@login_required
def owner(request, station_id):
    pos = get_object_or_404(PlayerStation, id=station_id)
    profile = request.user.get_profile()
    pos_allowed(request, pos)

    d = {}
    d['pos'] = pos
    #d['characters'] = [{
    #    'character':c,
    #    'director':c.is_director,
    #    'monkey':c.is_pos_monkey
    #}]


    d['nav'] = [pos_nav, pos, {'name':'Owner'}]
    return render_to_response('owner.html', d,
                              context_instance=RequestContext(request))
