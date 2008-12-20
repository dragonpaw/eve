# Django settings for eve project.
# $Id$

from database_settings import *
import sys
import deseb
import os

os.environ['TZ'] = 'UTC'

ADMINS = (
    ('Ash', 'ash@dragonpaw.org'),
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

TEMPLATE_DEBUG = DEBUG

DEFAULT_FROM_EMAIL='ash@dragonpaw.org'

# Necessary for (mt) Django GridContainer
FORCE_SCRIPT_NAME = ""

# Local time zone for this installation. All choices can be found here:
# http://www.postgresql.org/docs/8.1/static/datetime-keywords.html#DATETIME-TIMEZONE-SET-TABLE
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Pacific'

# Language code for this installation. All choices can be found here:
# http://www.w3.org/TR/REC-html40/struct/dirlang.html#langcodes
# http://blogs.law.harvard.edu/tech/stories/storyReader$15
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'eve.tracker.middleware.ChangeLogMiddleware'
)

ROOT_URLCONF = 'eve.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    "/home/56240/users/.home/container/eve/_templates",
    #"/home/ash/django-sites/eve/_templates",
    "C:/django-sites/eve/_templates",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'eve.lib.context_processors.borwser_id',
)

AUTHENTICATION_BACKENDS = (
    #"email-auth.EmailBackend",
    "django.contrib.auth.backends.ModelBackend",
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.flatpages',
    'django.contrib.markup',
    'django_extensions',
    'eve.mining',
    'eve.tracker',
    'eve.ccp',
    'eve.user',
    'eve.emails',
    'eve.trade',
    'eve.pos',
)

if sys.platform == 'win32':
    STATIC_DIR = 'C:/django-sites/eve/_static/'
else:
    STATIC_DIR = '/home/56240/users/.home/domains/eve.magicwidget.net/html/static'

AUTH_PROFILE_MODULE = 'user.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
