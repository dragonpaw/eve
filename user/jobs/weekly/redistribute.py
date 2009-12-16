#!/usr/bin/env python
# $Id$
from eve.lib.log import BaseJob

from datetime import timedelta, datetime

from eve.user.models import Character
from eve.pos.models import PlayerStation

hour = 3600
now = datetime.utcnow()

class Job(BaseJob):
    help = "Reset the cache_until time for objects so as to spread out the refresh load."
    when = 'weekly'

    def execute(self):
        log = self.logger()
        self.redistribute_characters()
        self.redistribute_poses()

    def redistribute_characters(self):
        characters = Character.objects.all()
        char_span = timedelta(seconds=( hour/characters.count() ))
        hour_from_now = now + timedelta(hours=1)
        x = timedelta(0)
        for c in characters:
            x += char_span
            c.cached_until = hour_from_now + x
            c.save()
            log.debug("%-30s | %s", c.name, c.cached_until)

    def redistribute_poses(self):
        poses = PlayerStation.objects.all().order_by('cached_until')
        pos_span = timedelta(seconds=( hour*6/poses.count() ))
        x = timedelta(0)
        for p in poses:
            x += pos_span
            test = now + x
            p.cached_until = max(test, p.cached_until)
            p.save()
            log.debug("%-30s | %s", p.name, p.cached_until)
