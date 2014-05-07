import os
from os.path import abspath, dirname, join, normpath
import random
import sys
#from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _


########## PATH CONFIGURATION
# Absolute filesystem path to this Django project directory.
DJANGO_ROOT = os.path.dirname(os.path.dirname(__file__))
SITE_NAME = "possum"
# Absolute filesystem path to the top-level project folder.
SITE_ROOT = dirname(DJANGO_ROOT)
# Add all necessary filesystem paths to our system path so that we can use
# python import statements.
sys.path.append(SITE_ROOT)
sys.path.append(normpath(join(DJANGO_ROOT, SITE_NAME, 'base')))
########## END PATH CONFIGURATION

########## Configuration de POSSUM
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/bills/'
# tmp est en memoire (tmpfs)
PATH_TICKET = normpath(join(DJANGO_ROOT, 'tickets'))
if not os.path.exists(PATH_TICKET):
    os.makedirs(PATH_TICKET)
# list of authorized permissions codename
PERMS = ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9']
########## END POSSUM CONFIGURATION

########## KEY CONFIGURATION
# Absolute filesystem path to the secret file which holds this project's
# SECRET_KEY. Will be auto-generated the first time this file is interpreted.
SECRET_FILE = normpath(join(DJANGO_ROOT, SITE_NAME, 'secret_key'))


def create_secret_key():
    ''' Try to load the SECRET_KEY from our SECRET_FILE. If that fails, then
    generate a random SECRET_KEY and save it into our SECRET_FILE for future
     loading. If everything fails, then just raise an exception. '''
    with open(abspath(SECRET_FILE), 'w') as f:
        SECRET_KEY_TEXT = "".join([random.choice("abcdefghijklmnopqrstuvwxyz"
                                                 "0123456789!@#$%^&*(-_=+)") \
                                   for i in range(50)])
        f.write(SECRET_KEY_TEXT)
    return SECRET_KEY_TEXT

try:
    if os.path.isfile(SECRET_FILE):
        SECRET_KEY_TEXT = open(SECRET_FILE).read()
        if not SECRET_KEY_TEXT:
            SECRET_KEY_TEXT = create_secret_key()
    else:
        SECRET_KEY_TEXT = create_secret_key()
    SECRET_KEY = SECRET_KEY_TEXT
except IOError as exc:
        raise Exception('Cannot open file `%s` for writing. (%s)'
                        % (SECRET_FILE, exc))

########## END KEY CONFIGURATION

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

SITE_ID = 1

# Supported languages
LANGUAGES = (
    ('fr', _('French')),
    ('en', _('English')),
    ('ru', _('Russian')),
)
LOCALE_PATHS = (normpath(join(DJANGO_ROOT, 'locale')), )

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = normpath(join(DJANGO_ROOT, SITE_NAME, 'media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = normpath(join(DJANGO_ROOT, SITE_NAME, 'static'))
#STATIC_ROOT = ''
if not os.path.isdir(STATIC_ROOT):
    os.mkdir(STATIC_ROOT)

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
#    normpath(join(DJANGO_ROOT, SITE_NAME, 'static')),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'possum.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'possum.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    normpath(join(DJANGO_ROOT, SITE_NAME, 'templates')),
)

LOCK_STATS = '/tmp/possum-stats.lock'
# CSS for colors on categories (auto update)
CAT_CSS = normpath(join(STATIC_ROOT, 'categories.css'))
if not os.path.isfile(CAT_CSS):
    # create an empty one
    open(CAT_CSS, "w")

INSTALLED_APPS = (
    'south',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'chartit',
    'possum.base',
    'possum.stats',
    'django_extensions',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_SERIALIZER = "django.contrib.sessions.serializers.PickleSerializer"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s %(module)s:%(lineno)d %(funcName)s] '
                      '%(levelname)-8s %(message)s',
            'datefmt': '%H:%M:%S'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
        'syslog': {
            'format': 'POSSUM: %(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
             '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'syslog': {
            'level': 'INFO',
            'class': 'logging.handlers.SysLogHandler',
            'address': '/dev/log',
            'formatter': 'syslog',
            'filters': ['require_debug_false'],
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
        },
        'mail_bugwatch': {
            'level': 'ERROR',
            'class': 'logging.handlers.SMTPHandler',
            'filters': ['require_debug_false'],
            'mailhost': 'localhost',
            'fromaddr': 'bugwatch@possum-software.org',
            'toaddrs': ['bugwatch@possum-software.org'],
            'subject': '[BUG] Houston, we have a problem.',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'possum': {
            'handlers': ['mail_admins', 'syslog', 'mail_bugwatch'],
            'level': 'WARNING',
        }
    }
}
