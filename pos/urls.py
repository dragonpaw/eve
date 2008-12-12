from django.conf.urls.defaults import patterns

urlpatterns = patterns('eve.pos.views',
    (r'^$', 'pos_list'),
    
    (r'^(?P<station_id>\d+)/fuel/$', 'fuel_detail'),
    (r'^(?P<station_id>\d+)/profit/$', 'profit_detail'),
    (r'^(?P<station_id>\d+)/refuel/$', 'refuel'),
    (r'^(?P<station_id>\d+)/owner/$', 'owner'),
    (r'^(?P<station_id>\d+)/owner/(?P<character_id>\d+)/$', 'owner_set'),
    (r'^(?P<station_id>\d+)/reactions/$', 'setup_reactions'),
    #(r'^(?P<station_id>\d+)/grant/(?P<character_name>.+)/$', 'delegate_add'),
    #(r'^(?P<station_id>\d+)/revoke/(?P<character_name>.+)/$', 'delegate_delete'),

    (r'^profit/$', 'profit_list'),
    (r'^consumption/$', 'consumption'),
    
    (r'^helpers/$', 'monkey_list'),
)
