from django.conf.urls.defaults import patterns

urlpatterns = patterns('',
    (r'^$', 'eve.user.views.main'),
    (r'^character/(?P<id>\d+)/$', 'eve.user.views.character'),
    
    (r'^add/$', 'eve.user.views.account'),
    (r'^account/(?P<id>\d+)/$', 'eve.user.views.account'),
    
    (r'^create/$', 'eve.user.views.user_creation'),
)