from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'eve.user.views.main'),
    (r'^character/(?P<id>\d+)/$', 'eve.user.views.character'),
    
    (r'^add/$', 'eve.user.views.account_edit'),
    
    (r'^api-log/$', 'eve.user.views.account_log'),
    
    (r'^account/(\d+)/$', 'eve.user.views.account_overview'),
    (r'^account/(\d+)/edit/$', 'eve.user.views.account_edit'),
    (r'^account/(\d+)/refreshing/$', 'eve.user.views.account_refresh_warning'),
    (r'^account/(\d+)/refresh/$', 'eve.user.views.account_refresh'),
    
    (r'^create/$', 'eve.user.views.user_creation'),
)