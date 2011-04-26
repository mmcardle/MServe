from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseNotFound
import settings as settings
from dataservice.models import mfile_get_signal

import utils as utils
import api as api
import usage_store as usage_store
import time
import logging
import os
import os.path
import shutil

sleeptime = 10
DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

metric_corruption = "http://mserve/corruption"
metric_dataloss = "http://mserve/dataloss"

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
        api.delete_container(request,id)
        r = rc.DELETED
        return r

    def create(self, request):
        form = HostingContainerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            hostingcontainer = api.create_container(request,name)
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
        api.delete_service(request,id)
        r = rc.DELETED
        return r

    def create(self, request):
        logging.info(request.POST)
        form = DataServiceForm(request.POST)

        if form.is_valid(): 
            dataservice = form.save()
            dataservice = api.create_data_service(dataservice)
            return dataservice
        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):
        # TODO: Fix URL form for creating dataservices (could remove)
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
        api.delete_mfile(request,id)
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
            api.mfile_post_process(mfile)
            
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
        logging.debug("Create MFile len(request.raw_post_data)=%s "% (len(request.raw_post_data)))

        form = MFileForm(request.POST,request.FILES)
        if form.is_valid():

            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None

            logging.debug("API call Creating mfile %s" % serviceid)

            if serviceid == None:
                serviceid = form.cleaned_data['sid']

            logging.debug("API call Creating mfile")

            mfile = api.create_mfile(request, serviceid, file)
            return mfile
        else:
            r = rc.BAD_REQUEST
            logging.debug("API call Creating mfile %s " % form)
            r.write("Invalid Request!")
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