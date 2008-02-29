#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.ccp.models import Reaction

# CCP farked up the DB for reactions.
for r in Reaction.objects.all():
    if r.item.group.name not in (
                                 'Moon Materials', 
                                 'Intermediate Materials',
                                 'Composite'
                                ):
        continue
    
    starting = r.quantity
    
    # All intermediate products are 1 + 1 = 2
    if r.item.group.name == 'Intermediate Materials':
        if r.input:
            r.quantity = 100
        else:
            r.quantity = 200
    elif r.item.group.name == 'Moon Materials':
        r.quantity = 100
    elif r.item.group.name == 'Composite':
        if r.input:
            r.quantity = 100
        else:
            r.quantity = r.item.attribute_by_name('moonMiningAmount').value

    print "Input: %-30s, Old: %5d, New: %5d" % (r.reaction,
                                                starting,
                                                r.quantity
                                                )
    r.save()