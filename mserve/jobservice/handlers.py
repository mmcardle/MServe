
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
from django.http import *
from django.http import HttpResponse
from django.shortcuts import redirect
from mserve.dataservice.models import DataService
from mserve.dataservice.models import MFile
from mserve.jobservice.models import *
from mserve.jobservice.models import Job
from mserve.jobservice.models import JobMFile
from mserve.jobservice.models import JobOutput
from piston.handler import BaseHandler
from piston.utils import rc
import settings as settings
from tasks import render_blender

import dataservice.utils as utils

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
            dict["percent"] = int(tsr.completed_count())/int(tsr.total)*100
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
            dict["percent"] = (tsr.completed_count())/(tsr.total)*100.0
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
    fields = ('id','name','created','taskset_id','joboutput_set')
    #fields = ('id','name','created','taskset_id','jobmfile_set')

    def delete(self, request, id):
        job = Job.objects.get(id=id)
        job.delete()
        r = rc.DELETED
        return r
    
    def read(self, request, id):
        job = Job.objects.get(id=id)
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
        dict["percent"] = int(tsr.completed_count())/int(tsr.total)*100
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
        return HttpResponse(dict,mimetype="application/json")


class JobOutputHandler(BaseHandler):
    model = JobOutput
    fields = ('id','job_id','name','thumb','thumburl','file')

class RenderResultsHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, jobid):
        job = Job.objects.get(id=jobid)
        output = job.joboutput_set.all()
        return output

class RenderHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def read(self, request, jobid):

        tsr = TaskSetResult.restore(taskset_id)
        dict = {}
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
        return HttpResponse(JSON_dump(dict),mimetype="application/json")
        #return djcelery.views.task_status(request, taskid)

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

        padding = 4
        for i in range(int(start),int(end)+1):
            output = JobOutput(name="%s Render"%mfile.name,job=job)
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
            thumbpath = os.path.join( str(job.id) , "%s%s" % (fname,".thumb.png") )

            output.file = outputpath
            output.thumb = thumbpath
            output.save()
            
            t = render_blender.subtask([mfile.file.path,i,i,folder,mfile.name,thumbfile],thumbsize=settings.thumbsize,padding=padding,callback=thumbimage)
            tasks.append(t)
        
        ts = TaskSet(tasks=tasks)
        tsr = ts.apply_async()
        tsr.save()

        job.taskset_id=tsr.taskset_id
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
        dict["percent"] = tsr.completed_count()/tsr.total*100
        dict["ready"] = tsr.ready()
        dict["successful"] = tsr.successful()
        dict["total"] = tsr.total
        dict["waiting"] = tsr.waiting()
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
            logging.info("linking %s to %s" % (mfilefilepath,fullfilepath))
            os.link(mfilefilepath,fullfilepath)

        import dataservice.models as models
        import dataservice.usage_store as usage_store
        usage_store.record(joboutput.id,models.metric_access,joboutput.file.size)

        return redirect("/%s"%redirecturl)