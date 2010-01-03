#!/usr/bin/env python

from django.conf.urls.defaults import patterns

urlpatterns = patterns('eve.ccp.views',
    #(r'^npc/$', 'npc_groups'),
    #(r'^npc/(?P<slug>[\w\-]+)/$', 'npc_group'),

    (r'^solarsystem/(?P<name>.*)/$', 'solarsystem'),
    (r'^constellation/(?P<name>.*)/$', 'constellation'),
    (r'^region/(?P<slug>[\w\-]+)/$', 'region'),
    (r'^regions/$', 'region_list'),

    (r'^item/(?P<slug>[\w\-]+)/$', 'item'),
    (r'^item/(?P<slug>[\w\-]+)/uses/$', 'item_uses'),
    (r'^items/$', 'group_index'),
    (r'^items/(?P<slug>[\w\-]+)/$', 'group'),

    (r'^sov/changes/$', 'sov_changes'),

)
