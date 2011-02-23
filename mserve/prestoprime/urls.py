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
