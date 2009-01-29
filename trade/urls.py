from django.conf.urls.defaults import patterns

urlpatterns = patterns('eve.trade.views',
    (r'^blueprints/$', 'blueprint_list'),
    (r'^blueprint/(?P<slug>[\w\-]+)/$', 'blueprint_edit'),

    (r'^indexes/$', 'market_index_list'),
    (r'^index/customize/(?P<id>\d+)/$', 'fixed_price_update'),
    (r'^index/(?P<name>.+)/$', 'market_index_detail'),

    (r'^transactions/$', 'transactions'),
    (r'^transaction/(?P<id>\d+)/$', 'transaction_detail'),
    (r'^journal/(?P<id>\d+)/$', 'journal_detail'),

    (r'^salvage/$', 'salvage'),
)
