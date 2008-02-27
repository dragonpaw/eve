    from django.http import HttpResponseRedirect

from eve.lib.browser_id import what_browser

def require_igb (function):
    def wrapper (request):
        browser = what_browser(request)
        if browser == 'eve':
            return function(arg)
        else:
            return HttpResponseRedirect('%s?%s=%s' % tup)

    return wrapper