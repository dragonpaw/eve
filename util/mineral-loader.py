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

# TODO: Remove old prices for the index. Just use the date for the last update date.

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
qtc.description = QtcIndustries['description']
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

def set_value(item, value):
    try:
        index = MarketIndexValue.objects.get(index=qtc, item=item)
    except MarketIndexValue.DoesNotExist:
        index = MarketIndexValue(index=qtc, item=item)
    index.value = value
    index.date = today
    index.save()
    print "Value: %s = %s" % (index.item, index.value)


def derrived_value(item):
    refines_into = item.refines()
    if refines_into.count() == 0:
        return None
    
    value = 0
    for r in refines_into:
        #print "Refines into: %s" % r
        if r.value:
            value += r.value
        else:
            return None
    return value/item.portionsize

minerals = {}
for node in doc.getElementsByTagName("index"):
    days = node.getAttribute("timeperiod")
    if int(days) == 30:
        for m in node.childNodes:
            if m.localName:
                mineral_name = m.localName
                minerals[mineral_name] = find_price(m)
                 
# mapping now has the same value as in the SAX example:
pprint.pprint(minerals)
map = QtcIndustries['item_map']
today = date.today()
for m in minerals.items():
    try:
        item = Item.objects.get(pk=map[m[0]])
    except KeyError:
        print "No such key in item mapping: '%s'" % (m[0])
        exit(1)
    set_value(item, value = m[1])

filter = (Q(group__name='Refinables') | Q(group__category__name='Asteroid')) & Q(published=True)
for m in Item.objects.filter(filter):
    value = derrived_value(m)
    if value: 
        set_value(m, value)
    else:
        print "Unable to calculate value of: %s" % m
