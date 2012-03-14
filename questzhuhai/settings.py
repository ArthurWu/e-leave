# Django settings for mysite project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

import os
ROOTDIR = os.path.dirname(__file__)
UPLOADDIR = os.path.join(ROOTDIR, 'uploaded/')
REPORT_FILES = os.path.join(ROOTDIR, 'report files/')
REPORT_TEMPLATE = os.path.join(ROOTDIR, 'templates/report/')

LEAVESYSTEMHOST = 'http://arthur10:3134'
LEAVE_REPORT_FIRST_DAY = 10
LEAVE_REPORT_SECEND_DAY = 25
LEAVE_RECORD_REPORT_DAY = 25

from common.logger import log
log.Init(ROOTDIR + '\Logs\WebReports.log')

# use old style settings for non-django dbapi tests
DATABASE_NAME = 'HrAdmin'
DATABASE_HOST = 'arthur10'
DATABASE_USER = 'sa'
DATABASE_PASSWORD = '1'
DATABASE_COMMAND_TIMEOUT = 60
DATABASE_ENGINE = 'sqlserver_ado'

#django required database settings
DATABASES = {
    'default': {
        'NAME': DATABASE_NAME,
        'ENGINE': 'sqlserver_ado',
        'HOST': DATABASE_HOST,
        'USER': DATABASE_USER,
        'PASSWORD': DATABASE_PASSWORD,
        'COMMAND_TIMEOUT': DATABASE_COMMAND_TIMEOUT,
        'OPTIONS' : {
            'use_mars': True,
            'provider': 'SQLNCLI10',
            'extra_params': 'MARS Connection=True',
        },
    }
}


# DATABASES = {
    # 'default': {
        # 'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        # 'NAME': os.path.join(ROOTDIR, 'database\model.sqlite'),  # Or path to database file if using sqlite3.
        # 'USER': '',                      # Not used with sqlite3.
        # 'PASSWORD': '',                  # Not used with sqlite3.
        # 'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        # 'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    # }
# }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

DATE_FORMAT = 'N j, Y'
DATETIME_FORMAT = 'N j, Y'
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.normpath(os.path.join(ROOTDIR, 'templates/static/'))

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# URL prefix for admin static files -- CSS, JavaScript and images.
# Make sure to use a trailing slash.
# Examples: "http://foo.com/static/admin/", "/static/admin/".
ADMIN_MEDIA_PREFIX = '/static/admin/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(ROOTDIR, 'templates/static/'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
	'compressor.finders.CompressorFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@b3zs+bd8x@rk-qay534)fqq&y(h%9&i#07-mun((iv4fclc!#'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
	"django.contrib.auth.context_processors.auth",
	"django.core.context_processors.debug",
	"django.core.context_processors.i18n",
	"django.core.context_processors.media",
	"django.core.context_processors.static",
	"django.contrib.messages.context_processors.messages",
	"context_processor.employee",
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'middleware.security.RequestHandlerMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	os.path.join(ROOTDIR, 'templates'),
	#os.path.join(ROOTDIR, 'leave/templates'),
	
)

INSTALLED_APPS = (
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.sites',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	# Uncomment the next line to enable the admin:
	'django.contrib.admin',
	# Uncomment the next line to enable admin documentation:
	'django.contrib.admindocs',
	'django.contrib.messages',
	'maitenance',
	'leave',
	'compressor',
	#'south',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

#CACHES = {
#	'default': {
#		'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache'
#	}
#}

#CACHE_BACKEND = 'memcached://10.30.147.197:3149/'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
    # 'version': 1,
    # 'disable_existing_loggers': False,
    # 'handlers': {
        # 'mail_admins': {
            # 'level': 'ERROR',
            # 'class': 'django.utils.log.AdminEmailHandler'
        # }
    # },
    # 'loggers': {
        # 'django.request': {
            # 'handlers': ['mail_admins'],
            # 'level': 'ERROR',
            # 'propagate': True,
        # },
    # }
# }

#EMAIL_USE_TLS = True
#EMAIL_HOST = '10.1.0.160'
#EMAIL_HOST_USER = 'Arthur.Wu@quest.com'
#EMAIL_HOST_PASSWORD = 'wzhai34WZH4'
#EMAIL_PORT = '25'

#EMAIL_USE_TLS = True
#EMAIL_HOST = 'smtp.gmail.com'
#EMAIL_HOST_USER = 'arthur.wu.34@gmail.com'
#EMAIL_HOST_PASSWORD = 
#EMAIL_PORT = 587
