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
# Create your models here.

thumbpath = settings.THUMB_PATH

class Job(NamedBase):
    service  = models.ForeignKey(DataService)
    created  = models.DateTimeField(auto_now_add=True)
    taskset_id = models.CharField(max_length=200)

    class Meta:
        ordering = ('-created', 'name')

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(Job, self).save()

    def __unicode__(self):
        return "%s" % (self.name);

class JobMFile(Base):
    job  = models.ForeignKey(Job)
    mfile = models.ForeignKey(MFile)
    index = models.IntegerField(default=0)
    created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created', 'job')

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(JobMFile, self).save()

class JobOutput(NamedBase):
    job   = models.ForeignKey(Job)
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    file  = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    thumb = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())

    def thumburl(self):
        return "%s%s" % (thumbpath,self.thumb)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(JobOutput, self).save()