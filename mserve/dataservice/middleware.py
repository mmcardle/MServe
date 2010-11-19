import re
import logging
import usage_store as usage_store

class AuthMiddleware(object):

    def process_response(self, request, response):
        uri = request.META['REQUEST_URI']
        if uri.startswith("/stagerapi/get/"):
            match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
            # No match
            if match is not None:
                stagerid = match.group(0)
                logging.info("Match %s" % stagerid)
                logging.info("Match %s" % stagerid)
                usage_store.stoprecording(stagerid,usage_store.metric_responsetime)

        return response

    def process_request(self, request):

        uri = request.META['REQUEST_URI']
        if uri.startswith("/stagerapi/get/"):
            match = re.search("[\w]{8}(-[\w]{4}){3}-[\w]{12}", uri)
            # No match
            if match is not None:
                stagerid = match.group(0)
                logging.info("Match %s" % stagerid)
                usage_store.startrecording(stagerid,usage_store.metric_responsetime,1)

        return

