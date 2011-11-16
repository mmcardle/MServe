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
from models import RemoteMServeService
from django.http import HttpResponseForbidden
from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.conf import settings
import settings as settings
import utils as utils
import logging

sleeptime = 10
DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

class ProfileHandler(BaseHandler):
    ''' Profile Handler '''
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

    def update(self, request, servicerequestid=None):
        if request.user.is_staff:
            if request.POST.has_key("state"):
                if request.POST['state'] == "A":

                    if request.POST.has_key('cid'):

                        cid = request.POST['cid']
                        sr = ServiceRequest.objects.get(id=servicerequestid)

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
                    sr = ServiceRequest.objects.get(id=servicerequestid)
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

    def delete(self, request, servicerequestid=None):
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response
        sr = ServiceRequest.objects.get(id=servicerequestid)
        if request.user.get_profile() == sr.profile:
            sr.delete()
            r = rc.DELETED
            return r
        else:
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

    def read(self, request, servicerequestid=None):

        if request.user.is_staff:
            if servicerequestid:
                sr = ServiceRequest.objects.get(id=servicerequestid)
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

        if servicerequestid:
            return ServiceRequest.objects.filter(profile=profile,id=servicerequestid)
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
    allowed_methods = ('GET', 'POST', 'DELETE','PUT')
    model = HostingContainer
    fields = ('name', 'id', 'default_profile', ('dataservice_set', ('name', 'id', 'reportnum', 'starttime', 'endtime','thumbs','mfile_set')  ) ,'reportnum', 'thumbs', ('properties', ('id','value','property', ), ), )
    exclude = ()

    def update(self, request, id):
        if request.user.is_staff:
            return HostingContainer.objects.get(id=id).do("PUT", request=request)
        else:
            return HttpResponseForbidden()

    def read(self, request, id=None, murl=None):

        if id == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)

        if murl and id:
            hc =  get_object_or_404(HostingContainer,id=id)
            r = hc.do(request.method,murl)
            return r

        if id == None and not request.user.is_staff:
            r = rc.FORBIDDEN
            return r

        if id:
            hc = get_object_or_404(HostingContainer,id=id)
            return hc.do("GET")
        else:
            r = rc.FORBIDDEN
            return r

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
                r.write("Invalid Request! %s " % (form))
                return r
        else:
            return HttpResponseForbidden()

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE','PUT')
    model = DataService
    fields = ('name', 'id', 'reportnum', 'starttime', 'endtime', 'mfile_set', 'job_set', 'mfolder_set', 'thumbs', 'priority','subservices_url','folder_structure')
    exclude = ('pk')

    def read(self,request, id=None, containerid=None,serviceid=None):
        if serviceid:
            return self.model.objects.get(id=serviceid).subservices.all()
        if containerid:
            return HostingContainer.objects.get(pk=containerid).do("GET","services")
        if id:
            dataservice = get_object_or_404(self.model, pk=id)
            return dataservice.do("GET")
        return []

    def update(self, request, id):
        try:
            service = DataService.objects.get(pk=id).do("PUT",request=request)
            return service
        except Exception as e:
            r = rc.BAD_REQUEST
            logging.info("Exception %s" % (e))
            r.write("Invalid Request!")
            return r

    def delete(self, request, id):
        logging.info("Deleting Service %s " % id)
        return DataService.objects.get(id=id).do("DELETE")

    def create(self, request, containerid=None, serviceid=None):
        service = None
        if serviceid:
            service = DataService.objects.get(id=serviceid)
            form = SubServiceForm(request.POST)
        else:
            form = DataServiceForm(request.POST)
        if form.is_valid(): 
            if 'name' in request.POST:
                name = request.POST['name']
                if service:
                    dataservice = service.create_subservice(name)
                else:
                    if containerid:
                        container = HostingContainer.objects.get(id=containerid)
                        dataservice = container.create_data_service(name)
                    elif 'container' in request.POST:
                        containerid = request.POST['container']
                        container = HostingContainer.objects.get(id=containerid)
                        dataservice = container.create_data_service(name)
                    else:
                        r = rc.BAD_REQUEST
                        r.write("Invalid Request! - No name in POST parameters")
                        return r
                if request.POST.has_key('starttime'):
                    dataservice.starttime = request.POST['starttime']
                if request.POST.has_key('endtime'):
                    dataservice.endtime = request.POST['endtime']
                dataservice.save()
                return dataservice
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request! - No container in POST parameters")
                return r
        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class SubServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, containerid=None):

        if containerid and request.user.is_staff:
            return DataService.objects.filter(parent__container=containerid)
        else:
            r = rc.FORBIDDEN
            return r

    def create(self, request, containerid=None):
        if "serviceid" in request.POST and "name" in request.POST :
            serviceid = request.POST['serviceid']
            name = request.POST['name']
            container = HostingContainer.objects.get(id=containerid)
            service = container.dataservice_set.get(id=serviceid)
            subservice = service.create_subservice(name=name)
            if request.POST.has_key('starttime'):
                subservice.starttime = request.POST['starttime']
            if request.POST.has_key('endtime'):
                subservice.endtime = request.POST['endtime']
            subservice.save()
            return subservice
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request! %s not valid " % request.POST)
            return r


class DataServiceProfileHandler(BaseHandler):
    allowed_methods = ('GET')
    model = DataServiceProfile
    fields = ('name','id','workflows')

    def read(self, request, serviceid):
        service = DataService.objects.get(id=serviceid)
        return service.do("GET","profiles")


class DataServiceWorkflowHandler(BaseHandler):
    allowed_methods = ('GET')
    model = DataServiceWorkflow
    fields = ('name', 'id', 'tasksets', )


class DataServiceTaskSetHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST','DELETE')
    model = DataServiceTaskSet
    fields = ('name', 'id', 'tasks', 'order')

    def delete(self, request, serviceid, profileid, tasksetid ):
        dsts = DataServiceTaskSet.objects.get(id=tasksetid)
        dsts.delete()
        r = rc.DELETED
        return r

    def update(self, request, serviceid, profileid, tasksetid ):
        dsts = DataServiceTaskSet.objects.get(id=tasksetid)
        dstsf = DataServiceTaskSetForm(request.POST, instance=dsts)
        if dstsf.is_valid():
            dsts = dstsf.save()
            return dsts
        else:
            r = rc.BAD_REQUEST
            logging.info(dstsf)
            r.write("Invalid Request!")
            return r

    def create(self, request, serviceid, profileid ):
        DataService.objects.get(id=serviceid).profiles.get(id=profileid)
        dstsf = DataServiceTaskSetForm(request.POST)
        if dstsf.is_valid():
            dst = dstsf.save()
            return dst
        else:
            r = rc.BAD_REQUEST
            logging.info(dstsf)
            r.write("Invalid Request!")
            return r

class DataServiceTaskHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = DataServiceTask
    fields = ('name', 'task_name', 'id', 'condition', 'args')

    def delete(self, request, serviceid, profileid, taskid ):
        dst = DataServiceTask.objects.get(id=taskid)
        dst.delete()
        r = rc.DELETED
        return r

    def update(self, request, serviceid, profileid, taskid ):
        dst = DataServiceTask.objects.get(id=taskid)
        dstf = DataServiceTaskForm(request.POST, instance=dst)
        if dstf.is_valid():
            dst = dstf.save()
            return dst
        else:
            r = rc.BAD_REQUEST
            logging.info(dstf)
            r.write("Invalid Request!")
            return r

    def create(self, request, serviceid, profileid ):
        DataService.objects.get(id=serviceid).profiles.get(id=profileid)
        dstf = DataServiceTaskForm(request.POST)
        if dstf.is_valid():
            dst = dstf.save()
            return dst
        else:
            r = rc.BAD_REQUEST
            logging.info(dstf)
            r.write("Invalid Request!")
            return r


class BackupFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = BackupFile

    def read(self, request, backupid=None):
        if backupid:
            return BackupFile.objects.get(id=backupid)
        return {}

    def create(self, request, backupid):
        backupfile = BackupFile.objects.get(pk=backupid)
        if request.FILES.has_key("file"):
            file = request.FILES["file"]
            backupfile.file.save(backupfile.name, file, save=True)
            return {"message":"updated backup file"}
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request! no file in request.")
            return r

    def update(self, request, backupid):
        backupfile = BackupFile.objects.get(pk=backupid)
        try:
            utils.write_request_to_field(request, backupfile.file, "%s_%s"%("backup",backupfile.mfile.name))
            return {"message":"updated backup file"}
        except Exception, e:
            logging.info(e)
            raise e

class MFolderHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFolder
    fields = ('name','id','parent')

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
    fields = ('name', 'id' ,'file', 'checksum', 'size', 'mimetype', 'thumb', 'poster', 'proxy', \
                'created' , 'updated', 'thumburl', 'posterurl', 'proxyurl', 'reportnum',\
                ('folder', ('id','name') ) )

    def read(self,request, id=None, serviceid=None, authid=None):
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
        #MFile.objects.get(id=id).delete()
        MFile.objects.get(id=id).do("DELETE")
        r = rc.DELETED
        return r

    def update(self, request, id, field=None):

        mfile = MFile.objects.get(pk=id)
        if field == "thumb":
            utils.write_request_to_field(request, mfile.thumb, 'thumb.png')
            return {"message":"updated thumb"}
        if field == "poster":
            utils.write_request_to_field(request, mfile.poster, 'poster.png')
            return {"message":"updated poster"}
        if field == "proxy":
            utils.write_request_to_field(request, mfile.proxy, 'proxy.mp4')
            return {"message":"updated proxy"}

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

    def create(self, request, id=None ,serviceid=None, authid=None, field=None):

        if field:
            try:
                mfile = MFile.objects.get(pk=id)
                if field == "thumb":
                    file = request.FILES[field]
                    mfile.thumb.save("thumb.png", file, save=True)
                    return {"message":"updated thumb"}
                if field == "poster":
                    file = request.FILES[field]
                    mfile.poster.save("poster.png", file, save=True)
                    return {"message":"updated poster"}
                if field == "proxy":
                    file = request.FILES[field]
                    mfile.proxy.save("proxy.mp4", file, save=True)
                    return {"message":"updated proxy"}
            except MFile.DoesNotExist:
                r = rc.BAD_REQUEST
                r.write("Invalid Request!")
                return r

        form = MFileForm(request.POST, request.FILES)
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

    def read(self, request, containerid=None, serviceid=None, mfileid=None, authid=None ):
        if containerid or serviceid or mfileid:
            base = NamedBase.objects.get(id__in=[containerid,serviceid,mfileid])
            result = {}
            result["usages"] = base.get_usage_summary()
            result["reportnum"] = base.reportnum
            return result
        elif authid:
            auth = Auth.objects.get(pk=authid)
            base = utils.get_base_for_auth(auth)
            result = {}
            result["usages"] = base.get_real_base().get_usage_summary()
            result["reportnum"] = base.reportnum
            return result
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r


class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')
    model = ManagementProperty
    fields = ("value","property","id","values")
    exclude = ()
            
    def read(self, request, containerid=None, serviceid=None, mfileid=None, authid=None):
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

    def create(self, request, id=None, serviceid=None):
        if id==None:
            id=serviceid
        form = ManagementPropertyForm(request.POST)
        if form.is_valid():
            mp = form.save(commit=False)
            mp.base = DataService.objects.get(id=id)
            try:
                ManagementProperty.objects.get(property=mp.property, base=mp.base)
                logging.info("Bad Form %s " % form)
                resp = rc.BAD_REQUEST
                resp.write(". A Management Property called '%s' allready exists " % (mp.property))
                return resp
            except ManagementProperty.DoesNotExist:
                pass
            mp.save()
            return mp
        else:
            logging.info("Bad Form %s " % form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def update(self, request, id=None, serviceid=None):
        if id==None:
            id=serviceid
        form = ManagementPropertyForm(request.POST) 
        if form.is_valid():
            try:
                property = form.cleaned_data['property']
                base = NamedBase.objects.get(id=id)
                existingmanagementproperty = ManagementProperty.objects.get(property=property,base=base)
                form = ManagementPropertyForm(request.POST,instance=existingmanagementproperty)
                mp = form.save()
                return mp
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
            return auth.do("GET",murl)

        return []

    def create(self, request, id=None, containerid=None, serviceid=None,
                        mfileid=None, authid=None):

        if containerid:
            container = HostingContainer.objects.get(id=containerid)
            return container.do("POST", "auths", request=request)
        elif serviceid:
            dataservice = DataService.objects.get(id=serviceid)
            return dataservice.do("POST", "auths", request=request)
        elif mfileid:
            mf = MFile.objects.get(id=mfileid)
            return mf.do("POST", "auths", request=request)
        elif authid:
            auth = Auth.objects.get(id=authid)
            return auth.do("POST", "auths", request=request)
        else:
            resp = rc.BAD_REQUEST
            return resp