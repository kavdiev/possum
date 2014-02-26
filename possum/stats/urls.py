from django.conf.urls import patterns, url

urlpatterns = patterns('possum.stats.views',
                       url(r'^update/$', 'update', name='stats_update'),
                       url(r'^daily/$', 'daily', name='stats_daily'),
                       url(r'^weekly/$', 'weekly', name='stats_weekly'),
                       url(r'^monthly/$', 'monthly', name='stats_monthly'),
                       url(r'^charts/$', 'charts', name='stats_charts'),
                       url(r'^charts/(?P<choice>[a-zA-Z0-9_-]+)/$', 'charts',
                           name='stats_charts'),
                      )


