# $Id$
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from eve.mining.models import MiningOp
from eve.util.formatting import make_nav

mining_op_nav = make_nav("Mining Operations", "/mining/ops/", '40_14')

def op_list(request):
    d = {}
    d['nav'] = [mining_op_nav]
    d['objects'] = MiningOp.objects.all() 
    
    return render_to_response('mining_op_list.html', d, context_instance=RequestContext(request))


def op_detail(request, id):
    op = get_object_or_404(MiningOp, id=id)
    
    d = {}
    d['nav'] = [mining_op_nav, op]
    d['op'] = op
    
    ore_per_person = {}

    ores = {}
    for phase in op.phases.all():
        for ore in phase.ores.all():
            if not ores.has_key(ore.type.id):
                ores[ore.type.id] = {'quantity':0, 'type':ore.type, 'value':ore.type.value}
            ores[ore.type.id]['quantity'] += ore.quantity
        for person in phase.miners.all():
            miner = person.user.id
            if not ore_per_person.has_key(miner):
                ore_per_person[miner] = {'miner':person, 'shares':{} }
            for ore in phase.ores.all():
                share = ore.quantity * (person.share/phase.shares)
                if ore_per_person[miner]['shares'].has_key(ore.type.id):
                    ore_per_person[miner]['shares'][ore.type.id]['share'] += share
                else:
                    ore_per_person[miner]['shares'][ore.type.id] = {'type':ore.type, 'share':share }
    
    total_value = 0
    for miner in ore_per_person.values():
        value = 0
        for ore in miner['shares'].values():
            ore['value'] = ore['type'].value * ore['share']
            value += ore['value']
            ore['pct'] = (ore['share'] / ores[ore['type'].id]['quantity']) * 100.0
        total_value += value
        miner['total_value'] = value
    
    d['ores'] = ores
    d['ore_per_person'] = ore_per_person
    d['total_value'] = total_value
    
    return render_to_response('mining_op_detail.html', d, context_instance=RequestContext(request))
