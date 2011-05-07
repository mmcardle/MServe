from piston.handler import BaseHandler
from piston.utils import rc
import piston.authentication as pauth
import piston.oauth as poauth
from dataservice.models import *
from jobservice.models import *
from mserveoauth.models import *
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render_to_response
from django.template import RequestContext
import logging
import cgi
import oauth2 as oauth2
from jobservice.tasks import copyfromurl

from piston.handler import BaseHandler

class RemoteServiceHandler(BaseHandler):
    allowed_methods = ('GET')
    model = RemoteService
    fields = ( 'id','url')
    exclude = ()

class ProtectedResourceHandler(BaseHandler):

    def read(self, request):

        received_token = dict(cgi.parse_qsl(request.META['QUERY_STRING']))
        oauth_token = received_token['oauth_token']
        token = Token.objects.get(key=oauth_token)

        mfile_token_auth = MFileOAuthToken.objects.get(access_token=token)

        retdict = {}
        retdict['auths'] = mfile_token_auth.auths.all()

        logging.info("Returning %s "% retdict)

        return retdict


def oauth_access_token(request):
    oauth_server, oauth_request = pauth.initialize_server_request(request)

    if oauth_request is None:
        return INVALID_PARAMS_RESPONSE

    try:
        access_token = oauth_server.fetch_access_token(oauth_request)

        oauth_token = request.POST['oauth_token']
        request_token = Token.objects.get(key=oauth_token)

        mfile_token_auth = MFileOAuthToken.objects.get(request_token=request_token)
        mfile_token_auth.access_token = access_token
        mfile_token_auth.save()

        return HttpResponse(access_token.to_string())
    except poauth.OAuthError, err:
        return poauth.send_oauth_error(err)

class ReceiveHandler(BaseHandler):

    def read(self,request):

        received_token = dict(cgi.parse_qsl(request.META['QUERY_STRING']))

        if received_token.has_key('oauth_token'):

            oauth_verifier = received_token['oauth_verifier']
            oauth_token = received_token['oauth_token']

            cc = ClientConsumer.objects.get(oauth_token=oauth_token)
            remote_service = cc.remote_service
            oauth_token_secret=cc.oauth_token_secret
            consumer = oauth2.Consumer(remote_service.consumer_key, remote_service.consumer_secret)

            token = oauth2.Token(oauth_token, oauth_token_secret)
            token.set_verifier(oauth_verifier)
            client = oauth2.Client(consumer, token)

            ACCESS_TOKEN_URL = cc.remote_service.get_access_token_url()

            resp, content = client.request(ACCESS_TOKEN_URL, "POST")

            access_token = dict(cgi.parse_qsl(content))

            RESOURCE_URL = remote_service.get_protected_resource_url()

            mconsumer = oauth2.Consumer(remote_service.consumer_key, remote_service.consumer_secret)
            mtoken = oauth2.Token(access_token['oauth_token'],access_token['oauth_token_secret'])
            mclient = oauth2.Client(mconsumer, mtoken)

            mresponse,resourcecontent = mclient.request(RESOURCE_URL)

            import simplejson
            result = simplejson.loads(resourcecontent)
            logging.info(result)
            
            service = DataService.objects.get(id=cc.service_auth.base.id)

            tasks = []
            for auth in result['auths']:

                mfile = service.create_mfile(None,"Import File")

                options = {}
                options['url'] = "%s/auth/%s/getcontents/" % (remote_service.url,auth['id'])
                options['mfile'] = mfile

                outputpath = os.path.join( str(mfile.id) , "content-%s"%auth['id'])
                mfile.file = outputpath
                mfile.save()

                outputs = []
                outputs.append(mfile.file.path)
                (head,tail) = os.path.split(mfile.file.path)

                if not os.path.isdir(head):
                    os.makedirs(head)

                task = copyfromurl.delay([],outputs,options)

                tasks.append(task)

                logging.info("created ouath task %s "% (task))

            retdict = {}
            retdict['message'] = "Importing %s Files" % (len(tasks))

            return render_to_response('receive.html', retdict, context_instance=RequestContext(request))

        else:
            rdict = {}
            if received_token.has_key('error'):
                rdict["error"] = received_token['error']
            else:
                rdict["error"] = "An error occured"
            return rdict     

class ConsumerHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST','DELETE')

    def delete(self, request, id, oauth_token):

        token = Token.objects.get(key=oauth_token)

        try:
            mfile_token_auth = MFileOAuthToken.objects.get(request_token=token)

            for auth in list(mfile_token_auth.auths.all()):
                if auth.base.id == id:
                    auth.delete()

            mfile_token_auth.save()

            return rc.DELETED

        except MFileOAuthToken.DoesNotExist:
            logging.info("MFileOAuthToken Base does not exist")
            return rc.NOT_FOUND

    def update(self, request):

        oauth_token = request.POST['oauthtoken']
        id    = request.POST['id']

        token = Token.objects.get(key=oauth_token)

        try:
            mfile = MFile.objects.get(id=id)
            mfile_token_auth,created = MFileOAuthToken.objects.get_or_create(request_token=token)
            mfile_token_auth.save()
            ro_auth = mfile.create_read_only_auth()
            mfile_token_auth.auths.add(ro_auth)
            mfile_token_auth.save()

            return mfile_token_auth

        except MFile.DoesNotExist:
            logging.info("MFile Base does not exist")
            return rc.NOT_FOUND

    def create(self, request):

        CONSUMER_SERVER = request.POST['url']
        authid= request.POST['authid']

        auth = Auth.objects.get(id=authid)

        remote_service = get_object_or_404(RemoteService, url=CONSUMER_SERVER)
        REQUEST_TOKEN_URL = remote_service.get_request_token_url()

        # key and secret granted by the service provider for this consumer application - same as the MockOAuthDataStore
        consumer = oauth2.Consumer(remote_service.consumer_key, remote_service.consumer_secret)
        client = oauth2.Client(consumer)

        # Get a request token. This is a temporary token that is used for
        # having the user authorize an access token and to sign the request to obtain
        # said access token.
        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(cgi.parse_qsl(content))

        cc = ClientConsumer(oauth_token=request_token['oauth_token'], \
                oauth_token_secret=request_token['oauth_token_secret'], \
                service_auth = auth, \
                remote_service=remote_service)
        cc.save()

        authurl = remote_service.get_full_authcallback_url(request_token['oauth_token'])

        return { "authurl": authurl }