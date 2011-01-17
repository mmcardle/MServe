from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from dataservice.handlers import *

hosting_handler = Resource(HostingContainerHandler)
managedresources_container_handler = Resource(ManagedResourcesContainerHandler)
managedresources_service_handler = Resource(ManagedResourcesServiceHandler)
managedresources_mfile_handler = Resource(ManagedResourcesmfileHandler)
managementproperty_handler = Resource(ManagementPropertyHandler)
dataservice_handler = Resource(DataServiceHandler)
dataservice_url_handler = Resource(DataServiceURLHandler)
mfile_handler = Resource(MFileHandler)
mfile_json_handler = Resource(MFileJSONHandler)
mfile_url_handler = Resource(MFileURLHandler)
mfile_contents_handler = Resource(MFileContentsHandler)
mfile_verify_handler = Resource(MFileVerifyHandler)
mfile_auth_handler = Resource(MFileAuthHandler)
auth_handler = Resource(AuthHandler)
usagesummary_handler = Resource(UsageSummaryHandler)
role_handler = Resource(RoleHandler)
role_info_handler = Resource(RoleInfoHandler)
global_handler = Resource(GlobalHandler)
render_handler = Resource(RenderHandler)
job_handler = Resource(JobHandler)
jobmfile_handler = Resource(JobMFileHandler)
jobservice_handler = Resource(JobServiceHandler)
render_results_handler = Resource(RenderResultsHandler)
access_control_handler = Resource(AccessControlHandler)
container_access_control_handler = Resource(ContainerAccessControlHandler)
service_access_control_handler = Resource(ServiceAccessControlHandler)
mfile_access_control_handler = Resource(MFileAccessControlHandler)
thumb_handler = Resource(ThumbHandler)
mfile_corruption_handler = Resource(CorruptionHandler)

urlpatterns = patterns('',

    # REST Methods for POST
    url(r'^container/$', hosting_handler),
    url(r'^service/$', dataservice_handler),
    url(r'^mfile/$', mfile_handler),
    url(r'^mfileauth/$', mfile_auth_handler),
    url(r'^auth/$', auth_handler),

    # HTML Views
    url(r'^browse/container/(?P<id>[^/]+)/', "dataservice.views.render_container"),
    url(r'^browse/service/(?P<id>[^/]+)/', "dataservice.views.render_service"),
    url(r'^browse/mfile/(?P<id>[^/]+)/', "dataservice.views.render_mfile",{'show':True}),
    url(r'^browse/auth/(?P<id>[^/]+)/', "dataservice.views.render_auth"),

    # HTML Forms
    url(r'^form/container/', "dataservice.views.create_container"),
    url(r'^form/service/', "dataservice.views.create_service"),
    url(r'^form/mfile/', "dataservice.views.create_mfile"),
    url(r'^form/mfileauth/', "dataservice.views.create_mfileauth"),
    url(r'^form/auth/', "dataservice.views.create_auth"),

    # REST Methods for GET
    url(r'^container/(?P<id>[^/]+)/', hosting_handler),
    url(r'^service/(?P<id>[^/]+)/', dataservice_handler),
    url(r'^mfile/(?P<id>[^/]+)/$', mfile_handler),
    url(r'^mfileauth/(?P<mfileauthid>[^/]+)/', mfile_auth_handler),
    url(r'^auth/(?P<id>[^/]+)/', auth_handler),

    url(r'^roles/(?P<roleid>[^/]+)/$', role_handler),
    url(r'^authority/(?P<method>[^/]+)/(?P<id>[^/]+)/$', access_control_handler),

    # Container Methods
    url(r'^containerapi/makeserviceinstance/(?P<containerid>[^/]+)/$', dataservice_url_handler),
    url(r'^containerapi/getmanagedresources/(?P<containerid>[^/]+)/$', managedresources_container_handler),
    url(r'^containerapi/getmanagedresources/(?P<containerid>[^/]+)/(?P<last_known>[^/]+)/$', managedresources_container_handler),
    url(r'^containerapi/managementproperty/(?P<baseid>[^/]+)/$', managementproperty_handler),
    url(r'^containerapi/getusagesummary/(?P<baseid>[^/]+)/$', usagesummary_handler),
    url(r'^containerapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^containerapi/getroleinfo/(?P<pk>[^/]+)/$', role_info_handler),
    url(r'^containerapi/getaccesscontrol/(?P<baseid>[^/]+)/$', container_access_control_handler),

    # Service Methods
    url(r'^serviceapi/create/(?P<serviceid>[^/]+)/$', mfile_url_handler),
    url(r'^serviceapi/getmanagedresources/(?P<serviceid>[^/]+)/$', managedresources_service_handler),
    url(r'^serviceapi/getmanagedresources/(?P<serviceid>[^/]+)/(?P<last_known>[^/]+)/$', managedresources_service_handler),
    url(r'^serviceapi/managementproperty/(?P<baseid>[^/]+)/$', managementproperty_handler),
    url(r'^serviceapi/getusagesummary/(?P<baseid>[^/]+)/$', usagesummary_handler),
    url(r'^serviceapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^serviceapi/getroleinfo/(?P<pk>[^/]+)/$', role_info_handler),
    url(r'^serviceapi/getaccesscontrol/(?P<baseid>[^/]+)/$', service_access_control_handler),
    url(r'^serviceapi/getjobs/(?P<serviceid>[^/]+)/$', jobservice_handler),

    # MFile Methods
    url(r'^mfileapi/update/(?P<mfileid>[^/]+)/$', mfile_url_handler),
    url(r'^mfileapi/getmanagedresources/(?P<mfileid>[^/]+)/$', managedresources_mfile_handler),
    url(r'^mfileapi/getmanagedresources/(?P<mfileid>[^/]+)/(?P<last_known>[^/]+)/$', managedresources_mfile_handler),
    url(r'^mfileapi/get/(?P<mfileid>[^/]+)/$', mfile_contents_handler),
    url(r'^mfileapi/verify/(?P<mfileid>[^/]+)/$', mfile_verify_handler),
    url(r'^mfileapi/getusagesummary/(?P<baseid>[^/]+)/$', usagesummary_handler),
    url(r'^mfileapi/getusagesummary/(?P<baseid>[^/]+)/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^mfileapi/getroleinfo/(?P<pk>[^/]+)/$', role_info_handler),
    url(r'^mfileapi/getaccesscontrol/(?P<baseid>[^/]+)/$', mfile_access_control_handler),
    url(r'^mfileapi/corrupt/(?P<mfileid>[^/]+)/$', mfile_corruption_handler),
    url(r'^mfileapi/corruptbackup/(?P<mfileid>[^/]+)/$', mfile_corruption_handler, {'backup':True}),
    url(r'^mfileapi/thumb/(?P<mfileid>[^/]+)/$', 'dataservice.views.thumb'),
    url(r'^mfileapi/(?P<id>[^/]+)/$', mfile_json_handler),
    url(r'^mfileapi/getpreview/(?P<mfileid>[^/]+)/$', render_results_handler),
    url(r'^mfileapi/getjobs/(?P<mfileid>[^/]+)/$', jobmfile_handler),

    #url(r'^auth/getorcreateauth/(?P<pk>[^/]+)/$', access_control_handler),
    #url(r'^auth/addauth/(?P<pk>[^/]+)/$', access_control_handler),
    #url(r'^auth/getauths/(?P<pk>[^/]+)/$', access_control_handler),
    #url(r'^auth/getroles/(?P<pk>[^/]+)/$', access_control_handler),
    #url(r'^auth/setroles/(?P<pk>[^/]+)/$', access_control_handler),
    #url(r'^auth/revokeauth/(?P<pk>[^/]+)/$', access_control_handler),

    # Job Methods
    url(r'^jobapi/render/(?P<mfileid>[^/]+)/$', render_handler),
    url(r'^jobapi/(?P<id>[^/]+)/$', job_handler),

    # TEMP - Needs Sorting
    url(r'^tasks/', 'djcelery.views.registered_tasks'),

    # Thumb methods
    url(r'^thumbapi/$', thumb_handler),
    url(r'^thumbapi/(?P<pk>[^/]+)/$', thumb_handler),

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
