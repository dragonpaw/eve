from django import forms
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from eve.lib.jinja import render_to_response

import re
import logging

from decimal import Decimal
#from datetime import date

from eve.trade.models import Transaction, BlueprintOwned, MarketIndex, MarketIndexValue, JournalEntry
from eve.ccp.models import Item, Material
from eve.lib.formatting import make_nav

index_nav = make_nav("Indexes", "/trade/indexes/", '25_08',
                      note="Where the prices come from.")
blueprint_nav = make_nav("Blueprints Owned", "/trade/blueprints/", '09_15',
                          note="The blueprints you can make things with.")
transaction_nav = make_nav("Transactions", "/trade/transactions/", '64_14',
                            note="Everything you've bought and sold.")
salvage_nav = make_nav('Salvage', '/trade/salvage/', '69_11',
                       'Calculate what rigs you can make with that pile of salvage filling your hangar.')

# Cache this crap!
salvage_mat_q = Q(item__group__slug__startswith='rig-')
salvage_mat_q &= ~Q(material__group__category__name='Skill')
salvage_mat_q &= Q(activity__name='Manufacturing')
SALVAGE_MATS = {}
for m in Material.objects.filter(salvage_mat_q).select_related('item'):
    if m.item not in SALVAGE_MATS:
        SALVAGE_MATS[m.item] = []
    SALVAGE_MATS[m.item].append((m.material_id, m.quantity))

@login_required
def transactions(request):
    profile = request.user.get_profile()

    t = profile.trade_transactions(days=14).select_related('item', 'character', 'station__solarsystem')
    j = profile.journal_entries(days=14, is_boring=False).select_related('character','type')
    t = list(t) + list(j)
    t.sort(key=lambda x:x.time, reverse=True)

    return render_to_response('transactions.html', {
        'nav': (transaction_nav,),
        'user': request.user,
        'transactions': t,
    }, request)

#@login_required
#def journal_detail(request, id=None):
#    profile = request.user.get_profile()
#    transaction = JournalEntry.objects.filter(transaction_id=id, character__user=profile)
#    if transaction.count() == 0:
#        raise Http404
#    else:
#        transaction = transaction[0]
#
#    return render_to_response('journal_detail.html', {
#        'nav': ( transaction_nav, transaction ),
#        'transaction': transaction,
#    }, request)

@login_required
def transaction_detail(request, type, id=None):
    profile = request.user.get_profile()
    if type == 'transaction':
        transaction = Transaction.objects.filter(transaction_id=id, character__user=profile).select_related()
        template = 'transaction_detail.html'
    else:
        transaction = JournalEntry.objects.filter(transaction_id=id, character__user=profile).select_related()
        template = 'journal_detail.html'
    if transaction.count() == 0:
        raise Http404
    else:
        transaction = transaction[0]

    return render_to_response(template, {
        'nav': ( transaction_nav, transaction ),
        'transaction': transaction,
    }, request)

@login_required
def blueprint_list(request):
    d = {}
    d['nav'] = [ blueprint_nav ]
    d['user'] = request.user
    d['blueprints'] = request.user.get_profile().blueprints.select_related().order_by('ccp_item.name')

    return render_to_response('blueprint_list.html', d, request)

class BlueprintOwnedForm(forms.ModelForm):
    class Meta:
        model = BlueprintOwned
        exclude = ('user','blueprint',)

@login_required
def blueprint_edit(request, slug):
    d = {}
    form = None
    d['item'] = item = get_object_or_404(Item, slug=slug)
    d['nav'] = [ blueprint_nav, {'name':'Add'} ]
    profile = request.user.get_profile()
    blueprint, _ = BlueprintOwned.objects.get_or_create(blueprint=item, user=profile)

    if request.method == 'GET':
        form = BlueprintOwnedForm(instance=blueprint)
        d['form'] = form
        return render_to_response('blueprint_edit.html', d, request)

    assert(request.method == 'POST')

    if request.POST.has_key('delete'):
        blueprint.delete()
        return HttpResponseRedirect(blueprint_nav.get_absolute_url() )

    form = BlueprintOwnedForm(request.POST, instance=blueprint)
    d['form'] = form

    if form.is_valid() is False:
        return render_to_response(template, d, request)
    else:
        form.save()
        return HttpResponseRedirect(blueprint_nav.get_absolute_url() )

@login_required
def blueprint_add(request):
    i = get_object_or_404(Item, pk=request.POST['id'])
    bo = BlueprintOwned(user=request.user, blueprint = i, original=True)
    bo.save()
    return HttpResponseRedirect('/trade/blueprints/')

def market_index_list(request):
    if request.user.is_anonymous():
        q = Q(user__isnull=True)
    else:
        q = Q(user__isnull=True) | Q(user=request.user.get_profile())
    d = {}
    d['nav'] = [ index_nav ]

    d['indexes'] = MarketIndex.objects.filter(q).select_related().order_by('-trade_marketindex.priority')


    return render_to_response('indexes.html', d, request)

def market_index_detail(request, name):
    if request.user.is_anonymous() == False:
        profile = request.user.get_profile()
        q = (Q(user__isnull=True) | Q(user=profile)) & Q(name=name)
    else:
        q = Q(user__isnull=True) & Q(name=name)

    index = get_object_or_404(MarketIndex, q)

    d = {}
    d['nav'] = [ index_nav, index ]
    d['index'] = index
    d['values'] = index.items.select_related().order_by('ccp_item.name')

    return render_to_response('index_detail.html', d, request)

class FixedPriceForm(forms.Form):
    buy_price = forms.DecimalField(label='Buy Price', initial=0)
    sell_price = forms.DecimalField(label='Sell Price', initial=0)

@login_required
def fixed_price_update(request, id):
    profile = request.user.get_profile()
    item = get_object_or_404(Item, pk=id)
    index = MarketIndex.objects.get(name='Custom Prices', user=profile)

    d = {}
    d['nav'] = [index_nav, item,  {'name':'Set Fixed'}]
    d['item'] = item
    d['buy'] = profile.get_buy_price(item)
    d['sell'] = profile.get_sell_price(item)

    if request.method == 'POST':
        form = FixedPriceForm(request.POST)
        if form.is_valid():
            buy_price = Decimal(form.cleaned_data['buy_price'])
            sell_price = Decimal(form.cleaned_data['sell_price'])
            index.set_value(item, buy=buy_price, sell=sell_price)
            return HttpResponseRedirect( index.get_absolute_url() )
        else:
            d['form'] = form
    else:
        buy_price = 0
        sell_price = 0
        try:
            item_index = index.items.get(item=item)
            buy_price = item_index.buy
            sell_price = item_index.sell
        except MarketIndexValue.DoesNotExist:
            pass

        d['form'] = FixedPriceForm(initial={'buy_price':buy_price,'sell_price':sell_price})

    return render_to_response('index_update.html', d, request)


def salvage(request):
    d = {}
    d['items'] = Item.objects.filter(group__name='Salvaged Materials').select_related('graphic', 'group')
    d['nav'] = [salvage_nav]
    log = logging.getLogger('eve.trade.views.salvage')

    if request.method != 'POST':
        return render_to_response('salvage.html', d, request)

    assert(request.method=='POST')

    if request.user.is_anonymous() is False:
        profile = request.user.get_profile()
    else:
        profile = None

    bits = {}
    d['bits'] = bits
    d['nav'].append({'name':'Rigs you can make'})

    # Make a lookup table out of the salvage available.
    digits = re.compile(r'\d+')

    for key in request.POST.keys():
        id = int(key)
        if not id > 0:
            continue

        match = digits.search(request.POST[key])
        if not match:
            bits[id] = 0
        else:
            bits[id] = int(match.group(0))

    rigs = {}
    for rig in SALVAGE_MATS:
        log.debug('Trying: %s' % rig.name)
        can_make = None
        for id, quantity in SALVAGE_MATS[rig]:
            log.debug('Material ID: %d, Qty: %d' % (id, quantity))
            if id not in bits:
                can_make = 0
            elif can_make is None:
                can_make = int(bits[id] / quantity)
            else:
                can_make = min(bits[id] / quantity, can_make)

            # If we can make 0, it's not going to get higher.
            if can_make == 0:
                break
        if can_make > 0:
            rigs[rig] = can_make
            log.debug('Can make: %s' % rig.name)

    objects = []
    d['objects'] = objects
    for rig in rigs.keys():
        item = rig.blueprint_makes # We're actually storing the BP ID, not the item.
        if profile:
            buy = profile.get_buy_price(item)
            sell =  profile.get_sell_price(item)
        else:
            buy = sell = None
        objects.append({
                        'item':item,
                        'quantity':rigs[rig],
                        'buy':buy,
                        'sell':sell,
                        })
    objects.sort(key=lambda x:x['item'].name)
    return render_to_response('item_list.html', d, request)
