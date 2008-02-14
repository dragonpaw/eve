# $Id$
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.mining.models import MiningOp
from eve.util.formatting import make_nav
from django.contrib.auth.decorators import login_required

mining_op_nav = make_nav("Mining Operations", "/mining/ops/", '40_14')

def op_list(request):
    d = {}
    d['nav'] = [mining_op_nav]
    d['objects'] = MiningOp.objects.all() 
    
    return render_to_response('mining_op_list.html', d, context_instance=RequestContext(request))


@login_required
def op_detail(request, id):
    op = get_object_or_404(MiningOp, id=id)
    
    d = {}
    d['nav'] = [mining_op_nav, op]
    d['op'] = op
    
    profile = request.user.get_profile()
    
    total_value = 0.0
    minerals = {}
    for m in op.minerals.all():
        sell = profile.get_sell_price(m.type)
        minerals[m.type.id] = {'quantity':m.quantity, 'type':m.type, 'sell':sell}
        total_value += sell * m.quantity
        
    miners = {}
    for miner in op.miners.all():
        id = miner.name
        if not miners.has_key(id):
            miners[id] = {'miner':miner, 'percent':0.0, 'hours':0.0,}
        # One miner can be listed multiple times in the DB.
        miners[id]['percent'] += miner.percent()
        miners[id]['hours'] += miner.hours()
        miners[id]['isk'] = total_value * miners[id]['percent']
        miners[id]['percent_display'] = "%0.2f" % (miners[id]['percent'] * 100) 
    
    ore_per_person = []
    for miner in miners.keys():
        temp = []
        profit = 0
        for mineral in minerals.keys():
            quantity = int(minerals[mineral]['quantity'] * miners[miner]['percent'])
            isk = quantity * minerals[mineral]['sell']
            profit += isk
            temp.append({'type' :minerals[mineral]['type'],
                         'sell': isk,
                         'quantity':quantity })
        temp.sort(key=lambda x:x['type'].name)
        ore_per_person.append({'miner':miners[miner]['miner'],'shares':temp, 'sell':profit})
    
#    total_value = 0
#    for miner in ore_per_person.values():
#        value = 0
#        for ore in miner['shares'].values():
#            ore['value'] = ore['type'].value * ore['share']
#            value += ore['value']
#            ore['pct'] = (ore['share'] / minerals[ore['type'].id]['quantity']) * 100.0
#        total_value += value
#        miner['total_value'] = value

    d['minerals'] = minerals.values()
    d['minerals'].sort(key=lambda x:x['type'].name)
    d['miners'] = miners.values()
    d['miners'].sort(key=lambda x:x['miner'].name)
    d['ore_per_person'] = ore_per_person
    d['ore_per_person'].sort(key=lambda x:x['miner'].name)
    d['total_value'] = total_value
    
    return render_to_response('mining_op_detail.html', d, context_instance=RequestContext(request))
