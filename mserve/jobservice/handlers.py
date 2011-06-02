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
import os
import os.path
import logging
from celery.task.sets import TaskSet
from dataservice.forms import *
from dataservice.models import *
from dataservice.tasks import thumbimage

from django.http import *
from django.shortcuts import redirect
from mserve.dataservice.models import DataService
from mserve.dataservice.models import MFile
from mserve.jobservice.models import *
from mserve.jobservice.models import Job
from mserve.jobservice.models import JobOutput
import dataservice.models as models
import dataservice.usage_store as usage_store
from piston.handler import BaseHandler
from piston.utils import rc
import settings as settings
import dataservice.utils as utils

#should be
#from django.core.cache import cache
cache = {}
cache['dataservice.tasks.thumbimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "image/png" },
        "output-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }
cache['jobservice.tasks.copyfromurl'] = {
        "nbinputs" : 0,
        "nboutputs" : 1,
        "output-0" : { "mimetype" : "application/octet-stream" },
        "options":['url'],
        "results" :[]
    }
cache['jobservice.tasks.render_blender'] =    {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "image/png"},
        "options":['frame'],
        "results" : []
    }
cache['prestoprime.tasks.mxftechmdextractor'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "text/plain"},
        "options":[],
        "results" : []
    }
cache['prestoprime.tasks.d10mxfchecksum'] =    {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "text/plain"},
        "options":[],
        "results" : []
    }
cache['prestoprime.tasks.mxfframecount'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options":[],
        "results" : ["lines"]
    }
cache['prestoprime.tasks.extractd10frame'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "output-0" : { "mimetype" : "image/png" },
        "options":['frame'],
        "results" : []
    }


class JobServiceHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, serviceid=None, authid=None):
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET","jobs")
        elif authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET","jobs")
        else:
            r = rc.BAD_REQUEST
            r.write("\nRequest has no serviceid or authid - Creation Failed!")
            return r

class JobHandler(BaseHandler):
    model = Job
    allowed_methods = ('GET','POST','DELETE')
    fields = ('id','name','created','taskset_id','joboutput_set','tasks')

    def create(self, request, mfileid=None):
        
        jobtype = request.POST['jobtype']

        name = "newfile"
        inputs = []
        outputs = []
        callbacks = []
        options = {}

        if mfileid != "":
            mfile = MFile.objects.get(id=mfileid)
            name = mfile.name
            inputs.append(mfile.file.path)
        else:
            r = rc.BAD_REQUEST
            r.write("\nRequest has no serviceid or mfileid - Creation Failed!")
            return r

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

        job = Job(name="Job",mfile=mfile)
        job.save()

        for i in range(1,nbinputs-1):
            mfileid = request.POST['input-%s'%i]
            mfile = MFile.objects.get(id=mfileid)
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

                logging.info("THUMBFILE %s" % thumbfile)

                output.thumb = thumbpath
                output.save()
                thumboptions = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                callback = thumbimage.subtask([[output.file.path],[thumbfile],thumboptions])

                logging.info("THUMBFILE callback %s" % callback)

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

        # TODO : Submit to correct Q options={"queue":"%s"%job.id}
        task = m.subtask([inputs,outputs,options],callbacks=callbacks)

        tasks = [task]

        ts = TaskSet(tasks=tasks)
        tsr = ts.apply_async()
        tsr.save()

        job.taskset_id=tsr.taskset_id
        job.save()

        logging.info("Creating Job Type %s on file %s" % (jobtype,mfileid))

        logging.info("Created Job  %s" % (m))

        return job

    def delete(self, request, id):
        job = Job.objects.get(id=id)
        job.delete()
        r = rc.DELETED
        return r
    
    def read(self, request, jobid=None, mfileid=None):
        if jobid:
            job = Job.objects.get(id=jobid)
            return job
        elif mfileid:
            jobs = Job.objects.filter(mfile=mfileid)
            return jobs

class JobOutputHandler(BaseHandler):
    model = JobOutput
    fields = ('id','job_id','name','thumb','thumburl','file','mimetype')

class JobOutputContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, outputid):

        joboutput = JobOutput.objects.get(id=outputid)

        logging.info(joboutput)
        job = joboutput.job
        logging.info(job)
        accessspeed = settings.DEFAULT_ACCESS_SPEED
        service = job.mfile.service
        container = service.container
        logging.info("Finding limit for %s " % (job))
        
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

        dlfoldername = "dl%s"%accessspeed
        #dlfoldername = "dl"

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

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m