from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^blueprints/$', 'eve.trade.views.blueprint_list'),
    (r'^blueprints/edit/$', 'eve.trade.views.blueprint_edit'),
    (r'^blueprints/edit/(?P<item_id>\d+)/$', 'eve.trade.views.blueprint_edit'),
    (r'^indexes/$', 'eve.trade.views.market_index_list'),
    (r'^index/(?P<id>\d+)/$', 'eve.trade.views.market_index_detail'),
    (r'^transactions/$', 'eve.trade.views.transactions'),
    (r'^transaction/(?P<id>\d+)/$', 'eve.trade.views.transaction_detail'),

)