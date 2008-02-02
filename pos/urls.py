from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'eve.pos.views.list'),
    (r'^(?P<station_id>\d+)/detail/$', 'eve.pos.views.detail'),
    (r'^(?P<station_id>\d+)/refuel/$', 'eve.pos.views.refuel'),
    (r'^profit/$', 'eve.pos.views.profit'),
    (r'^consumption/$', 'eve.pos.views.consumption'),
)