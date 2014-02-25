from django.conf.urls import patterns, url

urlpatterns = patterns('possum.stats.views',
#                       url(r'^$', 'home', name='stats_home'),
                       url(r'^update/$', 'update', name='stats_update'),
                       url(r'^daily/$', 'daily', name='stats_daily'),
                       url(r'^weekly/$', 'weekly', name='stats_weekly'),
                       url(r'^monthly/$', 'monthly', name='stats_monthly'),
                      )

#urlpatterns += patterns('possum.base.views.manager.rapports',
    #url(r'^manager/rapports/$', 'rapports_daily', name='rapports_home'),

    #url(r'^manager/rapports/update/$', 'update_rapports', name='update_rapports'),
    #url(r'^manager/rapports/daily/$', 'rapports_daily', name='rapports_daily'),

    #url(r'^manager/rapports/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/vats/print/$', 'rapports_daily_vats_print', name='rapports_daily_vats_print'),
    #url(r'^manager/rapports/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/vats/send/$', 'rapports_daily_vats_send', name='rapports_daily_vats_send'),
    #url(r'^manager/rapports/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/print/$', 'rapports_daily_print', name='rapports_daily_print'),
    #url(r'^manager/rapports/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/send/$', 'rapports_daily_send', name='rapports_daily_send'),
    #url(r'^manager/rapports/weekly/$', 'rapports_weekly', name='rapports_weekly'),
    #url(r'^manager/rapports/weekly/(?P<year>\d{4})/(?P<week>\d+)/vats/print/$', 'rapports_weekly_vats_print', name='rapports_weekly_vats_print'),
    #url(r'^manager/rapports/weekly/(?P<year>\d{4})/(?P<week>\d+)/vats/send/$', 'rapports_weekly_vats_send', name='rapports_weekly_vats_send'),
    #url(r'^manager/rapports/weekly/(?P<year>\d{4})/(?P<week>\d+)/print/$', 'rapports_weekly_print', name='rapports_weekly_print'),
    #url(r'^manager/rapports/weekly/(?P<year>\d{4})/(?P<week>\d+)/send/$', 'rapports_weekly_send', name='rapports_weekly_send'),
    #url(r'^manager/rapports/monthly/$', 'rapports_monthly', name='rapports_monthly'),
    #url(r'^manager/rapports/monthly/(?P<year>\d{4})/(?P<month>\d+)/vats/print/$', 'rapports_monthly_vats_print', name='rapports_monthly_vats_print'),
    #url(r'^manager/rapports/monthly/(?P<year>\d{4})/(?P<month>\d+)/vats/send/$', 'rapports_monthly_vats_send', name='rapports_monthly_vats_send'),
    #url(r'^manager/rapports/monthly/(?P<year>\d{4})/(?P<month>\d+)/print/$', 'rapports_monthly_print', name='rapports_monthly_print'),
    #url(r'^manager/rapports/monthly/(?P<year>\d{4})/(?P<month>\d+)/send/$', 'rapports_monthly_send', name='rapports_monthly_send'),
#)

#urlpatterns += patterns('possum.base.views.manager.charts',
                        #url(r'^manager/charts/year/$', 'charts_year',
                            #name='charts_year'),
                        #url(r'^manager/charts/year/(?P<choice>[a-zA-Z0-9_-]+)/$',
                            #'charts_year', name='charts_year_with_argument'),
                        #)

