import re
import logging
import usage_store as usage_store

class AuthMiddleware(object):

    def process_response(self, request, response):
        if request.META.has_key('REQUEST_URI'):
            uri = request.META['REQUEST_URI']
            if uri.startswith("/mfileapi/get/"):
                match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
                # No match
                if match is not None:
                    mfileid = match.group(0)
                    logging.info("Match %s" % mfileid)
                    usage_store.stoprecording(mfileid,usage_store.metric_responsetime)

        return response

    def process_request(self, request):
        if request.META.has_key('REQUEST_URI'):
            uri = request.META['REQUEST_URI']
            if uri.startswith("/mfileapi/get/"):
                match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
                # No match
                if match is not None:
                  mfileid = match.group(0)
                  logging.info("Match %s" % mfileid)
                  usage_store.startrecording(mfileid,usage_store.metric_responsetime,1)

        return

