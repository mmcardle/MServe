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
jobservice_handler = Resource(JobServiceHandler)
joboutput_handler = Resource(JobOutputHandler)

urlpatterns = patterns('',

    url(r'^mfiles/(?P<mfileid>[^/]+)/jobs/$', job_handler, name="mfile_job"),
    url(r'^services/(?P<serviceid>[^/]+)/jobs/$', jobservice_handler),
    url(r'^auths/(?P<authid>[^/]+)/jobs/$', job_handler),
    url(r'^jobs/$', job_handler),
    url(r'^jobs/(?P<jobid>[^/]+)/$', job_handler),
    url(r'^joboutputs/(?P<outputid>[^/]+)/$', joboutput_handler, name="joboutput"),
    url(r'^joboutputs/(?P<outputid>[^/]+)/file/$', joboutput_handler, {"field":"file"}, name="joboutput_upload"),
    # Creates an MFile from a job Output
    url(r'^joboutputs/(?P<outputid>[^/]+)/mfile/$', joboutput_handler, {"field":"mfile"}, name="joboutput_mfile"),
    url(r'^joboutputs/(?P<outputid>[^/]+)/thumb/$', joboutput_handler, {"field":"thumb"}, name="joboutput_upload_thumb"),

    # Tasks
    url(r'^tasks/', 'jobservice.views.list_tasks'),

)
