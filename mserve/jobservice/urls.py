from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from piston.resource import Resource
from jobservice.handlers import *

job_handler = Resource(JobHandler)
jobmfile_handler = Resource(JobMFileHandler)
jobservice_handler = Resource(JobServiceHandler)
render_handler = Resource(RenderHandler)
render_results_handler = Resource(RenderResultsHandler)
joboutput_handler = Resource(JobOutputContentsHandler)

urlpatterns = patterns('',

    # Job Methods
    url(r'^jobapi/render/(?P<mfileid>[^/]+)/$', render_handler),
    url(r'^jobapi/render/(?P<mfileid>[^/]+)/(?P<start>[^/]+)/(?P<end>[^/]+)/$', render_handler),
    url(r'^jobapi/(?P<id>[^/]+)/$', job_handler),
    url(r'^jobapi/getpreview/(?P<jobid>[^/]+)/$', render_results_handler),
    url(r'^jobapi/contents/(?P<outputid>[^/]+)/$', joboutput_handler),

    url(r'^serviceapi/getjobs/(?P<serviceid>[^/]+)/$', jobservice_handler),
    url(r'^jobapi/getjobs/(?P<mfileid>[^/]+)/$', jobmfile_handler),
)
