from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^blueprints/$', 'eve.trade.views.blueprint_list'),
    (r'^blueprint/(?P<slug>[\w\-]+)/$', 'eve.trade.views.blueprint_edit'),
    
    (r'^indexes/$', 'eve.trade.views.market_index_list'),
    (r'^index/customize/(?P<id>\d+)/$', 'eve.trade.views.fixed_price_update'),
    (r'^index/(?P<name>.+)/$', 'eve.trade.views.market_index_detail'),

    (r'^transactions/$', 'eve.trade.views.transactions'),
    (r'^transaction/(?P<id>\d+)/$', 'eve.trade.views.transaction_detail'),
    (r'^journal/(?P<id>\d+)/$', 'eve.trade.views.journal_detail'),
    
    (r'^salvage/$', 'eve.trade.views.salvage'),
)