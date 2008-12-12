import time
import tempfile
import cPickle
import zlib
import os
from os.path import join, exists
from httplib import HTTPException


class MyCacheHandler(object):
    # Note: this is an example handler to demonstrate how to use them.
    # a -real- handler should probably be thread-safe and handle errors
    # properly (and perhaps use a better hashing scheme).

    def __init__(self, debug=False, throw=False):
        self.debug = debug
        self.count = 0
        self.throw = throw
        self.tempdir = join(tempfile.gettempdir(), "eveapi")
        if not exists(self.tempdir):
            os.makedirs(self.tempdir)

    def log(self, what):
        if self.debug:
            print "[%d] %s" % (self.count, what)

    def retrieve(self, host, path, params):
        # eveapi asks if we have this request cached
        key = hash((host, path, frozenset(params.items())))
        full_path = path + '?' + ';'.join([ "%s=%s" % (x[0], x[1]) for x in params.items() ])
        self.log('Path: %s' % full_path)

        self.count += 1  # for logging

        # see if we have the requested page cached...
        cacheFile = join(self.tempdir, str(key) + ".cache")
        if not exists(cacheFile):
            self.log("Not cached, fetching from server..." % full_path)
            return None

        try:
            self.log("Retrieving from disk...")
            f = open(cacheFile, "rb")
            cached = self.cache[key] = cPickle.loads(zlib.decompress(f.read()))
            f.close()

            # check if the cached doc is fresh enough
            if time.time() < cached[0]:
                    self.log("Returning cached document")
                    return cached[1]  # return the cached XML doc
            # it's stale. purge it.
            else: 
                self.log("Cache expired, purging!")
                if exists(cacheFile):
                    os.remove(cacheFile)
                return None

        except:
            self.log("Error reading cache. Unlinking." % full_path)
            if exists(cacheFile):
                os.remove(cacheFile)
            return None


        def store(self, host, path, params, doc, obj):
                # eveapi is asking us to cache an item
                key = hash((host, path, frozenset(params.items())))

                cachedFor = obj.cachedUntil - obj.currentTime
                if cachedFor:
                        self.log("%s: cached (%d seconds)" % (path, cachedFor))

                        cachedUntil = time.time() + cachedFor

                        # store in memory
                        cached = self.cache[key] = (cachedUntil, doc)

                        # store in cache folder
                        cacheFile = join(self.tempdir, str(key) + ".cache")
                        f = open(cacheFile, "wb")
                        f.write(zlib.compress(cPickle.dumps(cached, -1)))
                        f.close()


