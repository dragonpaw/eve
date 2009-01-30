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
pos_consumption_nav = make_nav('Consumption', '/pos/consumption/', '10_07',
                               'Consumption and shopping list for all of your POSes')
pos_profit_nav = make_nav('Profits', '/pos/profit/', '06_03',
                          'Profits and costs for all of your POSes')
pos_monkey_nav = make_nav('POS Helpers', '/pos/helpers/','02_16',
                          'Check who is able to see POS status.')

REFUEL_NAV = make_nav('Update Fuel Quantities', '/pos/%d/refuel/', '10_07',
                      'The EVE Widget automatically refreshes all POS data every 6 hours. '
                      + 'Click here to update quantities if you have just refueled the tower and do not wish '
                      + 'to wait.')
REACTION_NAV = make_nav('Configure Reactions', '/pos/%d/reactions/', '50_04',
                        'Update what mining/reactions this POS is running.')
PROFIT_NAV = make_nav('View Profit & Loss', '/pos/%d/profit/', '06_03',
                      'View the profit/loss for this POS.')

DEFAULT_DAYS = 30

def get_poses(request, profile=None):
    if profile is None:
        profile = request.user.get_profile()

    corps = {}
    for c in profile.characters.all():
        # Workaround CCP bug as of 2008-09-23. Some corps not queryable by members.
        #try:
        #    c.corporation
        #except Corporation.DoesNotExist:
        #    continue

        poses = []
        for pos in c.corporation.pos.all():
            if pos_allowed(pos, c):
                poses.append(pos)

        if len(poses) > 0:
            poses.sort(key=lambda x:"%s/%s/%03d/%03d" % (
                x.owner,
                x.solarsystem.name,
                x.moon.celestialindex,
                x.moon.orbitindex)
            )
            corps[c.corporation.name] = {
                'name':c.corporation.name,
                'pos':poses,
            }


    return corps.values()

def pos_allowed(pos, character):
    if pos.corporation_id == character.corporation_id:
        if character.is_director:
            return True
        elif character.is_pos_monkey:
            return True
        elif pos.owner == character:
            return True
    return False

def check_rights(request, pos, profile=None):
    if profile is None:
        profile = request.user.get_profile()

    for c in profile.characters.all():
        if pos_allowed(pos, c):
            return True

    # Guess not.
    raise Http404

@login_required
def pos_list(request):
    d = {}
    d['nav'] = [pos_nav]

    d['poses'] = get_poses(request)
    d['inline_nav'] = [ pos_consumption_nav, pos_profit_nav, pos_monkey_nav ]

    return render_to_response('pos_list.html', d, context_instance=RequestContext(request))


@login_required
def fuel_detail(request, station_id, days=DEFAULT_DAYS):
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos)

    d = {}
    d['nav'] = [pos_nav, pos]
    d['pos'] = pos
    d['days'] = days
    d['id'] = pos.id # Used by the inline nav function.
    fuels = []
    for f in pos.fuel.all():
        fuels.append({'need':f.need(days=days),
                      'run_time':f.time_remaining,
                      'type':f.type,
                      'fuel':f})

    fuels.sort(key=lambda x:x['type'].name)
    d['fuels'] = fuels


    nav = []
    # Build of the nav options for the POS.
    for x in (REFUEL_NAV, REACTION_NAV, PROFIT_NAV):
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

    d['inline_nav'] = nav

    return render_to_response('pos_fuel_detail.html', d,
                              context_instance=RequestContext(request))

@login_required
def profit_detail(request, station_id):
    profile = request.user.get_profile()
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos, profile=profile)

    d = {}
    d['nav'] = [pos_nav, pos_profit_nav, pos]
    d['pos'] = pos
    cost = 0
    fuels = []
    for f in pos.fuel.all():
        price = profile.get_buy_price(f.type)

        weekly = 0
        if f.purpose != 'Reinforce':
            weekly = f.consumption * 24 * 7
            weekly_cost = price * weekly
            cost += weekly_cost

        fuels.append({'price':price,
                      'weekly':weekly,
                      'weekly_cost':weekly_cost,
                      'type':f.type,
                      'fuel':f})

    fuels.sort(key=lambda x:x['type'].name)
    d['weekly_cost'] = cost
    d['fuels'] = fuels
    d['reactions'] = list( pos.reactions.all() )
    d['reactions'].sort(key=lambda x:'%d-%s' % (x.is_reaction, x.type.name))

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
    d['reaction_values'] = reaction_values
    d['weekly_value'] = weekly_value
    d['weekly_total'] = abs(weekly_value - cost)
    d['profitable'] = d['weekly_total'] > 0
    nav = []
    # Build of the nav options for the POS.
    for x in (REACTION_NAV,):
        x.id = pos.id
        nav.append(x)
    d['inline_nav'] = nav

    return render_to_response('pos_profit_detail.html', d,
                              context_instance=RequestContext(request))

@login_required
def consumption(request, days=DEFAULT_DAYS):
    d = {}
    d['nav'] = [pos_nav, pos_consumption_nav]

    profile = request.user.get_profile()
    poses = get_poses(request, profile=profile)
    corps = []

    for pos_list in poses:
        corp_name = pos_list['name']
        needs = {}
        cost_weekly = 0
        cost_total = 0
        pos_costs = []
        for pos in pos_list['pos']:
            for fuel in pos.fuel.all():
                if not needs.has_key(fuel.type.id):
                    needs[fuel.type.id] = {
                                           'purpose':fuel.purpose,
                                           'quantity':0,
                                           'consumption':0,
                                           'weekly':0,
                                           'needed':0,
                                           'type':fuel.type,
                                           'buy_price':profile.get_buy_price(fuel.type)
                                          }

                f = needs[fuel.type.id]
                f['quantity'] += fuel.quantity
                f['needed'] += fuel.need(days=days)
                if fuel.purpose != 'Reinforce':
                    f['consumption'] += fuel.consumption
                    f['weekly'] += fuel.consumption * 24 * 7

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
def profit_list(request):
    d = {}
    d['nav'] = [pos_nav, pos_profit_nav]

    profile = request.user.get_profile()

    corps = []
    poses = get_poses(request)
    for pos_list in poses:
        corp_name = pos_list['name']
        prices = {}
        cost_weekly = 0
        income_weekly = 0
        m3_weekly = 0
        poses = []
        for pos in pos_list['pos']:
            pos_weekly_cost = 0
            pos_weekly_value = 0
            m3 = 0
            for fuel in pos.fuel.all():
                if fuel.purpose == 'Reinforce':
                    continue
                if not prices.has_key(fuel.type.id):
                    prices[fuel.type.id] = profile.get_buy_price(fuel.type)
                pos_weekly_cost += fuel.consumption * 24 * 7 * prices[fuel.type.id]

            for type, quantity in pos.reacted_quantities():
                if not prices.has_key(type.id):
                    prices[type.id] = profile.get_sell_price(type)
                pos_weekly_value += prices[type.id] * 24 * 7 * quantity
                m3 += type.volume * 24 * 7 * quantity
            profit = pos_weekly_value - pos_weekly_cost
            poses.append({'pos':pos,
                          'cost':pos_weekly_cost,
                          'value':pos_weekly_value,
                          'profit':profit,
                          'm3':m3,
                          'is_profitable': profit > 0,
                          })
            cost_weekly += pos_weekly_cost
            income_weekly += pos_weekly_value
            m3_weekly += m3
        corps.append({'name':corp_name,
                      'cost_weekly':cost_weekly,
                      'income_weekly':income_weekly,
                      'profit_weekly': abs(income_weekly - cost_weekly),
                      'm3_weekly':m3_weekly,
                      'poses':poses,
                      'profitable': (income_weekly > cost_weekly),
                      })

    d['fuels'] = corps
    return render_to_response('pos_profits.html', d, context_instance=RequestContext(request))

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
    template = 'pos_edit_reactions.html'
    pos = get_object_or_404(PlayerStation, id=station_id)
    check_rights(request, pos)

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
            return HttpResponseRedirect( pos.get_profit_url() )
    else:
        index = 1
        reactions = {}
        for r in pos.reactions.all():
            key = "r%d" % index
            reactions[key] = r.type.slug
            index += 1

        d['form'] = ReactionForm(reactions)
        return render_to_response(template, d,
                                  context_instance=RequestContext(request))


@login_required
def refuel(request, station_id, days=DEFAULT_DAYS):
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
        if not (character.is_director or character.is_pos_monkey):
            continue
        corporations.append(character.corporation)


    return render_to_response('pos_helpers.html', d,
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
    check_rights(request, pos)
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
    check_rights(request, pos)

    d = {}
    d['pos'] = pos
    #d['characters'] = [{
    #    'character':c,
    #    'director':c.is_director,
    #    'monkey':c.is_pos_monkey
    #}]


    d['nav'] = [pos_nav, pos, {'name':'Owner'}]
    return render_to_response('pos_owner.html', d,
                              context_instance=RequestContext(request))
