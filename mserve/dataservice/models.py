from django.db import models
import uuid
import pickle
import base64
import os
import time
import logging

ID_FIELD_LENGTH = 200

fmt = "%3.2f"

def random_id():
    return str(uuid.uuid4())

def create_filename(instance, filename):
    timeformat = time.strftime("%Y/%m/%d/")
    return os.path.join(timeformat ,instance.id ,filename)
    #return os.path.join('files', timeformat ,instance.id ,filename)

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
        return "%s %s reported=%s rate=%f usageSoFar=%f" % (self.base,self.metric,self.current,self.rate,self.usageSoFar)


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
        if self.metric == usage_store.metric_stager or usage_store.metric_stager:
            return "/stager/"
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
    count = models.IntegerField(default=0)

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

    def save(self):
        if not self.id:
            self.id = random_id()
        super(HostingContainer, self).save()

class ManagementProperty(models.Model):
    base        = models.ForeignKey(NamedBase)
    property    = models.CharField(max_length=200)
    value       = models.CharField(max_length=200)

class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer)
    status = models.CharField(max_length=200)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataService, self).save()

class DataStager(NamedBase):
    # TODO : Add bitmask to Datastager for deleted,remote,input,output, etc
    service = models.ForeignKey(DataService)
    file = models.FileField(upload_to=create_filename,blank=True,null=True)
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)

    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataStager, self).save()

class ContainerResourcesReport(models.Model):
    base = models.ForeignKey('NamedBase')
    reportnum = models.IntegerField(default=0)
    services   = models.ManyToManyField(DataService,related_name="con2ser")
    meta       = models.CharField(max_length=200,blank=True,null=True)

    def __unicode__(self):
        return "Container Managed Services Report for %s reportnum=%s" % (self.base,self.reportnum);

class ServiceResourcesReport(models.Model):
    base = models.ForeignKey('NamedBase')
    reportnum = models.IntegerField(default=0)
    stagers   = models.ManyToManyField(DataStager,related_name="ser2sta")
    meta       = models.CharField(max_length=200,blank=True,null=True)

    def __unicode__(self):
        return "Service Managed Services Report for %s reportnum=%s" % (self.base,self.reportnum);

class Auth(Base):
    authname = models.CharField(max_length=50)
    description= models.CharField(max_length=200)
    methods_encoded = models.TextField()

    def methods(self):
        return pickle.loads(base64.b64decode(self.methods_encoded))

    def setmethods(self,methods):
        self.methods_encoded = base64.b64encode(pickle.dumps(methods))

    def __unicode__(self):
        return self.authname + " -> " + str(self.methods())

    class Meta:
        abstract = True

class SubAuth(Auth):
    def save(self):
        if not self.id:
            self.id = random_id()
        super(SubAuth, self).save()

class JoinAuth(models.Model):
    parent = models.CharField(max_length=50)
    child  = models.CharField(max_length=50)

    def __unicode__(self):
        return str(self.parent) + " - " + str(self.child)

class DataStagerAuth(Auth):
    stager = models.ForeignKey(DataStager)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataStagerAuth, self).save()

class DataServiceAuth(Auth):
    dataservice = models.ForeignKey(DataService)
    def save(self):
        if not self.id:
            self.id = random_id()
        super(DataServiceAuth, self).save()

class HostingContainerAuth(Auth):
    hostingcontainer = models.ForeignKey(HostingContainer)

    def save(self):
        if not self.id:
            self.id = random_id()
        super(HostingContainerAuth, self).save()


