import re
import usage_store as usage_store
import datetime
import logging
import utils as utils
from django.http import HttpResponseForbidden
from dataservice.models import Auth
from dataservice.models import NamedBase

metric_responsetime = "http://mserve/responsetime"

class AuthMiddleware(object):

    def process_request(self, request):
        if request.META.has_key('REQUEST_URI'):
            uri = request.META['REQUEST_URI']
            match = re.match("\/api\/(?P<id>[\w]{8}(-[\w]{4}){3}-[\w]{12})\/(?P<methodstring>.*)\/",uri)
            if match:
                id   = match.group('id')
                methodstring = match.group('methodstring')
                method = methodstring.split("/")[0]
                logging.info("method = %s id = %s" % (method,id))
                try:
                    auth = Auth.objects.get(id=id)
                    logging.debug("Authority Check for Auth id=%s for method=%s " % (id, method))
                    allowed = utils.check_method_for_auth(id,method)
                    if not allowed:
                        logging.debug("Authority Check for Auth id=%s for method=%s is %s " % (id, method, allowed))
                        r = HttpResponseForbidden("No Access")
                        return r
                except Auth.DoesNotExist:
                    pass

                try:
                    base = NamedBase.objects.get(id=id)
                    if not method in utils.get_methods_for_base(id):
                        logging.debug("Authority Check for Base id=%s for method=%s " % (id, method))
                        r = HttpResponseForbidden("No Access")
                        return r
                except NamedBase.DoesNotExist:
                    pass
        return

class ResponseMiddleware(object):

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
                    usage_store.record(mfileid,metric_responsetime,tt)
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

