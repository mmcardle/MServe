from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from prestoprime.handlers import *

pp_usagesummary_handler = Resource(PPUsageHandler)

urlpatterns = patterns('',

    # Generic Job Methods
    url(r'^containerapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^containerapi/(?P<id>[^/]+)/getusagesummary/(?P<last_report>[^/]+)/$', pp_usagesummary_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^serviceapi/(?P<id>[^/]+)/getusagesummary/(?P<last_report>[^/]+)/$', pp_usagesummary_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getusagesummary/$', pp_usagesummary_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/getusagesummary/(?P<last_report>[^/]+)/$', pp_usagesummary_handler),
)
