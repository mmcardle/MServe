########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-03-25
#	Created for Project :		PrestoPrime
#
########################################################################
# Django settings for mserve project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf-8'

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(filename)s %(lineno)d %(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S',
    #change as needed
    filename='/var/mserve/mserve.log',
    filemode='a'
)

import platform
HOSTNAME = platform.uname()[1]

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

LOG_FILE="django_log"

MANAGERS = ADMINS

#DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
#DATABASE_NAME = '/var/mserve/mservedb'             # Or path to database file if using sqlite3.
#DATABASE_USER = ''             # Not used with sqlite3.
#DATABASE_PASSWORD = ''         # Not used with sqlite3.
#DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
#DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'mservedb'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'pass'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/var/mserve/www-root/mservemedia/'
THUMB_ROOT = '/var/mserve/www-root/mservethumbs/'
THUMB_PATH = "/mservethumbs/"

# MServe Specific Settings
STORAGE_ROOT = '/var/mserve/mservedata/'
SECDOWNLOAD_ROOT = '/var/mserve/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/mservemedia/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'jfdp(uxhhp)c#+j_f#s9_3wc0)qs58aqz_n^jx5b5_swz59==5'

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
    'dataservice.middleware.AuthMiddleware',
    'dataservice.middleware.ResponseMiddleware',
    'request.middleware.RequestMiddleware'
)

## OPEN ID ###

AUTHENTICATION_BACKENDS = (
    'django_openid_auth.auth.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)
OPENID_CREATE_USERS = True
OPENID_UPDATE_DETAILS_FROM_SREG = True

ROOT_URLCONF = 'mserve.urls'

TEMPLATE_DIRS = (

    # Change to where your checkout is
    "/opt/mserve/pp-dataservice/mserve/templates",
    # Change to where the admin templates are
    "/usr/lib/pymodules/python2.6/django/contrib/admin/templates/",
    
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "myuser"
BROKER_PASSWORD = "mypassword"
BROKER_VHOST = "myvhost"

CELERY_DEFAULT_QUEUE = "local_tasks"
CELERY_QUEUES = {
    "local_tasks": {
        "binding_key": "local.#",
    },
    "remote_tasks": {
        "binding_key": "remote.#",
    },
}
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
CELERY_DEFAULT_ROUTING_KEY = "task.default"
#CELERY_RESULT_BACKEND = "amqp"

class Router(object):

    def route_for_task(self, task, args=None, kwargs=None):
        if task.endswith(".remote"):
            return {
                    "exchange": "tasks",# Not Needed (will go to default)
                    "exchange_type": "topic",# Not Needed (will go to default)
                    "routing_key": "remote.1"
                    }
        return None

CELERY_ROUTES = (Router(), )
CELERY_IMPORTS = ("dataservice.tasks", "jobservice.tasks", "prestoprime.tasks" )

import djcelery
djcelery.setup_loader()

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django_openid_auth',
    'dataservice',
    'mserveoauth',
    'piston',
    'webdav',
    'jobservice',
    'prestoprime',
    'djcelery',
    'request'
)

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

REQUEST_IGNORE_PATHS = (
    r'^admin/',
)

AUTH_PROFILE_MODULE = "dataservice.mserveprofile"

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL='/'

# JOB CONFIG
USE_CELERY=True
DEFAULT_ACCESS_SPEED = "unlimited"

# Define Sizes
thumbsize = (210,128)
postersize = (420,256)
wuxga = (1920,1200)

# For FGCI
FORCE_SCRIPT_NAME = ''