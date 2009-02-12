# $Id$
def what_browser(request):
    # The test client doesn't set a header.
    if not 'HTTP_USER_AGENT' in request.META:
        return 'unknown'

    ua = request.META['HTTP_USER_AGENT']
    if 'Firefox' in ua:
        return 'firefox'
    elif 'MSIE 7.0' in ua:
        return 'ie7'
    elif 'MSIE' in ua:
        return 'ie'
    elif 'iPhone' in ua:
        return 'iphone'
    elif 'EVE-minibrowser' in ua:
        return 'eve'
    else:
        return 'unknown'

def borwser_id(request):
    return { 'browser' : what_browser(request) }
