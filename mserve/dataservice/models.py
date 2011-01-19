from django.db import models
import pickle
import base64
import os
import time
import storage
import datetime
import utils as utils
from django.conf import settings

ID_FIELD_LENGTH = 200
fmt = "%3.2f"

thumbpath = settings.THUMB_PATH

class UsageReport(models.Model):
    base = models.ForeignKey('NamedBase')
    reportnum = models.IntegerField(default=0)
    summarys   = models.ManyToManyField("UsageSummary")
    inprogress = models.ManyToManyField("AggregateUsageRate")

    def __unicode__(self):
        return "Usage Report for %s reportnum=%s" % (self.base,self.reportnum);

class Usage(models.Model):
    base = models.ForeignKey('NamedBase',null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True,null=True)
    metric = models.CharField(max_length=4096)
    value  = models.FloatField()

    def fmt_ctime(self):
        return self.created.ctime()

    def fmt_value(self):
        import usage_store as usage_store
        if self.metric == usage_store.metric_disc:
            return sizeof_fmt(self.value)
        else:
            return "%3.2f" % (self.value)
    
    def __unicode__(self):
        return "%s %s created=%s value=%f " % (self.base,self.metric,self.created,self.value);

class UsageRate(models.Model):
    base       = models.ForeignKey('NamedBase')
    current    = models.DateTimeField() # When the current rate was reported
    metric     = models.CharField(max_length=4096)
    rate       = models.FloatField() # The current rate
    usageSoFar = models.FloatField() # Cumulative unreported usage before that point

    def __unicode__(self):
        return "Usage: %s %s %s reported=%s rate=%f usageSoFar=%f" % (self.base,self.base.id,self.metric,self.current,self.rate,self.usageSoFar)


    def ctime(self):
        return self.current.ctime()

    def time_since_last_report(self):
        import datetime
        import time
        now = datetime.datetime.now()
        #t1 = time.mktime(datetime.datetime.now().timetuple())
        #t2 = time.mktime(self.current.timetuple())
        #print float(now) - float(self.current)
        x = now - self.current
        y = datetime.timedelta(seconds=x.seconds,days=x.days)
        return y

    def path(self):
        import usage_store as usage_store
        if self.metric == usage_store.metric_container:
            return "/container/"
        if self.metric == usage_store.metric_service:
            return "/service/"
        if self.metric == usage_store.metric_mfile or usage_store.metric_mfile:
            return "/mfile/"
        return "/error/"

    def calc_rate(self):
        import usage_store as usage_store
        if self.metric == usage_store.metric_disc:
            return sizeof_fmt(self.rate)
        else:
            return self.rate
    
    def calc_so_far(self):
        import datetime
        import time
        import usage_store as usage_store
        now = datetime.datetime.now()

        t2 = time.mktime(now.timetuple())+float("0.%s"%now.microsecond)
        t1 = time.mktime(self.current.timetuple())+float("0.%s" % self.current.microsecond)

        x = (t2 - t1) * self.rate
        return fmt % (x)

class AggregateUsageRate(models.Model):
    base       = models.ForeignKey('NamedBase')
    current    = models.DateTimeField() # When the current rate was reported
    metric     = models.CharField(max_length=4096)
    rate       = models.FloatField() # The current rate
    usageSoFar = models.FloatField() # Cumulative unreported usage before that point
    count      = models.IntegerField(default=0)

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')

class UsageSummary(models.Model):
    metric = models.CharField(primary_key=True, max_length=4096)
    n      = models.FloatField(default=0.0)
    sum    = models.FloatField(default=0.0)
    min    = models.FloatField(default=0.0)
    max    = models.FloatField(default=0.0)
    sums   = models.FloatField(default=0.0)

    def __fmt(self,num):
        import usage_store as usage_store
        if self.metric in usage_store.byte_metrics:
            return sizeof_fmt(num)
        else:
            return fmt % (num)

    def fmt_n(self):
        return fmt % (self.n)

    def fmt_sum(self):
        return self.__fmt(self.sum)
    
    def fmt_min(self):
        return self.__fmt(self.min)
    
    def fmt_max(self):
        return self.__fmt(self.max)
    
    def fmt_sums(self):
        import locale
        locale.setlocale(locale.LC_ALL, "")
        return locale.format(fmt, self.sums, True)

    def fmt_avg(self):
        if self.n == 0:
            return self.__fmt(self.sum)
        return self.__fmt(self.sum/self.n)

    def __unicode__(self):
        return "%s {n=%s,sum=%s,min=%s,max=%s,sums=%s}" % (self.metric,self.n,self.sum,self.min,self.max,self.sums);


class Base(models.Model):
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)

    class Meta:
        abstract = True

class NamedBase(Base):
    name = models.CharField(max_length=200)

    #class Meta:
        #abstract = True

    def __unicode__(self):
        return self.name;

class HostingContainer(NamedBase):
    status = models.CharField(max_length=200)
    reportnum = models.IntegerField(default=0)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(HostingContainer, self).save()

class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer)
    status = models.CharField(max_length=200)
    reportnum = models.IntegerField(default=0)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(DataService, self).save()

class MFile(NamedBase):
    # TODO : Add bitmask to MFile for deleted,remote,input,output, etc
    service  = models.ForeignKey(DataService)
    #file     = models.FileField(upload_to=create_filename,storage=storage.getdiscstorage())
    file     = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    size     = models.IntegerField(default=0)
    thumb    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    poster   = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    created  = models.DateTimeField(auto_now_add=True)
    updated  = models.DateTimeField(auto_now=True)
    reportnum = models.IntegerField(default=0)

    class Meta:
        ordering = ('-created','name')

    def thumburl(self):
        return "%s%s" % (thumbpath,self.thumb)

    def posterurl(self):
        return "%s%s" % (thumbpath,self.poster)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        self.updated = datetime.datetime.now()
        super(MFile, self).save()

class BackupFile(NamedBase):
    mfile = models.ForeignKey(MFile)
    file = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.gettapestorage())
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(BackupFile, self).save()

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

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(JobMFile, self).save()

class ManagementProperty(models.Model):
    base        = models.ForeignKey(NamedBase)
    property    = models.CharField(max_length=200)
    value       = models.CharField(max_length=200)

class Auth(Base):
    authname = models.CharField(max_length=50)

class Role(Base):
    auth = models.ManyToManyField(Auth, related_name='roles')
    rolename = models.CharField(max_length=50)
    description= models.CharField(max_length=200)
    methods_encoded = models.TextField()

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(Role, self).save()

    def methods(self):
        currentmethods = pickle.loads(base64.b64decode(self.methods_encoded))
        if currentmethods == None:
            return []
        else:
            return currentmethods

    def setmethods(self,methods):
        self.methods_encoded = base64.b64encode(pickle.dumps(methods))

    def addmethods(self,methods):
        newmethods = list(set(methods + self.methods()))
        self.methods_encoded = base64.b64encode(pickle.dumps(newmethods))

class SubAuth(Auth):
    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(SubAuth, self).save()

class JoinAuth(models.Model):
    parent = models.CharField(max_length=50)
    child  = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.parent) + " - " + str(self.child)

class MFileAuth(Auth):
    mfile = models.ForeignKey(MFile)
    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(MFileAuth, self).save()

class DataServiceAuth(Auth):
    dataservice = models.ForeignKey(DataService)
    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(DataServiceAuth, self).save()

class HostingContainerAuth(Auth):
    hostingcontainer = models.ForeignKey(HostingContainer)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(HostingContainerAuth, self).save()


