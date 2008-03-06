from django import newforms as forms
from django.newforms import ModelForm
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db.models.query import Q, QNot

import re

from decimal import Decimal
#from datetime import date

from eve.trade.models import Transaction, BlueprintOwned, MarketIndex, MarketIndexValue, JournalEntry
from eve.ccp.models import Item
from eve.lib.formatting import make_nav

index_nav = make_nav("Indexes", "/trade/indexes/", '25_08',
                      note="Where the prices come from.")
blueprint_nav = make_nav("Blueprints Owned", "/trade/blueprints/", '09_15',
                          note="The blueprints you can make things with.")
transaction_nav = make_nav("Transactions", "/trade/transactions/", '64_14',
                            note="Everything you've bought and sold.")
salvage_nav = make_nav('Salvage', '/trade/salvage/', '69_11', 
                       'Calculate what rigs you can make with that pile of salvage filling your hangar.')

@login_required
def transactions(request):
    d = {}
    d['nav'] = [transaction_nav]
    d['user'] = request.user
    
    profile = request.user.get_profile()
    
    t = profile.trade_transactions(days=14)
    j = profile.journal_entries(days=14, is_boring=False)
    t = list(t) + list(j)
    t.sort(key=lambda x:x.time, reverse=True)
    
    d['transactions'] = t
    
    return render_to_response('trade_transactions.html', d)

@login_required
def journal_detail(request, id=None):
    profile = request.user.get_profile()
    transaction = JournalEntry.objects.filter(transaction_id=id, character__user=profile)
    if transaction.count() == 0:
        raise Http404
    else:
        transaction = transaction[0]

    d = {}
    d['nav'] = [ transaction_nav, transaction ]
    d['transaction'] = transaction
    
    return render_to_response('trade_journal_detail.html', d)

@login_required
def transaction_detail(request, id=None):
    profile = request.user.get_profile()
    transaction = Transaction.objects.filter(transaction_id=id, character__user=profile)
    if transaction.count() == 0:
        raise Http404
    else:
        transaction = transaction[0]
    
    d = {}
    d['nav'] = [ transaction_nav, transaction]
    d['transaction'] = transaction
    
    return render_to_response('trade_transaction_detail.html', d)

@login_required
def blueprint_list(request):
    d = {}
    d['nav'] = [ blueprint_nav ]
    d['user'] = request.user
    d['blueprints'] = request.user.get_profile().blueprints.select_related().order_by('ccp_item.name')
    
    return render_to_response('trade_blueprint_list.html', d)

class BlueprintOwnedForm(ModelForm):
    class Meta:
        model = BlueprintOwned
        exclude = ('user','blueprint',)

@login_required
def blueprint_edit(request, slug):
    d = {}
    form = None
    d['item'] = item = get_object_or_404(Item, slug=slug)
    d['nav'] = [ blueprint_nav, {'name':'Add'} ]
    template = 'trade_blueprint_edit.html'
    profile = request.user.get_profile()
    blueprint, _ = BlueprintOwned.objects.get_or_create(blueprint=item, user=profile)
    
    if request.method == 'GET':
        form = BlueprintOwnedForm(instance=blueprint)
        d['form'] = form
        return render_to_response(template, d)
    
    assert(request.method == 'POST')

    if request.POST.has_key('delete'):
        blueprint.delete()
        return HttpResponseRedirect(blueprint_nav.get_absolute_url() )

    form = BlueprintOwnedForm(request.POST, instance=blueprint)
    d['form'] = form

    if form.is_valid() is False:
        return render_to_response(template, d)
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
    
    
    return render_to_response('trade_indexes.html', d, 
                              context_instance=RequestContext(request))

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
    
    return render_to_response('trade_index_detail.html', d, 
                              context_instance=RequestContext(request))

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
    
    return render_to_response('trade_index_update.html', d, 
                              context_instance=RequestContext(request))


def salvage(request):
    d = {}
    d['items'] = Item.objects.filter(group__name='Salvaged Materials')
    d['nav'] = [salvage_nav]
    
    if request.method != 'POST':
        return render_to_response('trade_salvage.html', d, 
                                  context_instance=RequestContext(request))

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
        
    q = Q(material__group__name='Salvaged Materials')
    rigs = {}
    for rig in Item.objects.filter(marketgroup__parent__id='955'):
        for m in rig.materials(activity='Manufacturing').filter(q):
            id = m.material.id
            can_make = int(bits[id] / m.quantity)
            if rigs.has_key(rig.id):
                rigs[rig.id]['qty'] = min(rigs[rig.id]['qty'], can_make)
            else:
                rigs[rig.id] = { 'qty': can_make, 'item': rig }
                
            # If we can make 0, it's not going to get higher.
            if rigs[rig.id]['qty'] == 0:
                break
            
    objects = []
    d['objects'] = objects
    for id in rigs.keys():
        if rigs[id]['qty'] == 0:
            continue
        if profile:
            buy = profile.get_buy_price(rigs[id]['item'])
            sell =  profile.get_sell_price(rigs[id]['item'])
        else:
            buy = sell = None
        objects.append({
                        'item':rigs[id]['item'], 
                        'quantity':rigs[id]['qty'],
                        'buy':buy,
                        'sell':sell,
                        })
    objects.sort(key=lambda x:x['item'].name)
    return render_to_response('ccp_item_list.html', d, 
                              context_instance=RequestContext(request))