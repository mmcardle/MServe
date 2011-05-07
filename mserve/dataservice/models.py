from django.db import models
import pickle
import base64
import storage
import logging
import datetime
import os
import utils as utils
import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_init
from django.db.models.signals import pre_delete
import django.dispatch

from dataservice.tasks import thumbvideo
from dataservice.tasks import proxyvideo
from dataservice.tasks import thumbimage
from dataservice.tasks import mimefile
from dataservice.tasks import md5file

use_celery = settings.USE_CELERY

if use_celery:
    thumbvideo = thumbvideo.delay
    thumbimage = thumbimage.delay
    proxyvideo = proxyvideo.delay
    
# Declare Signals
mfile_get_signal = django.dispatch.Signal(providing_args=["mfile"])

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


class MServeProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    bases = models.ManyToManyField('NamedBase', related_name='bases')

    def mfiles(self):
        ret = []
        for base in self.bases.all():
            if utils.is_mfile(base):
                ret.append(MFile.objects.get(id=base.id))
        return ret

    def dataservices(self):
        ret = []
        for base in self.bases.all():
            if utils.is_service(base):
                ret.append(DataService.objects.get(id=base.id))
        return ret

    def mfolders(self):
        ret = []
        for base in self.bases.all():
            if utils.is_mfolder(base):
                ret.append(MFolder.objects.get(id=base.id))
        return ret

    def containers(self):
        ret = []
        for base in self.bases.all():
            if utils.is_container(base):
                ret.append(HostingContainer.objects.get(id=base.id))
        return ret

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
        return "usage"
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

    @staticmethod
    def create_container(name):
        import api
        hostingcontainer = HostingContainer(name=name)
        hostingcontainer.save()

        hostingcontainerauth = Auth(base=hostingcontainer,authname="full")

        hostingcontainerauth.save()

        owner_role = Role(rolename="admin")
        owner_role.setmethods(api.all_container_methods)
        owner_role.description = "Full access to the container"
        owner_role.save()

        hostingcontainerauth.roles.add(owner_role)

        managementproperty = ManagementProperty(property="accessspeed",base=hostingcontainer,value=settings.DEFAULT_ACCESS_SPEED)
        managementproperty.save()

        return hostingcontainer

    def create_data_service(self,name):
        import api

        dataservice = DataService(name=name,container=self)
        dataservice.save()

        serviceauth = Auth(base=dataservice,authname="full")

        serviceauth.save()

        owner_role = Role(rolename="serviceadmin")
        owner_role.setmethods(api.service_admin_methods)
        owner_role.description = "Full control of the service"
        owner_role.save()

        customer_role = Role(rolename="customer")
        customer_role.setmethods(api.service_customer_methods)
        customer_role.description = "Customer Access to the service"
        customer_role.save()

        serviceauth.roles.add(owner_role)
        serviceauth.roles.add(customer_role)

        customerauth = Auth(base=dataservice,authname="customer")
        customerauth.save()

        customerauth.roles.add(customer_role)

        managementproperty = ManagementProperty(property="accessspeed",base=dataservice,value=settings.DEFAULT_ACCESS_SPEED)
        managementproperty.save()

        return dataservice

    def get_rate_for_metric(self, metric):
        if metric == metric_container:
            return 1

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(HostingContainer, self).save()

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)

class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer)
    status    = models.CharField(max_length=200)
    starttime = models.DateTimeField(blank=True)
    endtime   = models.DateTimeField(blank=True)

    def __init__(self, *args, **kwargs):
        super(DataService, self).__init__(*args, **kwargs)
        self.metrics = service_metrics

    def get_rate_for_metric(self, metric):
        if metric == metric_service:
            return 1

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(DataService, self).save()

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage,obj=self.container)

    def create_mfile(self,file,name,fid=None):
        import api
        service = self

        if file==None:
            mfile = MFile(name="Empty File",service=service,empty=True)
        else:
            if type(file) == django.core.files.base.ContentFile:
                mfile = MFile(name=name,service=service)
                mfile.file.save(name, file)
            else:
                mfile = MFile(name=name,service=service,file=file,empty=False)
        mfile.save()

        logging.debug("MFile creation started '%s' "%mfile)
        logging.debug("Creating roles for '%s' "%mfile)

        mfileauth_owner = Auth(base=mfile,authname="owner")
        mfileauth_owner.save()

        owner_role = Role(rolename="owner")
        methods = api.mfile_owner_methods
        owner_role.setmethods(methods)
        owner_role.description = "Owner of the data"
        owner_role.save()

        mfileauth_owner.roles.add(owner_role)

        monitor_role = Role(rolename="monitor")
        methods = api.mfile_monitor_methods
        monitor_role.setmethods(methods)
        monitor_role.description = "Collect usage reports"
        monitor_role.save()

        mfileauth_owner.roles.add(monitor_role)

        mfileauth_monitor = Auth(base=mfile,authname="monitor")
        mfileauth_monitor.save()

        mfileauth_monitor.roles.add(monitor_role)

        mfile.save()
        mfile.post_process()

        logging.debug("Backing up '%s' "%mfile)

        if file is not None:
            if type(file) == django.core.files.base.ContentFile:
                backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum)
                backup.file.save(name, file)
                backup.save()
            else:
                backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
                backup.save()

        return mfile

class MFolder(NamedBase):
    service  = models.ForeignKey(DataService)
    parent   = models.ForeignKey('self',null=True)

    def duplicate(self,name,parent):

        new_mfolder = MFolder(name=name,service=self.service,parent=parent)
        new_mfolder.save()

        for mfile in self.mfile_set.all():
            new_mfile = MFile(name=mfile.name, file=mfile.file, folder=new_mfolder, mimetype=mfile.mimetype, empty=False, service=mfile.service )
            new_mfile.save()

        for submfolder in self.mfolder_set.all():
            new_submfolder = submfolder.duplicate(submfolder.name,new_mfolder)
            new_submfolder.save()

        new_mfolder.save()
        return new_mfolder

    def __unicode__(self):
        return "MFolder: %s " % self.name

    def get_rel_path(self):
        if self.parent is not None:
            return os.path.join(self.parent.get_rel_path(),self.name)
        else:
            return self.name

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(MFolder, self).save()

class MFile(NamedBase):
    # TODO : Add bitmask to MFile for deleted,remote,input,output, etc
    empty    = models.BooleanField(default=False)
    service  = models.ForeignKey(DataService)
    folder   = models.ForeignKey(MFolder,null=True)
    file     = models.FileField(upload_to=utils.create_filename,blank=True,null=True,storage=storage.getdiscstorage())
    mimetype = models.CharField(max_length=200,blank=True,null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    size     = models.IntegerField(default=0)
    thumb    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    poster   = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    proxy    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getproxystorage())
    created  = models.DateTimeField(auto_now_add=True)
    updated  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created','name')

    def __init__(self, *args, **kwargs):
        super(MFile, self).__init__(*args, **kwargs)
        self.metrics = mfile_metrics

    def duplicate(self):
        new_mfile = self.service.create_mfile(self.file)
        new_mfile.save()
        return new_mfile

    def create_read_only_auth(self):
        mfileauth_ro = Auth(base=self,authname="Read Only Auth")
        mfileauth_ro.save()

        ro_role = Role(rolename="ro")
        methods = ["get"]
        ro_role.setmethods(methods)
        ro_role.description = "Read Only"
        ro_role.save()

        mfileauth_ro.roles.add(ro_role)

        self.save()

        return mfileauth_ro

    def post_process(self):
        if self.file:
            # MIME type
            self.mimetype = mimetype = mimefile(self.file.path)
            # checksum
            self.checksum = md5file(self.file.path)
            # record size
            self.size = self.file.size

            thumbpath = os.path.join( str(self.file) + ".thumb.jpg")
            posterpath = os.path.join( str(self.file) + ".poster.jpg")
            proxypath = os.path.join( str(self.file) + ".proxy.ogg")
            fullthumbpath = os.path.join(settings.THUMB_ROOT , thumbpath)
            fullposterpath = os.path.join(settings.THUMB_ROOT , posterpath)
            fullproxypath = os.path.join(settings.THUMB_ROOT , proxypath)
            (thumbhead,tail) = os.path.split(fullthumbpath)
            (posterhead,tail) = os.path.split(fullposterpath)
            (proxyhead,tail) = os.path.split(fullproxypath)

            if not os.path.isdir(thumbhead):
                os.makedirs(thumbhead)

            if not os.path.isdir(posterhead):
                os.makedirs(posterhead)

            if use_celery:
                logging.info("Using CELERY for processing ")
            else:
                logging.info("Processing synchronously (change settings.USE_CELERY to 'True' to use celery)" )

            if mimetype.startswith('video') or self.file.name.endswith('mxf'):
                thumbtask = thumbvideo(self.file.path,fullthumbpath,settings.thumbsize[0],settings.thumbsize[1])
                self.thumb = thumbpath
                postertask = thumbvideo(self.file.path,fullposterpath,settings.postersize[0],settings.postersize[1])
                self.poster = posterpath
                proxytask = proxyvideo(self.file.path,fullproxypath,width=settings.postersize[0],height=settings.postersize[1])
                self.proxy = proxypath

            elif mimetype.startswith('image'):
                logging.info("Creating thumb inprocess for Image '%s' %s " % (self,mimetype))
                thumbtask = thumbimage(self.file.path,fullthumbpath,options={"width":settings.thumbsize[0],"height":settings.thumbsize[1]})
                self.thumb = thumbpath
                postertask = thumbimage(self.file.path,fullposterpath,options={"width":settings.postersize[0],"height":settings.postersize[1]})
                self.poster = posterpath

            elif self.file.name.endswith('blend'):
                logging.info("Creating Blender thumb '%s' %s " % (self,mimetype))
                # TODO : Change to a Preview of a frame of the blend file
                thumbtask = thumbimage("/var/mserve/www-root/mservemedia/images/blender.png",fullthumbpath,options={"width":settings.thumbsize[0],"height":settings.thumbsize[1]})
                self.thumb = thumbpath
            else:
                logging.info("Not creating thumb for '%s' %s " % (self,mimetype))

            self.save()
        
    def get_rel_path(self):
        if self.folder is not None:
            return os.path.join(self.folder.get_rel_path(),self.name)
        else:
            return self.name

    def get_rate_for_metric(self, metric):
        if metric == metric_mfile:
            return 1

    def get_value_for_metric(self, metric):
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

    def proxyurl(self):
        return "%s%s" % (thumbpath,self.proxy)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        self.updated = datetime.datetime.now()
        super(MFile, self).save()

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage,obj=self.service)

def pre_delete_handler( sender, instance=False, **kwargs):
    instance._delete_usage_()

pre_delete.connect(pre_delete_handler, sender=MFile, dispatch_uid="dataservice.models")
pre_delete.connect(pre_delete_handler, sender=DataService, dispatch_uid="dataservice.models")
pre_delete.connect(pre_delete_handler, sender=HostingContainer, dispatch_uid="dataservice.models")

def post_init_handler( sender, instance=False, **kwargs):
    pass

post_init.connect(post_init_handler, sender=MFile, dispatch_uid="dataservice.models")

def post_save_handler( sender, instance=False, **kwargs):
    pass

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

class ManagementProperty(models.Model):
    base        = models.ForeignKey(NamedBase)
    property    = models.CharField(max_length=200)
    value       = models.CharField(max_length=200)

class Auth(Base):
    authname = models.CharField(max_length=50)
    base     = models.ForeignKey(NamedBase, blank=True, null=True)
    parent   = models.ForeignKey('Auth', blank=True, null=True)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(Auth, self).save()

    def __unicode__(self):
        return "Auth: authname=%s base=%s parent=%s" % (self.authname,self.base,self.parent);


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
