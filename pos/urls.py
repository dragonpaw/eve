from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'eve.pos.views.list'),
    (r'^(?P<station_id>\d+)/detail/$', 'eve.pos.views.detail'),
    (r'^(?P<station_id>\d+)/refuel/$', 'eve.pos.views.refuel'),
    (r'^(?P<station_id>\d+)/delegations/$', 'eve.pos.views.delegate_list'),
    (r'^(?P<station_id>\d+)/grant/(?P<character_name>.+)/$', 'eve.pos.views.delegate_add'),
    (r'^(?P<station_id>\d+)/revoke/(?P<character_name>.+)/$', 'eve.pos.views.delegate_delete'),
    (r'^profit/$', 'eve.pos.views.profit'),
    (r'^consumption/$', 'eve.pos.views.consumption'),
    
    (r'^helpers/$', 'eve.pos.views.monkey_list'),
    (r'^grant/(?P<grant>.+)/$', 'eve.pos.views.monkey_grant'),
    (r'^revoke/(?P<revoke>.+)/$', 'eve.pos.views.monkey_grant'),
)