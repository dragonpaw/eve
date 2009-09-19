#!/usr/bin/env python
from django_extensions.management.jobs import BaseJob
from exceptions import Exception

from eve.ccp.models import MarketGroup, Item, Region, Alliance, Group
from eve.lib.formatting import unique_slug


class Job(BaseJob):
    help = "Add slug values for all the CCP items."
    when = 'once'

    def execute(self):
        self.slugify_item()
        self.slugify_marketgroup()
        self.slugify_region()
        self.slugify_group()
        # No longer needed, as the save handler is taking care of it.
        #self.slugify_alliance()
        print "ADD INDEXES TO ALL SLUG FIELDS NOW!!!!"

    def slugify_something(self, things):
        for x in things:
            # print x
            if x.slug:
                continue
            try:
                x.slug = unique_slug(x)
                x.save()
                print "Slugged: %-20s %s" % (x.slug, x.name)
            except Exception, e:
                print "Unable to slug: %s: '%s'" % (x.name, e)

    def slugify_group(self):
        print "Slugging the groups."
        self.slugify_something( Group.objects.all() )

    def slugify_region(self):
        print "Slugging the Regions."
        self.slugify_something( Region.objects.all() )

    def slugify_alliance(self):
        for a in Alliance.objects.all():
            # It's in the save handler.
            a.save()

    def slugify_item(self):
        print "Slugging the Items."
        self.slugify_something( Item.objects.all() )

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
