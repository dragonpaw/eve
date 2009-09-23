import memcache
from settings import logging

class MyCacheHandler(object):
    def __init__(self, server=['127.0.0.1:11211']):
        self.mc = memcache.Client(server, debug=1)
        self.log = logging.getLogger('eve.lib.cachehandler.MyCacheHandler')

    def key(self, path, params):
        key = path + '?' + '&'.join([ "%s=%s" % (x[0], x[1]) for x in params.items() if x[0].lower() != 'apikey'])
        self.log.debug('Key: %s' % key)
        return key

    def retrieve(self, host, path, params):
        key = self.key(path, params)

        # see if we have the requested page cached...
        self.log.debug("Retrieving from memcache...")
        cache = self.mc.get(key)
        if cache:
            self.log.debug('Returning cached document')
            return cache
        else:
            self.log.debug('No cache hit.')
            return None

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        key = self.key(path, params)
        self.log.debug('Document length for cahing: %d', len(doc))

        time = obj.cachedUntil - obj.currentTime or 300
        time = max(time, 300) # Make sure we alwyas cache at least a little.
        # Cache time of 0 would mean 'forever', which we don't want.

        ret = self.mc.set(key, doc, time=time, min_compress_len=100000)
        if ret:
            self.log.debug('Cached (%d seconds)' % time)
        else:
            self.log.warn('Cache failed for key: "%s"', key)
        return ret