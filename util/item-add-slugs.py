#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'
from sys import exit

from exceptions import Exception
from django.template.defaultfilters import slugify
from eve.ccp.models import Item

for item in Item.objects.all():
    try:
        item.slug = slugify(item.name)
        #print "%s = %s" % (item.name, item.slug)
        item.save()
    except Exception, e:
        print "Unable to slug: %s: '%s'" % (item.name, e)
        
