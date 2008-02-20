#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from eve.trade.models import *
import sys

from cachehandler import MyCacheHandler

import eveapi
import pprint

import os
os.environ['TZ'] = 'UTC'

api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=True, throw=False)).context(version=2)
for t in api.eve.RefTypes().refTypes:
    id = t['refTypeID']
    name = t['refTypeName']
    print "%s: %s" % (id, name)
    JournalEntryType.objects.get_or_create(id=id, name=name)