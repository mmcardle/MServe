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
from django.db import models
from dataservice.models import *
from dataservice import utils
from dataservice import storage
from dataservice.tasks import thumbimage
from celery.result import TaskSetResult
# Create your models here.

thumbpath = settings.THUMB_PATH
mediapath = settings.MEDIA_URL

class Job(NamedBase):
    #service  = models.ForeignKey(DataService)
    mfile  = models.ForeignKey(MFile)
    created  = models.DateTimeField(auto_now_add=True)
    taskset_id = models.CharField(max_length=200)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(Job, self).save()

    def __unicode__(self):
        return "%s" % (self.name);

    def tasks(self):
        tsr = TaskSetResult.restore(self.taskset_id)
        dict = {}
        if tsr is not None:
            
            dict["taskset_id"] = tsr.taskset_id
            # Dont return results until job in complete
            #if tsr.successful():
            #    dict["result"] = tsr.join()
            #else:
            results = []
            for subtask in tsr.subtasks:
                #if subtask.successful():
                #    results.append(subtask.result)
                    #results.append({"name":subtask.task_name,"success":subtask.successful()})
                #else:
                results.append({"name":subtask.task_name,"result":subtask.result,"success":subtask.successful()})
            dict["result"] = results

            dict["completed_count"] = tsr.completed_count()
            dict["failed"] = tsr.failed()
            if int(tsr.total) != 0:
                dict["percent"] = int(tsr.completed_count())/int(tsr.total)*100
            else:
                dict["percent"] = 0
            dict["ready"] = tsr.ready()
            dict["successful"] = tsr.successful()
            dict["total"] = tsr.total
            dict["waiting"] = tsr.waiting()
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

        if self.file and not self.thumb and self.mimetype.startswith('image'):
            options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
            thumbimage.delay([self],[],options)

        super(JobOutput, self).save()