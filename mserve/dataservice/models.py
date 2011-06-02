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
import storage
import logging
import datetime
import os
import utils as utils
import settings
from piston.utils import rc
import django.dispatch
from celery.task.sets import TaskSet
from django.shortcuts import redirect
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_init
from django.db.models.signals import pre_delete
from dataservice.tasks import thumbvideo
from dataservice.tasks import proxyvideo
from dataservice.tasks import thumbimage
from dataservice.tasks import mimefile
from dataservice.tasks import md5file

# Declare Signals
mfile_get_signal = django.dispatch.Signal(providing_args=["mfile"])

ID_FIELD_LENGTH = 200
thumbpath = settings.THUMB_PATH
mediapath = settings.MEDIA_URL

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

DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

roles = {}
roles["containeradmin"] = {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls" : {\
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET","PUT"],\
        "usages":["GET"],\
        "services":["GET","POST"],\
        }
    }

roles["serviceadmin"] = {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET","PUT"],\
        "usages":["GET"],\
        "mfiles":["GET","POST","PUT","DELETE"],\
        "jobs":["GET","POST","PUT","DELETE"],\
        "mfolders":["GET","POST","PUT","DELETE"]\
        }
    }

roles["servicecustomer"] = {
    "methods" : ["GET"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "mfiles":["GET","POST","PUT","DELETE"],\
        "jobs":["GET","POST","PUT","DELETE"],\
        "mfolders":["GET","POST","PUT","DELETE"]\
        }
    }
        
roles["mfileowner"] = {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET","PUT","POST","DELETE"],\
        "base":["GET","PUT","POST","DELETE"],\
        }
    }

roles["mfilereadwrite"] = {
    "methods" : ["GET","PUT","POST","DELETE"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET","PUT","POST","DELETE"],\
        "base":["GET"],\
        }
    }

roles["mfilereadonly"] = {
    "methods" : ["GET"],\
    "urls": {
        "auths":["GET","PUT","POST","DELETE"],\
        "properties":["GET"],\
        "usages":["GET"],\
        "file":["GET"],\
        }
    }


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

    def __unicode__(self):
        return "Mserve Profile for '%s' (%s) " % (self.user.get_full_name(),self.user.username)

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

    methods = []
    urls = {
        "auths":[],
        "properties":[],
        "usages":[]
        }

    def getmethods(self):
        return self.methods

    def geturls(self):
        return self.urls

    def get_real_base(self):
        if utils.is_container(self):
            return HostingContainer.objects.get(id=self.id)
        if utils.is_service(self):
            return DataService.objects.get(id=self.id)
        if utils.is_mfile(self):
            return MFile.objects.get(id=self.id)
        if utils.is_mfolder(self):
            return MFolder.objects.get(id=self.id)
        if self.base:
            return self.base.get_real_base()
        if self.parent:
            return self.parent.get_real_base()

        raise Exception("Dont know how to get real base for %s" % (self) )

    def check(self, url , method):
        if url==None:
            if method in self.methods:
                return True,None
            else:
                return False,HttpResponseForbidden()
        else:
            if self.urls.has_key(url):
                if method in self.urls[url]:
                    return True,None
                else:
                    return False,HttpResponseForbidden()
            else:
                return False,HttpResponseNotFound()

    def do(self, method, url=None, *args , **kwargs):

        if url==None:
            logging.info("%s : on %s args=%s kwargs=%s" % (method,self,args,kwargs))
            if method not in ["GET","PUT","POST","DELETE"]:
                return HttpResponseForbidden()
        else:
            logging.info("%s : /%s/ on %s args=%s kwargs=%s" % (method,url,self,args,kwargs))

        passed,error = self.check(url,method)

        if not passed:
            if url:
                logging.info("Exception: %s Cannot do %s: /%s/ on %s urls are %s" % (error.status_code,method,url,self,self.geturls()))
            else:
                logging.info("Exception: %s Cannot do %s: /%s/ on %s methods are %s" % (error.status_code,method,url,self,self.getmethods()))
            return error

        if method=="GET" and url==None:
            return self.get(url)

        if method=="GET" and url=="auths":
            return self.auth_set.all()

        if method=="GET" and url=="usages":
            return self.usages.all()

        if method=="GET" and url=="properties":
            if type(self) == Auth:
                return self.get_real_base().managementproperty_set.all()
            else:
                return self.managementproperty_set.filter(base=self)

        if method=="PUT" and url=="properties":
            for k in kwargs.keys():
                try:
                    mp = self.get_real_base().managementproperty_set.get(base=self, property=k)
                    mp.value = kwargs[k]
                    mp.save()
                except ManagementProperty.DoesNotExist:
                    return HttpResponseNotFound()
            return self.get_real_base().managementproperty_set.all()

        if method=="PUT" and url=="auths":
            if url == "auths":
                for authname in kwargs.keys():
                    try:

                        auth = self.auth_set.get(authname=authname)
                        auth.setroles(kwargs[authname]['roles'])
                        auth.save()
                        logging.info("PUT AUTHS updated auth %s " % (auth))
                        return self.auth_set.all()

                    except Auth.DoesNotExist:
                        logging.info("PUT AUTHS Auth '%s' does not exist "% (authname))
                        return HttpResponseBadRequest()

            return HttpResponseNotFound()

        if method=="POST" and url=="auths":

            if not kwargs.has_key('name') or not kwargs.has_key('roles'):
                return HttpResponseBadRequest()

            if type(self) == Auth:
                auth = Auth(authname=kwargs['name'],parent=self)
                auth.setroles(kwargs['roles'])
                auth.save()
                self.auth_set.add(auth)
                return auth
            else:
                auth = Auth(authname=kwargs['name'],base=self)
                auth.setroles(kwargs['roles'])
                auth.save()
                self.auth_set.add(auth)
                return auth

        if method=="GET":
            return self.get(url,*args,**kwargs)
        if method=="POST":
            return self.post(url,*args,**kwargs)
        if method=="PUT":
            return self.put(url,*args,**kwargs)
        if method=="DELETE":
            if url == None:
                r = self.delete()
                logging.info("DELETE %s" % r)
                return r
            if url == "auths":
                if kwargs.has_key('name'):
                    auth = self.auth_set.get(authname=kwargs['name'])
                    logging.info("DELETE AUTH %s" % auth)
                    auth.delete()
                    r = rc.DELETED
                    r.write("Deleted '%s'"%kwargs['name'])
                    return r
                else:
                    return HttpResponseBadRequest()
            return HttpResponseNotFound()


        logging.info("ERROR: 404 Pattern not matched for %s on %s" % (method,url))

        return rc.NOT_FOUND

    class Meta:
        abstract = True

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
    status      = models.CharField(max_length=200)

    methods = ["GET","POST","PUT","DELETE"]
    urls = {
        "auths":["GET","PUT","POST","DELETE"],
        "properties":["GET","PUT"],
        "usages":["GET"],
        "services":["GET","POST"],
        }

    def __init__(self, *args, **kwargs):
        super(HostingContainer, self).__init__(*args, **kwargs)
        self.metrics = container_metrics

    def get(self,url, *args, **kwargs):
        if url == "services":
            return self.dataservice_set.all()
        if not url:
            return self

    def post(self,url, *args, **kwargs):
        if url == "services":
            return self.create_data_service(kwargs['name'])
        else:
            return None

    def put(self,url, *args, **kwargs):
        logging.info("PUT CONTAINER %s %s %s " % (url, args, kwargs))
        if url == "auths":
            for authname in kwargs.keys():
                try:
                    auth = self.auth_set.get(authname=authname)
                    auth.setmethods(kwargs[authname])
                    auth.save()
                    logging.info("PUT CONTAINER updated auth %s " % (auth))
                    return self.auth_set.all()
                except Auth.DoesNotExist:
                    logging.info("PUT CONTAINER Auth '%s' does not exist "% (authname))
                    return HttpResponseBadRequest()
        return HttpResponseNotFound()

    @staticmethod
    def create_container(name):
        hostingcontainer = HostingContainer(name=name)
        hostingcontainer.save()
        
        managementproperty = ManagementProperty(property="accessspeed",base=hostingcontainer,value=settings.DEFAULT_ACCESS_SPEED)
        managementproperty.save()

        hostingcontainerauth = Auth(base=hostingcontainer,authname="full")
        hostingcontainerauth.setroles(['containeradmin'])
        hostingcontainerauth.save()

        return hostingcontainer

    def create_data_service(self,name):

        dataservice = DataService(name=name,container=self)
        dataservice.save()

        serviceauth = Auth(base=dataservice,authname="full")
        serviceauth.setroles(["serviceadmin"])
        serviceauth.save()

        customerauth = Auth(base=dataservice,authname="customer")
        customerauth.setroles(["servicecustomer"])
        customerauth.save()

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
    starttime = models.DateTimeField(blank=True,null=True)
    endtime   = models.DateTimeField(blank=True,null=True)
    
    methods = ["GET","POST","PUT","DELETE"]
    urls = {
        "auths":["GET","PUT","POST","DELETE"],
        "properties":["GET","PUT"],
        "usages":["GET"],
        "mfiles":["GET","POST"],
        "mfolders":["GET","POST"],
        "jobs":["GET"],
        }

    def __init__(self, *args, **kwargs):
        super(DataService, self).__init__(*args, **kwargs)
        self.metrics = service_metrics

    def get(self,url, *args, **kwargs):
        if url == "mfiles":
            return self.mfile_set.all()
        if url == "mfolders":
            return self.mfolder_set.all()
        if url == "jobs":
            from jobservice.models import Job
            jobs = Job.objects.filter(mfile__in=MFile.objects.filter(service=self).all())
            return jobs
        if not url:
            return self

    def post(self,url, *args, **kwargs):
        # TODO : Folders and Jobs
        logging.info("%s %s " % (args, kwargs))
        if url == "mfiles":
            return self.create_mfile(kwargs['name'],file=kwargs['file'])
        if url == "mfolders":
            return self.create_mfolder(kwargs['name'])
        if url == "jobs":
            return self.create_job(kwargs['name'])
        return HttpResponseNotFound()

    def put(self,url, *args, **kwargs):
        logging.info("PUT SERVICE %s %s %s " % (url, args, kwargs))
        if url == "auths":
            for authname in kwargs.keys():
                try:
                    auth = self.auth_set.get(authname=authname)
                    auth.setmethods(kwargs[authname])
                    auth.save()
                    logging.info("PUT SERVICE updated auth %s " % (auth))
                    return self.auth_set.all()
                except Auth.DoesNotExist:
                    logging.info("PUT SERVICE Auth '%s' does not exist "% (authname))
                    return HttpResponseBadRequest()
        return HttpResponseNotFound()

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

    def create_mfolder(self,name,parent=None):
        try :
            MFolder.objects.get(name=name,service=self,parent=parent)
            r = rc.DUPLICATE_ENTRY
            return r
        except MFolder.DoesNotExist:
            folder = MFolder(name=name,service=self,parent=parent)
            folder.save()
            return folder

    def create_mfile(self,name,file=None,post_process=True):
        service = self

        # Check for duplicates
        done =False
        n=0
        fn,ext = os.path.splitext(name)
        while not done:
            existing_files = MFile.objects.filter(name=name,folder=None,service=service)
            if len(existing_files) == 0:
                done = True
            else:
                n=n+1
                name = "%s-%s%s" % (fn,str(n),ext)

        if file==None:
            emptyfile = ContentFile('')
            mfile = MFile(name=name,service=service,empty=True)
            mfile.file.save(name, emptyfile)
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
        mfileauth_owner.setroles(['mfileowner'])
        mfileauth_owner.save()

        mfile.save()

        logging.debug("Backing up '%s' " % mfile)

        if file is not None:
            if type(file) == django.core.files.base.ContentFile:
                backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum)
                backup.file.save(name, file)
                backup.save()
            else:
                backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
                backup.save()

        if post_process:
            mfile.post_process()

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
    size     = models.BigIntegerField(default=0)
    thumb    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    poster   = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getthumbstorage())
    proxy    = models.ImageField(upload_to=utils.create_filename,null=True,storage=storage.getproxystorage())
    created  = models.DateTimeField(auto_now_add=True)
    updated  = models.DateTimeField(auto_now=True)

    methods = ["GET","POST","PUT","DELETE"]
    urls = {
            "auths":["GET","PUT","POST","DELETE"],
            "properties":[],
            "usages":["GET"],
            "file": ["GET","PUT","DELETE"],
            "jobs":["GET","POST"],
            }

    class Meta:
        ordering = ('-created','name')

    def __init__(self, *args, **kwargs):
        super(MFile, self).__init__(*args, **kwargs)
        self.metrics = mfile_metrics

    def get(self,url, *args, **kwargs):
        if url == "jobs":
            return self.job_set.all()
        elif url == "file":
            # TODO Add Usage here
            #self.usage["disc_access"] = self.usage["disc_access"] + 100
            if self.file:
                return self.__get_file()
            else:
                return HttpResponseNotFound()
        elif url == "" or url == None:
            return self

        return None

    def post(self,url, *args, **kwargs):
        if url == "jobs":
            if kwargs.has_key('name'):
                name = kwargs['name']
                job = self.create_job(name)
                return job
            return HttpResponseBadRequest()
        return None

    def put(self,url, *args, **kwargs):
        if url == "auths":
            for authname in kwargs.keys():
                try:
                    auth = self.auth_set.get(authname=authname)
                    auth.setmethods(kwargs[authname])
                    auth.save()
                    return self.auth_set.all()
                except Auth.DoesNotExist:
                    return HttpResponseBadRequest()
        if url == None:
            if kwargs.has_key('file'):
                file = kwargs['file']
                if type(file) == django.core.files.base.ContentFile:
                    self.file.save(self.name, file)
                else:
                    mfile.file=file
                self.save()
                self.post_process()
                return self
            return HttpResponseBadRequest()
        return HttpResponseNotFound()

    def __get_file(self):
        mfile = self

        # Access Speed default is unlimited
        accessspeed = ""

        service = mfile.service
        container = service.container
        logging.info("Finding limit for %s " % (mfile.name))
        accessspeed = DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (accessspeed,mfile.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (accessspeed,mfile.name))
            except ObjectDoesNotExist:
                pass
            

        check1 = mfile.checksum
        check2 = utils.md5_for_file(mfile.file)

        file=mfile.file

        sigret = mfile_get_signal.send(sender=self, mfile=mfile)

        for k,v in sigret:
            logging.info("Signal %s returned %s " % (k,v))

        import usage_store as usage_store
        if(check1==check2):
            logging.info("Verification of %s on read ok" % mfile)
        else:
            logging.info("Verification of %s on read FAILED" % mfile)
            usage_store.record(mfile.id,metric_corruption,1)
            backup = BackupFile.objects.get(mfile=mfile)
            check3 = mfile.checksum
            check4 = utils.md5_for_file(backup.file)
            if(check3==check4):
                shutil.copy(backup.file.path, mfile.file.path)
                file = backup.file
            else:
                logging.info("The file %s has been lost" % mfile)
                usage_store.record(mfile.id,metric_dataloss,mfile.size)
                return rc.NOT_HERE

        file=mfile.file

        mfile_get_signal.send(sender=self, mfile=mfile)

        p = str(file)
        dlfoldername = "dl%s" % accessspeed

        redirecturl = utils.gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = file.path

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            logging.info("Linking ")
            logging.info("   %s " % mfilefilepath )
            logging.info("to %s " % fullfilepath )
            os.link(mfilefilepath,fullfilepath)

        import dataservice.models as models
        
        usage_store.record(mfile.id,models.metric_access,mfile.size)

        response = redirect("/%s"%redirecturl)
        return response

    def create_job(self,name):
        from jobservice.models import Job
        job = Job(name=name,mfile=self)
        job.save()
        return job

    def duplicate(self):
        new_mfile = self.service.create_mfile(self.name,file=self.file)
        new_mfile.save()
        return new_mfile

    def create_read_only_auth(self):
        mfileauth_ro = Auth(base=self,authname="%s Read Only"%self)
        mfileauth_ro.setroles(["mfilereadonly"])
        mfileauth_ro.save()
        return mfileauth_ro

    def post_process(self):
        if self.file:

            from jobservice.models import Job

            job = Job(name="%s Ingest Job"%(self.name),mfile=self)
            job.save()

            # MIME type
            self.mimetype = mimetype = mimefile([self.file.path],[],{})

            # checksum
            self.checksum = md5file([self],[],{})

            # record size
            self.size = self.file.size            
            self.save()

            thumbpath = os.path.join( str(self.file) + ".thumb.jpg")
            posterpath = os.path.join( str(self.file) + ".poster.jpg")
            proxypath = os.path.join( str(self.file) + ".proxy.m4v")
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

            tasks = []

            if mimetype.startswith('video') or self.file.name.endswith('mxf'):

                th_options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                thumbtask = thumbvideo.subtask([[self.file.path],[fullthumbpath],th_options ])
                self.thumb = thumbpath

                po_options = {"width":settings.postersize[0],"height":settings.postersize[1]}
                postertask = thumbvideo.subtask([[self.file.path],[fullposterpath],po_options])
                self.poster = posterpath

                proxytask = proxyvideo.subtask([[self.file.path],[fullproxypath],po_options])
                self.proxy = proxypath
                tasks.extend([thumbtask,postertask,proxytask])

            elif mimetype.startswith('image'):
                logging.info("Creating thumb inprocess for Image '%s' %s " % (self,mimetype))
                th_options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                thumbtask = thumbimage.subtask([[self.file.path],[fullthumbpath],th_options])
                self.thumb = thumbpath

                po_options = {"width":settings.postersize[0],"height":settings.postersize[1]}
                postertask = thumbimage.subtask([[self.file.path],[fullposterpath],po_options])
                self.poster = posterpath
                tasks.extend([thumbtask,postertask])

            elif self.file.name.endswith('blend'):
                logging.info("Creating Blender thumb '%s' %s " % (self,mimetype))
                # TODO : Change to a Preview of a frame of the blend file
                th_options = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                blender_path = os.path.join(settings.MEDIA_ROOT,"images/blender.png")
                thumbtask = thumbimage.subtask([[blender_path],[fullthumbpath],th_options])
                self.thumb = thumbpath
                tasks.extend([thumbtask])
            else:
                logging.info("Not creating thumb for '%s' %s " % (self,mimetype))

            ts = TaskSet(tasks=tasks)
            tsr = ts.apply_async()
            tsr.save()

            job.taskset_id=tsr.taskset_id
            job.save()

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
        if self.thumb and self.thumb != "":
            return "%s%s" % (thumbpath,self.thumb)
        else:
            if self.mimetype:
                if self.mimetype.startswith("image"):
                    return os.path.join(mediapath,"images","image-x-generic.png")
                if self.mimetype.startswith("text"):
                    return os.path.join(mediapath,"images","text-x-generic.png")
        return os.path.join(mediapath,"images","package-x-generic.png")

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

    def values(self):
        if self.property == "accessspeed":
            return {"type" : "step", "min":50 , "max" : 5000, "step" : 50}
        elif self.property == "anotherprop":
            return {"type" : "enum", "choices" : ["This","That"] }
        else:
            return {}

class Auth(Base):
    authname    = models.CharField(max_length=50)
    base        = models.ForeignKey(NamedBase, blank=True, null=True)
    parent      = models.ForeignKey('Auth', blank=True, null=True)
    usages      = models.ManyToManyField("Usage")
    roles_csv   = models.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(Auth, self).__init__(*args, **kwargs)

    def geturls(self):
        urls = {}
        for rolename in self.getroles():
            urls.update(roles[rolename]['urls'])
        return urls

    def getroles(self):
        return self.roles_csv.split(",")

    def setroles(self,new_roles):
        for rolename in new_roles:
            if rolename not in roles.keys():
                raise Exception("Rolename '%s' not valid " %rolename)
        self.roles_csv = ",".join(new_roles)

    def getmethods(self):
        methods = []
        for rolename in self.getroles():
            methods = methods + roles[rolename]['methods']
        return methods

    def check(self, url, method):
        if url==None:
            if self.base:
                if method in self.getmethods() and self.base.get_real_base().check(url,method):
                    return True,None
                else:
                    return False,HttpResponseForbidden()
            else:
                if method in self.getmethods() and self.parent.get_real_base().check(url,method):
                    return True,None
                else:
                    return False,HttpResponseForbidden()
        else:
            if self.base:
                passed=False
                if url != "base":
                    passed,error = self.base.get_real_base().check(url,method)
                else:
                    passed = True

                if self.geturls().has_key(url)\
                and method in self.geturls()[url]\
                and passed:
                    return True,None
                else:
                    return False,HttpResponseForbidden()
            else:
                passed,error = self.parent.get_real_base().check(url,method)

                if self.geturls().has_key(url)\
                and method in self.geturls()[url]\
                and passed:
                    return True,None
                else:
                    return False,HttpResponseForbidden()

    def get(self,url, *args, **kwargs):
        logging.info("AUTH %s %s " % (self,url) )
        if not url:
            return self
        if url == "base":
            if utils.is_mfile(self.base):
                mfile = MFile.objects.get(id=self.base.id)
                return utils.clean_mfile(mfile)
        return self.base.get_real_base().do("GET",url)

    def put(self,url, *args, **kwargs):
        return self.get_real_base().do("PUT",url, *args, **kwargs)

    def post(self,url, *args, **kwargs):
        return self.get_real_base().do("POST",url, *args, **kwargs)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        if not self.roles_csv:
            self.roles_csv = ""
        super(Auth, self).save()

    def __unicode__(self):
        return "Auth: authname=%s base=%s roles=%s " % (self.authname,self.base,self.getroles());
        if self.base:
            return "Auth: authname=%s base=%s methods=%s urls=%s" % (self.authname,self.base,self.getmethods(),self.geturls());
        elif self.parent:
            return "Auth: authname=%s parent=%s methods=%s urls=%s" % (self.authname,self.parent.authname,self.getmethods(),self.geturls());
        else:
            return "Auth: authname=%s No Base/Parent methods=%s urls=%s" % (self.authname,self.getmethods(),self.geturls());