import cmemcache as memcache
import logging

class MyCacheHandler(object):
    def __init__(self, debug=True, throw=False, server=['127.0.0.1:11211']):
        self.debug = debug
        self.throw = throw # depricated.
        self.mc = memcache.Client(server, debug=debug)
        self.log = logging.getLogger('eveapi.CacheHandler')

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

        time = obj.cachedUntil - obj.currentTime or 300
        time = max(time, 300) # Make sure we alwyas cache at least a little.
        # Cache time of 0 would mean 'forever', which we don't want.
        self.log.debug('Cached (%d seconds)' % time)

        self.mc.set(key, doc, time=time)
        return True
