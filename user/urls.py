from django.conf.urls.defaults import patterns

urlpatterns = patterns('eve.user.views.',
    (r'^$', 'main'),
    (r'^character/(?P<id>\d+)/$', 'character'),

    (r'^add/$', 'account_edit'),

    (r'^api-log/$', 'account_log'),

    (r'^account/(\d+)/$', 'account_overview'),
    (r'^account/(\d+)/edit/$', 'account_edit'),
    (r'^account/(\d+)/refreshing/$', 'account_refresh_warning'),
    (r'^account/(\d+)/refresh/$', 'account_refresh'),

    (r'^create/$', 'user_creation'),

    # The built-in one doesn't offer a reset key.
    (r'lost/$', 'account_password_lost'),
    (r'recover/(?P<key>\w+)/$', 'account_password_found'),
)
