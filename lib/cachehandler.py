import memcache

class MyCacheHandler(object):
    def __init__(self, debug=False, throw=False, server=['127.0.0.1:11211']):
        self.debug = debug
        self.throw = throw # depricated.
        self.mc = memcache.Client(server, debug=debug)

    def log(self, what):
        if self.debug:
            print what

    def key(self, path, params):
        key = path + '?' + '&'.join([ "%s=%s" % (x[0], x[1]) for x in params.items() if x[0].lower() != 'apikey'])
        self.log('Key: %s' % key)
        return key

    def retrieve(self, host, path, params):
        key = self.key(path, params)

        # see if we have the requested page cached...
        self.log("Retrieving from memcache...")
        cache = self.mc.get(key)
        if cache:
            self.log('Returning cached document')
            return cache
        else:
            self.log('No cache hit.')
            return None

    def store(self, host, path, params, doc, obj):
        # eveapi is asking us to cache an item
        key = self.key(path, params)

        time = obj.cachedUntil - obj.currentTime or 0
        self.log('Cached (%d seconds)' % time)

        self.mc.set(key, doc, time=time)
        return True
