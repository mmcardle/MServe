from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.conf import settings
from django.http import HttpResponseNotFound
from django.http import HttpResponse
import settings as settings
from dataservice.models import mfile_get_signal
from django.shortcuts import render_to_response
import utils as utils
import usage_store as usage_store
import time
import logging
import os
import os.path
import shutil
import os
import cgi
import oauth2 as oauth
import urllib2

sleeptime = 10
DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

metric_corruption = "http://mserve/corruption"
metric_dataloss = "http://mserve/dataloss"

from piston.handler import AnonymousBaseHandler
from piston.handler import BaseHandler
from piston.utils import require_mime
from piston.utils import require_extended

CONSUMER_KEY = 'mmckey'
CONSUMER_SECRET = 'mmcsecret'

class ProfileHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = MServeProfile
    fields = (('user', () ),'mfiles','mfolders',('dataservices', ('id', 'name','mfile_set')), ('containers', ('id', 'name'))  )

    def read(self, request):
        if not request.user.is_authenticated():
            return {}
        try:
            profile = MServeProfile.objects.get(user=request.user)           
            return  profile

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            pp = MServeProfile(user=request.user)
            pp.save()
            return pp

class TestAuthHandler(BaseHandler):

    def read(self, request):

        logging.info("TestAuthHandler %s " % request.META['REQUEST_URI'])

        received_token = dict(cgi.parse_qsl(request.META['QUERY_STRING']))
        #oauth_verifier = received_token['oauth_verifier']
        oauth_token = received_token['oauth_token']
        #oauth_callback_confirmed = received_token['oauth_callback_confirmed']

        #token = Token.objects.get(key=oauth_token,verifier=oauth_verifier)
        token = Token.objects.get(key=oauth_token)

        try:
            logging.info("Returning ")
            mfile_token_auth = MFileOAuthToken.objects.get(token=token)
            mf = mfile_token_auth.mfile
            logging.info("Returning %s "% mf)

            enc_url = urllib2.quote(mf.file.path)

            response = HttpResponse(mimetype=mf.mimetype)
            response['Content-Length'] = mf.file.size
            response['Content-Disposition'] = 'attachment; filename=%s'%(mf.name)
            response["X-SendFile2"] = " %s %s" % (enc_url,"0-")

            #dict = {"name": "somedata" , "url" : mf.thumburl()}
            logging.info("Returning %s "% response)

            return response

        except MFileOAuthToken.DoesNotExist:
            logging.info("Named Base does not exist")

        #oauth_token_secret=cc.oauth_token_secret
        #consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        r = rc.BAD_REQUEST
        r.write("Invalid Request!")
        return r

        

class ReceiveHandler(BaseHandler):

    def read(self,request):

        logging.info("ReceiveHandler REQ %s " % request.META['REQUEST_URI'])

        received_token = dict(cgi.parse_qsl(request.META['QUERY_STRING']))
        oauth_verifier = received_token['oauth_verifier']
        oauth_token = received_token['oauth_token']
        oauth_callback_confirmed = received_token['oauth_callback_confirmed']

        cc = ClientConsumer.objects.get(session=request.COOKIES['sessionid'],oauth_token=oauth_token)
        oauth_token_secret=cc.oauth_token_secret
        consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)

        token = oauth.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)
        client = oauth.Client(consumer, token)

        ACCESS_TOKEN_URL = 'http://%s/api/oauth/access_token/' % (cc.url)

        resp, content = client.request(ACCESS_TOKEN_URL, "POST")
        access_token = dict(cgi.parse_qsl(content))

        logging.info("Access Token:")
        logging.info("    - oauth_token        = %s" % access_token['oauth_token'])
        logging.info("    - oauth_token_secret = %s" % access_token['oauth_token_secret'])
        logging.info("You may now access protected resources using the access tokens above.")

        RESOURCE_URL = 'http://%s/posts/' % (cc.url)

        mconsumer = oauth.Consumer(CONSUMER_KEY,CONSUMER_SECRET)
        mtoken = oauth.Token(access_token['oauth_token'],access_token['oauth_token_secret'])
        mclient = oauth.Client(mconsumer, mtoken)

        mresponse,content = mclient.request(RESOURCE_URL)

        logging.info("mresponse %s "% mresponse)
        logging.info("Content %s "% len(content))
        logging.info("Content %s "% content)

        return {"receive":"ok"}

class ConsumerHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')

    def read(self, request):

        logging.info("REQ %s " % request.META['REQUEST_URI'])

        return {"name": "somedata"}


    def update(self, request):

        logging.info("ConsumerHandler %s"%request.META['REQUEST_URI'])

        oauth_token = request.POST['oauthtoken']
        id    = request.POST['id']

        token = Token.objects.get(key=oauth_token)

        try:
            mfile = MFile.objects.get(id=id)
            logging.info("Mfile %s" % mfile)

            mfile_token_auth = MFileOAuthToken(token=token,mfile=mfile)

            logging.info("mfile_token_auth %s" % mfile_token_auth)
            mfile_token_auth.save()

        except MFile.DoesNotExist:
            logging.info("Named Base does not exist")

        return {}


    def create(self, request):

        logging.info("ConsumerHandler REQ %s " % request.META['REQUEST_URI'])

        # settings for the local test consumer
        CONSUMER_SERVER = request.POST['url']
        #CONSUMER_PORT = os.environ.get("CONSUMER_PORT") or '80'

        logging.info("CONSUMER_SERVER %s"%CONSUMER_SERVER)

        # fake urls for the test server (matches ones in server.py)
        REQUEST_TOKEN_URL = 'http://%s/api/oauth/request_token/' % (CONSUMER_SERVER)

        AUTHORIZE_URL = 'http://%s/api/oauth/authorize/' % (CONSUMER_SERVER)

        logging.info("REQUEST_TOKEN_URL %s"%REQUEST_TOKEN_URL)

        # key and secret granted by the service provider for this consumer application - same as the MockOAuthDataStore


        consumer = oauth.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
        client = oauth.Client(consumer)

        # Step 1: Get a request token. This is a temporary token that is used for
        # having the user authorize an access token and to sign the request to obtain
        # said access token.

        resp, content = client.request(REQUEST_TOKEN_URL, "GET")
        logging.info(content)

        if resp['status'] != '200':
            raise Exception("Invalid response %s." % resp['status'])

        request_token = dict(cgi.parse_qsl(content))

        logging.info("Request Token:")
        logging.info("    - oauth_token        = %s" % request_token['oauth_token'])
        logging.info("    - oauth_token_secret = %s" % request_token['oauth_token_secret'])

        cc = ClientConsumer(session=request.COOKIES['sessionid'],oauth_token=request_token['oauth_token'],oauth_token_secret=request_token['oauth_token_secret'],url=CONSUMER_SERVER)
        cc.save()

        logging.info("Go to the following link in your browser:")
        logging.info( "%s?oauth_token=%s" % (AUTHORIZE_URL, request_token['oauth_token']))

        callback = urllib2.quote("http://ogio/receive")

        authurl = "%s?oauth_token=%s&oauth_callback=%s"% (AUTHORIZE_URL, request_token['oauth_token'],callback)

        return { "authurl": authurl }

class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST','DELETE')
    model = HostingContainer
    fields = ('name', 'id','dataservice_set',"reportnum")
    exclude = ('pk')

    def read(self, request, id=None):
        if id == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)
        else:
            if id == None and not request.user.is_staff:
                r = rc.FORBIDDEN
                return r
            else:
                return HostingContainer.objects.get(id=str(id))

    def delete(self, request, id):
        logging.info("Deleting Container %s " % id)
        HostingContainer.objects.get(id=str(id)).delete()
        r = rc.DELETED
        return r

    def create(self, request):
        form = HostingContainerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            hostingcontainer = HostingContainer.create_container(name)
            return hostingcontainer
        else:
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE')
    model = DataService
    fields = ('name', 'id', 'reportnum', 'starttime', 'endtime', 'mfile_set', 'job_set', 'mfolder_set')
    exclude = ('pk')

    def delete(self, request, id):
        logging.info("Deleting Service %s " % id)
        DataService.objects.get(id=id).delete()
        r = rc.DELETED
        return r

    def create(self, request):
        logging.info(request.POST)
        form = DataServiceForm(request.POST)

        if form.is_valid(): 

            logging.info("CREATE DATASERVICE %s" % request.POST)

            name = request.POST['name']
            containerid = request.POST['container']

            container = HostingContainer.objects.get(id=containerid)

            dataservice = container.create_data_service(name)
            
            return dataservice
        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):
        logging.info(request.POST)
        form = DataServiceURLForm(request.POST)

        if form.is_valid():

            logging.info("CREATE DATASERVICE %s" % request.POST)

            name = request.POST['name']

            container = HostingContainer.objects.get(id=containerid)

            dataservice = container.create_data_service(name)

            return dataservice
        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class InfoHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, id):
        try:
            auth = Auth.objects.get(id=id)
            parent = auth

            while parent.base == None:
                parent = parent.parent

            base = parent.base
            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=base.id)
                return utils.clean_mfile(mfile)
        except Auth.DoesNotExist:
            # TODO - fix
            logging.error("Auth does not exist")
            r = rc.BAD_REQUEST
            return r

class MFolderHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFolder
    fields = ('name','id')

    def read(self, request, id=None):
        return MFolder.objects.get(id=str(id))

class MFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFile
    fields = ('name', 'id' ,'file', 'checksum', 'size', 'mimetype', 'thumb', 'poster', 'proxy', 'created' , 'updated', 'thumburl', 'posterurl', 'proxyurl', 'reportnum')

    def delete(self, request, id):
        logging.info("Deleting mfile %s " % id)
        MFile.objects.get(id=id).delete()
        r = rc.DELETED
        return r

    def update(self, request, id):
        form = UpdateMFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            mfile = MFile.objects.get(pk=id)
            logging.info("Update %s with file %s" % (id,file))
            mfile.file = file
            mfile.name = file.name
            mfile.size = file.size
            mfile.save()
            mfile.post_process()
            
            backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
            backup.save()

            return mfile

        else:
            r = rc.BAD_REQUEST
            logging.info("Bad Form %s" % (form))
            r.write("Invalid Request!")
            return r

    def create(self, request, serviceid=None):
        logging.debug("Create MFile")

        form = MFileForm(request.POST,request.FILES)
        if form.is_valid():

            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None

            if serviceid == None:
                serviceid = form.cleaned_data['sid']

            try:
                service = DataService.objects.get(id=serviceid)
                name = "Empty File"
                if file is not None:
                    name = file.name
                mfile = service.create_mfile(file,name)
                return mfile
            except DataService.DoesNotExist:
                try:
                    auth = Auth.objects.get(id=serviceid)

                    if utils.is_service(auth.base):
                        service = DataService.objects.get(id=auth.base.id)
                        name = "Empty File"
                        if file is not None:
                            name = file.name
                        mfile = service.create_mfile(file,name)
                        return mfile

                    r = rc.BAD_REQUEST
                    r.write("Invalid Request! Auth '%s' is not a DataService Auth" % serviceid)

                except Auth.DoesNotExist:
                    logging.info("Auth.DoesNotExist")
                    r = rc.BAD_REQUEST
                    r.write("Invalid Request! DataService '%s' does not exist " % serviceid)
                    return r

        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request! Submitted Form Invalid %s"% form)
            return r

class MFileVerifyHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        md5 = utils.md5_for_file(mfile.file)

        dict= {}
        dict["mfile"] = mfile
        dict["md5"] = md5
        
        return dict

class MFileContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        service = mfile.service
        container = service.container
        logging.info("Finding limit for %s " % (mfile.name))
        accessspeed = DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (accessspeed,mfile.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (accessspeed,mfile.name))
            except ObjectDoesNotExist:
                pass

        

        check1 = mfile.checksum
        check2 = utils.md5_for_file(mfile.file)

        file=mfile.file

        sigret = mfile_get_signal.send(sender=self, mfile=mfile)
        for k,v in sigret:
            logging.info("Signal %s returned %s " % (k,v))

        if(check1==check2):
            logging.info("Verification of %s on read ok" % mfile)
        else:
            logging.info("Verification of %s on read FAILED" % mfile)
            usage_store.record(mfile.id,metric_corruption,1)
            backup = BackupFile.objects.get(mfile=mfile)
            check3 = mfile.checksum
            check4 = utils.md5_for_file(backup.file)
            if(check3==check4):
                shutil.copy(backup.file.path, mfile.file.path)
                file = backup.file
            else:
                logging.info("The file %s has been lost" % mfile)
                usage_store.record(mfile.id,metric_dataloss,mfile.size)
                return rc.NOT_HERE

        p = str(file)
        dlfoldername = "dl%s" % accessspeed

        redirecturl = utils.gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = file.path

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            logging.info("Linking ")
            logging.info("   %s " % mfilefilepath )
            logging.info("to %s " % fullfilepath )
            os.link(mfilefilepath,fullfilepath)

        import dataservice.models as models
        usage_store.record(mfile.id,models.metric_access,mfile.size)

        return redirect("/%s"%redirecturl)


class RoleHandler(BaseHandler):
    def read(self,request, id):
        base = NamedBase.objects.get(pk=id)
        if utils.is_container(base):
            containerauths = Auth.objects.filter(base=base.id)
            roles = []
            for containerauth in containerauths:
                roledict = []
                for role in containerauth.roles.all():
                    roles.append(role)
                roledict.append(roles)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        if utils.is_service(base):
            serviceauths = Auth.objects.filter(base=base.id)
            roles = []
            for serviceauth in serviceauths:
                for role in serviceauth.roles.all():
                    roles.append(role)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        if utils.is_mfile(base):
            mfileauths = Auth.objects.filter(base=base.id)
            roles = []
            for mfileauth in mfileauths:
                for a in mfileauth.roles.all():
                    roles.append(a)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        r = rc.BAD_REQUEST
        r.write("Invalid Request!")
        return r

class UsageHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Usage
    fields = ('squares','total','nInProgress','metric','rate','reports','time,','rateCumulative','total','rateTime')

    def read(self,request, id):
        return usage_store.get_usage(id)

class UsageSummaryHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self,request, id, last_report=-1):
        last = int(last_report)
        try:
            base = NamedBase.objects.get(pk=id)
        except NamedBase.DoesNotExist:
            auth = Auth.objects.get(pk=id)
            base = utils.get_base_for_auth(auth)

        if last is not -1:
            while last == base.reportnum:
                logging.debug("Waiting for new usage lastreport=%s" % last)
                time.sleep(sleeptime)
                base = NamedBase.objects.get(id=id)

        usages = usage_store.get_usage_summary(id)

        result = {}
        result["usages"] = usages
        result["reportnum"] = base.reportnum

        return result

class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')
    fields = ("value","property","id")

    def read(self,request, id):
        base = NamedBase.objects.get(id=id)
        properties = ManagementProperty.objects.filter(base=base)
        properties_json = []
        for prop in properties:
            properties_json.append(prop)
        return properties_json

    def create(self, request, id):
        resp = rc.BAD_REQUEST
        #resp.write("Not Allowed")
        return resp

    def update(self, request, id):
        form = ManagementPropertyForm(request.POST) 
        if form.is_valid(): 

            property = form.cleaned_data['property']

            base = NamedBase.objects.get(id=id)

            try:
                existingmanagementproperty = ManagementProperty.objects.get(property=property,base=base)
                value    = form.cleaned_data['value']
                existingmanagementproperty.value = value
                existingmanagementproperty.save()
                logging.warn("### Management Property '%s' on '%s' set to '%s' ###"%(property,base,value))
                return existingmanagementproperty
            except ObjectDoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write(" The Management Property '%s' doesn't exist " % (property))
                return resp

        else:
            logging.info("Bad Form %s " % form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        
class AuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = Auth
    fields = ('authname','id','auth_set',('roles' ,('id','rolename','description','methods') ) )


    def read(self, request, id):
        try:
            auth = Auth.objects.get(id=id)
            return auth
        except Auth.DoesNotExist:
            pass

        try:
            base = NamedBase.objects.get(id=id)
            return base.auth_set.all()
        except NamedBase.DoesNotExist:
            logging.debug("NamedBase does not exist")



        return HttpResponseNotFound("Auth not found")


    def create(self, request, id):

        methods_string = request.POST['methods']
        methods = methods_string.split(",")

        try:
            base = NamedBase.objects.get(id=id)

            

        except NamedBase.DoesNotExist:
            logging.debug("NamedBase does not exist")

        try:
            auth = Auth.objects.get(id=id)

            subauth = Auth(parent=auth,authname="New Auth")
            subauth.save()

            role = Role(rolename="newrole")
            role.setmethods(methods)
            role.description = "New Role"
            role.save()

            subauth.roles.add(role)

            logging.debug("create subauth %s for %s with methods %s " % (subauth,auth,methods) )

            return subauth
        except Auth.DoesNotExist:
            logging.debug("Auth does not exist")

        return []
        

class ResourcesHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, id, last_known=None):

        if last_known == None:
            last = -1
        else:
            last = int(last_known)
        try:
            base = NamedBase.objects.get(pk=id)

            logging.debug("reportnum = %s " % (base.reportnum))

            if last > base.reportnum:
                last = base.reportnum

            if last is not -1:
                while last == base.reportnum:
                    logging.debug("Waiting for new services lastreport=%s" % (last))
                    time.sleep(sleeptime)
                    base = NamedBase.objects.get(id=id)

            if utils.is_container(base):
                container = HostingContainer.objects.get(id=id)
                return container

            if utils.is_service(base):
                service = DataService.objects.get(id=id)
                return service

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=id)
                return mfile
        except NamedBase.DoesNotExist:
            pass

        try:
            auth = Auth.objects.get(pk=id)
            base = auth.base

            if last is not -1:
                while last == base.reportnum:
                    logging.debug("Waiting for new services lastreport=%s" % (last))
                    time.sleep(sleeptime)
                    base = NamedBase.objects.get(id=base.id)

            if utils.is_container(base):
                container = HostingContainer.objects.get(id=base.id)
                return container

            if utils.is_service(base):
                service = DataService.objects.get(id=base.id)
                logging.info("Returning Mfile %s " % service)
                return service

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=base.id)

                return mfile

        except Auth.DoesNotExist:
            pass

        r = rc.BAD_REQUEST
        r.write("Unknown Resource")
        return r