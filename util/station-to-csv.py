#!/usr/bin/env python

from eve.ccp.models import Region

def dump_csv(region_name):
    region = Region.objects.get(name=region_name)
    for s in region.stations.all():
        print ",".join([str(s.id), s.name, s.solarsystem.name, s.region.name])

if __name__ == '__main__':
    import sys
    region = sys.argv[1]
    #print "Loading: %s" % region
    dump_csv(region)
