#!/usr/bin/env python
from django.core.management.base import BaseCommand

commands = {}

def flush(server):
    server.flush_all()
commands['flush'] = flush

def stats(server):
    data = server.get_stats()
    for server, d in data:
        print "Server: %s" % server
        keys = d.keys()
        keys.sort()
        for k in keys:
            print "%s: %s" % (k, d[k])
commands['stats'] = stats

class Command(BaseCommand):
    def handle(self, *args, **options):
        from django.core.cache import cache

        cmd = args[0]
        server = cache._cache

        if cmd in commands:
            commands[cmd](server)
        else:
            print "Unknown command: %s" % cmd
