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
from mserve.dataservice.models import RemoteMServeService
from django.http import Http404
from django.http import HttpResponseForbidden
from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.conf import settings
from django.http import HttpResponseNotFound
import settings as settings
from django.contrib.admin.views.decorators import staff_member_required
import static as static
from dataservice.models import mfile_get_signal
import utils as utils
import usage_store as usage_store
import time
import logging
import os
import os.path
import shutil
import os

sleeptime = 10
DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

metric_corruption = "http://mserve/corruption"
metric_dataloss = "http://mserve/dataloss"

class ProfileHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT')
    model = MServeProfile
    fields = (('user', () ),'mfiles','mfolders', 'myauths' ,('dataservices', ('id', 'name','mfile_set')), ('containers', ('id', 'name')),   )

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

class ServiceRequestHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE','PUT')
    model = ServiceRequest
    fields = ('id','name','reason','state','status','time','ctime', ('profile', ( 'id',  'user' )  ))

    def update(self,request,id=None):
        if request.user.is_staff:
            if request.POST.has_key("state"):
                if request.POST['state'] == "A":

                    if request.POST.has_key('cid'):

                        cid = request.POST['cid']
                        sr = ServiceRequest.objects.get(id=id)

                        sr.state = "A"
                        sr.save()

                        dataservice = HostingContainer.objects.get(id=cid).create_data_service(sr.name)

                        custauth = dataservice.auth_set.get(authname="customer")

                        sr.profile.auths.add(custauth)

                        return sr
                    else:
                        r = rc.BAD_REQUEST
                        r.write("Invalid arguments - No Container id specified")
                        return r
                elif request.POST['state'] == "R":
                    sr = ServiceRequest.objects.get(id=id)
                    sr.state = "R"
                    sr.save()
                    return sr
                else:
                    r = rc.BAD_REQUEST
                    r.write("Unknown state")
                    return r
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid arguments")
                return r

        else:
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

    def delete(self, request, id=None):
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response
        sr = ServiceRequest.objects.get(id=id)
        if request.user.get_profile() == sr.profile:
            sr.delete()
            r = rc.DELETED
            return r
        else:
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

    def read(self, request, id=None):

        if request.user.is_staff:
            if id:
                sr = ServiceRequest.objects.get(id=id)
                return sr
            else:
                sr = ServiceRequest.objects.all()
                return sr

        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response
        try:
            profile = MServeProfile.objects.get(user=request.user)

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            profile = MServeProfile(user=request.user)
            profile.save()

        if id:
            return ServiceRequest.objects.filter(profile=profile,id=id)
        else:
            return ServiceRequest.objects.filter(profile=profile)

    def create(self, request):
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

        try:
            profile = MServeProfile.objects.get(user=request.user)

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            profile = MServeProfile(user=request.user)
            profile.save()

        srform = ServiceRequestForm(request.POST)
        if srform.is_valid():
            servicerequest = srform.save()
            profile.servicerequests.add(servicerequest)
            profile.save()
            return  servicerequest
        else:
            r = rc.BAD_REQUEST
            r.write(srform.as_p())
            return r

class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST', 'DELETE',)
    model = HostingContainer
    fields = ('name', 'id', ('dataservice_set', ('name', 'id', 'reportnum', 'starttime', 'endtime','thumbs','mfile_set')  ) ,'reportnum', 'thumbs', ('properties', ('id','value','property', ), ), )
    exclude = ()

    def read(self, request, id=None, murl=None):

        if id == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)

        hc =  HostingContainer.objects.get(id=str(id))
        if murl:
            r = hc.do(request.method,murl)
            return r

        if id == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)
        else:
            if id == None and not request.user.is_staff:
                r = rc.FORBIDDEN
                return r
            else:
                return HostingContainer.objects.get(id=str(id)).do("GET")

    def delete(self, request, id):
        logging.info("Deleting Container %s " % id)
        return HostingContainer.objects.get(id=str(id)).do("DELETE")

    def create(self, request):
        if request.user.is_staff:
            form = HostingContainerForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                hostingcontainer = HostingContainer.create_container(name)
                return hostingcontainer
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request! %s " %s)
                return r
        else:
            return HttpResponseForbidden()

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE')
    model = DataService
    fields = ('name', 'id', 'reportnum', 'starttime', 'endtime', 'mfile_set', 'job_set', 'mfolder_set', 'thumbs')
    exclude = ('pk')

    def read(self,request, id=None, containerid=None):
        if containerid:
            return HostingContainer.objects.get(pk=containerid).do("GET","services")
        if id:
            return self.model.objects.get(id=id).do("GET")
        return Http404()

    def delete(self, request, id):
        logging.info("Deleting Service %s " % id)
        return DataService.objects.get(id=id).do("DELETE")

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

class DataServiceTaskHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataServiceTask
    fields = ('task_name','id','condition','allowremote','remotecondition','args')

    def create(self, request, serviceid, profileid ):

        DataService.objects.get(id=serviceid).profiles.get(id=profileid)

        dstf = DataServiceTaskForm(request.POST)

        if dstf.is_valid():
            dst = dstf.save()
            logging.info("DST %s "  % dst.id)
            return dst
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class DataServiceWorkflowHandler(BaseHandler):
    allowed_methods = ('GET')
    model = DataServiceWorkflow
    fields = ('name','id','tasks')

class DataServiceProfileHandler(BaseHandler):
    allowed_methods = ('GET')
    model = DataServiceProfile
    fields = ('name','id','workflows')

    def read(self, request, serviceid):

        service = DataService.objects.get(id=serviceid)

        return service.do("GET","profiles")

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

    def read(self,request, id=None, serviceid=None, authid=None):
        if id:
            return self.model.objects.get(id=id).do("GET")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","mfolders")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET","mfolders")
        return []

class MFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFile
    fields = ('name', 'id' ,'file', 'checksum', 'size', 'mimetype', 'thumb', 'poster', 'proxy', 'created' , 'updated', 'thumburl', 'posterurl', 'proxyurl', 'reportnum')

    def read(self,request, id=None, serviceid=None, authid=None):
        logging.info(id)
        if id :
            return self.model.objects.get(id=id).do("GET")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","mfiles")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET","mfiles")
        return []

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

    def create(self, request, serviceid=None, authid=None):
        logging.debug("Create MFile")

        form = MFileForm(request.POST,request.FILES)
        if form.is_valid():

            kwargs = {}
            if request.FILES.has_key('file'):
                file = request.FILES['file']
                kwargs = {"name":file.name,"file":file}
            else:
                file = None
                kwargs = {"name":"Empty File","file":None}


            if serviceid:
                service = DataService.objects.get(pk=serviceid)
                return service.do("POST","mfiles",**kwargs)
            if authid:
                auth = Auth.objects.get(pk=authid)
                return auth.do("POST","mfiles",**kwargs)
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request when submitting creating mfile")
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

class AuthContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, id):
        try:
            auth = Auth.objects.get(id=id)
            return auth.do("GET","file")
        except Exception as e:
            logging.error(e)
            raise e

class RemoteMServeServiceHandler(BaseHandler):
    allowed_methods = ('GET')
    model = RemoteMServeService

    def read(self, request):
        if request.user.is_staff:
            return RemoteMServeService.objects.all()
        else:
            return []

class MFileContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid=None, authid=None):

        if mfileid:
            logging.info("MFileContentsHandler mfile")
            return MFile.objects.get(pk=mfileid).do("GET","file")
        elif authid:
            logging.info("MFileContentsHandler auth")
            return Auth.objects.get(pk=authid).do("GET","file")
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class MFileWorkflowHandler(BaseHandler):
    allowed_methods = ('POST')

    def create(self, request, mfileid=None, authid=None):

        if not request.POST.has_key('name'):
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

        name = request.POST['name']
        kwargs = { "name":name }

        if mfileid:
            logging.info("MFileWorkflowHandler mfile")
            return MFile.objects.get(pk=mfileid).do("POST","workflows",**kwargs)
        elif authid:
            logging.info("MFileWorkflowHandler auth")
            return Auth.objects.get(pk=authid).do("POST","workflows",**kwargs)
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

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

    def read(self,request, containerid=None,serviceid=None,mfileid=None,authid=None):
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET","usages",**request.GET)
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","usages",**request.GET)
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET","usages",**request.GET)
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET","usages",**request.GET)

class UsageSummaryHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self,request, cid, last_report=-1):
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
    model = ManagementProperty
    fields = ("value","property","id","values")
    exclude = ()
    
    def read(self,request, containerid=None,serviceid=None,mfileid=None,authid=None):
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET","properties")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","properties")
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET","properties")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET","properties")

        return []

        base = NamedBase.objects.get(id=id)
        return base.do("GET","properties")
    
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
    fields = ('authname','id','auth_set','urls','methods','basename','thumburl',('roles' ,('id','rolename','description','methods') ) )

    def read(self,request, id=None, containerid=None,serviceid=None,mfileid=None,authid=None,murl=None):
        if id:
            return self.model.objects.get(id=id).do("GET")
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET","auths")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","auths")
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET","auths")
        if authid:
            auth = Auth.objects.get(pk=authid)
            logging.info("AUTH GET %s"%murl)
            return auth.do("GET",murl)

        return []

    def read2(self, request, id):
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
                ret = {}
                ret["resources"] = container.dataservice_set.all()
                ret["reportnum"] = container.reportnum
                return ret

            if utils.is_service(base):
                service = DataService.objects.get(id=id)
                resources = []
                resources.append(list(service.mfile_set.all()))
                resources.append(list(service.mfolder_set.all()))
                ret = {}
                ret["resources"] = resources
                ret["reportnum"] = service.reportnum
                return ret

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=id)
                ret = {}
                ret["resources"] = list(mfile)
                ret["reportnum"] = mfile.reportnum
                return ret
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
                ret = {}
                ret["resources"] = container.dataservice_set.all()
                ret["reportnum"] = container.reportnum
                return ret

            if utils.is_service(base):
                service = DataService.objects.get(id=base.id)
                resources = []
                resources.append(list(service.mfile_set.all()))
                resources.append(list(service.mfolder_set.all()))
                ret = {}
                ret["resources"] = resources
                ret["reportnum"] = service.reportnum
                logging.info("RET %s" % ret)
                return ret

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=base.id)
                ret = {}
                ret["resources"] = list(mfile)
                ret["reportnum"] = mfile.reportnum
                return ret

        except Auth.DoesNotExist:
            pass

        r = rc.BAD_REQUEST
        r.write("Unknown Resource")
        return r