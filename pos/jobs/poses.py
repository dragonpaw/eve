#!/usr/bin/env python

from django_extensions.management.jobs import BaseJob
import traceback

from eve.lib import eveapi
from eve.settings import DEBUG
from eve.user.models import UserProfile
from eve.pos.models import PlayerStation
from eve.ccp.models import Corporation, Name

#from Queue import Queue
#import workerpool

class Job(BaseJob):
    help = "Reload all of the player-owned structures."
    when = '5min'

    def execute(self):
        update_poses()

def get_director(corp):
    for c in corp.characters.all():
        if c.is_director:
            return c
    return None

def update_poses(corp=None, force=False):
    messages = []
    api = eveapi.get_api()

    if corp:
        name = Name.objects.get(name=corp)
        corps = [ Corporation.objects.get(id=name.id) ]
    else:
        # All the player corps.
        corps = [c for c in Corporation.objects.all() if c.is_player_corp]

    if force:
        print("Forcing reload, cache times will be ignored.")

    for c in corps:

        # Skip corps that we don't have a director for.
        # (Which is actually like 99%, as we have all alliance members as corps)
        director = get_director(c)
        if director is None:
            continue

        print  "-" * 77
        print "Corp: %s" % c
        print " Director: %s" % director

        try:
            ids = []
            api = director.api_corporation()
            for record in api.StarbaseList().starbases:
                ids.append(record.itemID)
                try:
                    station = PlayerStation.objects.get(id=record.itemID)
                except PlayerStation.DoesNotExist:
                    station = PlayerStation(id=record.itemID)

                messages = station.refresh(record, api, corp=c, force=force)
                #print "  %s:" % station
                for m in messages:
                    print "  " + m

            # Look for POSes that got taken down.
            for pos in PlayerStation.objects.filter(corporation=c).exclude(id__in=ids):
                print "  Removed POS: %s will be purged." % pos.moon
                pos.delete()
        except Exception, e:
            print "ERROR refreshing corporation '%s': %s" % (c, e)
            print '-'*60
            traceback.print_exc()
            print '-'*60
