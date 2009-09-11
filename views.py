from eve.lib.jinja import render_to_response
from django.template import RequestContext
from trade.views import blueprint_nav, index_nav, transaction_nav, salvage_nav
from ccp.views import region_nav, item_nav, sov_nav, npc_nav
from pos.views import pos_nav
from user.views import user_nav, user_create_nav, login_nav, logout_nav
from lib.formatting import NavigationElement
from tracker.views import changelog_nav
from debug.views import debug_nav
from status.views import status_nav

about_nav = NavigationElement(
    "About", "/about/", '07_15', note='The origins of the Widget.'
)
admin_nav = NavigationElement(
    'Admin', '/admin/', '09_08', note='Thou art God.'
)
#ship_fit_nav = NavigationElement(
#    'Ship Fitting', '/fitting/', '09_05', note='A little tool to assist you with fitting a ship.'
#)
features_nav = NavigationElement(
    'Features', '/features/', '06_07', note='Why you want to use the Widget.'
)

def home(request):
    user = request.user

    objects = [about_nav, changelog_nav,
               region_nav, item_nav,
               index_nav, sov_nav,
               features_nav, salvage_nav,
               status_nav, npc_nav,
    ]

    if user.is_authenticated():
        objects.append(blueprint_nav)
        objects.append(user_nav)
        objects.append(transaction_nav)
        objects.append(pos_nav)
        objects.append(logout_nav)
        if user.is_staff:
            objects.append(admin_nav)
            objects.append(debug_nav)
    else:
        objects.append(login_nav)
        objects.append(user_create_nav)

    objects.sort(key=lambda x: x.name)

    return render_to_response('generic_menu.html', {
        'inline_nav': objects,
        'request': request,
    }, request)
