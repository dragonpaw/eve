from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^ops/$', 'eve.mining.views.op_list'),
    (r'^op/(?P<id>\d+)/$', 'eve.mining.views.op_detail'),
)