from django.conf.urls import patterns, include, url

#from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('possum.base.views',
    url(r'^$', 'home', name='home'),
#    (r'^accueil$', 'accueil'),

    url(r'^carte/categories/$', 'categories'),
    url(r'^carte/categories/new/$', 'categories_new'),
    url(r'^carte/categories/(?P<cat_id>\d+)/less/$', 'categories_less_priority'),
    url(r'^carte/categories/(?P<cat_id>\d+)/more/$', 'categories_more_priority'),
    url(r'^carte/categories/(?P<cat_id>\d+)/less-10/$', 'categories_less_priority', {'nb': 10}),
    url(r'^carte/categories/(?P<cat_id>\d+)/more-10/$', 'categories_more_priority', {'nb': 10}),
    url(r'^carte/categories/(?P<cat_id>\d+)/surtaxable/$', 'categories_surtaxable'),
    url(r'^carte/categories/(?P<cat_id>\d+)/change/$', 'categories_change'),
    url(r'^carte/categories/(?P<cat_id>\d+)/alcool/$', 'categories_alcool'),
    url(r'^carte/categories/(?P<cat_id>\d+)/delete/$', 'categories_delete'),
    url(r'^carte/categories/(?P<cat_id>\d+)/disable_surtaxe/$', 'categories_disable_surtaxe'),

    url(r'^carte/products/$', 'categories'),
    url(r'^carte/products/cat/(?P<cat_id>\d+)/$', 'products'),
    url(r'^carte/products/cat/(?P<cat_id>\d+)/enable/$', 'products', {'only_enable': True}),
    url(r'^carte/products/(?P<product_id>\d+)/change/$', 'products_change'),
    url(r'^carte/products/(?P<product_id>\d+)/details/$', 'products_details'),
    url(r'^carte/products/cat/(?P<cat_id>\d+)/new/$', 'products_new'),

    url(r'^pos/$', 'pos'),
    url(r'^bills/$', 'factures'),
    url(r'^bill/new/$', 'bill_new'),
    url(r'^bill/(?P<bill_id>\d+)/table/select/$', 'table_select'),
    url(r'^bill/(?P<bill_id>\d+)/table/set/(?P<table_id>\d+)/$', 'table_set'),
    url(r'^bill/(?P<bill_id>\d+)/couverts/select/$', 'couverts_select'),
    url(r'^bill/(?P<bill_id>\d+)/couverts/set/(?P<number>\d+)/$', 'couverts_set'),
    url(r'^bill/(?P<bill_id>\d+)/category/select/$', 'category_select'),
    url(r'^bill/(?P<bill_id>\d+)/product/add/(?P<product_id>\d+)/$', 'product_add'),
    url(r'^bill/(?P<bill_id>\d+)/product/(?P<category_id>\d+)/select/$', 'product_select'),
    url(r'^bill/(?P<bill_id>\d+)/sold/(?P<sold_id>\d+)/category/(?P<category_id>\d+)/select/$', 'subproduct_select'),
    url(r'^bill/(?P<bill_id>\d+)/sold/(?P<sold_id>\d+)/view/$', 'sold_view'),
    url(r'^bill/(?P<bill_id>\d+)/sold/(?P<sold_id>\d+)/delete/$', 'sold_delete'),
    url(r'^bill/(?P<bill_id>\d+)/sold/(?P<sold_id>\d+)/(?P<product_id>\d+)/add/$', 'subproduct_add'),
    url(r'^bill/(?P<bill_id>\d+)/delete/$', 'bill_delete'),
    url(r'^bill/(?P<bill_id>\d+)/$', 'bill_view'),
    url(r'^jukebox/$', 'jukebox'),
    url(r'^manager/$', 'manager'),
    url(r'^kitchen/$', 'kitchen'),

    url(r'^profile/$', 'profile'),

    url(r'^users/$', 'users'),
    url(r'^users/new/$', 'users_new'),
    url(r'^users/(?P<user_id>\d+)/passwd/$', 'users_passwd'),
    url(r'^users/(?P<user_id>\d+)/active/$', 'users_active'),
    url(r'^users/(?P<user_id>\d+)/change/$', 'users_change'),
    url(r'^users/(?P<user_id>\d+)/perm/(?P<codename>p\d+)/$', 'users_change_perm'),

)

urlpatterns += patterns('',
    url(r'^users/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout_then_login'),
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
