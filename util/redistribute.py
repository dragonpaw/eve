#!/usr/bin/env python
# $Id$
"""Script to reset the cache_until time for objects so as to spread out the refresh load."""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

from datetime import timedelta, datetime

from eve.user.models import Character
from eve.pos.models import PlayerStation

hour = 3600
hour_from_now = datetime.utcnow() + timedelta(hours=1)
six_from_now = datetime.utcnow() + timedelta(hours=6)

def redistribute_characters():
    characters = Character.objects.all()
    char_span = timedelta(seconds=( hour/characters.count() ))
    x = timedelta(0)
    for c in characters:
        x += char_span
        c.cached_until = hour_from_now + x
        c.save()
        print "%-30s | %s" % (c.name, c.cached_until)

def redistribute_poses():
    poses = PlayerStation.objects.all()
    pos_span = timedelta(seconds=( hour*6/poses.count() ))
    x = timedelta(0)
    for p in poses:
        x += pos_span
        p.cached_until = six_from_now + x
        p.save()
        print "%-30s | %s" % (p.name, p.cached_until)
        
redistribute_characters()
print "-" * 78
redistribute_poses()