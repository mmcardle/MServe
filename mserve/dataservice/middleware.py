# To change this template, choose Tools | Templates
# and open the template in the editor.
import re
import logging
class AuthMiddleware():

    def process_request(self, request):
        logging.info("Request %s" % request.META['REQUEST_URI'])

        uri = request.META['REQUEST_URI']

        match = re.match("/auth/[\w]{8}(-[\w]{4}){3}-[\w]{12}/", uri)  # No match

        #logging.info("Match %s" % match)