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

DEBUG = False
TEMPLATE_DEBUG = DEBUG
DEFAULT_CHARSET = 'utf-8'

import os

try:
    from settings_dev import *
except ImportError:
    MSERVE_HOME='/opt/mserve'
    MSERVE_DATA='/var/opt/mserve-data'
    MSERVE_LOG='/var/log/mserve'
    DBNAME='mservedb'

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(pathname)s %(lineno)d %(asctime)s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M:%S',
    #change as needed
    filename=os.path.join(MSERVE_LOG, 'mserve.log'),
    filemode='a'
)

import platform
HOSTNAME = platform.uname()[1]

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

LOG_FILE="django_log"

MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
	'NAME' : DBNAME,             # Or path to database file if using sqlite3.
	'USER' : 'root',        # Not used with sqlite3.
	'PASSWORD' : 'pass',       # Not used with sqlite3.
	'HOST' : '',            # Set to empty string for localhost. Not used with sqlite3.
	'PORT' : '',            # Set to empty string for default. Not used with sqlite3.
    }
}

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
MEDIA_ROOT = os.path.join(MSERVE_DATA, 'mservemedia') 
THUMB_ROOT = os.path.join(MSERVE_DATA, 'www-root', 'mservethumbs')
THUMB_PATH = "/mservethumbs/"

# MServe Specific Settings
STORAGE_ROOT = os.path.join(MSERVE_DATA, 'mservedata')
BACKUP_ROOT = os.path.join(MSERVE_DATA, 'mservebackup')
TESTDATA_ROOT = os.path.join(STORAGE_ROOT, 'test-data')
SECDOWNLOAD_ROOT = os.path.join(MSERVE_DATA)

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
    os.path.join(MSERVE_HOME, "templates"),
    #"/opt/mserve/pp-dataservice/mserve/templates",
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

CELERY_DEFAULT_QUEUE = "normal_tasks"
CELERY_QUEUES = {
    "normal_tasks": {
        "binding_key": "normal.#",
    },
    "priority_tasks": {
        "binding_key": "priority.#",
    },
}
CELERY_DEFAULT_EXCHANGE = "tasks"
CELERY_DEFAULT_EXCHANGE_TYPE = "topic"
CELERY_DEFAULT_ROUTING_KEY = "task.default"
CELERY_RESULT_BACKEND = "djcelery.backends.database.DatabaseBackend"

CELERY_IMPORTS = ("dataservice.tasks", "jobservice.tasks", )

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
    'djcelery',
    'request',
    #'django_extensions',
)

# Do POSTMark setup
POSTMARK = True
if POSTMARK:
    CELERY_IMPORTS += ("postmark.tasks",)
    INSTALLED_APPS += ('postmark',)

# Do PrestoPRIME setup
PRESTOPRIME = False
if PRESTOPRIME:
    CELERY_IMPORTS += ("prestoprime.tasks",)
    INSTALLED_APPS += ('prestoprime',)


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

# DATA CONFIG
FILE_TRANSPORTS = {
    "localhost": { "schema":"http","port":"8000", "netloc":"127.0.0.1", "path" : "/mfiles/%s/file/" },
    HOSTNAME: { "schema":"http","port":"80", "netloc":HOSTNAME, "path" : "/mfiles/%s/file/" },
}

if DEBUG:
    FILE_TRANSPORTS["mfile"] = { "schema" : "direct" }
    #FILE_TRANSPORTS["folder"] = { "schema" : "localpath", "path" : TESTDATA_ROOT }


# JOB CONFIG
USE_CELERY=True
DEFAULT_ACCESS_SPEED = "unlimited"

# Define Sizes
thumbsize = (210,128)
postersize = (420,256)
wuxga = (1920,1200)
hd1080 = (1920,1080)

# For FGCI
FORCE_SCRIPT_NAME = ''

# POSTMARK SPECIFIC
DIGITAL_RAPIDS_INPUT_DIR = "/mnt/postmark/postmark/input/QuickTime_H264_768x576_2Mbps_AAC_192Kbps_Stereo/"
DIGITAL_RAPIDS_OUTPUT_DIR = "/mnt/postmark/postmark/output/QuickTime_H264_768x576_2Mbps_AAC_192Kbps_Stereo/"
R3D_HOST="r3dhost"
R3D_USER="r3dusername"
R3D_PASS="r3dpassword"
