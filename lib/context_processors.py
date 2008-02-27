# $Id$
from eve.lib.browser_id import what_browser

def borwser_id(request):
    return { 'browser' : what_browser(request) }