#!/usr/bin/env python

from eve.lib.log import BaseJob
import traceback

from eve.lib import eveapi
from eve.ccp.models import Corporation
from eve.pos.models import PlayerStation

class Job(BaseJob):
    help = "Reload all of the player-owned structures."
    when = '5min'

    # Change to ignore POS timers and refresh them all.
    force = False

    def execute(self):
        messages = []
        api = eveapi.get_api()
        log = self.logger()

        # All the player corps.
        corps = [c for c in Corporation.objects.all() if c.is_player_corp]

        for c in corps:
            # Skip corps that we don't have a director for.
            # (Which is actually like 99%, as we have all alliance members as corps)
            try:
                director = c.directors()[0]
                log.debug("Corp: %s", c)
                log.debug('%s: Director: %s.', c, director)
            except IndexError:
                director = None
                log.debug('%s: No director avilable.', c)
                if c.pos.count():
                    log.warn("%s: Can't refresh. No director found. Purging POSes.")
                    c.pos.all().delete()
                # Nothing else do be done.
                continue

            try:
                ids = set()
                api = director.api_corporation()
                for record in api.StarbaseList().starbases:

                    # Sometimes CCP likes to give out moon ID's of 0 or like
                    # 1941.
                    if record.moonID < 10000 :
                        log.warn("%s: POS #%d has moon ID of %d", c, record.itemID, record.moonID)
                        continue

                    ids.add(record.itemID)
                    try:
                        pos = c.pos.get(id=record.itemID)
                    except PlayerStation.DoesNotExist:
                        pos = PlayerStation(id=record.itemID)

                    messages = pos.refresh(record, api, corp=c, force=self.force)
                    log.debug('%s: Messages: %s', pos, messages)

            except Exception, e:
                if str(e) in ( 'Login denied by account status',
                               'Character must be a Director or CEO',
                               'Authentication failure' ):
                    director.is_director = False
                    director.save()
                    log.info("%s: Marked as no longer a director, %s", director, e)
                elif 'EVE backend database temporarily disabled' in str(e):
                    log.warn('EVE API taken offline by CCP. No refresh available.')
                    return
                elif str(e) == 'Connection reset by peer':
                    log.warn('EVE API server closed connection. No refresh available.')
                    continue
                else:
                    log.error(traceback.format_exc())
                    continue

            # Look for POSes that got taken down.
            for pos in c.pos.exclude(id__in=ids):
                log.info("%s removed. POS will be purged.", pos.moon)
                pos.delete()
