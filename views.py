from django.shortcuts import render_to_response
from django.template import RequestContext
from eve.trade.views import blueprint_nav, index_nav, transaction_nav
from eve.ccp.views import region_nav, item_nav
from eve.pos.views import pos_nav
from eve.user.views import user_nav
from eve.util.formatting import make_nav

about_nav = make_nav("About", "/about/", '07_15')
changelog_nav = make_nav("ChangeLog", "/changelog/", '10_16')
admin_nav = make_nav('Admin', '/admin/', '09_08')
login_nav = make_nav('Login', '/login/', '09_06')

def home(request):
    d = {}

    user = request.user
    
    objects = [about_nav, changelog_nav,
               region_nav, item_nav,
               index_nav,
    ]
    
    if user.is_authenticated() and user.is_staff:
        objects.append(admin_nav)
    
    if user.is_authenticated():
        objects.extend([blueprint_nav,
                       user_nav,
                       transaction_nav,
                       pos_nav,
                       ])
    else:
        objects.append(login_nav)
    
    objects.sort(lambda a,b: cmp(a['name'], b['name']))
    
    d['objects'] = objects
    d['title'] = "EVE Tool"
    d['nav'] = [ {'name':'EVE Magic Widget', 'get_absolute_url':'/'} ]
    return render_to_response('generic_menu.html', d, context_instance=RequestContext(request))    
