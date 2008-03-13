from django.shortcuts import render_to_response
from django.template import RequestContext

from eve.lib.formatting import make_nav
from eve.status.models import Tranquility

status_nav = make_nav("Tranquility Status", "/status/", '74_13', 
                      'Current status of the Tranquility cluster.')

def status(request):
    d = {}
    d['nav'] = [status_nav]
    
    server = Tranquility()
    server.update_status()
    
    d['server'] = server
    return render_to_response('status.html', d,
                              context_instance=RequestContext(request))
