from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from dataservice.handlers import HostingContainerHandler
from dataservice.handlers import DataServiceHandler
from dataservice.handlers import DataServiceURLHandler
from dataservice.handlers import DataStagerHandler
from dataservice.handlers import DataStagerURLHandler
from dataservice.handlers import DataStagerAuthHandler
from dataservice.handlers import DataStagerContentsHandler
from dataservice.handlers import AuthHandler
from dataservice.handlers import GlobalHandler
from dataservice.handlers import ManagedResourcesContainerHandler
from dataservice.handlers import ManagedResourcesServiceHandler
from dataservice.handlers import ManagementPropertyHandler
from dataservice.handlers import UsageSummaryHandler
from dataservice.handlers import RoleHandler

hosting_handler = Resource(HostingContainerHandler)
managedresources_container_handler = Resource(ManagedResourcesContainerHandler)
managedresources_service_handler = Resource(ManagedResourcesServiceHandler)
managementproperty_handler = Resource(ManagementPropertyHandler)
dataservice_handler = Resource(DataServiceHandler)
dataservice_url_handler = Resource(DataServiceURLHandler)
datastager_handler = Resource(DataStagerHandler)
datastager_url_handler = Resource(DataStagerURLHandler)
datastager_contents_handler = Resource(DataStagerContentsHandler)
datastager_auth_handler = Resource(DataStagerAuthHandler)
auth_handler = Resource(AuthHandler)
usagesummary_handler = Resource(UsageSummaryHandler)
role_handler = Resource(RoleHandler)
global_handler = Resource(GlobalHandler)

urlpatterns = patterns('',

    # REST Methods for POST
    url(r'^container/$', hosting_handler),
    url(r'^service/$', dataservice_handler),
    url(r'^stager/$', datastager_handler),
    url(r'^stagerauth/$', datastager_auth_handler),
    url(r'^auth/$', auth_handler),

    # REST Methods for GET
    url(r'^container/(?P<containerid>[^/]+)/', hosting_handler),
    url(r'^service/(?P<serviceid>[^/]+)/', dataservice_handler),
    url(r'^stager/(?P<stagerid>[^/]+)/', datastager_handler),
    url(r'^stagerauth/(?P<stagerauthid>[^/]+)/', datastager_auth_handler),
    url(r'^auth/(?P<id>[^/]+)/', auth_handler),

    # METHODS
    url(r'^roles/(?P<roleid>[^/]+)/$', role_handler),

    # Container Methods
    url(r'^containerapi/makeserviceinstance/(?P<containerid>[^/]+)/$', dataservice_url_handler),
    url(r'^containerapi/getmanagedresources/(?P<containerid>[^/]+)/(?P<last_known>[^/]+)/$', managedresources_container_handler),
    url(r'^containerapi/managementproperty/(?P<baseid>[^/]+)/$', managementproperty_handler),
    url(r'^containerapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^containerapi/getroleinfo/(?P<baseid>[^/]+)/$', role_handler),

    # Service Methods
    url(r'^serviceapi/create/(?P<serviceid>[^/]+)/$', datastager_url_handler),
    url(r'^serviceapi/getmanagedresources/(?P<serviceid>[^/]+)/(?P<last_known>[^/]+)/', managedresources_service_handler),
    url(r'^serviceapi/managementproperty/(?P<baseid>[^/]+)/$', managementproperty_handler),
    url(r'^serviceapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^serviceapi/getroleinfo/(?P<baseid>[^/]+)/$', role_handler),

    # Stager Methods
    url(r'^stagerapi/update/(?P<stagerid>[^/]+)/$', datastager_url_handler),
    url(r'^stagerapi/getcontents/(?P<stagerid>[^/]+)/$', datastager_contents_handler),
    url(r'^stagerapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^stagerapi/getroleinfo/(?P<baseid>[^/]+)/$', role_handler),

    # Global Methods
    url(r'^api/getcontainers/$', global_handler),

    # HTML Views
    (r'^home/',  'dataservice.views.home'),
    (r'^usage/',  'dataservice.views.usage'),
    (r'^map/',  'dataservice.views.map'),
    (r'^viz/',  'dataservice.views.viz'),

    (r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    (r'^accounts/profile/$', 'dataservice.views.profile'),

    # Root
    (r'^$',  'dataservice.views.profile'),
)
