import os.path
from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from dataservice import views
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.conf import settings

from dataservice.tasks import thumbvideo
from dataservice.tasks import thumbimage
from dataservice.tasks import add
from django.http import HttpResponse
from celery.result import AsyncResult

import utils as utils
import usage_store as usage_store

import time
import pickle
import base64
import logging
import magic
import hashlib
import os
import shutil
import Image
import tempfile

base            = "/home/"
container_base  = "/container/"
service_base    = "/service/"
stager_base     = "/stager/"
auth_base       = "/auth/"

thumbsize = (210,128)
postersize = (420,256)
sleeptime = 10
DEFAULT_ACCESS_SPEED = "50"

generic_get_methods = ["getauths","getroles"]

generic_post_methods = ["getorcreateauth","addauth"]

generic_put_methods = ["setroles"]

generic_delete_methods = ["revokeauth"]

generic_methods = ["getusagesummary","getroleinfo","getmanagedresources"] + generic_get_methods + generic_post_methods + generic_put_methods + generic_delete_methods

all_container_methods = ["makeserviceinstance","getservicemetadata","getdependencies",
    "getprovides","setresourcelookup", "getstatus","setmanagementproperty"] + generic_methods

service_customer_methods =  ["createstager"] + generic_methods
service_admin_methods =  service_customer_methods + ["setmanagementproperty"]

all_service_methods = [] + service_admin_methods

data_stager_monitor_methods = ["getusagesummary"]
data_stager_owner_methods = ["get", "put", "post", "delete", "verify"] + generic_methods

all_stager_methods = data_stager_owner_methods + data_stager_monitor_methods

def gen_sec_link_orig(rel_path,prefix):
      import time, hashlib
      if not rel_path.startswith("/"):
        rel_path = "%s%s" % ("/", rel_path)
      secret = 'ugeaptuk6'
      uri_prefix = '/%s/' % prefix
      hextime = "%08x" % time.time()
      token = hashlib.md5(secret + rel_path + hextime).hexdigest()
      return '%s%s/%s%s' % (uri_prefix, token, hextime, rel_path)

def create_container(request,name):
    hostingcontainer = HostingContainer(name=name)
    hostingcontainer.save()

    hostingcontainerauth = HostingContainerAuth(hostingcontainer=hostingcontainer,authname="full")

    hostingcontainerauth.save()

    owner_role = Role(rolename="admin")
    owner_role.setmethods(all_container_methods)
    owner_role.description = "Full access to the container"
    owner_role.save()

    hostingcontainerauth.roles.add(owner_role)

    logging.info(owner_role)

    managementproperty = ManagementProperty(property="accessspeed",base=hostingcontainer,value=DEFAULT_ACCESS_SPEED)
    managementproperty.save()

    usage_store.startrecording(hostingcontainer.id,usage_store.metric_container,1)

    return hostingcontainer

def delete_container(request,containerid):
    usage_store.stoprecording(containerid,usage_store.metric_container)
    container = HostingContainer.objects.get(id=containerid)
    logging.info("Deleteing service %s %s" % (container.name,containerid))

    usages = Usage.objects.filter(base=container)
    for usage in usages:
        usage.base = None
        usage.save()

    container.delete()
    logging.info("Container Deleted %s " % containerid)

def create_data_service(request,containerid,name):
    container = HostingContainer.objects.get(id=containerid)
    dataservice = DataService(name=name,container=container)
    dataservice.save()

    serviceauth = DataServiceAuth(dataservice=dataservice,authname="full")
    
    serviceauth.save()

    owner_role = Role(rolename="serviceadmin")
    owner_role.setmethods(service_admin_methods)
    owner_role.description = "Full control of the service"
    owner_role.save()

    customer_role = Role(rolename="customer")
    customer_role.setmethods(service_customer_methods)
    customer_role.description = "Customer Access to the service"
    customer_role.save()

    serviceauth.roles.add(owner_role)
    serviceauth.roles.add(customer_role)

    customerauth = DataServiceAuth(dataservice=dataservice,authname="customer")
    customerauth.save()

    customerauth.roles.add(customer_role)

    managementproperty = ManagementProperty(property="accessspeed",base=dataservice,value=DEFAULT_ACCESS_SPEED)
    managementproperty.save()

    usage_store.startrecording(dataservice.id,usage_store.metric_service,1)
    
    return dataservice

def delete_service(request,serviceid):
    usage_store.stoprecording(serviceid,usage_store.metric_service)
    service = DataService.objects.get(id=serviceid)
    logging.info("Deleteing service %s %s" % (service.name,serviceid))

    usages = Usage.objects.filter(base=service)
    for usage in usages:
        usage.base = service.container
        usage.save()

    service.delete()
    logging.info("Service Deleted %s " % serviceid)

def create_data_stager(request,serviceid,file):
    service = DataService.objects.get(id=serviceid)
    if file==None:
        datastager = DataStager(name="Empty File",service=service)
    else:
        datastager = DataStager(name=file.name,service=service,file=file)
    datastager.save()

    if datastager.file:
        # MIME type
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        mimetype = m.file(datastager.file.path)
        datastager.mimetype = mimetype
        # checksum
        datastager.checksum = utils.md5_for_file(datastager.file)
        # record size
        datastager.size = file.size
        # save it
        datastager.save()

        thumbpath = os.path.join( str(datastager.file) + ".thumb.jpg")
        posterpath = os.path.join( str(datastager.file) + ".poster.jpg")
        fullthumbpath = os.path.join(settings.THUMB_ROOT , thumbpath)
        fullposterpath = os.path.join(settings.THUMB_ROOT , posterpath)
        (thumbhead,tail) = os.path.split(fullthumbpath)
        (posterhead,tail) = os.path.split(fullposterpath)

        if not os.path.isdir(thumbhead):
            os.makedirs(thumbhead)

        if not os.path.isdir(posterhead):
            os.makedirs(posterhead)

        if mimetype.startswith('video'):
            logging.info("Creating thumb in process for Video '%s' %s " % (datastager,mimetype))
            # Do this in Process
            thumbtask = thumbvideo(datastager.file.path,fullthumbpath,thumbsize[0],thumbsize[1])
            datastager.thumb = thumbpath
            postertask = thumbvideo(datastager.file.path,fullposterpath,postersize[0],postersize[1])
            datastager.poster = posterpath
            logging.info("Tasks thumb:%s poster:%s " % (thumbtask,postertask))
        elif mimetype.startswith('image'):
            logging.info("Creating thumb inprocess for Image '%s' %s " % (datastager,mimetype))
            thumbtask = thumbimage(datastager.file.path,fullthumbpath,thumbsize[0],thumbsize[1])
            datastager.thumb = thumbpath
            postertask = thumbimage(datastager.file.path,fullposterpath,postersize[0],postersize[1])
            datastager.poster = posterpath
            # Do this asynchronously
            #logging.info("Creating thumb asynchronously for Image '%s' %s " % (datastager,mimetype))
            #thumbtaskPIL = thumbimage.delay("http://ogio/stagerapi/get/%s/"%(datastager.id),datastager.id,"http://ogio/thumbapi/",(210,128))
            logging.info("Tasks thumb:%s poster:%s " % (thumbtask,postertask))
        else:
            logging.info("Not creating thumb for '%s' %s " % (datastager,mimetype))

        datastager.save()

    datastagerauth_owner = DataStagerAuth(stager=datastager,authname="owner")
    datastagerauth_owner.save()

    owner_role = Role(rolename="owner")
    methods = data_stager_owner_methods
    owner_role.setmethods(methods)
    owner_role.description = "Owner of the data"
    owner_role.save()

    datastagerauth_owner.roles.add(owner_role)

    monitor_role = Role(rolename="monitor")
    methods = data_stager_monitor_methods
    monitor_role.setmethods(methods)
    monitor_role.description = "Collect usage reports"
    monitor_role.save()

    datastagerauth_owner.roles.add(monitor_role)

    datastagerauth_monitor = DataStagerAuth(stager=datastager,authname="monitor")
    datastagerauth_monitor.save()

    datastagerauth_monitor.roles.add(monitor_role)

    if file is not None:
        backup = BackupFile(name="backup_%s"%file.name,stager=datastager,mimetype=datastager.mimetype,checksum=datastager.checksum,file=file)
        backup.save()

    #logging.info("backup %s " % dir(backup))
    #logging.info("datastager.file %s " % datastager.file)
    #logging.info("datastager.file.path %s " % datastager.file.path)
    #logging.info("backup.file %s " % backup.file)
    #logging.info("backup.file.path %s " % backup.file.path)
    #logging.info("backup.file %s " % dir(backup.file))
    #logging.info("models.fs " % mserve.dataservice.models.fs)

    usage_store.startrecording(datastager.id,usage_store.metric_stager,1)
    usage_store.startrecording(datastager.id,usage_store.metric_archived,1)

    if file is not None:
        usage_store.record(datastager.id,usage_store.metric_disc,datastager.size)
        usage_store.record(datastager.id,usage_store.metric_ingest,datastager.size)

    return datastager

def delete_stager(request,stagerid):
    usage_store.stoprecording(stagerid,usage_store.metric_stager)
    usage_store.stoprecording(stagerid,usage_store.metric_archived)
    stager = DataStager.objects.get(id=stagerid)
    logging.info("Deleteing stager %s %s" % (stager.name,stagerid))

    usages = Usage.objects.filter(base=stager)
    logging.info("Deleteing stager usage")
    for usage in usages:
        logging.info("Saving Usage %s " % usage)
        usage.base = stager.service
        usage.save()

    stager.delete()
    logging.info("Stager Deleted %s " % stagerid)

class GlobalHandler(BaseHandler):
     allowed_methods = ('GET')

     def read(self, request):
         containers = HostingContainer.objects.all()
         dict = {}
         dict["containers"] = containers
         return dict


class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST','DELETE')
    model = HostingContainer
    fields = ('name', 'id' )
    exclude = ('pk')

    def delete(self, request, containerid):
        logging.info("Deleting Container %s " % containerid)
        delete_container(request,containerid)

    def read(self, request, containerid):
        container = HostingContainer.objects.get(id=containerid)
        if request.META["HTTP_ACCEPT"] == "application/json":
            return container
        return views.render_container(request,containerid)

    def create(self, request):
        reqjson = (request.META["HTTP_ACCEPT"] == "application/json")
        form = HostingContainerForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            hostingcontainer = create_container(request,name)

            if reqjson:
                return hostingcontainer

            return redirect('/container/'+str(hostingcontainer.id))
        else:
            return views.home(request,form=form)
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            if request.META.has_key("HTTP_REFERER"):
                return HttpResponseRedirect(request.META["HTTP_REFERER"])
            else:
                r = rc.BAD_REQUEST
                return r

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE')
    model = DataService
    fields = ('name', 'id' )
    exclude = ('pk')

    def delete(self, request, serviceid):
        logging.info("Deleting Service %s " % serviceid)
        delete_service(request,serviceid)
    
    def read(self, request, serviceid):
        service = DataService.objects.get(id=serviceid)
        if request.META["HTTP_ACCEPT"] == "application/json":
           return service
        return views.render_service(request,service.id)

    def create(self, request):
        reqjson = (request.META["HTTP_ACCEPT"] == "application/json")
        form = DataServiceForm(request.POST) 
        if form.is_valid(): 
            
            containerid = form.cleaned_data['cid']
            name = form.cleaned_data['name']
            dataservice = create_data_service(request,containerid,name)

            if reqjson:
                return dataservice

            return redirect('/service/'+str(dataservice.id))
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            containerid = form.data['cid']
            return views.render_container(request,containerid,form=form)

class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):

        form = DataServiceURLForm(request.POST)
        logging.info("Request data = %s" % form)
        if form.is_valid(): 
            logging.info("Form valid = %s" % form)
            name = form.cleaned_data['name']
            dataservice = create_data_service(request,containerid,name)

            if request.META["HTTP_ACCEPT"] == "application/json":
                logging.info("Returning JSON = " % dataservice)
                return dataservice

            logging.info("Returning Redirect = %s" % dataservice)
            return redirect('/service/'+str(dataservice.id))
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class ThumbHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def create(self, request):
        logging.info("Thumb Update")
        if request.FILES.has_key('file'):
            file = request.FILES['file']
            logging.info("file %s"%file)
            if request.POST.has_key('stagerid'):
                stagerid = request.POST['stagerid']
                logging.info("stagerid %s"%stagerid)
                stager = DataStager.objects.get(id=stagerid)
                if stager == None:
                    logging.info("No such stager %s"%stagerid)
                    r = rc.BAD_REQUEST
                    r.write("Invalid Request!")
                    return r

                try:
                    thumb = stager.thumb
                    logging.info("Deleting existing thumb for stager %s"%stager)
                    stager.thumb.delete()
                except ObjectDoesNotExist:
                    pass

                logging.info("Updating thumb for stager %s"%stager)

                thumb = Thumb(stager=stager,file=file)
                thumb.file = file
                thumb.save()
                logging.info("Updated %s"%thumb)

                return thumb
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request!")
                return r
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class CorruptionHandler(BaseHandler):
    allowed_methods = ('PUT')

    def update(self, request, stagerid, backup=False):
        stager = DataStager.objects.get(pk=stagerid)
        if not backup:
            stager = DataStager.objects.get(pk=stagerid)
            logging.info("Attempting to corrupt file '%s' " % (stager))
            f = open(stager.file.path,'wb')
            f.writelines(["corruption"])
        else:
            logging.info("Attempting to corrupt backup file for file'%s'" % (stager))
            backup = BackupFile.objects.get(stager=stager)
            f = open(backup.file.path,'wb')
            f.writelines(["corruption"])
        
        return stager

class DataStagerJSONHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = DataStager
    fields = ('name', 'id', 'file','checksum', 'thumb', 'poster', 'mimetype', 'created', 'updated' )
    exclude = ('pk')

class DataStagerHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    #model = DataStager
    #fields = ('name', 'id', 'file','checksum', ('thumb', ('id','name','file') ) )
    #exclude = ('pk')

    def delete(self, request, stagerid):
        logging.info("Deleting Stager %s " % stagerid)
        delete_stager(request,stagerid)

    def read(self, request, stagerid):
        try:
            stager = DataStager.objects.get(pk=stagerid)
            base = NamedBase.objects.get(pk=stagerid)

            if re.match("application/json", request.META["HTTP_ACCEPT"]):
            #if request.META["HTTP_ACCEPT"].contains("application/json"):
                return stager
            return views.render_stager(request,stager.id,show=True)
        except ObjectDoesNotExist:
            error = "The file with the id %s does not exist "%stagerid
            if re.match("application/json", request.META["HTTP_ACCEPT"]):
                r = rc.NOT_FOUND
                r.write(error)
                return r
            return views.render_error(request,error)

    def update(self, request):
        form = UpdateDataStagerForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            stagerid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            datastager = DataStager.objects.get(pk=stagerid)
            datastager.file = file
            datastager.size = file.size

            backup = BackupFile(name="backup_%s"%file.name,stager=datastager,mimetype=datastager.mimetype,checksum=datastager.checksum,file=file)
            backup.save()

            usage_store.startrecording(stagerid,usage_store.metric_disc,datastager.size)
            usage_store.startrecording(stagerid,usage_store.metric_archived,datastager.size)

            datastager.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r
        
    def render_subauth(self, stager, auth, show=False):
        sub_auths = JoinAuth.objects.filter(parent=auth.id)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        form = SubAuthForm()
        form.fields['id_parent'].initial = auth.id
        dict = {}
        dict["stager"] = stager
        if stager.file == '' or stager.file == None:
            dict["altfile"] = "/mservemedia/images/empty.png"
        if not show:
            stager.file = None
            dict["altfile"] = "/mservemedia/images/forbidden.png"
    
        dict["form"] = form
        dict["auths"] = subauths
        dict["formtarget"] = "/auth/"
        return render_to_response('stager.html', dict)

    def create(self, request):
        logging.info(request)
        logging.info(request.FILES)
        reqjson=(request.META["HTTP_ACCEPT"] == "application/json")
        form = DataStagerForm(request.POST,request.FILES) 
        if form.is_valid(): 
            
            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None
            serviceid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            datastager = create_data_stager(request, serviceid, file)

            if reqjson:
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
            #return views.render_service(request,serviceid,newstager=datastager.id)
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                r.write("Invalid Request!")
                return r
                #return views.render_stager(request,stager.id)
            r = rc.BAD_REQUEST
            r.write("%s"%form)
            return r

class DataStagerVerifyHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, stagerid):
        datastager = DataStager.objects.get(pk=stagerid)
        md5 = utils.md5_for_file(datastager.file)

        dict= {}
        dict["stager"] = datastager
        dict["md5"] = md5
        
        return dict

class DataStagerContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, stagerid):
        datastager = DataStager.objects.get(pk=stagerid)
        service = datastager.service
        container = service.container
        logging.info("Finding limit for %s " % (datastager.name))
        accessspeed = DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (accessspeed,datastager.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (accessspeed,datastager.name))
            except ObjectDoesNotExist:
                pass

        dlfoldername = "dl%s"%accessspeed

        check1 = datastager.checksum
        check2 = utils.md5_for_file(datastager.file)

        file=datastager.file

        if(check1==check2):
            logging.info("Verification of %s on read ok" % datastager)
        else:
            logging.info("Verification of %s on read FAILED" % datastager)
            usage_store.record(datastager.id,usage_store.metric_corruption,1)
            backup = BackupFile.objects.get(stager=datastager)
            check3 = datastager.checksum
            check4 = utils.md5_for_file(backup.file)
            if(check3==check4):
                shutil.copy(backup.file.path, datastager.file.path)
                file = backup.file
            else:
                logging.info("The file %s has been lost" % datastager)
                usage_store.record(datastager.id,usage_store.metric_dataloss,datastager.size)
                return rc.NOT_HERE

        p = str(file)

        redirecturl = gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        datastagerfilepath = file.path

        logging.info("Redirect URL      = %s " % redirecturl)
        logging.info("fullfilepath      = %s " % fullfilepath)
        logging.info("fullfilefolder    = %s " % fullfilepathfolder)
        logging.info("datastagerfp      = %s " % datastagerfilepath)
        logging.info("datastagerf       = %s " % file)

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            os.link(datastagerfilepath,fullfilepath)

        usage_store.record(datastager.id,usage_store.metric_access,datastager.size)

        return redirect("/%s"%redirecturl)


class DataStagerURLHandler(BaseHandler):
    
    def update(self, request, stagerid):
        form = UpdateDataStagerFormURL(request.POST,request.FILES) 
        if form.is_valid(): 
            
            file = request.FILES['file']
            datastager = DataStager.objects.get(pk=stagerid)
            datastager.file = file
            datastager.name = file.name
            datastager.size = file.size
            datastager.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            logging.info("DataStagerURLHandler %s "%form)
            return r

    def create(self, request, serviceid):
        logging.info(request)
        logging.info(request.FILES)
        form = DataStagerURLForm(request.POST,request.FILES) 
        if form.is_valid(): 
            
            file = request.FILES['file']
            #service = DataService.objects.get(id=serviceid)
            datastager = create_data_stager(request, serviceid, file)

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class ManagedResourcesContainerHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ContainerResourcesReport
    fields = ('services','base','reportnum')
    exclude = ('pk')
    
    def read(self, request, containerid, last_known=-1):

        last = int(last_known)
        container = None
        try:
            container = HostingContainer.objects.get(id=containerid)
        except ObjectDoesNotExist:
            try:
                containerauth = HostingContainerAuth.objects.get(id=containerid)
                container = containerauth.hostingcontainer
            except ObjectDoesNotExist:
                pass

        report,created = ContainerResourcesReport.objects.get_or_create(base=container)

        if last is not -1:
            while last == report.reportnum:
                logging.info("Waiting for new services lastreport=%s" % (last))
                time.sleep(sleeptime)
                report = ContainerResourcesReport.objects.get(base=container)

        services = DataService.objects.filter(container=container)
        report.services = services
        report.save()
        return report

class ManagedResourcesServiceHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ServiceResourcesReport
    fields = ('stagers','meta','base','reportnum')


    def read(self, request, serviceid, last_known=-1):

        last = int(last_known)
        service = DataService.objects.get(id=serviceid)

        report,created = ServiceResourcesReport.objects.get_or_create(base=service)

        if last is not -1:
            while last == report.reportnum:
                logging.info("Waiting for new stagers lastreport=%s" % (last))
                time.sleep(sleeptime)
                report = ServiceResourcesReport.objects.get(base=service)
        
        stagers = DataStager.objects.filter(service=service)
        report.stagers = stagers
        report.save()
        return report

class ManagedResourcesStagerHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, stagerid, last_known=-1):
        return {}

class AggregateUsageRateHandler(BaseHandler):
    model =  AggregateUsageRate
    exclude =('pk','base','id')
    
class RoleHandler(BaseHandler):
    allowed_methods = ('GET','PUT')
    model = Role
    fields = ('id','rolename','description','methods',('auth'))

    def update(self,request,roleid):
        import logging
        logging.info("updating role")

        role = Role.objects.get(id=roleid)
        newmethods = request.POST["methods"].split(',')

        logging.info("updating role with methods %s " % newmethods)
        logging.info("auth %s " % role.auth)
        logging.info("dir %s " % dir(role.auth))

        for a in role.auth.all():
            logging.info(a)
            logging.info(dir(a))

        allowed_methods = all_container_methods + all_service_methods + all_stager_methods

        # TODO: Should we check each type of authority this role could be under?
        #if hasattr(role.auth,"hostingcontainerauth"):
        #    allowed_methods = all_container_methods

        #if hasattr(role.auth,"dataserviceauth"):
        #    allowed_methods = all_service_methods

        #if hasattr(role.auth,"datastagerauth"):
        #    allowed_methods = all_stager_methods

        if not set(newmethods).issubset(set(allowed_methods)):
            return HttpResponseBadRequest("The methods '%s' are not allowed. Allowed Methods '%s' " % (newmethods, allowed_methods))

        existingmethods = role.methods()

        if set(newmethods).issubset(set(existingmethods)):
            return HttpResponseBadRequest("The methods '%s' are already contained in this role . Existing Methods '%s' " % (newmethods, existingmethods))

        role.addmethods(newmethods)
        role.save()
        return role

class AccessControlHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST')
    #fields = ('id','authname',('roles', ('description') ), )
    #fields = ('id','authname' )
    #model = Auth

    def create(self, request, method, pk):

        if not method in generic_post_methods:
            return HttpResponseBadRequest("Cannot do 'PUT' %s on %s" % (method,pk))

        if method == "getorcreateauth" or method == "addauth":
            name = request.POST["name"]
            roles_string = request.POST["roles"]
            roleids = roles_string.split(",")
            base = NamedBase.objects.get(pk=pk)

            if utils.is_container(base):
                hc = HostingContainer.objects.get(pk=pk)
                hca,created = HostingContainerAuth.objects.get_or_create(hostingcontainer=hc,authname=name)
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return hca
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                hca.save()
                hca.roles = roles
                return hca

            if utils.is_service(base):
                ser = DataService.objects.get(pk=pk)
                dsa,created  = DataServiceAuth.objects.get_or_create(dataservice=ser,authname=name)
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return dsa
                roles = []
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                dsa.save()
                dsa.roles = roles
                return dsa

            if utils.is_stager(base):
                stager = DataStager.objects.get(pk=pk)
                dsa,created  = DataStagerAuth.objects.get_or_create(stager=stager,authname=name)
                logging.info("%s %s " % (created,method))
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return dsa
                roles = []
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                dsa.save()
                dsa.roles = roles
                return dsa

        return HttpResponse("called %s on %s" % (method,pk))

    def update(self, request, method, pk):

        logging.info("update %s %s" % (method,pk))

        if not method in generic_put_methods:
            return HttpResponseBadRequest("Cannot do 'PUT' %s on %s" % (method,pk))

        if method == "setroles":
            roles_string = request.POST["roles"]
            roleids = roles_string.split(",")

            logging.info("auth pk = %s " % (pk))
            auth = Auth.objects.get(pk=pk)

            for roleid in roleids:
                role = Role.objects.get(id=roleid)
                auth.roles.add(role)

            auth.save()

            return HttpResponse("called %s on %s roles=%s" % (method,pk,",".join(roleids)))

            if utils.is_containerauth(auth):
                if roles in all_container_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_stagerauth(auth):
                if roles in all_service_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_stagerauth(auth):
                if roles in all_stager_methods:
                    role.setmethods(roles)
                    role.save()

            return HttpResponse("called %s on %s name=%s roles=%s" % (method,pk,name,",".join(roles)))

        return HttpResponse("called %s on %s" % (method,pk))

    def read(self,request, method, pk):

        if not method in generic_get_methods:
            return HttpResponseBadRequest("Cannot do 'GET' %s on %s" % (method,pk))
        
        if method == "getauths":
            try:
                base = NamedBase.objects.get(pk=pk)

                if utils.is_container(base):
                    return HostingContainerAuth.objects.filter(hostingcontainer=base)

                if utils.is_service(base):
                    return DataServiceAuth.objects.filter(dataservice=base)

                if utils.is_stager(base):
                    return DataStagerAuth.objects.filter(stager=base)
            except ObjectDoesNotExist:
                pass

            auth = Auth.objects.get(pk=pk)
            if utils.is_containerauth(auth) \
                or utils.is_serviceauth(auth) \
                    or utils.is_stagerauth(auth):
                        joins = JoinAuth.objects.filter(parent=auth.id)
                        return SubAuth.objects.filter(pk=joins)

            return HttpResponseBadRequest("Called %s on %s" % (method,pk))

        if method == "getroles":
            try:
                auth = Auth.objects.get(pk=pk)
                dict = {}
                roles = Role.objects.filter(auth=auth)
                for role in roles:
                    dict[role.rolename] = True

                return dict
            except ObjectDoesNotExist:
                return HttpResponseBadRequest("No Such Auth %s" % (pk))

        return HttpResponse("called %s on %s" % (method,pk))

class ContainerAccessControlHandler(BaseHandler):
    allowed_methods = ('GET',)
    model = HostingContainerAuth
    fields = ('id', 'authname', ('roles', ('description','id','rolename'),),)
    #exclude = ('hostingcontainer', 'auth_ptr' )fg

    def read(self,request, baseid):
        container = HostingContainer.objects.get(pk=baseid)
        containerauths = HostingContainerAuth.objects.filter(hostingcontainer=container)
        #roles = []
        #for containerauth in containerauths:
        #    for role in containerauth.roles.all():
        #        roles.append(role)#

        #dict = {}
        #dict["auth"] = ""
        return containerauths

class ServiceAccessControlHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self,request, baseid):
        service = DataService.objects.get(pk=baseid)
        serviceauths = DataServiceAuth.objects.filter(dataservice=service)
        roles = []
        for serviceauth in serviceauths:
            for role in serviceauth.roles.all():
                roles.append(role)

        dict = {}
        dict["roles"] = roles
        return dict

class StagerAccessControlHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self,request, baseid):
        stager = DataStager.objects.get(pk=baseid)
        stagerauths = DataStagerAuth.objects.filter(stager=stager)
        roles = []
        for stagerauth in stagerauths:
            for role in stagerauth.roles.all():
                roles.append(role)

        dict = {}
        dict["roles"] = set(roles)
        return dict



class RoleInfoHandler(BaseHandler):
    def read(self,request, pk):
        base = NamedBase.objects.get(pk=pk)
        if utils.is_container(base):
            containerauths = HostingContainerAuth.objects.filter(hostingcontainer=base)
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
            serviceauths = DataServiceAuth.objects.filter(dataservice=base)
            roles = []
            for serviceauth in serviceauths:
                for role in serviceauth.roles.all():
                    roles.append(role)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        if utils.is_stager(base):
            stagerauths = DataStagerAuth.objects.filter(stager=base)
            roles = []
            for stagerauth in stagerauths:
                for a in stagerauth.roles.all():
                    roles.append(a)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        r = rc.BAD_REQUEST
        resp.write("Invalid Request!")
        return r

class UsageSummaryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = UsageReport
    fields = ('summarys','inprogress','reportnum')

    def read(self,request, baseid, last_report=-1):

        lr = int(last_report)

        base = NamedBase.objects.get(pk=baseid)

        usagereport, created = UsageReport.objects.get_or_create(base=base)

        logging.info("Report = %s" % usagereport)

        if lr != -1:
            while lr == usagereport.reportnum:
                #logging.info("Waiting for report=%s lastreport=%s" % (usagereport.reportnum,lr))
                time.sleep(sleeptime)
                usagereport = UsageReport.objects.get(pk=usagereport.pk)

        inprogress= []
        summarys= []
        if utils.is_container(base):
            inprogress = usage_store.container_inprogresssummary(baseid)
            summarys = usage_store.container_usagesummary(baseid)
            logging.info(summarys)

        if utils.is_service(base):
            inprogress = usage_store.service_inprogresssummary(baseid)
            summarys = usage_store.service_usagesummary(baseid)

        if utils.is_stager(base):
            inprogress = usage_store.stager_inprogresssummary(baseid)
            summarys = usage_store.stager_usagesummary(baseid)

        for summary in summarys:
            summary.save()
    
        for ip in inprogress:
            ip.save()

        usagereport.summarys = summarys
        usagereport.inprogress = inprogress
        usagereport.save()

        return usagereport

class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')

    def read(self,request, baseid):
        base = NamedBase.objects.get(id=baseid)
        properties = ManagementProperty.objects.filter(base=base)
        properties_json = []
        for prop in properties:
            properties_json.append(prop)
        return properties_json

    def create(self, request, baseid):
        resp = rc.BAD_REQUEST
        #resp.write("Not Allowed")
        return resp

    def update(self, request, baseid):
        form = ManagementPropertyForm(request.POST) 
        if form.is_valid(): 

            logging.info(baseid)
            property = form.cleaned_data['property']

            base = NamedBase.objects.get(id=baseid)

            try:
                existingmanagementproperty = ManagementProperty.objects.get(property=property,base=base)
                value    = form.cleaned_data['value']
                existingmanagementproperty.value = value
                existingmanagementproperty.save()
                logging.warn("### Management Property '%s' on '%s' set to '%s' ###"%(property,base,value))
                return existingmanagementproperty
            except ObjectDoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write("Object doesnt exist")
                return resp

        else:
            logging.info("Bad Form %s " % form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class DataStagerAuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStagerAuth

    def read(self, request, stagerauthid):

        sub_auths = JoinAuth.objects.filter(parent=stagerauthid)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        try:
            datastager_auth = DataStagerAuth.objects.get(id=stagerauthid)

            form = SubAuthForm()
            form.fields['parent'].initial = stagerauthid
            dict = {}
            dict["auth"] = datastager_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("DataStagerAuth  doesn't exist.")

        try:
            container_auth = HostingContainerAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = container_auth

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("HostingContainer Auth doesn't exist.")

        try:
            dataservice_auths = DataServiceAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = dataservice_auths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("HostingContainer Auth doesn't exist.")

        try:
            sub_auth = SubAuth.objects.get(id=id)
            form = SubAuthForm()
            dict = {}
            dict["auth"] = sub_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("Sub Auth doesn't exist.")

        dict = {}
        dict["error"] = "That Authority does not exist"
        return render_to_response('error.html', dict)
    
    def create(self, request):
        form = DataStagerAuthForm(request.POST) 
        if form.is_valid(): 
            authname = form.cleaned_data['authname']
            roles_csv = form.cleaned_data['roles']
            stagerid = form.cleaned_data['dsid']
            stager = DataStager.objects.get(pk=stagerid)

            datastagerauth = DataStagerAuth(stager=stager,authname=authname)
            datastagerauth.save()

            auths = DataStagerAuth.objects.filter(stager=stager)

            rolenames = roles_csv.split(',')
            existingroles = rolenames

            for auth in auths:
                roles  = Role.objects.filter(auth=auth)
                for role in roles:
                    if role.rolename in rolenames:
                        existingroles.remove(role.rolename)
                        datastagerauth.roles.add(role)

            if len(existingroles) != 0:
                datastagerauth.delete()
                return HttpResponseBadRequest("Could not add %s " % ','.join(existingroles))

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastagerauth

            return redirect('/stager/%s/' % str(stager.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class AuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = SubAuth

    def create(self, request):
        form = SubAuthForm(request.POST)
        if form.is_valid(): 
            
            authname = form.cleaned_data['authname']
            roles_csv = form.cleaned_data['roles_csv']
            parent = form.cleaned_data['id_parent']

            subauth = SubAuth(authname=authname)
            subauth.save()

            for role in roles_csv.split(','):
                role = Role.objects.get(rolename=role)
                import logging
                logging.info("Role %s" % role)

            child = str(subauth.id)
            join = JoinAuth(parent=parent,child=child)
            join.save()

            return redirect('/auth/%s/' % str(subauth.id))
            
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def read(self, request, id):

        '''
        Have to add the case where this could be a hosting container or data
        service auth.
        '''
        auth = Auth.objects.get(id=id)
        if utils.is_stagerauth(auth):
            stagerauth = DataStagerAuth.objects.get(id=id)
            methods = get_auth_methods(stagerauth)
            if 'get' in methods:
                return views.render_stagerauth(request, stagerauth.stager, stagerauth, show=True)
            else:
                return views.render_stagerauth(request, stagerauth.stager, stagerauth, show=False)


        if utils.is_serviceauth(auth):
            dsa = DataServiceAuth.objects.get(pk=auth.id)
            return views.render_serviceauth(request,dsa.id)

        if utils.is_containerauth(auth):
            hca = HostingContainerAuth.objects.get(pk=auth.id)
            return views.render_containerauth(request,hca.id)

        dsAuth, methods_intersection = find_datastager_auth(id)
                
        if dsAuth is None:
            return HttpResponseBadRequest("No Interface for %s " % (id))

        auth = SubAuth.objects.get(id=id)
        #methods = get_auth_methods(auth)

        dict = {}
        dict['actions'] = methods
        dict['actionprefix'] = "stagerapi"
        dict['authapi'] = id
        if 'get' in methods:
            return views.render_stagerauth(request, dsAuth.stager, auth, show=True, dict=dict)
        else:
            return views.render_stagerauth(request, dsAuth.stager, auth, show=False, dict=dict)

def get_auth_methods(auth):
    methods = []
    for role in auth.roles.all():
        methods = methods + role.methods()
    return list(set(methods))

def find_datastager_auth(parent):
    dsAuth = None
    methods_intersection = None
    all_methods = set()
    done = False
    while not done:
        try:
            joins = JoinAuth.objects.get(child=parent)
            parent = joins.parent

            try:
                subauth = SubAuth.objects.get(id=parent)
                if methods_intersection is None:
                    methods_intersection = set(get_auth_methods(subauth))
                methods_intersection = methods_intersection & set(get_auth_methods(subauth))
                all_methods = all_methods | set(get_auth_methods(subauth))
            except ObjectDoesNotExist:
                pass
            try:
                datastagerauth = DataStagerAuth.objects.get(id=parent)
                dsAuth = datastagerauth
                if methods_intersection is None:
                    methods_intersection = set(get_auth_methods(datastagerauth))
                methods_intersection = methods_intersection & set(get_auth_methods(datastagerauth))
                all_methods = all_methods | set(get_auth_methods(datastagerauth))
                done = True
                pass
            except ObjectDoesNotExist:
                pass

        except ObjectDoesNotExist:
            parent = None
            done = True
    return dsAuth, methods_intersection