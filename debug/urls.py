from django.conf.urls.defaults import patterns, handler404, handler500

urlpatterns = patterns('',
    (r'^test404/$', handler404),
    (r'^test500/$', handler500),

    (r'^$', 'eve.debug.views.debug_menu'),

    (r'^request/$', 'eve.debug.views.debug_request'),
    (r'^loader/$', 'eve.debug.views.debug_loader'),
    (r'^memcached/$', 'eve.debug.views.memcached'),

)