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

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from prestoprime.handlers import *

pp_usagesummary_handler = Resource(PPUsageHandler)
pp_managedresources_handler = Resource(PPManagedResourcesHandler)

urlpatterns = patterns('',

    url(r'^containerapi/getusagesummary/(?P<id>[^/]+)/$', pp_usagesummary_handler),
    url(r'^containerapi/getusagesummary/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_usagesummary_handler),
    url(r'^serviceapi/getusagesummary/(?P<id>[^/]+)/$', pp_usagesummary_handler),
    url(r'^serviceapi/getusagesummary/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_usagesummary_handler),
    url(r'^mfileapi/getusagesummary/(?P<id>[^/]+)/$', pp_usagesummary_handler),
    url(r'^mfileapi/getusagesummary/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_usagesummary_handler),

    url(r'^containerapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^containerapi/(?P<id>[^/]+)/getusagesummary/(?P<last>[^/]+)/$', pp_usagesummary_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getusagesummary/(?P<last>[^/]+)/$', pp_usagesummary_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getusagesummary/(?P<last>[^/]+)/$', pp_usagesummary_handler),

    url(r'^containerapi/(?P<id>[^/]+)/getmanagedresources/$', pp_managedresources_handler),
    url(r'^containerapi/(?P<id>[^/]+)/getmanagedresources/(?P<last>[^/]+)/$', pp_managedresources_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getmanagedresources/$', pp_managedresources_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getmanagedresources/(?P<last>[^/]+)/$', pp_managedresources_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getmanagedresources/$', pp_managedresources_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getmanagedresources/(?P<last>[^/]+)/$', pp_managedresources_handler),

    url(r'^containerapi/getmanagedresources/(?P<id>[^/]+)/$', pp_managedresources_handler),
    url(r'^containerapi/getmanagedresources/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_managedresources_handler),
    url(r'^serviceapi/getmanagedresources/(?P<id>[^/]+)/$', pp_managedresources_handler),
    url(r'^serviceapi/getmanagedresources/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_managedresources_handler),
    url(r'^mfileapi/getmanagedresources/(?P<id>[^/]+)/$', pp_managedresources_handler),
    url(r'^mfileapi/getmanagedresources/(?P<id>[^/]+)/(?P<last>[^/]+)/$', pp_managedresources_handler),

)
