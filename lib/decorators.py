#from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from eve.settings import logging
from django.core.cache import cache

from eve.lib.context_processors import what_browser

def require_igb (function):
    def wrapper (request):
        browser = what_browser(request)
        if browser == 'eve':
            return function(request)
        else:
            return render_to_response('decorator_need_igb.html', {},
                                      RequestContext(request))

    return wrapper

def require_oog (function):
    def wrapper (request):
        browser = what_browser(request)
        if browser != 'eve':
            return function(request)
        else:
            return render_to_response('decorator_need_oog.html', {},
                                      RequestContext(request))

    return wrapper

def require_trust (function):
    message = 'The Widget needs you to trust it to allow you access to this function.'
    def wrapper (request):
        browser = what_browser(request)
        if browser != 'eve':
            return render_to_response('decorator_need_igb.html', {},
                                      RequestContext(request))
        elif request.META['HTTP_EVE.TRUSTED'] == 'no':
            print "Asking..."
            response = render_to_response('decorator_need_trust.html', {},
                                          RequestContext(request))
            response['eve.trustMe'] = 'http://%s/::%s' % (request.META['HTTP_HOST'], message);
            return response
        else:
            print "No header?"
            return function(request)

    return wrapper

def require(expr):
    def decorator(func):
        def wrapper(*__args,**__kw):
            assert eval(expr),"Precondition failed"
            return func(*__args,**__kw)
        wrapper.__name__ = func.__name__
        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator

def render_to(template_name):
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if not isinstance(output, dict):
                return output
            return render_to_response(request, template_name, output)
        return wrapper
    return renderer


#from django.core.cache import cache
#
#def cachedmethod(cache_key, timeout=3600):
#    def paramed_decorator(func):
#        def decorated(self):
#            key = cache_key % self.__dict__
#            res = cache.get(key)
#            if res == None:
#                #self._logger.debug('Cache miss, Added: %s' % key)
#                res = func(self)
#                cache.set(key, res, timeout)
#            #self._logger.debug('Cache hit: %s' % key)
#            return res
#        decorated.__doc__ = func.__doc__
#        decorated.__dict__ = func.__dict__
#        #decorated._logger = logging.getLogger('CACHE')
#        return decorated
#    return paramed_decorator

import cPickle as pickle
import md5

def cachedmethod(length=5, cache_key=None):
    """
    A variant of the snippet posted by Jeff Wheeler at
    http://www.djangosnippets.org/snippets/109/

    Caches a function, using the function and its arguments as the key, and the return
    value as the value saved. It passes all arguments on to the function, as
    it should.

    Length is specified in minutes. (Converted to second for cache backend.)

    The decorator itself takes a length argument, which is the number of
    seconds the cache will keep the result around.

    It will put in a MethodNotFinishedError in the cache while the function is
    processing. This should not matter in most cases, but if the app is using
    threads, you won't be able to get the previous value, and will need to
    wait until the function finishes. If this is not desired behavior, you can
    remove the first two lines after the ``else``.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            from django.core.cache import cache
            key = "%s.%s.%s:" % (func.__module__, self.__class__.__name__, func.__name__)

            if cache_key:
                key += cache_key % self.__dict__
            else:
                raw = [self, args, kwargs]
                pickled = pickle.dumps(raw, protocol=pickle.HIGHEST_PROTOCOL)
                key += md5.new(pickled).hexdigest()
            value = cache.get(key)
            if value:
                return value
            else:
                # This will set a temporary value while ``func`` is being
                # processed. When using threads, this is vital, as otherwise
                # the function can be called several times before it finishes
                # and is put into the cache.
                #class MethodNotFinishedError(Exception): pass
                #cache.set(key, MethodNotFinishedError(
                #    'The function %s has not finished processing yet. This \
                # value will be replaced when it finishes.' % (func.__name__)
                #), length)
                result = func(self, *args, **kwargs)
                pickled = pickle.dumps(result, protocol=pickle.HIGHEST_PROTOCOL)
                cache.set(key, result, length*60)
                return result
        wrapper.__module__ = func.__module__
        wrapper.__name__ = func.__name__
        wrapper.__dict__ = func.__dict__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator


# Usage:

#
#def cachedmethod(timeout=60):
#    def decorator(func):
#        def wrapper(*__args,**__kw):
#            log = logging.getLogger('lib.decorators.cachedmethod')
#            key = hash( (f, tuple(args), frozenset(kwargs.items())) )
#            log.debug('Key: %s', (key))
#            return func(*__args,**__kw)
#        wrapper.__name__ = func.__name__
#        wrapper.__dict__ = func.__dict__
#        wrapper.__doc__ = func.__doc__
#        return wrapper
#    return decorator
#
#
#        #print 'Key: %s' % key
#        value = cache.get(key)
#        if not value:
#            log.debug('Cache miss, Added.')
#            #print 'Cache miss, Added.'
#            value = f(*args, **kwargs)
#            cache.add(key, value, timeout)
#        else:
#            log.debug('Cache hit.')
#            #print 'Cache hit.'
#        return value
#    return g
#
#


#if ($_SERVER['HTTP_EVE_TRUSTED']=='no') {
#            // request trust from client through headers
#              header("eve.trustme:".$this_host."/::please allow me to access your pilot information.");
#              $trusted = false;
#           } else {
#              $trusted = true;
#            // get pilotname
#              $pilotname = $_SERVER['HTTP_EVE_CHARNAME'];
#           }
#        }
#      }
#
#
#The following variables are available in from the header in the IGB:
#
#    * TRUSTED
#      Whether or not the user of the client has trusted your website. ('no'/'yes')
#    * REGIONNAME
#      The name of the region the pilot is currently in.
#    * CONSTELLATIONNAME
#      The name of the constellation the pilot is currently in.
#    * SOLARSYSTEMNAME
#      The name of the solarsystem the pilot is currently in.
#    * STATIONNAME
#      The name of the station the pilot is currently docked at. ('None' if undocked)
#    * CHARNAME
#      The name of the pilot.
#    * CHARID
#      The database id of the pilot, can be used to create showinfo links or get the pilot's portrait.
#    * ALLIANCENAME
#      The name of the alliance the pilot is part of. ('None' if not part of an alliance)
#    * ALLIANCEID
#      The database id of the alliance the pilot is part of. (0 (unsure) if not part of an alliance)
#    * CORPNAME
#      The name of the corp the pilot is part of.
#    * CORPID
#      The database id of the corp the pilot is part of.
#    * CORPROLE
#      The role of the pilot in his corporation.
#
#The corporation role is a bitmask. If you don't know what that is, ask Google, it goes beyond the scope of this article to explain basic programmer's math here.
#Corprole    Bit
#Director    1
#Personnel Manager    128
#Accountant    256
#Security Officer    512
#Factory Manager    1024
#Station Manager    2048
#Auditor    4096
#Hangar Can Take Division 1    8192
#Hangar Can Take Division 2    16384
#Hangar Can Take Division 3    32768
#Hangar Can Take Division 4    65536
#Hangar Can Take Division 5    131072
#Hangar Can Take Division 6    262144
#Hangar Can Take Division 7    524288
#Hangar Can Query Division 1    1048576
#Hangar Can Query Division 2    2097152
#Hangar Can Query Division 3    4194304
#Hangar Can Query Division 4    8388608
#Hangar Can Query Division 5    16777216
#Hangar Can Query Division 6    33554432
#Hangar Can Query Division 7    67108864
#Account Can Take Division 1    134217728
#Account Can Take Division 2    268435456
#Account Can Take Division 3    536870912
#Account Can Take Division 4    1073741824
#Account Can Take Division 5    2147483648
#Account Can Take Division 6    4294967296
#Account Can Take Division 7    8589934592
#Account Can Query Division 1    17179869184
#Account Can Query Division 2    34359738368
#Account Can Query Division 3    68719476736
#Account Can Query Division 4    137438953472
#Account Can Query Division 5    274877906944
#Account Can Query Division 6    549755813888
#Account Can Query Division 7    1099511627776
#Equipment Config    2199023255552
#ContainerCan Take Division 1    4398046511104
#ContainerCan Take Division 2    8796093022208
#ContainerCan Take Division 3    17592186044416
#ContainerCan Take Division 4    35184372088832
#ContainerCan Take Division 5    70368744177664
#ContainerCan Take Division 6    140737488355328
#ContainerCan Take Division 7    281474976710656
#Can Rent Office    562949953421312
#Can Rent FactorySlot    1125899906842624
#Can Rent ResearchSlot    2251799813685248
#Junior Accountant    4503599627370496
#Starbase Config    9007199254740992
#Trader    18014398509481984
