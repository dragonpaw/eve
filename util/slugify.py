#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from exceptions import Exception
from django.template.defaultfilters import slugify

from eve.ccp.models import MarketGroup, Item, Region, Alliance

def main():
    slugify_item()
    slugify_marketgroup()
    slugify_region()
    slugify_alliance()

def slugify_region():
    for r in Region.objects.all():
        r.slug = slugify(r.name)
        r.save()

def slugify_alliance():
    for a in Alliance.objects.all():
        # It's in the save handler.
        a.save()

def slugify_item():
    for item in Item.objects.all():
        try:
            item.slug = slugify(item.name)
            item.save()
        except Exception, e:
            print "Unable to slug: %s: '%s'" % (item.name, e)
            

def slugify_marketgroup():
    test = {}
    
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
        else:
            test[slug] = g.id
        
        g.slug = slug
        g.save()

main()