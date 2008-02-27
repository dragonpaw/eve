# $Id$
from django.conf.urls.defaults import include, patterns
from eve.settings import STATIC_DIR, DEBUG

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    
    (r'^trade/', include('eve.trade.urls')),
    (r'^pos/', include('eve.pos.urls')),
    (r'^mining/', include('eve.mining.urls')),
    (r'^user/', include('eve.user.urls')),
    
    (r'^debug/', include('eve.debug.urls')),

    (r'^$', 'eve.views.home'),

    # CCP Items count as part of the root.
    (r'^solarsystem/(?P<name>.*)/$', 'eve.ccp.views.solarsystem'),
    (r'^constellation/(?P<name>.*)/$', 'eve.ccp.views.constellation'),
    (r'^region/(?P<slug>[\w\-]+)/$', 'eve.ccp.views.region'),
    (r'^regions/$', 'eve.ccp.views.region_list'),
    (r'^item/(?P<slug>[\w\-]+)/$', 'eve.ccp.views.item'),
    (r'^items/$', 'eve.ccp.views.group_index'),
    (r'^items/(?P<slug>[\w\-]+)/$', 'eve.ccp.views.group'),

    (r'^sov/changes/$', 'eve.ccp.views.sov_changes'),
    
    (r'^changelog/$', 'eve.tracker.views.changelog'),
    (r'^changelog/(?P<when>\d{4}-\d\d-\d\d-\d\d:\d\d)/$', 'eve.tracker.views.changelog'),

    (r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'auth_login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'auth_logout.html'}),
    
)

if DEBUG:
    urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': STATIC_DIR}),
    )
