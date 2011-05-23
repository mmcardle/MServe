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

urlpatterns = patterns('',

    (r'^', include('mserve.dataservice.urls')),
    (r'^', include('mserve.jobservice.urls')),
    (r'^', include('mserve.webdav.urls')),
    (r'^', include('mserve.mserveoauth.urls')),
    (r'^', include('mserve.prestoprime.urls')),

    (r'^openid/', include('django_openid_auth.urls')),

    (r'^mservemedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/mserve/pp-dataservice/media/'}),
    (r'^mservethumbs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/mserve/www-root/mservethumbs'}),

    (r'^admin/', include(admin.site.urls)),
)
