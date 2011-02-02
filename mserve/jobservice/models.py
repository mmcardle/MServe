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
        ordering = ('created', 'name')

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
    file  = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    thumb = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())

    def thumburl(self):
        return "%s%s" % (thumbpath,self.thumb)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(JobOutput, self).save()