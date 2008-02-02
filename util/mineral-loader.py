#!/usr/bin/env python
# $Id$
import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'eve.settings'

import pprint
import httplib
import urllib
from eve.trade.models import *
from eve.ccp.models import *
import xml.dom.minidom
from xml.dom.minidom import Node
from eve.trade.sources import QtcIndustries
from datetime import date
from sys import exit

url = QtcIndustries['feed']

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
http.request("GET", "/"+path)

response = http.getresponse()
if response.status != 200:
    raise RuntimeError("'%s' request failed (%d %s)" % (path, response.status, response.reason))
    
doc = xml.dom.minidom.parse(response)

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
        try:
            value = MarketIndexValue.objects.get(index=index, item=r.material)
        except MarketIndexValue.DoesNotExist:
            print "No value for item '%s' in index '%s'." % (r.material, index)
            return None, None
        
        if buy is not None:
            if value.buy:
                buy += value.buy * r.quantity
            else:
                buy = None
        if sell is not None:
            if value.sell: 
                sell += value.sell * r.quantity
            else:
                sell = None
    
    if item.portionsize:
        if buy is not None:
            buy /= item.portionsize
        if sell is not None:
            sell /= item.portionsize
            
    return buy, sell

minerals = {}
for node in doc.getElementsByTagName("index"):
    days = node.getAttribute("timeperiod")
    if int(days) == 7:
        for m in node.childNodes:
            if m.localName:
                mineral_name = m.localName
                minerals[mineral_name] = find_price(m)
                 
# mapping now has the same value as in the SAX example:
pprint.pprint(minerals)
map = QtcIndustries['item_map']
for m in minerals.items():
    try:
        item = Item.objects.get(pk=map[m[0]])
    except KeyError:
        print "No such key in item mapping: '%s'" % (m[0])
        exit(1)
    v = qtc.set_value(item, buy=m[1], sell=m[1])
    print "Value: %s = %s/%s" % (v.item, v.buy, v.sell)

filter = (Q(group__name='Refinables') | Q(group__category__name='Asteroid')) & Q(published=True)
for m in Item.objects.filter(filter):
    buy, sell = derrived_value(m, qtc)
    if buy or sell: 
        v = qtc.set_value(m, buy=buy, sell=sell)
        print "Value: %s = %s/%s" % (v.item, v.buy, v.sell)
    else:
        print "Unable to calculate value of: %s" % m
