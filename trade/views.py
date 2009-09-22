from django import forms
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from collections import defaultdict

from decimal import Decimal
import re
import logging

from eve.lib.formatting import NavigationElement
from eve.lib.jinja import render_to_response
from eve.ccp.models import Item, Material
from eve.trade.models import Transaction, BlueprintOwned, MarketIndex, MarketIndexValue, JournalEntry, get_buy_price, get_sell_price

index_nav = NavigationElement(
    "Indexes", "/trade/indexes/", '25_08', "Where the prices come from."
)
blueprint_nav = NavigationElement(
    "Blueprints Owned", "/trade/blueprints/", '09_15',
    "The blueprints you can make things with."
)
transaction_nav = NavigationElement(
    "Transactions", "/trade/transactions/", '64_14',
    "Everything you've bought and sold."
)
salvage_nav = NavigationElement(
    'Salvage', '/trade/salvage/', '69_11',
    'Calculate what rigs you can make with that pile of salvage filling your hangar.'
)

# Cache this crap!
salvage_mat_q = (
    Q(item__group__slug__startswith='rig-')
    & Q(item__published=True)
    & Q(material__group__name='Salvaged Materials')
    & Q(activity__name='Manufacturing')
)
SALVAGE_NEEDED = defaultdict(dict)
SALVAGE_MATS = set()
SALVAGE_TECH_LEVEL = defaultdict(set)
for m in Material.objects.filter(salvage_mat_q).select_related('item', 'material'):
    makes = m.item.blueprint_makes
    SALVAGE_NEEDED[makes][m.material] = m.quantity
    SALVAGE_MATS.add(m.material)
    SALVAGE_TECH_LEVEL[makes.tech_level].add(m.material)
# Precalculate the short name, and the size name.
for rig in SALVAGE_NEEDED.keys():
    rig.size = rig.attribute_by_name('rigSize').display_value
    rig.short_name = rig.name.replace('Large ','').replace('Medium ','').replace('Small ','')
# Convert it back from sets to lists, and sort them.
for tl in SALVAGE_TECH_LEVEL:
    SALVAGE_TECH_LEVEL[tl] = list(SALVAGE_TECH_LEVEL[tl])
    SALVAGE_TECH_LEVEL[tl].sort(key=lambda x: x.name)

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

    # Pull the first transaction.
    # (Yes, there can be dupes. Buy something from yourself.)
    try:
        transaction = transaction[0]
    except (JournalEntry.DoesNotExist, Transaction.DoesNotExist):
        raise Http404

    return render_to_response(template, {
        'nav': ( transaction_nav, transaction ),
        'transaction': transaction,
    }, request)

@login_required
def blueprint_list(request):
    d = {}
    d['nav'] = [ blueprint_nav ]
    d['user'] = request.user
    d['blueprints'] = request.user.get_profile().blueprints.select_related().order_by('blueprint__name')

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
        return render_to_response('blueprint_edit.html', d, request)
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
    d['values'] = index.items.select_related().order_by('item__name')

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
    d['nav'] = [salvage_nav]
    d['SALVAGE_MATS'] = SALVAGE_MATS
    d['SALVAGE_TECH_LEVEL'] = SALVAGE_TECH_LEVEL
    #log = logging.getLogger('eve.trade.views.salvage')

    if request.method != 'POST':
        return render_to_response('salvage.html', d, request)

    assert(request.method=='POST')

    if request.user.is_anonymous() is False:
        profile = request.user.get_profile()
    else:
        profile = None

    bits = defaultdict(int)
    d['bits'] = bits
    d['nav'].append({'name':'Rigs you can make'})

    for mat in SALVAGE_MATS:
        try:
            bits[mat] = int( request.POST[unicode(mat.id)] )
        except ValueError:
            bits[mat] = 0

    rigs = defaultdict(dict)
    for rig in SALVAGE_NEEDED:
        can_make = min( (bits[mat] / SALVAGE_NEEDED[rig][mat] for mat in SALVAGE_NEEDED[rig] ) )
        if can_make:
            rigs[rig.short_name][rig.size] = {'item': rig, 'quantity': can_make }
    d['rigs'] = rigs

    #objects = []
    #d['objects'] = objects
    #for rig in rigs.keys():
    #    objects.append({
    #                    'item':item,
    #                    'quantity':rigs[rig],
    #                    'buy':get_buy_price(item, profile=profile),
    #                    'sell':get_sell_price(item, profile=profile),
    #                    })
    #objects.sort(key=lambda x:x['item'].name)
    return render_to_response('salvage_result.html', d, request)
