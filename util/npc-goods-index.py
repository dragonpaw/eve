#!/usr/bin/env python
# $Id$

import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.ccp.models import Item
from eve.trade.models import MarketIndex

def main():
    npc, created = MarketIndex.objects.get_or_create(name='Jita Prices')
    npc.note = 'Pseudo-fixed prices updated by the Widget Admins'
    npc.priority = 100
    npc.save()

    update(npc, 'Oxygen', 109.25)
    update(npc, 'Robotics', 6880)
    update(npc, 'Enriched Uranium', 5300)
    update(npc, 'Coolant', 1150)
    update(npc, 'Mechanical Parts', 600)

def update(index, item, value):
    index.set_value(Item.objects.get(name=item), buy=value, sell=value)

main()        
sys.exit(0)
