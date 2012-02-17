"""

MServe URLS
-----------

::

 This class defines the MServe URL mapping for the dataservice module

https://docs.djangoproject.com/en/dev/topics/http/urls/

"""
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
from django_openid_auth.forms import OpenIDLoginForm

hosting_handler = Resource(HostingContainerHandler)
remote_mserve_handler = Resource(RemoteMServeServiceHandler)
managementproperty_handler = Resource(ManagementPropertyHandler)
dataservice_handler = Resource(DataServiceHandler)
subservice_handler = Resource(SubServiceHandler)
dataservice_profile_handler = Resource(DataServiceProfileHandler)
dataservice_task_handler = Resource(DataServiceTaskHandler)
dataservice_taskset_handler = Resource(DataServiceTaskSetHandler)
mfile_handler = Resource(MFileHandler)
backupfile_handler = Resource(BackupFileHandler)
mfolder_handler = Resource(MFolderHandler)
mfile_contents_handler = Resource(MFileContentsHandler)
auth_handler = Resource(AuthHandler)
usage_handler = Resource(UsageHandler)
usagesummary_handler = Resource(UsageSummaryHandler)
profile_handler = Resource(ProfileHandler)
service_request_handler = Resource(ServiceRequestHandler)

urlpatterns = patterns('',

    # API v2

    # Container URLs
    url(r'^containers/$', hosting_handler, name="hostingcontainers" ),
    url(r'^containers/(?P<containerid>[^/]+)/$', hosting_handler, name="hostingcontainer" ),
    url(r'^containers/(?P<containerid>[^/]+)/properties/$', managementproperty_handler, name="hostingcontainer_props" ),
    url(r'^containers/(?P<containerid>[^/]+)/usages/$', usage_handler ,name="hostingcontainer_usages"),
    url(r'^containers/(?P<containerid>[^/]+)/usagesummary/$', usagesummary_handler, name='hostingcontainer_usagesummary'),
    url(r'^containers/(?P<containerid>[^/]+)/auths/$', auth_handler ,name="hostingcontainer_auths"),
    url(r'^containers/(?P<containerid>[^/]+)/services/$', dataservice_handler ,name="hostingcontainer_services"),
    url(r'^containers/(?P<containerid>[^/]+)/subservices/$', subservice_handler ,name="hostingcontainer_subservices"),

    # Service URLs
    url(r'^services/$', dataservice_handler, name="dataservices" ),
    url(r'^services/(?P<serviceid>[^/]+)/$', dataservice_handler, name="dataservice" ),
    url(r'^services/(?P<serviceid>[^/]+)/properties/$', managementproperty_handler, name="dataservice_props"),
    url(r'^services/(?P<serviceid>[^/]+)/usages/$', usage_handler, name="dataservice_usages"),
    url(r'^services/(?P<serviceid>[^/]+)/usagesummary/$', usagesummary_handler, name='dataservice_usagesummary'),
    url(r'^services/(?P<serviceid>[^/]+)/auths/$', auth_handler, name="dataservice_auths"),
    url(r'^services/(?P<serviceid>[^/]+)/mfiles/$', mfile_handler, name="dataservice_mfiles"),
    url(r'^services/(?P<serviceid>[^/]+)/mfolders/$', mfolder_handler, name="dataservice_mfolders"),
    url(r'^services/(?P<serviceid>[^/]+)/subservices/$', dataservice_handler, {"suburl":"subservices"}, name="dataservice_subservices"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/$', dataservice_profile_handler, name="dataservice_profiles"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/(?P<profileid>[^/]+)/tasksets/$', dataservice_taskset_handler, name="dataservice_profiles_tasksets"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/(?P<profileid>[^/]+)/tasksets/(?P<tasksetid>[^/]+)/$', dataservice_taskset_handler, name="dataservice_profiles_tasksets"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/(?P<profileid>[^/]+)/tasks/$', dataservice_task_handler, name="dataservice_profiles_tasks"),
    url(r'^services/(?P<serviceid>[^/]+)/profiles/(?P<profileid>[^/]+)/tasks/(?P<taskid>[^/]+)/$', dataservice_task_handler, name="dataservice_profiles_tasks"),

    # MFile URLs
    url(r'^mfiles/$', mfile_handler, name="mfiles"  ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/$', mfile_handler, name="mfile"  ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/thumb/$', mfile_handler, {"field":"thumb"}, name="mfile_upload_thumb"  ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/poster/$', mfile_handler, {"field":"poster"}, name="mfile_upload_poster"   ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/proxy/$', mfile_handler, {"field":"proxy"}, name="mfile_upload_proxy"   ),
    url(r'^mfiles/(?P<mfileid>[^/]+)/properties/$', managementproperty_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/usages/$', usage_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/usagesummary/$', usagesummary_handler, name='mfile_usagesummary'),
    url(r'^mfiles/(?P<mfileid>[^/]+)/auths/$', auth_handler),
    url(r'^mfiles/(?P<mfileid>[^/]+)/file/$', mfile_contents_handler, name='mfile_download'),

    # Auth URLs
    url(r'^auths/$', auth_handler, name='auths' ),
    url(r'^auths/(?P<authid>[^/]+)/$', auth_handler, name='auth'  ),
    url(r'^auths/(?P<authid>[^/]+)/properties/$', managementproperty_handler),
    url(r'^auths/(?P<authid>[^/]+)/usages/$', usage_handler),
    url(r'^auths/(?P<authid>[^/]+)/usagesummary/$', usagesummary_handler, name="auth_usagesummary"),
    url(r'^auths/(?P<authid>[^/]+)/auths/$', auth_handler, {"murl":"auths"}),
    url(r'^auths/(?P<authid>[^/]+)/base/$', auth_handler, {"murl":"base"}, name="auth_base"),
    url(r'^auths/(?P<authid>[^/]+)/services/$', dataservice_handler),
    url(r'^auths/(?P<authid>[^/]+)/mfiles/$', mfile_handler, name="auth_mfiles"),
    url(r'^auths/(?P<authid>[^/]+)/mfolders/$', mfolder_handler),
    url(r'^auths/(?P<authid>[^/]+)/file/$', mfile_contents_handler, name='auth_download'),

    # Other URLs
    url(r'^backups/(?P<backupid>[^/]+)/$', backupfile_handler, name="backup_upload" ),
    url(r'^remoteservices/$', remote_mserve_handler),
    url(r'^usagesummary/',  usagesummary_handler),

    # User URLs
    url(r'^users/$', profile_handler, name='users'),
    url(r'^users/requests/$', service_request_handler, name='user_requests'),
    url(r'^users/requests/(?P<servicerequestid>[^/]+)/$', service_request_handler, name='user_request'),

    # Account login/logout urls
    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html','extra_context' : { "oidform" : OpenIDLoginForm() } }, name="login"),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'dataservice.views.profile'),
    url(r'^openid/login/$', 'dataservice.views.login', {'template_name': 'login.html' }, name='openid-login'),
    url(r'^openid/complete/$', 'django_openid_auth.views.login_complete', name='openid-complete'),
    url(r'^openid/logo.gif$', 'django_openid_auth.views.logo', name='openid-logo'),

    # HTML Views
    url(r'^$',  'dataservice.views.home'),
    url(r'^/$',  'dataservice.views.home', name='home'),
    url(r'^usage/',  'dataservice.views.render_usage', name='usage'),
    url(r'^videoplayer/(?P<mfileid>[^/]+)/',  'dataservice.views.videoplayer', name='videoplayer'),
    url(r'^traffic/$',  'dataservice.views.traffic', name='traffic'),
    url(r'^stats/$',  'dataservice.views.stats', name='stats'),
    url(r'^stats/(?P<baseid>[^/]+)/$',  'dataservice.views.stats', name='stats'),
    url(r'^browse/(?P<baseid>[^/]+)/$', "dataservice.views.render_base", name='browse'),
    url(r'^redirect/$', 'dataservice.views.redirect_to', name="redirect_to"),
)
