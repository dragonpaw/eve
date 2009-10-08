#!/usr/bin/env python
from eve.lib.log import BaseJob

import httplib
import xml.dom.minidom
#import socket
import traceback
import workerpool

from datetime import datetime
from decimal import Decimal

from django.db.models import Q

from eve.trade.models import MarketIndex, MarketIndexValue
from eve.ccp.models import Item, SolarSystem
from eve.trade.sources import QtcIndustries, EveCentral

#socket.setdefaulttimeout(10)


class Job(BaseJob):
    help = "Load prices from external sources."
    when = 'daily'

    def execute(self):
        print("Starting EVE Central index...")
        start_time = datetime.utcnow()
        update_evecentral()
        print "Elapsed: %s" % (datetime.utcnow() - start_time)

        #update_qtc()  # Gives really wonky prices.
        update_refinables()


def text(node):
    '''XML is so annoying to deal with.'''
    return node[0].firstChild.data

def find_price(node):
    for x in node.childNodes:
        if x.localName == 'price':
            #print x.childNodes[0].data
            return x.childNodes[0].data

def derrived_value(item, index):
    refines_into = item.refines()
    if refines_into.count() == 0:
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
                    #print "Buy: %s (%s)" % (buy_price, v.index.name)
                if sell_price is None:
                    sell_price = v.sell
                    #print "Sell: %s (%s)" % (sell_price, v.index.name)

        except MarketIndexValue.DoesNotExist:
            print "No value for item '%s' in indexes." % r.material
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

def fetch_url(url, id=None):
    if url.lower().startswith("http://"):
        url = url[7:]

    if "/" in url:
        url, path = url.split("/", 1)
    else:
        path = ""

    http = httplib.HTTPConnection(url)
    if id:
        http.request("GET", "/"+path+str(id))
    else:
        http.request("GET", "/"+path)

    response = http.getresponse()
    if response.status != 200:
        raise RuntimeError("'%s' request failed (%d %s)" % (path,
                                                            response.status,
                                                            response.reason))

    return response

def update_evecentral():
    indexes = []

    # Setup the job queue and workers.
    def toolbox_factory():
        return EveCentralToolbox(EveCentral['host'])
    def worker_factory(queue):
        return workerpool.EquippedWorker(queue, toolbox_factory)
    pool = workerpool.WorkerPool(size=5, worker_factory=worker_factory)

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
        indexes.append((index, system))
        print "Updated index: %s" % index

    for item in Item.objects.filter(marketgroup__isnull=False, published=True):
        for index, system in indexes:
            job = EveCentralJob(item, system, index)
            pool.put(job)
    pool.shutdown()
    pool.wait()

class EveCentralToolbox(object):
    "Create a http connection to the server."
    def __init__(self, host):
        # Can't cache any more, as a non-200 error kills the connection.
        self.host = host
        #self.http = httplib.HTTPConnection(host)

    def fetch(self, url, id=None):
        http = httplib.HTTPConnection(self.host)
        http.request("GET", url)

        response = http.getresponse()
        if response.status != 200:
            raise RuntimeError("'%s' request failed (%d %s)" % (url,
                                                                response.status,
                                                                response.reason))
        return response.read()

class EveCentralJob(workerpool.Job):
    "Job for grabbing a single item in a single system, and saving it to an index."

    def __init__(self, item, system, index):
        self.item = item
        self.system = system
        self.index = index

    def run(self, toolbox):
        buy = Decimal(0)
        sell = Decimal(0)

        try:
            d = {'item_id':self.item.id, 'system_id':self.system.id}
            data = toolbox.fetch(EveCentral['path'] % d)
            doc = xml.dom.minidom.parseString(data)
            for node in doc.getElementsByTagName('order'):

                price = text(node.getElementsByTagName('price'))
                price = Decimal(price)

                if node.parentNode.nodeName == 'sell_orders':
                    if sell == 0 or price < sell:
                        sell = price
                else:
                    if price > buy:
                        buy = price

            print "Best %s prices in %s: %s/%s" % (self.item.name, self.system.name, buy, sell)
            self.index.set_value(self.item, buy=buy, sell=sell)

        except Exception, e:
            print "Error loading EVE Central for item: %s." % self.item
            print traceback.print_exc()

def update_qtc():
    name = QtcIndustries['name']
    try:
        qtc = MarketIndex.objects.get(name=name)
    except MarketIndex.DoesNotExist:
        qtc = MarketIndex(name=name)
    qtc.url = QtcIndustries['url']
    qtc.note = QtcIndustries['description']
    qtc.priority = 200
    qtc.save()

    response = fetch_url(QtcIndustries['feed'])

    doc = xml.dom.minidom.parse(response)

    minerals = {}
    for node in doc.getElementsByTagName("index"):
        days = node.getAttribute("timeperiod")
        if int(days) == 7:
            for m in node.childNodes:
                if m.localName:
                    mineral_name = m.localName
                    minerals[mineral_name] = find_price(m)

    # mapping now has the same value as in the SAX example:
    map = QtcIndustries['item_map']
    for m in minerals.items():
        try:
            item = Item.objects.get(pk=map[m[0]])
        except KeyError:
            raise RuntimeError("No such key in item mapping: '%s'" % (m[0]))
        v = qtc.set_value(item, buy=m[1], sell=m[1])
        print "Value: %s = %s/%s" % (v.item, v.buy, v.sell)

def update_refinables():
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
        buy, sell = derrived_value(m, index)
        if buy or sell:
            #print "Value: %s = %s/%s" % (m, buy, sell)
            v = index.set_value(m, buy=buy, sell=sell)
        else:
            print "Unable to calculate value of: %s" % m
