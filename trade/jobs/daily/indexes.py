#!/usr/bin/env python
# $Id$
from eve.lib.log import BaseJob

from collections import defaultdict
import cStringIO
import csv
from datetime import datetime, date, timedelta
from decimal import Decimal
import gzip

from django.db.models import Q
from eve.ccp.models import Item, SolarSystem
from eve.lib import fetch_url
from eve.trade.models import MarketIndex, MarketIndexValue
from eve.trade.sources import EveCentral

class Job(BaseJob):
    help = "Load prices from external sources."
    when = 'daily'

    def execute(self):
        self.log = self.logger()
        start_time = datetime.utcnow()
        self.update_evecentral()
        self.update_refinables()
        self.log.info("Elapsed: %s", datetime.utcnow() - start_time)


    def update_evecentral(self):
        indexes = dict()
        for s in EveCentral['systems']:
            system = SolarSystem.objects.get(name=s['name'])
            d = {'system':system.name, }
            name = EveCentral['name'] % d
            try:
                index = MarketIndex.objects.get(name=name)
            except MarketIndex.DoesNotExist:
                index = MarketIndex(name=name)
            index.url = EveCentral['url']
            index.note = EveCentral['description'] % d
            index.priority = s['priority']
            index.save()
            indexes[system.id] = index

        #day=date.today()
        day=date.today()-timedelta(days=1)
        url = "http://eve-central.com/dumps/{0}.dump.gz".format(
            day.strftime("%Y-%m-%d")
        )
        log.info("Fetching: %s", url)
        result = fetch_url(url)
        #result = open('2009-12-15.dump.gz')

        gzip_data = cStringIO.StringIO(result.read())
        file = gzip.GzipFile(fileobj=gzip_data)
        price_data = dict()

        for id in indexes.keys():
            price_data[id] = dict()
            self.log.debug("Created data structure for system: %d", id)

        reader = csv.DictReader(file, skipinitialspace=True)
        self.log.debug('Field names: %s', ','.join(reader.fieldnames))
        for row in reader:
            system = int(row['systemid'])

            # Skip any system we don't care about.
            if system not in indexes:
                continue

            # The other fields that matter.
            price = Decimal(row['price'])
            item_id = int(row['typeid'])

            # Populate a blank record for consistancy.
            if item_id not in price_data[system]:
                price_data[system][item_id] = { 'buy': None, 'sell': None }

            # Update prices.
            if int(row['bid']):
                # Buy order
                price_data[system][item_id]['buy'] = max(price_data[system][item_id]['buy'], price)
            else:
                if price_data[system][item_id]['sell']:
                    price_data[system][item_id]['sell'] = min(price_data[system][item_id]['sell'], price)
                else:
                    price_data[system][item_id]['sell'] = price

        for item in Item.objects.filter(marketgroup__isnull=False, published=True):
            for system_id in indexes.keys():
                if system_id in price_data and item.id in price_data[system_id]:
                    self.update_index(
                        indexes[system_id],
                        item=item,
                        buy=price_data[system_id][item.id]['buy'],
                        sell=price_data[system_id][item.id]['sell'],
                    )


    def update_index(self, index, item, buy=None, sell=None):
        self.log.debug("Updating: %s: %s is buy=%s, sell=%s",
            index, item, buy, sell
        )
        return index.set_value(item, buy=buy, sell=sell)


    def derrived_value(self, item, index):
        refines_into = item.refines()
        if refines_into.count() == 0:
            self.log.info("Item doesn't refine at all: %s", item)
            return None, None

        buy = 0
        sell = 0
        for r in refines_into:
            sell_price = None
            buy_price = None
            try:
                value = list(MarketIndexValue.objects.filter(item=r.material))
                value.sort(key=lambda x:x.index.priority, reverse=True)
                for v in value:
                    if v.index.user is not None:
                        # Skip personal indexes.
                        continue

                    if buy_price is None:
                        buy_price = v.buy
                    if sell_price is None:
                        sell_price = v.sell

            except MarketIndexValue.DoesNotExist:
                self.log.warn("No value for item '%s' in indexes.", r.material)
                return None, None

            # We set buy/sell to None when something wasn't available.
            if buy_price and buy is not None:
                buy += buy_price * r.quantity
            else:
                buy = None

            if sell_price and sell is not None:
                sell += sell_price * r.quantity
            else:
                sell = None

        if item.portionsize:
            if buy is not None:
                buy /= item.portionsize
            if sell is not None:
                sell /= item.portionsize

        return buy, sell


    def update_refinables(self):
        name = 'Derived'
        try:
            index = MarketIndex.objects.get(name=name)
        except MarketIndex.DoesNotExist:
            index = MarketIndex(name=name)
        index.note = 'Values calculated from the prevailing mineral prices.'
        index.priority = 250
        index.save()

        filter = (Q(group__name='Refinables') | Q(group__category__name='Asteroid')) & Q(published=True)
        for m in Item.objects.filter(filter):
            buy, sell = self.derrived_value(m, index)
            if buy or sell:
                v = self.update_index(index, item=m, buy=buy, sell=sell)
            else:
                self.log.info("Unable to calculate value of: %s", m)
