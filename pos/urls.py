from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'eve.pos.views.list'),
    (r'^detail/(?P<station_id>\d+)/$', 'eve.pos.views.detail'),
)