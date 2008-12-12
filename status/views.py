from django.shortcuts import render_to_response
from django.template import RequestContext

from eve.lib.formatting import make_nav
#from eve.status.models import Tranquility

from eve.lib import eveapi
from eve.lib.cachehandler import MyCacheHandler
from eve import settings

api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=settings.DEBUG, throw=False)).context(version=2)

status_nav = make_nav("Tranquility Status", "/status/", '74_13', 
                      'Current status of the Tranquility cluster.')

def status(request):
    d = {}
    d['nav'] = [status_nav]
    
    d['server'] = 'Tranquility'
    
    try:
        status = api.Server.ServerStatus()
    
        if status.serverOpen == 'True':
            d['status'] = 'Online'
        else:
            d['status'] = 'Offline'
        d['players'] = status.onlinePlayers
    
    except:
        d['status'] = 'Unknown. API Unavailable.'
        d['players'] = 0
    
    return render_to_response('status.html', d,
                              context_instance=RequestContext(request))
