from django.conf.urls.defaults import *
#from django.contrib import databrowse
#databrowse.site.register(Character)
#databrowse.site.register()

urlpatterns = patterns('',
    (r'^admin/', include('django.contrib.admin.urls')),
    
    (r'^trade/', include('eve.trade.urls')),
    (r'^pos/', include('eve.pos.urls')),

    (r'^$', 'eve.views.home'),

    # CCP Items count as part of the root.
    (r'^solarsystem/(?P<name>.*)/$', 'eve.ccp.views.solarsystem'),
    (r'^constellation/(?P<name>.*)/$', 'eve.ccp.views.constellation'),
    (r'^region/(?P<name>.*)/$', 'eve.ccp.views.region'),
    (r'^regions/$', 'eve.ccp.views.region_list'),
    (r'^changelog/$', 'eve.tracker.views.changelog'),
    (r'^item/(?P<item_id>\d+)/$', 'eve.ccp.views.item'),
    (r'^group/$', 'eve.ccp.views.group_index'),
    (r'^group/(?P<group_id>\d+)/$', 'eve.ccp.views.group'),

    (r'^user/$', 'eve.user.views.main'),

    (r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'auth_login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout',
        {'template_name': 'auth_logout.html'}),

    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'c:/django-sites/eve/_static'}),
)
