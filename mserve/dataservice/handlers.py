
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
from django.core.files.uploadedfile import SimpleUploadedFile
from dataservice.tasks import thumbimage
from dataservice.tasks import render_blender
from django.http import HttpResponse
from celery.result import TaskSetResult
from celery.task.sets import TaskSet
from anyjson import serialize as JSON_dump

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
    fields = ('name', 'id','dataservice_set',"reportnum")
    exclude = ('pk')

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
    #fields = ('name', 'id')
    fields = ('name', 'id', 'mfile_set','job_set','reportnum')
    exclude = ('pk')

    def delete(self, request, id):
        logging.info("Deleting Service %s " % id)
        api.delete_service(request,id)
        r = rc.DELETED
        return r

    def create(self, request):
        form = DataServiceForm(request.POST)
        logging.info(form)
        if form.is_valid(): 
            
            containerid = form.cleaned_data['cid']
            name = form.cleaned_data['name']
            dataservice = api.create_data_service(request,containerid,name)
            return dataservice

        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r


class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):
        form = DataServiceURLForm(request.POST)
        if form.is_valid(): 
            name = form.cleaned_data['name']
            dataservice = api.create_data_service(request,containerid,name)
            return dataservice
        else:
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r


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
    fields = ('name', 'id', 'size', 'file','checksum', 'thumb', 'poster', 'mimetype', 'created', 'updated')
    #fields = ('name', 'id', 'size', 'file','checksum', 'thumb', 'poster', 'mimetype', 'created', 'updated', 'jobmfile_set' )
    exclude = ('pk')

class MFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFile
    fields = ('name', 'id' ,'file', 'checksum', 'size', 'mimetype', 'thumb', 'poster', 'created' , 'updated')

    def delete(self, request, id):
        logging.info("Deleting mfile %s " % id)
        api.delete_mfile(request,id)
        r = rc.DELETED
        return r

    def update(self, request):
        form = UpdateMFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            mfileid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            mfile = MFile.objects.get(pk=mfileid)
            mfile.file = file
            mfile.size = file.size
            
            mfile.save()

            backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
            backup.save()

            usage_store.startrecording(mfileid,usage_store.metric_disc,mfile.size)
            usage_store.startrecording(mfileid,usage_store.metric_archived,mfile.size)

            return mfile

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
        logging.debug("Create MFile")
        form = MFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None
            serviceid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            mfile = api.create_mfile(request, serviceid, file)
            return mfile
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
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
    #fields = ()
    #fields = ('id','name','created','taskset_id')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        jobmfiles = JobMFile.objects.filter(mfile=mfile)

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
    #fields = ('id','name','created','taskset_id','jobmfile_set')

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

        jobmfile = JobMFile(mfile=mfile,job=job,index=0)
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
        js = JobMFile(job=job,mfile=mfile,index=0)
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

        redirecturl = utils.gen_sec_link_orig(p,dlfoldername)
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

            return mfile

        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

    def create(self, request, serviceid):
        logging.info("Loading content of size %s"%len(request.raw_post_data))

        if len(request.raw_post_data)!=0 :
            filename = request.META['HTTP_X_FILE_NAME']
            logging.info(filename)

            upload = SimpleUploadedFile( filename, request.raw_post_data )

            mfile = api.create_mfile(request, serviceid, upload)

            logging.info(mfile)

            return mfile

        #logging.info(dir(request))
        form = MFileURLForm(request.POST,request.FILES)
        if form.is_valid(): 

            logging.debug("Handler Files %s" %request.FILES)

            file = request.FILES['file']
            mfile = api.create_mfile(request, serviceid, file)

            logging.info(request.FILES)

            return mfile

        else:
            logging.info(form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class ManagedResourcesContainerHandler(BaseHandler):
    allowed_methods = ('GET')
    
    def read(self, request, containerid, last_known=-1):

        last = int(last_known)
        container = HostingContainer.objects.get(id=containerid)

        if last is not -1:
            while last == container.reportnum:
                logging.info("Waiting for new services lastreport=%s" % (last))
                time.sleep(sleeptime)
                container = HostingContainer.objects.get(id=containerid)

        return container

class ManagedResourcesServiceHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, serviceid, last_known=-1):

        last = int(last_known)
        service = DataService.objects.get(id=serviceid)
        logging.info("Waiting for new services lastreport=%s" % (service.reportnum))
        logging.info("Waiting for new services lastknown=%s" % (last ))
        if last is not -1:
            while last == service.reportnum:
                logging.info("Waiting for new mfiles lastreport=%s" % (last))
                time.sleep(sleeptime)
                service = DataService.objects.get(id=serviceid)

        return service

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

        allowed_methods = api.all_container_methods + api.all_service_methods + api.all_mfile_methods

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

        if not method in api.generic_put_methods:
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
                if roles in api.all_container_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_mfileauth(auth):
                if roles in api.all_service_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_mfileauth(auth):
                if roles in api.all_mfile_methods:
                    role.setmethods(roles)
                    role.save()

            return HttpResponse("called %s on %s name=%s roles=%s" % (method,pk,name,",".join(roles)))

        return HttpResponse("called %s on %s" % (method,pk))

    def read(self,request, method, pk):

        if not method in api.generic_get_methods:
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
    fields = ("value","property","id")

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

            return MFileauth

        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

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

            child = str(subauth.id)
            join = JoinAuth(parent=parent,child=child)
            join.save()
            
            return subauth
            
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r