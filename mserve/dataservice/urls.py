from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from dataservice.handlers import HostingContainerHandler
from dataservice.handlers import DataServiceHandler
from dataservice.handlers import DataStagerHandler

hosting_handler = Resource(HostingContainerHandler)
dataservice_handler = Resource(DataServiceHandler)
datastager_handler = Resource(DataStagerHandler)

urlpatterns = patterns('',

    url(r'api/hosting/(?P<id>[^/]+)', hosting_handler),
    url(r'api/hosting/', hosting_handler),
    url(r'api/service/(?P<id>[^/]+)', dataservice_handler),
    url(r'api/service/', dataservice_handler),
    url(r'api/stager/(?P<id>[^/]+)', datastager_handler),
    url(r'api/stager/', datastager_handler),

    (r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.MEDIA_ROOT}),

    (r'stager/(?P<id>[^/]+)/', 'dataservice.views.stager'),
    (r'service/(?P<id>[^/]+)/', 'dataservice.views.service'),
    (r'container/(?P<id>[^/]+)/', 'dataservice.views.container'),
    (r'home/',  'dataservice.views.home'),
    

)
