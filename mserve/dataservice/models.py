from django.db import models
import pickle
import base64
import storage
import logging
import datetime
import utils as utils
from django.conf import settings
from django.db.models.signals import post_save
from django.db.models.signals import post_init
from django.db.models.signals import pre_delete

ID_FIELD_LENGTH = 200
thumbpath = settings.THUMB_PATH

# Metrics for objects
metric_mfile = "http://mserve/file"
metric_backupfile = "http://mserve/backupfile"
metric_container = "http://mserve/container"
metric_service = "http://mserve/service"

# Metrics for mfiles
metric_disc = "http://mserve/disc"
metric_disc_space = "http://mserve/disc_space"
metric_ingest = "http://mserve/ingest"
metric_access = "http://mserve/access"
metric_archived = "http://mserve/archived"

metrics = [metric_mfile,metric_service,metric_container,metric_disc,metric_disc_space,metric_ingest,metric_access,metric_archived]

# What metric are reported fro each type
container_metrics = metrics
service_metrics = [metric_mfile,metric_service,metric_disc,metric_archived,metric_disc_space]
mfile_metrics = [metric_mfile,metric_disc,metric_ingest,metric_access,metric_archived,metric_disc_space]
backupfile_metrics = [metric_archived,metric_backupfile,metric_disc_space]

# Other Metric groups
byte_metrics = [metric_disc_space]

class Usage(models.Model):
    base            = models.ForeignKey('NamedBase',null=True, blank=True)
    metric          = models.CharField(max_length=4096)
    time            = models.DateTimeField(auto_now_add=True)   # Time first recorded (shouldnt change)
    reports         = models.BigIntegerField(default=0)         # Number of reports
    total           = models.FloatField(default=0)              # Sum of report values
    squares         = models.FloatField(default=0)              # Sum of squares of values
    nInProgress     = models.BigIntegerField(default=0)         # Sum of squares of values
    rateTime        = models.DateTimeField()                    # Time the rate last changed
    rate            = models.FloatField()                       # The current rate (change in value per second)
    rateCumulative  = models.FloatField()                       # Cumulative unreported usage before rateTime

    def fmt_ctime(self):
        return self.created.ctime()

    def fmt_rtime(self):
        return self.rateTime.ctime()
    
    def __unicode__(self):
        object = ""
        if self.base:
            object = self.base
        return "Usage:%s metric=%s total=%f reports=%s nInProgress=%s rate=%s rateTime=%s rateCumulative=%s" \
                % (object,self.metric,self.total,self.reports,self.nInProgress,self.rate,self.rateTime,self.rateCumulative);

class Base(models.Model):
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)

    class Meta:
        abstract = True

#class NamedBase(Base):
#    name = models.CharField(max_length=200)

    #def __unicode__(self):
     #   return self.name;

class NamedBase(Base):
    metrics = []
    initial_usage_recorded = models.BooleanField(default=False)
    name    = models.CharField(max_length=200)
    usages  = models.ManyToManyField("Usage")
    reportnum = models.IntegerField(default=1)

    def save(self):
        super(NamedBase, self).save()
        import usage_store as usage_store
        if not self.initial_usage_recorded:
            startusages = []
            for metric in self.metrics:
                #  Recored Initial Values
                v = self.get_value_for_metric(metric)
                if v is not None:
                    logging.info("Recording usage for metric %s value= %s" % (metric,v) )
                    usage = usage_store.record(self.id,metric,v)
                    startusages.append(usage)

                # Start recording initial rates
                r = self.get_rate_for_metric(metric)
                if r is not None:
                    logging.info("Recording usage rate for metric %s value= %s" % (metric,r) )
                    usage = usage_store.startrecording(self.id,metric,r)
                    startusages.append(usage)

            self.usages = startusages
            self.reportnum=1
            self.initial_usage_recorded = True
            super(NamedBase, self).save()

    def get_value_for_metric(self, metric):
        #logging.info("Override this method to report usage for metric %s" % metric)
        return None

    def get_rate_for_metric(self, metric):
        #logging.info("Override this method to report usage for metric %s" % metric)
        return None

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)

    def __unicode__(self):
        return self.name;

class HostingContainer(NamedBase):
    status = models.CharField(max_length=200)
    
    def __init__(self, *args, **kwargs):
        super(HostingContainer, self).__init__(*args, **kwargs)
        self.metrics = container_metrics

    def get_value_for_metric(self, metric):
        if metric == metric_container:
            return 1

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(HostingContainer, self).save()

class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer)
    status = models.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(DataService, self).__init__(*args, **kwargs)
        self.metrics = service_metrics

    def get_value_for_metric(self, metric):
        if metric == metric_service:
            return 1

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(DataService, self).save()

class MFile(NamedBase):
    # TODO : Add bitmask to MFile for deleted,remote,input,output, etc
    empty    = models.BooleanField(default=False)
    service  = models.ForeignKey(DataService)
    file     = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    size     = models.IntegerField(default=0)
    thumb    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    poster   = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    created  = models.DateTimeField(auto_now_add=True)
    updated  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created','name')

    def __init__(self, *args, **kwargs):
        super(MFile, self).__init__(*args, **kwargs)
        self.metrics = mfile_metrics

    def get_value_for_metric(self, metric):
        if metric == metric_mfile:
            return 1
        if not self.empty:
            if metric == metric_disc_space:
                return self.file.size
            if metric == metric_ingest:
                return self.file.size

    def get_rate_for_metric(self, metric):
        if not self.empty:
            if metric == metric_disc:
                return self.file.size

    def thumburl(self):
        return "%s%s" % (thumbpath,self.thumb)

    def posterurl(self):
        return "%s%s" % (thumbpath,self.poster)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        self.updated = datetime.datetime.now()
        super(MFile, self).save()

def pre_delete_handler( sender, instance=False, **kwargs):
    #logging.info("Pre delete sender=%s instance=%s" % (sender,instance))
    #logging.info("Deleting %s" % (instance.metrics))
    instance._delete_usage_()

pre_delete.connect(pre_delete_handler, sender=MFile, dispatch_uid="dataservice.models")

def post_init_handler( sender, instance=False, **kwargs):
    pass
    #logging.info("Post init sender=%s instance=%s" % (sender,instance))
    #logging.info(" %s" % (instance.metrics))
    #instance._delete_usage_()

post_init.connect(post_init_handler, sender=MFile, dispatch_uid="dataservice.models")

def post_save_handler( sender, instance=False, **kwargs):
    pass
    #logging.info("post_save sender=%s instance=%s" % (sender,instance))
    #logging.info(" %s" % (instance.metrics))
    #instance._delete_usage_()

post_save.connect(post_save_handler, sender=MFile, dispatch_uid="dataservice.models")

class BackupFile(NamedBase):
    mfile = models.ForeignKey(MFile)
    file = models.FileField(upload_to=utils.create_filename,storage=storage.gettapestorage())
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(BackupFile, self).__init__(*args, **kwargs)
        self.metrics = backupfile_metrics

    def get_value_for_metric(self, metric):
        if metric == metric_backupfile:
            return 1
        if file:
            if metric == metric_disc_space:
                return self.file.size

    def get_rate_for_metric(self, metric):
        if file:
            if metric == metric_disc:
                return self.file.size

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

    def __unicode__(self):
        return "Auth: authname=%s" % (self.authname);

class Role(Base):
    auth = models.ManyToManyField(Auth, related_name='roles')
    rolename = models.CharField(max_length=50)
    description= models.CharField(max_length=200)
    methods_encoded = models.TextField()

    def __unicode__(self):
        return "Role: rolename=%s methods=%s" % (self.rolename,self.methods());

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


