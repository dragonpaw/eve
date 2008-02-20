#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'
from sys import exit

from exceptions import Exception
from django.template.defaultfilters import slugify
from eve.ccp.models import MarketGroup

test = {}
failed = False

for g in MarketGroup.objects.all():
    if g.name in ('Small', 'Medium', 'Large', 'Micro', 'Extra Large', 'Capital', 'Heavy',
                  'Amarr', 'Gallente', 'Minmatar', 'Caldari', 'ORE', 'Serpentis', 'Guristas',):
        slug = "%s-%s" % (g.parent, g.name)
    else:
        slug = g.name
    
    parent = g
    while parent.parent:
        parent = parent.parent
    if parent.name == 'Blueprints':
        slug += " blueprints"
    elif parent.name == 'Skills':
        slug = 'skill ' + slug
    elif g.id == 138:
        slug = 'mining laser group'
        
    slug = slugify(slug)
    if test.has_key(slug):
        print "Failed: '%s' used by group %d and %d" % (slug, test[slug], g.id)
        failed = True
    else:
        test[slug] = g.id
    
    g.slug = slug
    g.save()
    
    #print "%s=%s" % (g.name, slug)

if failed:
    print "FAILED!"         
    