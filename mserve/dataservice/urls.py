from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from dataservice.handlers import *
from jobservice.handlers import *

hosting_handler = Resource(HostingContainerHandler)
managementproperty_handler = Resource(ManagementPropertyHandler)
dataservice_handler = Resource(DataServiceHandler)
dataservice_url_handler = Resource(DataServiceURLHandler)
mfile_handler = Resource(MFileHandler)
mfile_contents_handler = Resource(MFileContentsHandler)
mfile_verify_handler = Resource(MFileVerifyHandler)
auth_handler = Resource(AuthHandler)
usagesummary_handler = Resource(UsageSummaryHandler)
usage_handler = Resource(UsageHandler)
role_handler = Resource(RoleHandler)
resources_handler = Resource(ResourcesHandler)
info_handler = Resource(InfoHandler)

from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from dataservice.handlers import TestAuthHandler

#auth = HttpBasicAuthentication(realm='My sample API')
auth = OAuthAuthentication(realm="MServe Realm")

oauth_handler = Resource(handler=TestAuthHandler, authentication=auth)
consumer_handler = Resource(ConsumerHandler)
receive_handler = Resource(ReceiveHandler)

urlpatterns = patterns('',
    url(r'^posts', oauth_handler, name='blogposts'),
    url(r'^consumer', consumer_handler),
    url(r'^receive', receive_handler),
    # automated documentation url(r'^$', documentation_view),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^api/oauth/request_token/$','oauth_request_token'),
    url(r'^api/oauth/authorize/$','oauth_user_auth'),
    url(r'^api/oauth/access_token/$','oauth_access_token'),
)


urlpatterns += patterns('',

    # REST Methods 
    url(r'^container/$', hosting_handler),
    url(r'^service/$', dataservice_handler),
    url(r'^mfile/$', mfile_handler),
    url(r'^auth/$', auth_handler),

    # REST Methods for individual resources
    url(r'^container/(?P<id>[^/]+)/$', hosting_handler),
    url(r'^service/(?P<id>[^/]+)/$', dataservice_handler),
    url(r'^mfile/(?P<id>[^/]+)/$', mfile_handler),
    url(r'^auth/(?P<id>[^/]+)/$', auth_handler),

    #Global
    url(r'^api/(?P<id>[^/]+)/info/$', info_handler),
    url(r'^api/(?P<id>[^/]+)/resources/$', resources_handler),
    url(r'^api/(?P<id>[^/]+)/usage/$', usage_handler),
    #url(r'^api/(?P<id>[^/]+)/property/$', property_handler),

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
    url(r'^containerapi/makeserviceinstance/(?P<containerid>[^/]+)/$', dataservice_url_handler),

    # TING Service Methods
    url(r'^serviceapi/(?P<serviceid>[^/]+)/create/$', mfile_handler),
    url(r'^serviceapi/create/(?P<serviceid>[^/]+)/$', mfile_handler),

    # TING MFile Methods
    url(r'^mfileapi/get/(?P<mfileid>[^/]+)/$', mfile_contents_handler),
    url(r'^mfileapi/(?P<id>[^/]+)/$', mfile_handler),

    # This should be a job
    url(r'^mfileapi/verify/(?P<mfileid>[^/]+)/$', mfile_verify_handler),

    # HTML Views
    url(r'^$',  'dataservice.views.home'),
    url(r'^usage/',  'dataservice.views.usage'),
    url(r'^stats/$',  'dataservice.views.stats'),
    url(r'^browse/(?P<id>[^/]+)/$', "dataservice.views.render_base"),

    url(r'^accounts/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout_then_login'),
    url(r'^accounts/profile/$', 'dataservice.views.profile'),
)
