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
import re
import usage_store as usage_store
import settings as settings
import datetime
import logging
from models import MFile
from models import DataService

metric_responsetime = "http://mserve/responsetime"
metric_delivery_success = settings.DELIVERY_SUCCESS_METRIC

class ResponseMiddleware(object):

    def process_response(self, request, response):
        match = re.search("\/mfiles\/(?P<id>.*)\/file\/", request.path)
        if match is not None:
            mfileid = match.group("id")
            starttime = request.META["starttime"]
            endtime = datetime.datetime.now()
            timetaken = endtime - starttime
            time_taken = float("%s.%s" % (timetaken.seconds,timetaken.microseconds))
            usage_store.record(mfileid,metric_responsetime,time_taken)

            try:
                mfile = MFile.objects.get(id=mfileid)
                ds = DataService.objects.get(mfile__id=mfileid)
                multiplier = ds.managementproperty_set.get(property="deliverySuccessMultiplier_GB").value
                constant = ds.managementproperty_set.get(property="deliverySuccessConstant_Minutes").value

                target_delivery_time = mfile.size/(1024.0*1024.0*1024.0) * float(multiplier) + float(constant)

                time_taken_minutes = time_taken/60.0
                if target_delivery_time < time_taken_minutes:
                    usage_store.record(mfile.id, metric_delivery_success, 0)
                else:
                    usage_store.record(mfile.id, metric_delivery_success, 1)

            except Exception as e:
                logging.error("Request for mfile %s throws error - %s ", mfileid, e )
        return response

    def process_request(self, request):
        match = re.search("\/mfiles\/(?P<id>.*)\/file\/", request.path)
        if match is not None:
          request.META["starttime"] = datetime.datetime.now()
        return

