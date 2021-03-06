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
"""

JobService Handlers
----------------------

::

 This class jobservice/handlers.py defines the piston handlers for the jobservice module

For more information see :class:`dataservice.handlers`

"""
from django.http import HttpResponseNotFound
import os
import shutil
import os.path
import logging
from celery.task.sets import TaskSet
from celery.task.sets import subtask
from dataservice.forms import *
from dataservice.models import *
from django.http import *
from django.shortcuts import redirect
from dataservice.models import DataService
from dataservice.models import MFile
from jobservice.models import *
from jobservice.models import Job
from jobservice.models import JobOutput
import dataservice.models as models
import dataservice.usage_store as usage_store
from piston.handler import BaseHandler
from piston.utils import rc
import settings as settings
import dataservice.utils as utils
from django.core.cache import cache
from . import get_task_description

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
    allowed_methods = ('GET', 'POST', 'DELETE')
    fields = ('id', 'name', 'created', 'taskset_id', 'joboutput_set', 'tasks',
              'url')

    def create(self, request, mfileid=None):

        if request.POST.has_key('jobtype'):
            jobtype = request.POST['jobtype']

            inputs = []
            outputs = []
            callbacks = []
            options = {}

            if mfileid != "":
                mfile = MFile.objects.get(id=mfileid)

                check = mfile.service.check_times()
                if check:
                    return check

                inputs.append(mfile.id)
            else:
                r = rc.BAD_REQUEST
                r.write("\nRequest has no serviceid or mfileid - Creation Failed!")
                return r

            for v in request.POST:
                options[v]=request.POST[v]

            logging.info("Request for job type '%s' with options %s" % (jobtype, options) )

            task_description = None
            try:
                task_description = get_task_description(jobtype)
            except Exception as e:
                logging.error("No job description for job type '%s' %s" % (jobtype, e) )
                r = rc.BAD_REQUEST
                r.write("\nJob has no description - Creation Failed!")
                return r

            nbinputs = task_description["nbinputs"]
            nboutputs= task_description["nboutputs"]

            jobname = "%s" % jobtype
            job = mfile.do("POST","jobs",**{"name":jobname})
            job.save()

            for i in range(1,nbinputs):
                mfileid = request.POST['input-%s'%i]
                mfile = MFile.objects.get(id=mfileid)
                inputs.append(mfile.id)

            if job == None:
                r = rc.BAD_REQUEST
                r.write("Job Creation failed!")
                return r

            for i in range(0,nboutputs):
                outputmimetype = task_description["output-%s"%i]["mimetype"]
                output = JobOutput(name="Output %s '%s'"%(i,jobtype),job=job,mimetype=outputmimetype)
                output.save()
                outputs.append(output.id)

            logging.info("Creating task %s inputs= %s outputs= %s options= %s" % (jobtype,inputs,outputs,options))

            # TODO : Submit to correct Q options={"queue":"%s"%job.id}
            prioritise = mfile.service.priority
            q = "normal.%s"% (jobtype)
            if prioritise:
                q = "priority.%s"% (jobtype)
            kwargs={"routing_key":q}
            task = subtask(task=jobtype,args=[inputs,outputs,options],callbacks=callbacks,options=kwargs)
            logging.info("Task created %s " % task )

            tasks = [task]

            ts = TaskSet(tasks=tasks)
            tsr = ts.apply_async()
            tsr.save()

            job.taskset_id=tsr.taskset_id
            job.save()

            logging.info("Creating Job Type %s on file %s" % (jobtype,mfileid))

            logging.info("Created Job  %s" % (job))

            return job
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request! no jobtype in request.")
            return r

    def delete(self, request, jobid):
        job = Job.objects.get(id=jobid)
        job.delete()
        r = rc.DELETED
        return r
    
    def read(self, request, jobid=None, mfileid=None, authid=None):
        if jobid:
            job = Job.objects.get(id=jobid)
            return job
        elif mfileid:
            jobs = Job.objects.filter(mfile=mfileid)
            return jobs
        elif authid:
            auth = Auth.objects.get(pk=authid)
            logging.info("S %s" % auth)
            if utils.is_service(auth.base):
                ds = DataService.objects.get(id=auth.base.id)
                return ds.do("GET","jobs")

                jobs = Job.objects.filter(mfile=auth.base.id)
                return jobs
            if utils.is_mfile(auth.base):
                jobs = Job.objects.filter(mfile=auth.base.id)
                return jobs


class JobOutputHandler(BaseHandler):
    model = JobOutput
    allowed_methods = ('GET', 'POST', 'PUT')
    fields = ('id', 'job_id', 'name', 'thumb', 'thumburl', 'file', 'mimetype',
                'mfile_url')

    def update(self, request, outputid, field=None):
        if outputid:
            joboutput = JobOutput.objects.get(id=outputid)

            if field == "thumb":
                utils.write_request_to_field(request, joboutput.thumb, "thumb.png")
                return {"message":"updated job thumb"}

            utils.write_request_to_field(request, joboutput.file, "joboutput")

            return {"message":"updated job"}
        else:
            return HttpResponseNotAllowed([])

    def create(self, request, outputid, field=None):
        try:
            joboutput = JobOutput.objects.get(id=outputid)

            if field == "thumb":
                file = request.FILES["thumb"]
                joboutput.thumb.save("thumb.png", file, save=True)
                return {"message":"updated job output thumb"}
            elif field == "file":
                file = request.FILES["file"]
                joboutput.file.save(joboutput.name, file, save=True)
                logging.info("request.FILES SAVED")
                return {"message":"updated job output"}
            elif field == "mfile":
                name = request.POST.get("name","new-mfile")
                mfile = joboutput.job.mfile.service.create_mfile(name,
                    file=joboutput.job.mfile.file, post_process=True,
                    folder=joboutput.job.mfile.folder)
                relname = "created by %s" % joboutput.job.name
                rel = Relationship(entity1=joboutput.job.mfile, entity2=mfile,
                                name=relname)
                rel.save()
                return mfile
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request! no file in request.")
                return r
        except:
            raise

    def read(self, request, outputid, field=None):
        if outputid:
            if field == "file":
                joboutput = JobOutput.objects.get(id=outputid)

                file=joboutput.file

                if file == "":
                    return HttpResponseNotFound()

                outputfilepath = file.path

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

                if accessspeed == "unlimited":
                    dlfoldername = "dl"
                else:
                    dlfoldername = "dl%s" % accessspeed

                p = str(file)

                redirecturl = utils.gen_sec_link_orig(p,dlfoldername)
                redirecturl = redirecturl[1:]

                SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

                fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
                fullfilepathfolder = os.path.dirname(fullfilepath)
                outputfilepath = file.path

                logging.info("Redirect URL      = %s " % redirecturl)
                logging.info("fullfilepath      = %s " % fullfilepath)
                logging.info("fullfilefolder    = %s " % fullfilepathfolder)
                logging.info("mfilefp      = %s " % outputfilepath)
                logging.info("mfilef       = %s " % file)

                if not os.path.exists(fullfilepathfolder):
                    os.makedirs(fullfilepathfolder)

                if not os.path.exists(fullfilepath):
                    logging.info("linking %s (exist=%s) to %s (exists=%s)" % (outputfilepath,os.path.exists(outputfilepath),fullfilepath,os.path.exists(fullfilepath)))
                    try:
                        os.link(outputfilepath,fullfilepath)
                    except Exception as e:
                        logging.info("Caught error linking file, trying copy. %s" % str(e))
                        shutil.copy(outputfilepath,fullfilepath)

                usage_store.record(joboutput.id,models.METRIC_ACCESS,joboutput.file.size)

                logging.info("Redirecting  to %s " % redirecturl)
                return redirect("/%s"%redirecturl)
            else:
                joboutput = JobOutput.objects.get(id=outputid)
                return joboutput
        else:
            return HttpResponseNotAllowed([])