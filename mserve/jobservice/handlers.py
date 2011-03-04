import os
import os.path
import string
import logging

from anyjson import serialize as JSON_dump
from celery.result import TaskSetResult
from celery.task.sets import TaskSet
from dataservice.forms import *
from dataservice.models import *
from dataservice.tasks import thumbimage
from django.core.cache import cache
from django.http import *
from django.http import HttpResponse
from django.shortcuts import redirect
from mserve.dataservice.models import DataService
from mserve.dataservice.models import MFile
from mserve.jobservice.models import *
from mserve.jobservice.models import Job
from mserve.jobservice.models import JobMFile
from mserve.jobservice.models import JobOutput
import dataservice.models as models
import dataservice.usage_store as usage_store
from piston.handler import BaseHandler
from piston.utils import rc
import settings as settings
from tasks import render_blender

import dataservice.utils as utils


def job_to_dict(job):
    taskid = job.taskset_id
    tsr = TaskSetResult.restore(taskid)
    dict = {}
    if tsr is not None:
        dict["taskset_id"] = tsr.taskset_id
        # Dont return results until job in complete
        if tsr.successful():
            dict["result"] = tsr.join()
        else:
            dict["result"] = []
        dict["completed_count"] = tsr.completed_count()
        dict["failed"] = tsr.failed()
        dict["percent"] = int(tsr.completed_count())/int(tsr.total)*100
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
        dict["job"] = job
    else:
        return None

    return dict


class JobServiceHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, serviceid):
        service = DataService.objects.get(pk=serviceid)

        arr = []
        for job in service.job_set.all():
            dict = job_to_dict(job)
            if dict is not None:
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
            dict = job_to_dict(jobmfile.job)
            if dict is not None:
                arr.append(dict)

        return HttpResponse(arr,mimetype="application/json")

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

class JobHandler(BaseHandler):
    model = Job
    allowed_methods = ('GET','POST','DELETE')
    fields = ('id','name','created','taskset_id','joboutput_set')
    #fields = ('id','name','created','taskset_id','jobmfile_set')

    def create(self, request):
        
        jobtype = request.POST['jobtype']
        serviceid = request.POST['serviceid']
        mfileid = request.POST['mfileid']

        name = "newfile"

        if serviceid != "":
            service = DataService.objects.get(id=serviceid)
        elif mfileid != "":
            mfile = MFile.objects.get(id=mfileid)
            name = mfile.name
            service = mfile.service
        else:
            r = rc.BAD_REQUEST
            r.write("\nRequest has no serviceid or mfileid - Creation Failed!")
            return r

        logging.info("Creating job at service %s " % service)

        options = {}
        for v in request.POST:
            options[v]=request.POST[v]

        logging.info("Request for job type '%s' with options %s" % (jobtype,options) )

        job_description = None
        try:
            job_description = cache.get(jobtype)
        except Exception as e:
            logging.info("No job description for job type '%s' %s" % (jobtype,e) )

        if job_description == None:
            r = rc.BAD_REQUEST
            r.write("\nJob has no description - Creation Failed!")
            return r

        nbinputs = job_description["nbinputs"]
        nboutputs= job_description["nboutputs"]

        inputs = []
        outputs = []
        callbacks = [] 

        job = Job(name="Job",service=service)
        job.save()

        for i in range(0,nbinputs):
            mfileid = request.POST['input-%s'%i]
            mfile = MFile.objects.get(id=mfileid)
            jobmfile = JobMFile(mfile=mfile,job=job,index=0)
            jobmfile.save()
            inputs.append(mfile.file.path)

        if job == None:
            r = rc.BAD_REQUEST
            r.write("Job Creation failed!")
            return r

        for i in range(0,nboutputs):
            outputmimetype = job_description["output-%s"%i]["mimetype"]
            output = JobOutput(name="Job '%s'"%jobtype,job=job,mimetype=outputmimetype)
            output.save()
            
            callback=None
            if outputmimetype.startswith("image"):
                fname = "%s.%s" % (name,"png")
                outputpath = os.path.join( str(job.id) , fname)
                output.file = outputpath
                thumbfolder = os.path.join( settings.THUMB_ROOT, str(job.id))
                if not os.path.exists(thumbfolder):
                    os.makedirs(thumbfolder)

                thumbfile= os.path.join( thumbfolder , "%s%s" % (fname,".thumb.png"))
                thumbpath = os.path.join( str(job.id) , "%s%s" % (fname,".thumb.png"))
                output.thumb = thumbpath
                output.save()
                thumboptions = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                callback = thumbimage.subtask([output.file.path,thumbfile,thumboptions])
            else:
                fname = "%s.%s" % (name,"output")
                outputpath = os.path.join( str(job.id) , fname)
                output.file = outputpath
                output.save()

            if callback != None:
                callbacks.append(callback)

            outputs.append(output.file.path)

            (head,tail) = os.path.split(output.file.path)

            if not os.path.isdir(head):
                os.makedirs(head)


        m = get_class(jobtype)

        logging.info("Creating task %s inputs= %s outputs= %s options= %s" % (m,inputs,outputs,options))

        task = m.subtask([inputs,outputs,options],callbacks=callbacks)

        tasks = [task]

        ts = TaskSet(tasks=tasks)
        tsr = ts.apply_async()
        tsr.save()

        job.taskset_id=tsr.taskset_id
        job.save()



        logging.info("Creating Job Type %s on file %s" % (jobtype,mfileid))

        logging.info("Created Job  %s" % (m))

        return job_to_dict(job)

    def delete(self, request, id):
        job = Job.objects.get(id=id)
        job.delete()
        r = rc.DELETED
        return r
    
    def read(self, request, id):
        job = Job.objects.get(id=id)
        dict = job_to_dict(job)
        return HttpResponse(dict,mimetype="application/json")

class JobOutputHandler(BaseHandler):
    model = JobOutput
    fields = ('id','job_id','name','thumb','thumburl','file','mimetype')

class RenderResultsHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, jobid):
        job = Job.objects.get(id=jobid)
        output = job.joboutput_set.all()
        return output

class RenderHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, jobid):
        job = Job.objects.get(id=jobid)
        dict = job_to_dict(job)
        return HttpResponse(JSON_dump(dict),mimetype="application/json")

    def create(self,request,mfileid,start=0, end=10):
        mfile = MFile.objects.get(pk=mfileid)
        tasks = []

        job = Job(name="Render",service=mfile.service)
        job.save()

        folder = os.path.join( settings.MEDIA_ROOT, str(job.id))
        if not os.path.exists(folder):
            os.makedirs(folder)

        thumbfolder = os.path.join( settings.THUMB_ROOT, str(job.id))
        if not os.path.exists(thumbfolder):
            os.makedirs(thumbfolder)

        jobtype = "jobservice.tasks.render_blender"
        mimetype = "application/octet-stream; charset=binary"
        try:
            job_description = cache.get(jobtype)
            mimetype = job_description["outputmime"]
        except Exception as e:
            logging.info("No job description for job type '%s' %s" % (jobtype,e) )

        padding = 4
        for i in range(int(start),int(end)+1):
            output = JobOutput(name="%s Render"%mfile.name,job=job,mimetype=mimetype)
            ss= string.zfill(str(i), padding)
            fname = "%s.%s.png" % (mfile.name,ss)
            #fname = mfile.name
            #hashfname = "%s.%s" % (mfile.name,hashes)

            outputfile= os.path.join( folder , fname)
            thumbfile= os.path.join( thumbfolder , "%s%s" % (fname,".thumb.png"))
            #outputfile = outputpath

            #(outputhead,tail) = os.path.split(thumbfile)
            #if not os.path.isdir(outputhead):
            #    os.makedirs(outputhead)

            outputpath = os.path.join( str(job.id) , fname   )
            thumbpath = os.path.join( str(job.id) , "%s%s" % (fname,".thumb.png"))

            output.file = outputpath
            output.thumb = thumbpath
            output.save()

            thumboptions = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
            thumbsubtask = thumbimage.subtask([outputfile,thumbfile,thumboptions])

            renderoptions = {"padding":padding,"fname":fname,"frame":i}
            
            t = render_blender.subtask([mfile.file.path,outputfile,renderoptions],callback=thumbsubtask)
            tasks.append(t)
        
        ts = TaskSet(tasks=tasks)
        tsr = ts.apply_async()
        tsr.save()

        job.taskset_id=tsr.taskset_id
        job.save()

        jobmfile = JobMFile(mfile=mfile,job=job,index=0)
        jobmfile.save()

        dict = job_to_dict(job)
        return HttpResponse(dict,mimetype="application/json")


class JobOutputContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, outputid):

        joboutput = JobOutput.objects.get(id=outputid)

        logging.info(joboutput)
        job = joboutput.job
        logging.info(job)
        service = job.service
        container = service.container
        logging.info("Finding limit for %s " % (job))
        accessspeed = settings.DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (accessspeed,job.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (accessspeed,job.name))
            except ObjectDoesNotExist:
                pass

        #dlfoldername = "dl%s"%accessspeed
        dlfoldername = "dl"

        file=joboutput.file

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
            logging.info("linking %s (exist=%s) to %s (exists=%s)" % (mfilefilepath,os.path.exists(mfilefilepath),fullfilepath,os.path.exists(fullfilepath)))
            os.link(mfilefilepath,fullfilepath)


        usage_store.record(joboutput.id,models.metric_access,joboutput.file.size)

        logging.info("Redirecting  to %s " % redirecturl)
        return redirect("/%s"%redirecturl)