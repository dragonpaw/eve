#!/usr/bin/env python
# $Id$
from django_extensions.management.jobs import BaseJob
from django.template.defaultfilters import slugify

from eve.ccp.models import MarketGroup, Item, Region, Alliance

from exceptions import Exception

class Job(BaseJob):
    help = "Add slug values for all the CCP items."
    when = 'once'

    def execute(self):
        self.slugify_item()
        self.slugify_marketgroup()
        self.slugify_region()
        # No longer needed, as the save handler is taking care of it.
        #self.slugify_alliance()

    def slugify_region(self):
        print "Slugging the Regions."
        for r in Region.objects.all():
            if r.slug:
                continue

            r.slug = slugify(r.name)
            r.save()
            print "Slugged: %-20s %s" % (r.slug, r.name)

    def slugify_alliance(self):
        for a in Alliance.objects.all():
            # It's in the save handler.
            a.save()

    def slugify_item(self):
        print "Slugging the Items."
        for item in Item.objects.all():
            if item.slug:
                continue

            try:
                item.slug = slugify(item.name)
                item.save()
                print "Slugged: %-20s %s" % (item.slug, item.name)
            except Exception, e:
                print "Unable to slug: %s: '%s'" % (item.name, e)


    def slugify_marketgroup(self):
        print "Slugging the MarketGroups."
        test = {}

        for g in MarketGroup.objects.all():
            if g.slug:
                continue

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
            print "Slugged: %-20s %s(%d)" % (g.slug, g.name, g.id)
