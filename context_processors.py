# $Id$
import re

def borwser_id(request):
    ua = request.META['HTTP_USER_AGENT']
    if ua.count('Firefox'):
        return {'browser':'firefox'}
    elif ua.count('MSIE 7.0'):
        return {'browser':'ie7'}
    elif ua.count('MSIE'):
        return {'browser':'ie'}
    elif ua.count('iPhone'):
        return {'browser':'iphone'}
    elif ua.count('EVE-minibrowser'):
        return {'browser':'eve'}
    else:
        return {'browser':'unknown'}