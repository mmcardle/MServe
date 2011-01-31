import re
import logging
import usage_store as usage_store
import datetime
from dataservice.models import *

class AuthMiddleware(object):

    def process_response(self, request, response):
        if request.META.has_key('REQUEST_URI'):
            uri = request.META['REQUEST_URI']
            if uri.startswith("/mfileapi/get/"):
                match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
                if match is not None:
                    mfileid = match.group(0)
                    starttime = request.META["starttime"]
                    endtime = datetime.datetime.now()
                    timetaken = endtime - starttime
                    tt = float("%s.%s" % (timetaken.seconds,timetaken.microseconds))
                    usage_store.record(mfileid,usage_store.metric_responsetime,tt)

        return response

    def process_request(self, request):
        
        if request.META.has_key('REQUEST_URI'):
            uri = request.META['REQUEST_URI']
            if uri.startswith("/mfileapi/get/"):
                match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
                if match is not None:
                  request.META["starttime"] = datetime.datetime.now()
                  mfileid = match.group(0)
        return

