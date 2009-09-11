from django.template import RequestContext

from lib import eveapi
from lib.cachehandler import MyCacheHandler
from lib.formatting import NavigationElement
from lib.jinja import render_to_response
import settings

api = eveapi.EVEAPIConnection(cacheHandler=MyCacheHandler(debug=settings.DEBUG, throw=False)).context(version=2)

status_nav = NavigationElement(
    "Tranquility Status", "/status/", '74_13',
    'Current status of the Tranquility cluster.'
)

def status(request):
    try:
        stats = api.Server.ServerStatus()
        players = stats.onlinePlayers
        if stats.serverOpen == 'True':
            status = 'Online'
        else:
            status = 'Offline'
    except:
        status = 'Unknown. API Unavailable.'
        players = 0

    return render_to_response('status.html', {
        'nav': (status_nav,),
        'server': 'Tranquility',
        'status': status,
        'players': players,
    }, request)
