#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

import httplib
import urllib
from eve.trade.models import *
from eve.ccp.models import *
import xml.dom.minidom
from xml.dom.minidom import Node
from eve.trade.sources import QtcIndustries, EveCentral
from datetime import date
from sys import exit
import socket
socket.setdefaulttimeout(10)

def text(node):
    '''XML is so annoying to deal with.'''
    return node[0].firstChild.data

def find_mineral(node):
    pass

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
        
    name = QtcIndustries['name']     
    qtc, created = MarketIndex.objects.get_or_create(name=name)
    qtc.url = QtcIndustries['url']
    qtc.note = QtcIndustries['description']
    qtc.priority = 200
    qtc.save()
        
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
    indexes = {}
    group_filter = Q(published=True, marketgroup__isnull=False)
    
    for x in EveCentral['systems']:
        system = SolarSystem.objects.get(name=x['name'])
        d = {'system':system.name, }
        name = EveCentral['name'] % d
        index, created = MarketIndex.objects.get_or_create(name=name)
        index.url = EveCentral['url']
        index.note = EveCentral['description'] % d
        index.priority = x['priority']
        index.save()
        indexes[system.name] = index
        print "Updated index: %s" % index
        
    # Build the list of items to query.
    items = {}
    for cat_name in EveCentral['categories']:
        cat = Category.objects.get(name=cat_name)
        for group in cat.groups.all():
            for item in group.items.filter(group_filter):
                items[item.id] = item
    
    stations = {}
    for id in items.keys():
        item = items[id]
        print "Looking up: %s[%d]" % (item.name, item.id)
        
        prices = {}
        for x in indexes.keys():
            prices[x] = { 'buy': Decimal(0), 'sell': Decimal(0) }
            
        try:
            response = fetch_url(EveCentral['feed'] % {'item_id':item.id})
            doc = xml.dom.minidom.parse(response)
            for node in doc.getElementsByTagName('order'):
                station = text(node.getElementsByTagName('station'))
                #print "Station: %s" % station
                
                # Handle new stations.
                if not stations.has_key(station):
                    system = Station.objects.get(id=station).solarsystem
                    if system.name in indexes.keys():
                        is_wanted = True
                    else:
                        is_wanted = False
                    stations[station] = {'system': system,
                                         'is_wanted': is_wanted }
                else:
                    system = stations[station]['system']
                #print "Is located in: %s" % stations[station]['system']
                
                # Skip the useless.
                #print "Is wanted? %s" % stations[station]['is_wanted']
                if not stations[station]['is_wanted']:
                    continue
                
                local = prices[system.name]
                
                price = text(node.getElementsByTagName('price'))
                price = price.replace(',','')
                price = Decimal(price)
                #print "Price: %s" % price

                if node.parentNode.nodeName == 'sell_orders':
                    #print "Is a sell order."
                    if local['sell'] == 0 or price < local['sell']:
                        local['sell'] = price
                else:
                    #print "Is a buy order."
                    if price > local['buy']:
                        local['buy'] = price
                    
            for x in indexes.keys():
                buy = prices[x]['buy']
                sell = prices[x]['sell']
                print "Best %s prices: %s/%s" % (x, buy, sell)
                indexes[x].set_value(item, buy=buy, sell=sell)
        except Exception, e:
            print "Error loading EVE Central for item. [%s]" % e

def update_qtc():
    name = QtcIndustries['name']     
    qtc, created = MarketIndex.objects.get_or_create(name=name)
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
            print "No such key in item mapping: '%s'" % (m[0])
            exit(1)
        v = qtc.set_value(item, buy=m[1], sell=m[1])
        print "Value: %s = %s/%s" % (v.item, v.buy, v.sell)

def update_refinables():
    name = 'Derived'     
    index, created = MarketIndex.objects.get_or_create(name=name)
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


update_evecentral()
update_qtc()
update_refinables()

