# $Id$
from django.conf.urls.defaults import include, patterns, handler500, handler404 # need the handlers for django.
from eve.settings import STATIC_DIR, DEBUG
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    
    (r'^trade/', include('eve.trade.urls')),
    (r'^pos/', include('eve.pos.urls')),
    (r'^mining/', include('eve.mining.urls')),
    (r'^user/', include('eve.user.urls')),
    
    (r'^debug/', include('eve.debug.urls')),

    (r'^$', 'eve.views.home'),
    
    (r'^status/$', 'eve.status.views.status'),

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

    (r'^login/$', 'eve.user.views.login'),
    (r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'user_logout.html'}),
    
)

if DEBUG:
    urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': STATIC_DIR}),
    )
