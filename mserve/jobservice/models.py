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
import time
import datetime
import logging
from django.db import models
from dataservice.models import *
from dataservice import utils
from dataservice import storage
from dataservice.tasks import thumboutput
from dataservice.tasks import thumbvideooutput
from celery.result import TaskSetResult
from djcelery.models import TaskState

thumbpath = settings.THUMB_PATH
mediapath = settings.MEDIA_URL

metric_job = "http://mserve/job"

job_metrics = [metric_job]

class Job(NamedBase):
    mfile  = models.ForeignKey(MFile)
    created  = models.DateTimeField(auto_now_add=True)
    taskset_id = models.CharField(max_length=200)

    class Meta:
        ordering = ('-created','name')

    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.metrics = job_metrics

    @staticmethod
    def get_job_plots(types):
        taskstates = TaskState.objects.all()
        plots = []

        for type in types:

            if type == "last24":
                now = datetime.datetime.now()
                count = now - datetime.timedelta(days=1)
                step = datetime.timedelta(hours=1)
                prev = count - step
                taskplot = {}
                data = []
                while count <= now:
                    tasks = TaskState.objects.filter(tstamp__lt=count,tstamp__gt=prev)
                    prev = count
                    count = count + step
                    data.append( [time.mktime(count.timetuple())*1000, str(len(tasks)) ])

                taskplot["data"] = [data]
                taskplot["type"] = "time"
                taskplot["label"] = "Tasks in last 24 hours"
                plots.append(taskplot)

            if type == "last1":
                now = datetime.datetime.now()
                count = now - datetime.timedelta(hours=1)
                step = datetime.timedelta(minutes=5)
                prev = count - step
                taskplot = {}
                data = []
                while count <= now:
                    tasks = TaskState.objects.filter(tstamp__lt=count,tstamp__gt=prev)
                    logging.info("count for %s is %s ", count, len(tasks))
                    prev = count
                    count = count + step
                    data.append( [time.mktime(count.timetuple())*1000, str(len(tasks)) ])
                taskplot["data"] = [data]
                taskplot["type"] = "time"
                taskplot["label"] = "Tasks in last hour"
                plots.append(taskplot)

            if type == "jobsbytype":
                jobplot = {}
                jobplot["type"] = "pie"
                jobplot["label"] = "Jobs by Type",
                query = taskstates.values("name").annotate(n=Count("name"))
                for val in query:
                    val["label"] = val["name"].split(".")[-1]
                    val["data"] = val["n"]
                jobplot["data"] = [item for item in query]
                plots.append(jobplot)

            if type == "jobs":
                jobplot = {}
                jobplot["type"] = "pie"
                jobplot["size"] = "small"
                jobplot["label"] = "All Jobs"
                jobplot["data"] = [
                    {"label":"Success" , "data": taskstates.filter(state="SUCCESS").count(), "color" : "#00CC00"  },
                    {"label":"Failed" , "data": taskstates.filter(state="FAILURE").count(), "color" : "#CC0000",  }
                ]

                plots.append(jobplot)

                for taskname in set(taskstates.values_list("name",flat=True).distinct()):
                    logging.info(taskname)
                    subplot = {}
                    subplot["type"] = "pie"
                    subplot["size"] = "small"
                    subplot["label"] = "Job %s" % taskname.split(".")[-1]
                    tasks = taskstates.filter(name=taskname)
                    success = tasks.filter(state="SUCCESS").aggregate(success=Count('name'))["success"]
                    failure = tasks.filter(state="FAILURE").aggregate(failure=Count('name'))["failure"]
                    data = []
                    data.append({ "label" : "Failed" , "data" : failure, "color" : "#CC0000"})
                    data.append({ "label" : "Success" , "data" : success, "color" : "#00CC00"})
                    subplot["data"] = data
                    plots.append(subplot)



        logging.info(plots)
        return plots

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(Job, self).save()

    def __unicode__(self):
        return "%s" % (self.name);

    def get_rate_for_metric(self, metric):
        if metric == metric_job:
            return 1
        pass

    def get_updated_rate_for_metric(self, metric):
        pass
            
    def clean_base(self,authid):
        jobdict = {}
        jobdict["name"] = self.name
        jobdict["tasks"] = self.tasks()
        jobdict["joboutput_set"] = self.joboutput_set
        jobdict["id"] = self.id
        jobdict["taskset_id"] = self.taskset_id
        jobdict["created"] = self.created

        return jobdict

    def tasks(self):
        tsr = TaskSetResult.restore(self.taskset_id)
        dict = {}
        if tsr is not None and hasattr(tsr,"taskset_id"):
            
            dict["taskset_id"] = tsr.taskset_id
            results = []
            if tsr.subtasks:
                for subtask in tsr.subtasks:
                    results.append({"name":subtask.task_name,"result":subtask.result,"success":subtask.successful(),"state":subtask.state})
                dict["completed_count"] = tsr.completed_count()
                dict["failed"] = tsr.failed()
                dict["total"] = tsr.total
                if tsr.total != 0:
                    dict["percent"] = float(tsr.completed_count())/float(tsr.total)*100
                else:
                    dict["percent"] = 0
                dict["ready"] = tsr.ready()
                dict["successful"] = tsr.successful()
                dict["waiting"] = tsr.waiting()
            else:
                dict["completed_count"] = 0
                dict["failed"] = 0
                dict["total"] = 0
                dict["percent"] = 0
                dict["successful"] = False
                dict["waiting"] = False
            dict["result"] = results

            return dict
        else:
            dict["taskset_id"] = ""
            dict["completed_count"] = 0
            dict["failed"] = 0
            dict["percent"] = 0
            dict["ready"] = True
            dict["successful"] = False
            dict["total"] = 0
            dict["waiting"] = False
            return dict

        return dict

class JobOutput(NamedBase):
    job   = models.ForeignKey(Job)
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    file  = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    thumb = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())

    def get_upload_path(self):
        return reverse('joboutput_upload',args=[self.id])

    def get_upload_thumb_path(self):
        return reverse('joboutput_upload_thumb',args=[self.id])

    def thumburl(self):
        if self.thumb and self.thumb != "":
            return "%s%s" % (thumbpath,self.thumb)
        else:
            if self.mimetype:
                if self.mimetype.startswith("image"):
                    return os.path.join(mediapath,"images","image-x-generic.png")
                if self.mimetype.startswith("text"):
                    return os.path.join(mediapath,"images","text-x-generic.png")
        return os.path.join(mediapath,"images","package-x-generic.png")
    
    def save(self):
        if not self.id:
            self.id = utils.random_id()

        if self.file and not self.thumb:
            if self.mimetype.startswith('image'):
                options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                thumboutput.delay([self.id],[],options)
            if self.mimetype.startswith('video'):
                options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                thumbvideooutput.delay([self.id],[],options)

        super(JobOutput, self).save()