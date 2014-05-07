from common_settings import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
ALLOWED_HOSTS = ['*']
TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'fr'
DEFAULT_FROM_EMAIL = "noreply@example.org"
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', 
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

INSTALLED_APPS += (
    'django_jenkins',
)

JENKINS_TASKS = (
#    'django_jenkins.tasks.run_pylint',
#    'django_jenkins.tasks.run_pep8',
    'django_jenkins.tasks.with_coverage',
#    'django_jenkins.tasks.dir_tests',
#    'django_jenkins.tasks.run_csslint',
#    'django_jenkins.tasks.run_pyflakes',
)

COVERAGE_EXCLUDES_FOLDERS = ['possum/base/migrations/*',
                             'possum/stats/migrations/*', 'env/*']
