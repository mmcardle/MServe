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
from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

import settings
import os

cwd = os.getcwd()
DEV_STATIC_DIR = os.path.join(cwd, '..', 'static')
DEV_THUMBS_DIR = os.path.join(settings.MSERVE_DATA, 'www-root', 'mservethumbs')

urlpatterns = patterns('',

    (r'^', include('dataservice.urls')),
    (r'^', include('jobservice.urls')),
    (r'^', include('webdav.urls')),
    (r'^', include('mserveoauth.urls')),
    (r'^mservemedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DEV_STATIC_DIR}),
    (r'^mservethumbs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': DEV_THUMBS_DIR}),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^test/', 'dataservice.views.test' ),
        (r'^transformrequest/', 'dataservice.views.test_transformrequest' ),
        (r'^queryjobrequest/(?P<jobid>.*)$', 'dataservice.views.test_queryjobrequest' ),
    )
