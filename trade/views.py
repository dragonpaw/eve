from django import newforms as forms
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.trade.models import Transaction, BlueprintOwned, MarketIndex
from eve.ccp.models import Item
from eve.util.formatting import make_nav

index_nav = make_nav("Indexes", "/trade/indexes/", '25_08')
blueprint_nav = make_nav("Blueprints Owned", "/trade/blueprints/", '09_15')
transaction_nav = make_nav("Transactions", "/trade/transactions/", '64_14')

def transactions(request):
    d = {}
    d['nav'] = [transaction_nav]
    d['user'] = request.user
    
    t = request.user.get_profile().trade_transactions(days=14)
    t = t.select_related().order_by('-time')
    #t = t.order_by('ccp_category.categoryname','ccp_group.groupname','ccp_item.name')
    
    d['transactions'] = t
    
    return render_to_response('trade_transactions.html', d)

def transaction_detail(request, id=None):
    transaction = get_object_or_404(Transaction, transaction_id=id)
    # FIXME: ADD SECURITY!!!!
    
    d = {}
    d['nav'] = [ transaction_nav, transaction]
    d['transaction'] = transaction
    
    return render_to_response('trade_transaction_detail.html', d)

def blueprint_list(request):
    d = {}
    d['nav'] = [ blueprint_nav ]
    d['user'] = request.user
    d['blueprints'] = request.user.get_profile().blueprints.select_related().order_by('ccp_item.name')
    
    return render_to_response('trade_blueprint_list.html', d)

class BlueprintOwnedFormEdit(forms.Form):
    me = forms.IntegerField(label='Material Efficiency', initial=0)
    pe = forms.IntegerField(label='Production Efficiency', initial=0)
    original = forms.BooleanField(label='Original?', initial=True)

class BlueprintOwnedFormNew(forms.Form):
    set = Item.objects.filter(group__category__name__exact='Blueprint')
    set = set.order_by('name',)
    item = forms.ModelChoiceField(queryset=set)
    me = forms.IntegerField(label='Material Efficiency', initial=0)
    pe = forms.IntegerField(label='Production Efficiency', initial=0)
    original = forms.BooleanField(label='Original?', initial=True)

def blueprint_edit(request, item_id=None):
    d = {}
    item = None
    # FIXME: Either get a Django version where BooleanField works, or change 'original' to select

    if request.method == 'POST':
        form = BlueprintOwnedFormNew(request.POST)
        if form.is_valid():
            id = form.cleaned_data['item']
            me = form.cleaned_data['me']
            pe = form.cleaned_data['pe']
            original = form.cleaned_data['original']
            try:
                bpo = BlueprintOwned.objects.get(blueprint=id, user=request.user)
                bpo.me = me
                bpo.pe = pe
                bpo.original = original
                bpo.save()
            except BlueprintOwned.DoesNotExist:
                BlueprintOwned(blueprint=id, user=request.user, pe=pe, me=me, original=original).save()
            return HttpResponseRedirect('/trade/blueprints/')
    else:
        if item_id is None:
            form = BlueprintOwnedFormNew()
        else:
            try:
                bpo = BlueprintOwned.objects.get(blueprint=item_id, user=request.user)
                form = BlueprintOwnedFormEdit(initial={'me': bpo.me, 'pe': bpo.pe})
                item = bpo.blueprint
            except BlueprintOwned.DoesNotExist:
                form = BlueprintOwnedFormEdit(initial={'item': item_id})
                item = Item.objects.get(pk=item_id)
        
    d['form'] = form
    d['item'] = item
    d['title'] = "Add Blueprint"
    d['nav'] = [ blueprint_nav, {'name':'Add'} ]
    return render_to_response('trade_blueprint_edit.html', d)

                                         
def blueprint_add(request):
    # FIXME: Require a login!
    i = get_object_or_404(Item, pk=request.POST['id'])
    bo = BlueprintOwned(user=request.user, blueprint = i, original=True)
    bo.save()
    return HttpResponseRedirect( reverse('eve.trade.views.blueprints_owned') )

def market_index_list(request):
    d = {}
    d['nav'] = [ index_nav ]
    d['indexes'] = MarketIndex.objects.all()
    
    return render_to_response('trade_indexes.html', d, context_instance=RequestContext(request))

def market_index_detail(request, id):
    index = get_object_or_404(MarketIndex, pk=id)
    
    d = {}
    d['nav'] = [ index_nav, index ]
    d['index'] = index
    d['values'] = index.items.select_related().order_by('ccp_item.name')
    
    return render_to_response('trade_index_detail.html', d, context_instance=RequestContext(request))
    
