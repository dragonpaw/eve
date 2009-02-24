import urllib2
import sys
import re
import os
import socket
socket.setdefaulttimeout(15)

from eve.ccp.models import Item

#dir = 'c:/django-sites/eve/_static/ccp-icons/entity'
# http://games.chruker.dk/eve_online/graphics/types_graphic_id/1024/1223.png
url = 'http://games.chruker.dk/eve_online/graphics/types_graphic_id/%(size)d/%(id)d.png'
filename = 'c:/django-sites/eve/_static/ccp-icons/npc/%(size)d_%(size)d/%(id)d.png'
def save(url, filename):
    if os.path.exists(filename):
        print "Already saved."
        return
    print "Saving %s to %s:" % (url, filename)
    try:
        response = urllib2.urlopen(url)
        image = response.read()
        file = open(filename, 'w+b')
        file.write(image)
        file.close()
        print "Saved: %s" % filename
    except urllib2.HTTPError, e:
        if e.code == 404:
            print "No icon found."
        else:
            raise
for i in Item.objects.filter(group__category__name='Entity'):
    print i
    for size in (32, 64, 128, 256):
        d = {'size':size, 'id': i.graphic.id }
        save(url % d, filename % d)
