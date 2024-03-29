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
                msg = str(e)
                if msg in ( 'Login denied by account status',
                            'Character must be a Director or CEO',
                            'Authentication failure' ):
                    director.is_director = False
                    director.save()
                    log.info("%s: Marked as no longer a director, %s", director, e)
                elif msg == 'Character does not belong to account':
                    log.warn('Deleting director: %s, as not longer associated with account', director)
                    director.delete()
                elif 'EVE backend database temporarily disabled' in msg:
                    log.warn('EVE API taken offline by CCP. No refresh available.')
                    return
                elif msg == 'Connection refused':
                    log.warn('EVE API server is not accepting connections. No refresh available.')
                    continue
                elif msg == 'Connection reset by peer':
                    log.warn('EVE API server closed connection. No refresh available.')
                    continue
                elif msg == 'Invalid itemID provided':
                    log.warn('%s: POS ID is invalid: %s POS will be removed.', c, record.itemID)
                    pos.delete()
                elif msg == 'Unexpected failure accessing database':
                    log.warn('EVE API giving unexpected database failure.')
                    continue
                else:
                    log.exception('Unknown error refreshing POS.')
                    continue

            # Look for POSes that got taken down.
            for pos in c.pos.exclude(id__in=ids):
                log.info("%s removed. POS will be purged.", pos.moon)
                pos.delete()
