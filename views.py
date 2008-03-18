from django.shortcuts import render_to_response
from django.template import RequestContext
from eve.trade.views import blueprint_nav, index_nav, transaction_nav, salvage_nav
from eve.ccp.views import region_nav, item_nav, sov_nav
from eve.pos.views import pos_nav
from eve.user.views import user_nav, user_create_nav, login_nav
from eve.lib.formatting import make_nav
from eve.tracker.views import changelog_nav
from eve.debug.views import debug_nav
from eve.status.views import status_nav

about_nav = make_nav("About", "/about/", '07_15', note='The origins of the Widget.')
admin_nav = make_nav('Admin', '/admin/', '09_08', note='Thou art God.')
logout_nav = make_nav('Logout', '/logout/', '07_07', 
                      note='Log out if you like. (Or if you share your computer.)')
ship_fit_nav = make_nav('Ship Fitting', '/fitting/', '09_05',
                        note='A little tool to assist you with fitting a ship.')
features_nav = make_nav('Features', '/features/', '06_07',
                        note='Reasons why you want to use the Widget.')

def home(request):
    d = {}

    user = request.user
    
    objects = [about_nav, changelog_nav,
               region_nav, item_nav,
               index_nav, sov_nav, 
               features_nav, salvage_nav,
               status_nav,
    ]
    d['inline_nav'] = objects
    
    if user.is_authenticated() and user.username in ('ash', 'Ductape'):
        objects.append(ship_fit_nav)
    
    if user.is_authenticated() and user.is_staff:
        objects.append(admin_nav)
        objects.append(debug_nav)
    
    if user.is_authenticated():
        objects.extend([blueprint_nav,
                       user_nav,
                       transaction_nav,
                       pos_nav,
                       logout_nav,
                       ])
    else:
        objects.extend([login_nav, user_create_nav])
    
    objects.sort(key=lambda x: x.name)
    
    return render_to_response('generic_menu.html', d, context_instance=RequestContext(request))    