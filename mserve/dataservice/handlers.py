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
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile

from dataservice.tasks import thumbvideo
from dataservice.tasks import thumbimage
from dataservice.tasks import render_blender
from django.http import HttpResponse
from celery.result import AsyncResult
from celery.result import TaskSetResult
from celery.task.sets import TaskSet

from anyjson import serialize as JSON_dump
import utils as utils
import usage_store as usage_store
import djcelery
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
mfile_base      = "/mfile/"
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

service_customer_methods =  ["createmfile"] + generic_methods
service_admin_methods =  service_customer_methods + ["setmanagementproperty"]

all_service_methods = [] + service_admin_methods

mfile_monitor_methods = ["getusagesummary"]
mfile_owner_methods = ["get", "put", "post", "delete", "verify"] + generic_methods

all_mfile_methods = mfile_owner_methods + mfile_monitor_methods

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

def create_mfile(request,serviceid,file):
    service = DataService.objects.get(id=serviceid)
    if file==None:
        mfile = MFile(name="Empty File",service=service)
    else:
        mfile = MFile(name=file.name,service=service,file=file)
    mfile.save()

    logging.debug("MFile creation started '%s' "%mfile)
    logging.debug("Creating roles for '%s' "%mfile)
    
    mfileauth_owner = MFileAuth(mfile=mfile,authname="owner")
    mfileauth_owner.save()

    owner_role = Role(rolename="owner")
    methods = mfile_owner_methods
    owner_role.setmethods(methods)
    owner_role.description = "Owner of the data"
    owner_role.save()

    mfileauth_owner.roles.add(owner_role)

    monitor_role = Role(rolename="monitor")
    methods = mfile_monitor_methods
    monitor_role.setmethods(methods)
    monitor_role.description = "Collect usage reports"
    monitor_role.save()

    mfileauth_owner.roles.add(monitor_role)

    mfileauth_monitor = MFileAuth(mfile=mfile,authname="monitor")
    mfileauth_monitor.save()

    mfileauth_monitor.roles.add(monitor_role)

    if mfile.file:
        # MIME type
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        mimetype = m.file(mfile.file.path)
        mfile.mimetype = mimetype
        # checksum
        mfile.checksum = utils.md5_for_file(mfile.file)
        # record size
        mfile.size = file.size
        # save it
        mfile.save()

        thumbpath = os.path.join( str(mfile.file) + ".thumb.jpg")
        posterpath = os.path.join( str(mfile.file) + ".poster.jpg")
        fullthumbpath = os.path.join(settings.THUMB_ROOT , thumbpath)
        fullposterpath = os.path.join(settings.THUMB_ROOT , posterpath)
        (thumbhead,tail) = os.path.split(fullthumbpath)
        (posterhead,tail) = os.path.split(fullposterpath)

        if not os.path.isdir(thumbhead):
            os.makedirs(thumbhead)

        if not os.path.isdir(posterhead):
            os.makedirs(posterhead)
            
        use_celery = settings.USE_CELERY

        if use_celery:
            logging.info("Using CELERY for processing ")
        else:
            logging.info("Processing synchronously (change settings.USE_CELERY to 'True' to use celery)" )

        if mimetype.startswith('video'):

            if use_celery:
                thumbtask = thumbvideo.delay(mfile.file.path,fullthumbpath,thumbsize[0],thumbsize[1])
            else:
                thumbtask = thumbvideo(mfile.file.path,fullthumbpath,thumbsize[0],thumbsize[1])
            mfile.thumb = thumbpath
            if use_celery:
                postertask = thumbvideo.delay(mfile.file.path,fullposterpath,postersize[0],postersize[1])
            else:
                postertask = thumbvideo(mfile.file.path,fullposterpath,postersize[0],postersize[1])

            mfile.poster = posterpath

        elif mimetype.startswith('image'):
            logging.info("Creating thumb inprocess for Image '%s' %s " % (mfile,mimetype))
            if use_celery:
                thumbtask = thumbimage.delay(mfile.file.path,fullthumbpath,thumbsize[0],thumbsize[1])
            else:
                thumbtask = thumbimage(mfile.file.path,fullthumbpath,thumbsize[0],thumbsize[1])

            mfile.thumb = thumbpath
            if use_celery:
                postertask = thumbimage.delay(mfile.file.path,fullposterpath,postersize[0],postersize[1])
            else:
                postertask = thumbimage(mfile.file.path,fullposterpath,postersize[0],postersize[1])
            mfile.poster = posterpath
        else:
            logging.info("Not creating thumb for '%s' %s " % (mfile,mimetype))

        mfile.save()
        usage_store.startrecording(mfile.id,usage_store.metric_mfile,1)
        usage_store.startrecording(mfile.id,usage_store.metric_archived,1)
        usage_store.record(mfile.id,usage_store.metric_disc,mfile.size)
        usage_store.record(mfile.id,usage_store.metric_ingest,mfile.size)


    logging.debug("Backing up '%s' "%mfile)

    if file is not None:
        backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
        backup.save()

    return mfile

def delete_mfile(request,mfileid):
    mfile = MFile.objects.get(id=mfileid)
    if mfile.file == None:
        usage_store.stoprecording(mfileid,usage_store.metric_mfile)
        usage_store.stoprecording(mfileid,usage_store.metric_archived)
    logging.info("Deleteing mfile %s %s" % (mfile.name,mfileid))

    usages = Usage.objects.filter(base=mfile)
    logging.info("Deleteing mfile usage")
    for usage in usages:
        logging.info("Saving Usage %s " % usage)
        usage.base = mfile.service
        usage.save()

    mfile.delete()
    logging.info("MFile Deleted %s " % mfileid)

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
        r = rc.DELETED
        return r
    
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
                r.write("Invalid Request!")
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
        r = rc.DELETED
        return r
    
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
            if request.POST.has_key('mfileid'):
                mfileid = request.POST['mfileid']
                logging.info("mfileid %s"%mfileid)
                mfile = MFile.objects.get(id=mfileid)
                if mfile == None:
                    logging.info("No such mfile %s"%mfileid)
                    r = rc.BAD_REQUEST
                    r.write("Invalid Request!")
                    return r

                try:
                    thumb = mfile.thumb
                    logging.info("Deleting existing thumb for mfile %s"%mfile)
                    mfile.thumb.delete()
                except ObjectDoesNotExist:
                    pass

                logging.info("Updating thumb for mfile %s"%mfile)

                thumb = Thumb(mfile=mfile,file=file)
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

    def update(self, request, mfileid, backup=False):
        mfile = MFile.objects.get(pk=mfileid)
        if not backup:
            mfile = MFile.objects.get(pk=mfileid)
            logging.info("Attempting to corrupt file '%s' " % (mfile))
            f = open(mfile.file.path,'wb')
            f.writelines(["corruption"])
        else:
            logging.info("Attempting to corrupt backup file for file'%s'" % (mfile))
            backup = BackupFile.objects.get(mfile=mfile)
            f = open(backup.file.path,'wb')
            f.writelines(["corruption"])
        
        return mfile

class MFileJSONHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFile
    fields = ('name', 'id', 'file','checksum', 'thumb', 'poster', 'mimetype', 'created', 'updated', 'jobmfile_set' )
    exclude = ('pk')

class MFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    #model = MFile
    #fields = ('name', 'id', 'file','checksum', ('thumb', ('id','name','file') ) )
    #exclude = ('pk')

    def delete(self, request, mfileid):
        logging.info("Deleting mfile %s " % mfileid)
        delete_mfile(request,mfileid)
        r = rc.DELETED
        return r

    def read(self, request, mfileid):
        try:
            mfile = MFile.objects.get(pk=mfileid)
            base = NamedBase.objects.get(pk=mfileid)

            if re.match("application/json", request.META["HTTP_ACCEPT"]):
            #if request.META["HTTP_ACCEPT"].contains("application/json"):
                return mfile
            return views.render_mfile(request,mfile.id,show=True)
        except ObjectDoesNotExist:
            error = "The file with the id %s does not exist "%mfileid
            if re.match("application/json", request.META["HTTP_ACCEPT"]):
                r = rc.NOT_FOUND
                r.write(error)
                return r
            return views.render_error(request,error)

    def update(self, request):
        form = UpdateMFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            mfileid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            mfile = MFile.objects.get(pk=mfileid)
            mfile.file = file
            mfile.size = file.size

            backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
            backup.save()

            usage_store.startrecording(mfileid,usage_store.metric_disc,mfile.size)
            usage_store.startrecording(mfileid,usage_store.metric_archived,mfile.size)

            mfile.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return mfile

            return redirect('/mfile/'+str(mfile.id)+"/")
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r
        
    def render_subauth(self, mfile, auth, show=False):
        sub_auths = JoinAuth.objects.filter(parent=auth.id)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        form = SubAuthForm()
        form.fields['id_parent'].initial = auth.id
        dict = {}
        dict["mfile"] = mfile
        if mfile.file == '' or mfile.file == None:
            dict["altfile"] = "/mservemedia/images/empty.png"
        if not show:
            mfile.file = None
            dict["altfile"] = "/mservemedia/images/forbidden.png"
    
        dict["form"] = form
        dict["auths"] = subauths
        dict["formtarget"] = "/auth/"
        return render_to_response('mfile.html', dict)

    def create(self, request):
        reqjson=(request.META["HTTP_ACCEPT"] == "application/json")
        form = MFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None
            serviceid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            mfile = create_mfile(request, serviceid, file)

            if reqjson:
                return mfile

            return redirect('/mfile/'+str(mfile.id)+"/")
            #return views.render_service(request,serviceid,newmfile=MFile.id)
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                r.write("Invalid Request!")
                return r
                #return views.render_mfile(request,mfile.id)
            r = rc.BAD_REQUEST
            r.write("%s"%form)
            return r

class JobServiceHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, serviceid):
        service = DataService.objects.get(pk=serviceid)

        arr = []
        for job in service.job_set.all():
            tsr = TaskSetResult.restore(job.taskset_id)
            dict = {}
            dict["taskset_id"] = tsr.taskset_id
            # Dont return results until job in complete
            if tsr.successful():
                dict["result"] = tsr.join()
            else:
                dict["result"] = []
            dict["completed_count"] = tsr.completed_count()
            dict["failed"] = tsr.failed()
            dict["ready"] = tsr.ready()
            dict["successful"] = tsr.successful()
            dict["total"] = tsr.total
            dict["waiting"] = tsr.waiting()
            dict["job"] = job

            arr.append(dict)

        return HttpResponse(arr,mimetype="application/json")

class JobMFileHandler(BaseHandler):
    model = JobMFile
    allowed_methods = ('GET','POST','DELETE')
    fields = ('id','name','created','taskset_id')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        jobmfiles = Jobmfile.objects.filter(mfile=mfile)

        arr = []
        for jobmfile in jobmfiles:
            tsr = TaskSetResult.restore(jobmfile.job.taskset_id)
            dict = {}
            dict["taskset_id"] = tsr.taskset_id
            # Dont return results until job in complete
            if tsr.successful():
                dict["result"] = tsr.join()
            else:
                dict["result"] = []
            dict["completed_count"] = tsr.completed_count()
            dict["failed"] = tsr.failed()
            dict["ready"] = tsr.ready()
            dict["successful"] = tsr.successful()
            dict["total"] = tsr.total
            dict["waiting"] = tsr.waiting()
            dict["job"] = jobmfile.job

            arr.append(dict)

        return HttpResponse(arr,mimetype="application/json")

class JobHandler(BaseHandler):
    model = Job
    allowed_methods = ('GET','POST','DELETE')
    fields = ('id','name','created','taskset_id')

    def delete(self, request, id):
        job = Job.objects.get(id=id)
        job.delete()
        r = rc.DELETED
        return r
    
    def read(self, request, id):
        job = Job.objects.get(id=id)
        tsr = TaskSetResult.restore(job.taskset_id)
        print dir(tsr)
        dict = {}
        dict["taskset_id"] = tsr.taskset_id
        # Dont return results until job in complete
        if tsr.successful():
            dict["result"] = tsr.join()
        else:
            dict["result"] = []
        dict["completed_count"] = tsr.completed_count()
        dict["failed"] = tsr.failed()
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
        return HttpResponse(dict,mimetype="application/json")

class RenderResultsHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        folder = os.path.join(os.path.dirname(mfile.file.path),"render")
        urlfolder = os.path.join(os.path.dirname(str(mfile.file)),"render")
        files = []
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.find("thumb") > 0:
                    url = os.path.join(urlfolder,f)
                    files.append(url)
        files.sort()
        dict = {}
        dict["results"] = files
        return dict

class RenderHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, jobid):

        tsr = TaskSetResult.restore(taskset_id)
        print dir(tsr)
        dict = {}
        dict["taskset_id"] = tsr.taskset_id
        # Dont return results until job in complete
        if tsr.successful():
            dict["result"] = tsr.join()
        else:
            dict["result"] = []
        dict["completed_count"] = tsr.completed_count()
        dict["failed"] = tsr.failed()
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
        return HttpResponse(JSON_dump(dict),mimetype="application/json")
        #return djcelery.views.task_status(request, taskid)

    def create(self,request,mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        tasks = []
        folder = os.path.join(os.path.dirname(mfile.file.path),"render")
        if not os.path.exists(folder):
            os.makedirs(folder)
        for i in range(1,100):
            t = render_blender.subtask([mfile.file.path,i,i,folder],callback=thumbimage)
            tasks.append(t)
        
        ts = TaskSet(tasks=tasks)
        tsr = ts.apply_async()
        tsr.save()

        job = Job(name="Render",service=mfile.service,taskset_id=tsr.taskset_id)
        job.save()

        jobmfile = Jobmfile(mfile=mfile,job=job,index=0)
        jobmfile.save()
        dict = {}
        dict["taskset_id"] = tsr.taskset_id
        dict["job"] = job
        # Dont return results until job in complete
        if tsr.successful():
            dict["result"] = tsr.join()
        else:
            dict["result"] = []
        dict["completed_count"] = tsr.completed_count()
        dict["failed"] = tsr.failed()
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
        return HttpResponse(dict,mimetype="application/json")


        
        service = mfile.service
        job = Job(name="Render",service=service)
        job.save()
        js = Jobmfile(job=job,mfile=mfile,index=0)
        js.save()

        folder = os.path.join(os.path.dirname(mfile.file.path),"render")
        if not os.path.exists(folder):
            os.makedirs(folder)
        dict = {}
        tasks = []

        for x in range(1,100):
            t = render_blender.delay(mfile.file.path,x,x,folder,callback=thumbimage)
            jobtask = JobTask(job=job,task=t.task_id)
            jobtask.save()
            logging.info(dir(t))
            tasks.append(t)
        dict["job"] = job
        dict["n"] = len(tasks)
        return dict

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

        dlfoldername = "dl%s"%accessspeed

        check1 = mfile.checksum
        check2 = utils.md5_for_file(mfile.file)

        file=mfile.file

        if(check1==check2):
            logging.info("Verification of %s on read ok" % mfile)
        else:
            logging.info("Verification of %s on read FAILED" % mfile)
            usage_store.record(mfile.id,usage_store.metric_corruption,1)
            backup = BackupFile.objects.get(mfile=mfile)
            check3 = mfile.checksum
            check4 = utils.md5_for_file(backup.file)
            if(check3==check4):
                shutil.copy(backup.file.path, mfile.file.path)
                file = backup.file
            else:
                logging.info("The file %s has been lost" % mfile)
                usage_store.record(mfile.id,usage_store.metric_dataloss,mfile.size)
                return rc.NOT_HERE

        p = str(file)

        redirecturl = gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = file.path

        logging.info("Redirect URL      = %s " % redirecturl)
        logging.info("fullfilepath      = %s " % fullfilepath)
        logging.info("fullfilefolder    = %s " % fullfilepathfolder)
        logging.info("mfilefp      = %s " % mfilefilepath)
        logging.info("mfilef       = %s " % file)

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            os.link(mfilefilepath,fullfilepath)

        usage_store.record(mfile.id,usage_store.metric_access,mfile.size)

        return redirect("/%s"%redirecturl)


class MFileURLHandler(BaseHandler):
    
    def update(self, request, mfileid):
        form = UpdateMFileFormURL(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            mfile = MFile.objects.get(pk=mfileid)
            mfile.file = file
            mfile.name = file.name
            mfile.size = file.size
            mfile.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return mfile

            return redirect('/mfile/'+str(mfile.id)+"/")
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            logging.info("MFileURLHandler %s "%form)
            return r

    def create(self, request, serviceid):
        logging.info("Loading content of size %s"%len(request.raw_post_data))

        if len(request.raw_post_data)!=0 :
            filename = request.META['HTTP_X_FILE_NAME']
            logging.info(filename)

            upload = SimpleUploadedFile( filename, request.raw_post_data )

            mfile = create_mfile(request, serviceid, upload)

            logging.info(mfile)

            return mfile

        #logging.info(dir(request))
        form = MFileURLForm(request.POST,request.FILES)
        if form.is_valid(): 

            logging.debug("Handler Files %s" %request.FILES)

            file = request.FILES['file']
            mfile = create_mfile(request, serviceid, file)

            logging.info(request.FILES)

            return mfile

        else:
            logging.info(form)
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
    fields = ('mfiles','meta','base','reportnum')


    def read(self, request, serviceid, last_known=-1):

        last = int(last_known)
        service = DataService.objects.get(id=serviceid)

        report,created = ServiceResourcesReport.objects.get_or_create(base=service)

        if last is not -1:
            while last == report.reportnum:
                logging.info("Waiting for new mfiles lastreport=%s" % (last))
                time.sleep(sleeptime)
                report = ServiceResourcesReport.objects.get(base=service)
        
        mfiles = MFile.objects.filter(service=service)
        report.mfiles = mfiles
        report.save()
        return report

class ManagedResourcesmfileHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid, last_known=-1):
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

        allowed_methods = all_container_methods + all_service_methods + all_mfile_methods

        # TODO: Should we check each type of authority this role could be under?
        #if hasattr(role.auth,"hostingcontainerauth"):
        #    allowed_methods = all_container_methods

        #if hasattr(role.auth,"dataserviceauth"):
        #    allowed_methods = all_service_methods

        #if hasattr(role.auth,"MFileauth"):
        #    allowed_methods = all_mfile_methods

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

            if utils.is_mfile(base):
                mfile = MFile.objects.get(pk=pk)
                dsa,created  = MFileAuth.objects.get_or_create(mfile=mfile,authname=name)
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
            if utils.is_mfileauth(auth):
                if roles in all_service_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_mfileauth(auth):
                if roles in all_mfile_methods:
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

                if utils.is_mfile(base):
                    return MFileAuth.objects.filter(mfile=base)
            except ObjectDoesNotExist:
                pass

            auth = Auth.objects.get(pk=pk)
            if utils.is_containerauth(auth) \
                or utils.is_serviceauth(auth) \
                    or utils.is_mfileauth(auth):
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

class MFileAccessControlHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self,request, baseid):
        mfile = MFile.objects.get(pk=baseid)
        mfileauths = MFileAuth.objects.filter(mfile=mfile)
        roles = []
        for mfileauth in mfileauths:
            for role in mfileauth.roles.all():
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

        if utils.is_mfile(base):
            mfileauths = MFileAuth.objects.filter(mfile=base)
            roles = []
            for mfileauth in mfileauths:
                for a in mfileauth.roles.all():
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

        if utils.is_mfile(base):
            inprogress = usage_store.mfile_inprogresssummary(baseid)
            summarys = usage_store.mfile_usagesummary(baseid)

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

class MFileAuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = MFileAuth

    def read(self, request, mfileauthid):

        sub_auths = JoinAuth.objects.filter(parent=mfileauthid)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        try:
            MFile_auth = MFileAuth.objects.get(id=mfileauthid)

            form = SubAuthForm()
            form.fields['parent'].initial = mfileauthid
            dict = {}
            dict["auth"] = MFile_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("MFileAuth  doesn't exist.")

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
        form = MFileAuthForm(request.POST)
        if form.is_valid(): 
            authname = form.cleaned_data['authname']
            roles_csv = form.cleaned_data['roles']
            mfileid = form.cleaned_data['dsid']
            mfile = MFile.objects.get(pk=mfileid)

            MFileauth = MFileAuth(mfile=mfile,authname=authname)
            MFileauth.save()

            auths = MFileAuth.objects.filter(mfile=mfile)

            rolenames = roles_csv.split(',')
            existingroles = rolenames

            for auth in auths:
                roles  = Role.objects.filter(auth=auth)
                for role in roles:
                    if role.rolename in rolenames:
                        existingroles.remove(role.rolename)
                        MFileauth.roles.add(role)

            if len(existingroles) != 0:
                MFileauth.delete()
                return HttpResponseBadRequest("Could not add %s " % ','.join(existingroles))

            if request.META["HTTP_ACCEPT"] == "application/json":
                return MFileauth

            return redirect('/mfile/%s/' % str(mfile.id))
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
        if utils.is_mfileauth(auth):
            mfileauth = MFileAuth.objects.get(id=id)
            methods = get_auth_methods(mfileauth)
            if 'get' in methods:
                return views.render_mfileauth(request, mfileauth.mfile, mfileauth, show=True)
            else:
                return views.render_mfileauth(request, mfileauth.mfile, mfileauth, show=False)


        if utils.is_serviceauth(auth):
            dsa = DataServiceAuth.objects.get(pk=auth.id)
            return views.render_serviceauth(request,dsa.id)

        if utils.is_containerauth(auth):
            hca = HostingContainerAuth.objects.get(pk=auth.id)
            return views.render_containerauth(request,hca.id)

        dsAuth, methods_intersection = find_MFile_auth(id)
                
        if dsAuth is None:
            return HttpResponseBadRequest("No Interface for %s " % (id))

        auth = SubAuth.objects.get(id=id)
        #methods = get_auth_methods(auth)

        dict = {}
        dict['actions'] = methods
        dict['actionprefix'] = "mfileapi"
        dict['authapi'] = id
        if 'get' in methods:
            return views.render_mfileauth(request, dsAuth.mfile, auth, show=True, dict=dict)
        else:
            return views.render_mfileauth(request, dsAuth.mfile, auth, show=False, dict=dict)

def get_auth_methods(auth):
    methods = []
    for role in auth.roles.all():
        methods = methods + role.methods()
    return list(set(methods))

def find_MFile_auth(parent):
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
                MFileauth = MFileAuth.objects.get(id=parent)
                dsAuth = MFileauth
                if methods_intersection is None:
                    methods_intersection = set(get_auth_methods(MFileauth))
                methods_intersection = methods_intersection & set(get_auth_methods(MFileauth))
                all_methods = all_methods | set(get_auth_methods(MFileauth))
                done = True
                pass
            except ObjectDoesNotExist:
                pass

        except ObjectDoesNotExist:
            parent = None
            done = True
    return dsAuth, methods_intersection