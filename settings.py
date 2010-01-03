# Django settings for eve project.

from database_settings import *
import deseb
import logging, logging.handlers
import os
import sys
try:
    import pwd
    user = pwd.getpwuid(os.getuid())[0]
except ImportError:
    user = 'none'

ROOTDIR = os.path.abspath(os.path.dirname(__file__))

os.environ['TZ'] = 'UTC'

ADMINS = (
    ('Ash', 'ash@dragonpaw.org'),
    # ('Your Name', 'your_email@domain.com'),
)

INTERNAL_IPS = ('127.0.0.1', '10.0.2.2')

MANAGERS = ADMINS

TEMPLATE_DEBUG = False

LOGFILE = os.path.join(ROOTDIR, 'log', "%s-django.log" % user)

DEFAULT_FROM_EMAIL='ash@dragonpaw.org'

# Necessary for fcgi
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
MEDIA_ROOT = os.path.join(ROOTDIR, '_static')

# URL that handles the media served from MEDIA_ROOT.
# Example: "http://media.lawrence.com"
MEDIA_URL = '/static'

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

MIDDLEWARE_CLASSES = [
    #'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'eve.lib.jinja_flatpage.middleware.FlatpageFallbackMiddleware',
    'eve.tracker.middleware.ChangeLogMiddleware',

    #'maintenancemode.middleware.MaintenanceModeMiddleware',
]
#if DEBUG:
#    MIDDLEWARE_CLASSES.append('debug_toolbar.middleware.DebugToolbarMiddleware')

ROOT_URLCONF = 'eve.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #"/home/ash/django-sites/eve/_templates",
    #"C:/django-sites/eve/_templates",
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
    'eve.debug',
    'eve.mining',
    'eve.tracker',
    'eve.ccp',
    'eve.user',
    'eve.trade',
    'eve.pos',
    'eve.status',
    'eve.lib',
)
#if DEBUG:
#    INSTALLED_APPS.append('debug_toolbar')

CACHE_BACKEND = "memcached://127.0.0.1:11211/"
CACHE_MIDDLEWARE_KEY_PREFIX = 'eve_widget'

AUTH_PROFILE_MODULE = 'user.UserProfile'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/user/login/'

MAINTENANCE_MODE = True

# Big ugly logging setup handler.
if len(logging.getLogger('').handlers) == 0:
    root = logging.getLogger('')

    handler = logging.handlers.RotatingFileHandler(
        LOGFILE, maxBytes=500000, backupCount=2)
    handler.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(asctime)s %(name)-35s: %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)

    # add the handler to the root logger
    root.addHandler(handler)
    #logging.getLogger('MARKDOWN').setLevel(logging.INFO)

    if DEBUG:
        root.setLevel(logging.DEBUG)
        stream = logging.StreamHandler()
        stream.setLevel(logging.DEBUG)
        root.addHandler( stream )
    else:
        logging.getLogger('').setLevel(logging.INFO)
        email = logging.handlers.SMTPHandler(EMAIL_HOST,
                                             DEFAULT_FROM_EMAIL,
                                             [x[1] for x in ADMINS],
                                             'EVE Widget Error!')
        email.setLevel(logging.ERROR)
        logging.getLogger('').addHandler(email)

    logging.set_up_done=True
    logging.debug("Logging started.")