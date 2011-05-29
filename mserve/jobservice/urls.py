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
from jobservice.handlers import *

job_handler = Resource(JobHandler)
jobmfile_handler = Resource(JobMFileHandler)
jobservice_handler = Resource(JobServiceHandler)
render_handler = Resource(RenderHandler)
render_results_handler = Resource(RenderResultsHandler)
joboutput_handler = Resource(JobOutputContentsHandler)

urlpatterns = patterns('',

    url(r'^mfiles/(?P<mfileid>[^/]+)/jobs/$', job_handler),
    url(r'^services/(?P<serviceid>[^/]+)/jobs/$', jobservice_handler),

    url(r'^jobs/(?P<jobid>[^/]+)/$', job_handler),



    # Generic Job Methods
    url(r'^jobapi/$', job_handler),

    # Tasks
    url(r'^tasks/', 'jobservice.views.list_jobs'),

    # Job
    url(r'^jobapi/render/(?P<mfileid>[^/]+)/$', render_handler),
    url(r'^jobapi/render/(?P<mfileid>[^/]+)/(?P<start>[^/]+)/(?P<end>[^/]+)/$', render_handler),
    url(r'^jobapi/(?P<id>[^/]+)/$', job_handler),
    url(r'^jobapi/getpreview/(?P<jobid>[^/]+)/$', render_results_handler),
    url(r'^jobapi/contents/(?P<outputid>[^/]+)/$', joboutput_handler),

    url(r'^jobapi/getjobs/(?P<mfileid>[^/]+)/$', jobmfile_handler),
)
