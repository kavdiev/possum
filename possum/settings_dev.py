from common_settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

########## DJANGO-DEBUG-TOOLBAR CONFIGURATION
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

INSTALLED_APPS += (
    'debug_toolbar',
)

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr-fr'

# IPs allowed to see django-debug-toolbar output.
INTERNAL_IPS = ('127.0.0.1',)

DEBUG_TOOLBAR_CONFIG = {
    # If set to True (default), the debug toolbar will show an intermediate
    # page upon redirect so you can view any debug information prior to
    # redirecting. This page will provide a link to the redirect destination
    # you can follow when ready. If set to False, redirects will proceed as
    # normal.
    'INTERCEPT_REDIRECTS': False,

    # If not set or set to None, the debug_toolbar middleware will use its
    # built-in show_toolbar method for determining whether the toolbar should
    # show or not. The default checks are that DEBUG must be set to True and
    # the IP of the request must be in INTERNAL_IPS. You can provide your own
    # method for displaying the toolbar which contains your custom logic. This
    # method should return True or False.
    'SHOW_TOOLBAR_CALLBACK': None,

    # An array of custom signals that might be in your project, defined as the
    # python path to the signal.
    'EXTRA_SIGNALS': [],

    # If set to True (the default) then code in Django itself won't be shown in
    # SQL stacktraces.
    'HIDE_DJANGO_SQL': True,

    # If set to True (the default) then a template's context will be included
    # with it in the Template debug panel. Turning this off is useful when you
    # have large template contexts, or you have template contexts with lazy
    # datastructures that you don't want to be evaluated.
    'SHOW_TEMPLATE_CONTEXT': True,

    # If set, this will be the tag to which debug_toolbar will attach the debug
    # toolbar. Defaults to 'body'.
    'TAG': 'body',
}
########## END DJANGO-DEBUG-TOOLBAR CONFIGURATION

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': normpath(join(DJANGO_ROOT, 'possum.db')),  # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        'HOST': '',  # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '',  # Set to empty string for default.
    }
}

