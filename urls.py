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
    ('', include('eve.ccp.urls')),


    (r'^changelog/$', 'eve.tracker.views.changelog'),
    (r'^changelog/(?P<when>\d{4}-\d\d-\d\d-\d\d:\d\d)/$', 'eve.tracker.views.changelog'),
)

if DEBUG:
    urlpatterns += patterns('',
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': STATIC_DIR}),
    )
