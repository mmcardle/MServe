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
from dataservice.handlers import *
from jobservice.handlers import *

hosting_handler = Resource(HostingContainerHandler)
remote_mserve_handler = Resource(RemoteMServeServiceHandler)
managementproperty_handler = Resource(ManagementPropertyHandler)
dataservice_handler = Resource(DataServiceHandler)
subservice_handler = Resource(SubServiceHandler)
dataservice_url_handler = Resource(DataServiceURLHandler)
dataservice_profile_handler = Resource(DataServiceProfileHandler)
dataservice_task_handler = Resource(DataServiceTaskHandler)
mfile_handler = Resource(MFileHandler)
backupfile_handler = Resource(BackupFileHandler)
mfolder_handler = Resource(MFolderHandler)
mfile_contents_handler = Resource(MFileContentsHandler)
mfile_workflow_handler = Resource(MFileWorkflowHandler)
mfile_verify_handler = Resource(MFileVerifyHandler)
auth_handler = Resource(AuthHandler)
usagesummary_handler = Resource(UsageSummaryHandler)
usage_handler = Resource(UsageHandler)
role_handler = Resource(RoleHandler)
resources_handler = Resource(ResourcesHandler)
info_handler = Resource(InfoHandler)
profile_handler = Resource(ProfileHandler)
service_request_handler = Resource(ServiceRequestHandler)
auth_contents_handler = Resource(AuthContentsHandler)

urlpatterns = patterns('',

    # API v2
    url(r'^containers/$', hosting_handler),
    url(r'^containers/(?P<id>[^/]+)/$', hosting_handler, name="hostingcontainer" ),
    url(r'^containers/(?P<containerid>[^/]+)/properties/$', managementproperty_handler, name="hostingcontainer_properites" ),
    url(r'^containers/(?P<containerid>[^/]+)/usages/$', usage_handler ,name="hostingcontainer_usages"),
    url(r'^containers/(?P<containerid>[^/]+)/auths/$', auth_handler ,name="hostingcontainer_auths"),
    url(r'^containers/(?P<containerid>[^/]+)/services/$', dataservice_handler ,name="hostingcontainer_services"),
    url(r'^containers/(?P<containerid>[^/]+)/subservices/$', subservice_handler ,name="hostingcontainer_subservices"),

    url(r'^remoteservices/$', remote_mserve_handler),

    url(r'^services/$', dataservice_handler, name="dataservices" ),
    url(r'^services/(?P<id>[^/]+)/$', dataservice_handler, name="dataservice" ),
    url(r'^services/(?P<serviceid>[^/]+)/properties/$', managementproperty_handler),
    url(r'^services/(?P<serviceid>[^/]+)/usages/$', usage_handler),
    url(r'^services/(?P<serviceid>[^/]+)/auths/$', auth_handler),
    url(r'^services/(?P<serviceid>[^/]+)/mfiles/$', mfile_handler),
    url(r'^services/(?P<serviceid>[^/]+)/mfolders/$', mfolder_handler),
    url(r'^services/(?P<serviceid>[^/]+)/subservices/$', dataservice_handler, name="subservices"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/$', dataservice_profile_handler),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/(?P<profileid>[^/]+)/tasks/$', dataservice_task_handler),

    url(r'^mfiles/$', mfile_handler  ),
    url(r'^mfiles/(?P<id>[^/]+)/$', mfile_handler  ),
    url(r'^mfiles/(?P<id>[^/]+)/thumb/$', mfile_handler, {"field":"thumb"}, name="mfile_upload_thumb"  ),
    url(r'^mfiles/(?P<id>[^/]+)/poster/$', mfile_handler, {"field":"poster"}, name="mfile_upload_poster"   ),
    url(r'^mfiles/(?P<id>[^/]+)/proxy/$', mfile_handler, {"field":"proxy"}, name="mfile_upload_proxy"   ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/properties/$', managementproperty_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/usages/$', usage_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/auths/$', auth_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/file/$', mfile_contents_handler, name='mfile_download'),
    url(r'^mfiles/(?P<mfileid>[^/]+)/workflows/$', mfile_workflow_handler),

    url(r'^auths/$', auth_handler  ),
    url(r'^auths/(?P<id>[^/]+)/$', auth_handler  ),
    url(r'^auths/(?P<authid>[^/]+)/properties/$', managementproperty_handler),
    url(r'^auths/(?P<authid>[^/]+)/usages/$', usage_handler),
    url(r'^auths/(?P<authid>[^/]+)/auths/$', auth_handler, {"murl":"auths"}),
    url(r'^auths/(?P<authid>[^/]+)/base/$', auth_handler, {"murl":"base"}),
    url(r'^auths/(?P<authid>[^/]+)/services/$', dataservice_handler),
    url(r'^auths/(?P<authid>[^/]+)/mfiles/$', mfile_handler),
    url(r'^auths/(?P<authid>[^/]+)/mfolders/$', mfolder_handler),
    url(r'^auths/(?P<authid>[^/]+)/file/$', mfile_contents_handler),

    url(r'^backups/(?P<backupid>[^/]+)/$', backupfile_handler, name="backup_upload" ),
    
    # API V1

    # REST Methods 
    #url(r'^container/$', hosting_handler),
    #url(r'^service/$', dataservice_handler),
    #url(r'^mfile/$', mfile_handler),
    #url(r'^auth/$', auth_handler),
    url(r'^users/$', profile_handler,name='user'),
    url(r'^users/requests/$', service_request_handler,name='user_requests'),
    url(r'^users/requests/(?P<id>[^/]+)/$', service_request_handler),

    # REST Methods for individual resources
    #url(r'^container/(?P<id>[^/]+)/$', hosting_handler),
    #url(r'^service/(?P<id>[^/]+)/$', dataservice_handler),
    #url(r'^mfile/(?P<id>[^/]+)/$', mfile_handler),
    #url(r'^auth/(?P<id>[^/]+)/$', auth_handler),

    #Global
    #url(r'^api/(?P<id>[^/]+)/info/$', info_handler),
    url(r'^api/(?P<id>[^/]+)/resources/$', resources_handler),
    url(r'^api/(?P<id>[^/]+)/usage/$', usage_handler),
    #url(r'^api/(?P<id>[^/]+)/property/$', property_handler),

    url(r'^auth/(?P<id>[^/]+)/getcontents/$', auth_contents_handler),
    #url(r'^api/(?P<id>[^/]+)/role/$', role_handler),

    # TING specific
    url(r'^api/(?P<id>[^/]+)/getusagesummary/$', usagesummary_handler),
    url(r'^api/(?P<id>[^/]+)/getroles/$', role_handler),
    url(r'^api/(?P<id>[^/]+)/resources/(?P<last_known>[^/]+)/$', resources_handler),
    url(r'^api/(?P<id>[^/]+)/getusagesummary/(?P<last_report>[^/]+)/$', usagesummary_handler),
    url(r'^api/(?P<id>[^/]+)/getmanagedresources/$', resources_handler),
    url(r'^api/(?P<id>[^/]+)/getmanagedresources/(?P<last_known>[^/]+)/$', resources_handler),
    url(r'^api/(?P<id>[^/]+)/getmanagementproperties/$', managementproperty_handler),
    url(r'^api/(?P<id>[^/]+)/setmanagementproperty/$', managementproperty_handler),

    # TING Container Methods
    url(r'^containerapi/(?P<containerid>[^/]+)/makeserviceinstance/$', dataservice_url_handler),

    # TING Service Methods
    url(r'^serviceapi/(?P<serviceid>[^/]+)/create/$', mfile_handler),

    # TING MFile Methods
    url(r'^mfileapi/get/(?P<mfileid>[^/]+)/$', mfile_contents_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/$', mfile_handler),

    # This should be a job
    url(r'^mfileapi/verify/(?P<mfileid>[^/]+)/$', mfile_verify_handler),

    # HTML Views
    url(r'^$',  'dataservice.views.home'),
    url(r'^usage/',  'dataservice.views.render_usage'),
    url(r'^stats/$',  'dataservice.views.stats'),
    url(r'^browse/(?P<baseid>[^/]+)/$', "dataservice.views.render_base"),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'dataservice.views.profile'),
)
