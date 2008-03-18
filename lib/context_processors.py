# $Id$
def borwser_id(request):
    def what_browser(request):
        # The test client doesn't set a header.
        if not request.META.has_key('HTTP_USER_AGENT'):
            return 'unknown'
        
        ua = request.META['HTTP_USER_AGENT']
        if ua.count('Firefox'):
            return 'firefox'
        elif ua.count('MSIE 7.0'):
            return 'ie7'
        elif ua.count('MSIE'):
            return 'ie'
        elif ua.count('iPhone'):
            return 'iphone'
        elif ua.count('EVE-minibrowser'):
            return 'eve'
        else:
            return 'unknown'
        
    return { 'browser' : what_browser(request) }