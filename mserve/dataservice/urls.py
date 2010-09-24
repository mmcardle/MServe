from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from dataservice.handlers import HostingContainerHandler
from dataservice.handlers import DataServiceHandler
from dataservice.handlers import DataStagerHandler
from dataservice.handlers import DataStagerAuthHandler
from dataservice.handlers import AuthHandler

hosting_handler = Resource(HostingContainerHandler)
dataservice_handler = Resource(DataServiceHandler)
datastager_handler = Resource(DataStagerHandler)
datastager_auth_handler = Resource(DataStagerAuthHandler)
auth_handler = Resource(AuthHandler)

urlpatterns = patterns('',

    # Access
    url(r'api/container/(?P<id>[^/]+)', hosting_handler),
    url(r'api/service/(?P<id>[^/]+)', dataservice_handler),
    url(r'api/stager/(?P<id>[^/]+)', datastager_handler),
    url(r'api/auth/(?P<id>[^/]+)/', auth_handler),

    # Creation
    url(r'api/makehostingcontainer/(?P<fmt>[^/]+)/', hosting_handler),
    url(r'api/makeserviceinstance/(?P<containerid>[^/]+)/(?P<fmt>[^/]+)/', dataservice_handler),
    url(r'api/makestager/(?P<serviceid>[^/]+)/(?P<fmt>[^/]+)/', datastager_handler),
    url(r'api/makestagerauth/(?P<stagerid>[^/]+)/(?P<fmt>[^/]+)/', datastager_auth_handler),
    url(r'api/makeauth/(?P<auth>[^/]+)/(?P<fmt>[^/]+)/', auth_handler),
    # Authorizations
    
    # HTML Views
    (r'stager/(?P<id>[^/]+)/', 'dataservice.views.stager'),
    (r'service/(?P<id>[^/]+)/', 'dataservice.views.service'),
    (r'container/(?P<id>[^/]+)/', 'dataservice.views.container'),
    (r'auth/(?P<id>[^/]+)/', 'dataservice.views.auth'),
    (r'home/',  'dataservice.views.home'),
    (r'map/',  'dataservice.views.map'),

    # Media URLs
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

)
