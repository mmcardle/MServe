"""The Mserve dataservice models """
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

import storage
import logging
import datetime
import time
import os
import shutil
import utils as utils
import static as static
import django.dispatch
import settings
from tasks import continue_workflow_taskset
from piston.utils import rc
from django.db import models
from celery.task.sets import TaskSet
from celery.task.sets import subtask
from celery.registry import tasks
from djcelery.models import TaskState
from django.http import HttpResponseNotFound
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.db.models.signals import post_init
from django.db.models.signals import pre_delete
from django.core.urlresolvers import reverse
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.db.models import Count, Max, Min, Avg, Sum, StdDev, Variance
from dataservice.tasks import mimefile

# Declare Signals
MFILE_GET_SIGNAL = django.dispatch.Signal(providing_args=["mfile"])

FILE_FIELD_LENGTH = 400
ID_FIELD_LENGTH = 200
SLEEP_TIME = 10  # in seconds
SLEEP_TIMEOUT = 300  # in seconds

# Metrics for objects
METRIC_MFILE = "http://mserve/file"
METRIC_BACKUPFILE = "http://mserve/backupfile"
METRIC_CONTAINER = "http://mserve/container"
METRIC_SERVICE = "http://mserve/service"

# Metrics for mfiles
METRIC_DISC = "http://mserve/disc"
METRIC_DISC_SPACE = "http://mserve/disc_space"
METRIC_INGEST = "http://mserve/ingest"
METRIC_ACCESS = "http://mserve/access"
METRIC_ARCHIVED = "http://mserve/archived"
METRIC_CORRUPTION = "http://mserve/corruption"
METRIC_DATALOSS = "http://mserve/dataloss"

# Metrics for jobs
METRIC_JOBRUNTIME = "http://mserve/jobruntime"
METRIC_JOBTASK = "http://mserve/task/"

METRICS = [METRIC_MFILE, METRIC_SERVICE, METRIC_CONTAINER, METRIC_DISC,
        METRIC_DISC_SPACE, METRIC_INGEST, METRIC_ACCESS, METRIC_ARCHIVED]

# What metric are reported fro each type
CONTAINER_METRICS = METRICS
SERVICE_METRICS = [METRIC_MFILE, METRIC_SERVICE, METRIC_DISC, METRIC_ARCHIVED,
        METRIC_DISC_SPACE, METRIC_JOBRUNTIME]
MFILE_METRICS = [METRIC_MFILE, METRIC_DISC, METRIC_INGEST, METRIC_ACCESS,
        METRIC_ARCHIVED, METRIC_DISC_SPACE]
BACKUPFILE_METRICS = [METRIC_ARCHIVED, METRIC_BACKUPFILE, METRIC_DISC_SPACE]

# Other Metric groups
BYTE_METRICS = [METRIC_DISC_SPACE]

DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED
DEFAULT_PROFILE = "default"

TASK_CHOICES = []

#from celery.registry import tasks
for task in tasks.regular().keys():
    TASK_CHOICES.append((task, task))


class MServeProfile(models.Model):
    '''A Profile for a MServe user '''
    user = models.ForeignKey(User, unique=True)
    bases = models.ManyToManyField('NamedBase', related_name='bases',
        null=True, blank=True)
    auths = models.ManyToManyField('Auth', related_name='profileauths',
        null=True, blank=True)

    def myauths(self):
        '''Returns a users auths'''
        ret = []
        for auth in self.auths.all():
            ret.append(Auth.objects.get(id=auth.id))
        return set(ret)

    def mfiles(self):
        '''Returns a users mfiles'''
        ret = []
        for base in self.bases.all():
            if utils.is_mfile(base):
                ret.append(MFile.objects.get(id=base.id))
        for auth in self.auths.all():
            if utils.is_service(auth.base):
                dataservice = DataService.objects.get(id=auth.base.id)
                for mfile in dataservice.mfile_set.all():
                    ret.append(mfile)
        return set(ret)

    def dataservices(self):
        '''Returns a users data services'''
        ret = []
        for base in self.bases.all():
            if utils.is_service(base):
                ret.append(DataService.objects.get(id=base.id))
        return set(ret)

    def mfolders(self):
        '''Returns a users mfolders'''
        ret = []
        for base in self.bases.all():
            if utils.is_mfolder(base):
                ret.append(MFolder.objects.get(id=base.id))
        for auth in self.auths.all():
            if utils.is_service(auth.base):
                ret.append(DataService.objects.get(id=auth.base.id))
        return set(ret)

    def containers(self):
        '''Returns a users containers'''
        ret = []
        for base in self.bases.all():
            if utils.is_container(base):
                ret.append(HostingContainer.objects.get(id=base.id))
        return set(ret)

    def __unicode__(self):
        return "Mserve Profile for '%s' (%s) " % (self.user.get_full_name(),
            self.user.username)

SERVICEREQUEST_STATES = (
    ('P', 'PENDING'),
    ('A', 'ACCEPTED'),
    ('R', 'REJECTED'),
)


class ServiceRequest(models.Model):
    name = models.CharField(max_length=200)
    reason = models.TextField()
    profile = models.ForeignKey('MServeProfile', null=True, blank=True,
                                        related_name="servicerequests")
    state = models.CharField(max_length=1, choices=SERVICEREQUEST_STATES,
        default='P')
    time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-time"]

    def ctime(self):
        return self.time.ctime()

    def status(self):
        for index, word in SERVICEREQUEST_STATES:
            if index == self.state:
                return word
        return "unknown"

    def __unicode__(self):
        return self.name


class Usage(models.Model):
    '''The base object this report refers to'''
    base = models.ForeignKey('NamedBase', null=True, blank=True)
    '''The metric this report is recording'''
    metric = models.CharField(max_length=4096)
    '''Time first recorded (shouldnt change)'''
    time = models.DateTimeField(auto_now_add=True)
    '''Number of reports'''
    reports = models.BigIntegerField(default=0)
    '''Sum of report values'''
    total = models.FloatField(default=0)
    '''Sum of squares of values'''
    squares = models.FloatField(default=0)
    '''Sum of squares of values'''
    nInProgress = models.BigIntegerField(default=0)
    '''Time the rate last changed'''
    rateTime = models.DateTimeField()
    '''The current rate (change in value per second)'''
    rate = models.FloatField()
    '''Cumulative unreported usage before rateTime'''
    rateCumulative = models.FloatField()

    @staticmethod
    def get_full_usagesummary():
        usages = Usage.objects.all()
        usagesummary = Usage.usages_to_summary(usages)
        from jobservice.models import Job
        usagesummary.extend(Usage.get_job_usagesummary(Job.objects.all()))
        return usagesummary

    @staticmethod
    def aggregate(usages):
        import usage_store as usage_store
        for usage in usages:
            if usage.nInProgress > 0:
                usage_store._update_usage(usage)

        return usages.values('metric') \
                .annotate(reports=Count('reports')) \
                .annotate(total=Sum('total')) \
                .annotate(squares=Sum('squares')) \
                .annotate(nInProgress=Sum('nInProgress')) \
                .annotate(rate=Sum('rate')) \
                .annotate(rateTime=Max('rateTime')) \
                .annotate(rateCumulative=Sum('rateCumulative'))

    @staticmethod
    def usages_to_summary(usages):
        summary = []
        if not settings.DATABASES['default']['ENGINE'].endswith("sqlite3"):
            summary += usages.values('metric') \
                .annotate(n=Count('total')) \
                .annotate(avg=Avg('total')) \
                .annotate(max=Max('total')) \
                .annotate(min=Min('total')) \
                .annotate(sum=Sum('total')) \
                .annotate(stddev=StdDev('total'))\
                .annotate(variance=Variance('total'))

        else:
            # sqlite3 - No built-in variance and std deviation
            summary += usages.values('metric') \
                .annotate(sum=Sum('rate'))\
                .annotate(sum=Sum('rateCumulative'))
        return summary

    @staticmethod
    def get_job_usagesummary(jobs):
        from jobservice.models import Job
        from jobservice.models import JobASyncResult

        asyncs = JobASyncResult.objects.filter(job__in=jobs).values_list("async_id",flat=True)
        taskstates = TaskState.objects.filter(task_id__in=asyncs)

        jobtype_usage = taskstates.values("name").annotate(
            n=Count('id'),
            avg=Avg('runtime'),
            sum=Sum('runtime'),
            max=Max('runtime'),
            min=Min('runtime'),
            stddev=StdDev('runtime'),
            variance=Variance('runtime'))

        for jobtype in jobtype_usage:
            if jobtype["name"]:
                jobtype["metric"] = METRIC_JOBTASK + jobtype["name"]
            else:
                jobtype["metric"] = METRIC_JOBTASK + "unknown"

        jobtype_success_usage = taskstates.filter(state="SUCCESS")\
            .values("name").annotate(
                n=Count('id'),
                avg=Avg('runtime'),
                sum=Sum('runtime'),
                max=Max('runtime'),
                min=Min('runtime'),
                stddev=StdDev('runtime'),
                variance=Variance('runtime'))

        for jobtype in jobtype_success_usage:
            if jobtype["name"]:
                jobtype["metric"] = METRIC_JOBTASK + jobtype["name"]\
                                    + "/success/"
            else:
                jobtype["metric"] = METRIC_JOBTASK + "unknown/success/"

        jobtype_failed_usage = taskstates.filter(state="FAILURE")\
            .values("name").annotate(
                n=Count('id'),
                avg=Avg('runtime'),
                sum=Sum('runtime'),
                max=Max('runtime'),
                min=Min('runtime'),
                stddev=StdDev('runtime'),
                variance=Variance('runtime'))

        for jobtype in jobtype_failed_usage:
            if jobtype["name"]:
                jobtype["metric"] = METRIC_JOBTASK + jobtype["name"]\
                                        + "/failed/"
            else:
                jobtype["metric"] = METRIC_JOBTASK + "unknown/failed/"

        runtime_usage = taskstates.aggregate(
            n=Count('id'),
            avg=Avg('runtime'),
            sum=Sum('runtime'),
            max=Max('runtime'),
            min=Min('runtime'),
            stddev=StdDev('runtime'),
            variance=Variance('runtime'))
        runtime_usage["metric"] = METRIC_JOBRUNTIME

        runtime_usage_success = taskstates.filter(state="SUCCESS").aggregate(
            n=Count('id'),
            avg=Avg('runtime'),
            sum=Sum('runtime'),
            max=Max('runtime'),
            min=Min('runtime'),
            stddev=StdDev('runtime'),
            variance=Variance('runtime'))
        runtime_usage_success["metric"] = METRIC_JOBRUNTIME + "/success/"

        runtime_usage_failed = taskstates.filter(state="FAILURE").aggregate(
            n=Count('id'),
            avg=Avg('runtime'),
            sum=Sum('runtime'),
            max=Max('runtime'),
            min=Min('runtime'),
            stddev=StdDev('runtime'),
            variance=Variance('runtime'))
        runtime_usage_failed["metric"] = METRIC_JOBRUNTIME + "/failed/"

        summary = []
        summary.extend(jobtype_usage)
        summary.extend(jobtype_success_usage)
        summary.extend(jobtype_failed_usage)
        summary.append(runtime_usage)
        summary.append(runtime_usage_success)
        summary.append(runtime_usage_failed)
        return summary

    def save(self):
        super(Usage, self).save()

    def fmt_ctime(self):
        return self.created.ctime()

    def fmt_rtime(self):
        return self.rateTime.ctime()

    def copy(self, base, save=False):
        newusage = Usage(base=base, metric=self.metric, total=self.total,
                    reports=self.reports, nInProgress=self.nInProgress,
                    rate=self.rate, rateTime=self.rateTime,
                    rateCumulative=self.rateCumulative)
        if save:
            newusage.save()
        return newusage

    def __unicode__(self):
        object = ""
        if self.base:
            object = self.base
        return "Usage:%s metric=%s total=%f reports=%s nInProgress=%s rate=%s \
                    rateTime=%s rateCumulative=%s"\
                    % (object, self.metric, self.total, self.reports,
                        self.nInProgress, self.rate, self.rateTime,
                        self.rateCumulative)


class Base(models.Model):
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)

    methods = []
    urls = {
        "auths": [],
        "properties": [],
        "usages": []}

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

        raise Exception("Dont know how to get real base for %s" % (self))

    def _usages_to_summary(self, usages):
        return Usage.usages_to_summary(usages)

    def check(self, url, method):
        if url == None:
            if method in self.methods:
                return True, None
            else:
                return False, HttpResponseForbidden()
        else:
            if url in self.urls:
                if method in self.urls[url]:
                    return True, None
                else:
                    return False, HttpResponseForbidden()
            else:
                return False, HttpResponseNotFound()

    def do(self, method, url=None, *args, **kwargs):
        if url == None:
            if method not in ["GET", "PUT", "POST", "DELETE"]:
                return HttpResponseForbidden()

        passed, error = self.check(url, method)

        if not passed:
            if url:
                logging.info("Exception: %s Cannot do %s: /%s/ on %s urls are \
                                %s", error.status_code, method, url, \
                                self.get_real_base(),\
                                ",".join(self.geturls()))
            else:
                logging.info("Exception: %s Cannot do %s: /%s/ on %s methods \
                                are %s", error.status_code, method, url, \
                                self.get_real_base(),\
                                ",".join(self.getmethods()))
            return error

        if method == "GET" and url == None:
            return self.get(url)

        if method == "GET" and url == "auths":
            return self.auth_set.all()

        if method == "GET" and url == "usages":
            logging.info("check for full usage %s", kwargs)

            base = self.get_real_base()
            if 'last' in kwargs:
                last = int(kwargs.get('last')[0])
                logging.info("last usage seen %s", last)
                if last is not -1:
                    count = 0
                    while last == base.reportnum:
                        logging.debug("Waiting for new usage lastreport=%s",
                                        last)

                        time.sleep(SLEEP_TIME)
                        count += 1
                        if count * SLEEP_TIME >= SLEEP_TIMEOUT:
                            logging.debug("Usage timeout reached, aborting.")
                            return HttpResponseBadRequest()
                        base = NamedBase.objects.get(id=base.id)

            usages = []
            if 'full' in kwargs:
                values = kwargs.get('full')

                if 'true' in values or 'True' in values:
                    logging.info("full usage true")
                    import usage_store
                    usages = self.get_usage()

                    usages = usages
                else:
                    usages = base.usages.all()
            else:
                usages = base.usages.all()
                
            if 'aggregate' in kwargs:
                values = kwargs.get('aggregate')
                if 'true' in values or 'True' in values:
                    usages = Usage.aggregate(usages)

            usageresult = {}
            usageresult["usages"] = usages
            usageresult["reportnum"] = base.reportnum
            return usageresult

        if method == "GET" and url == "properties":
            if type(self) == Auth:
                return self.get_real_base().managementproperty_set.all()
            else:
                return self.managementproperty_set.filter(base=self)

        if method == "PUT" and url == "properties":
            for k in kwargs.keys():
                try:
                    mp = self.get_real_base()\
                        .managementproperty_set.get(
                            base=self, property=k)
                    mp.value = kwargs[k]
                    mp.save()
                except ManagementProperty.DoesNotExist:
                    return HttpResponseNotFound()
            return self.get_real_base().managementproperty_set.all()

        if method == "PUT" and url == "auths":
            if "request" in kwargs:
                for authname in kwargs["request"].POST.keys():
                    try:
                        auth = self.auth_set.get(authname=authname)
                        roles = kwargs["request"].POST[authname]['roles']
                        auth.setroles(roles.split(","))
                        auth.save()
                        logging.info("PUT AUTHS updated auth %s ",
                                        auth.authname)
                        return self.auth_set.all()
                    except Auth.DoesNotExist:
                        logging.info("PUT AUTHS Auth '%s' does not exist ",
                                        authname)
                        return HttpResponseBadRequest()

            return HttpResponseNotFound()

        if method == "POST" and url == "auths":
            if "request" in kwargs:
                request_args = kwargs["request"].POST
                if not 'name' in request_args or not 'roles' in request_args:
                    return HttpResponseBadRequest()

                name = request_args['name']
                roles = request_args['roles'].split(',')
                if type(self) == Auth:
                    auth = Auth(authname=name, parent=self)
                    auth.setroles(roles)
                    auth.save()
                    self.auth_set.add(auth)
                    return auth
                else:
                    auth = Auth(authname=name, base=self)
                    auth.setroles(roles)
                    auth.save()
                    self.auth_set.add(auth)
                    return auth
            else:
                return HttpResponseBadRequest()
        if method == "GET":
            return self.get(url, *args, **kwargs)
        if method == "POST":
            return self.post(url, *args, **kwargs)
        if method == "PUT":
            return self.put(url, *args, **kwargs)
        if method == "DELETE":
            if url == None:
                self.delete()
                r = rc.DELETED
                return r
            if url == "auths":
                if 'request' in kwargs:
                    if 'name' in kwargs["request"].POST:
                        name = kwargs["request"].POST["name"]
                        auth = self.auth_set.get(authname=name)
                        logging.info("DELETE AUTH %s", auth.authname)
                        auth.delete()
                        r = rc.DELETED
                        r.write("Deleted '%s'" % name)
                        return r
                    else:
                        return HttpResponseBadRequest()
                else:
                    return HttpResponseBadRequest()
            return HttpResponseNotFound()

        logging.info("ERROR: 404 Pattern not matched for %s on %s",\
                        method, url)

        return rc.NOT_FOUND

    def clean_base(self, authid):
        logging.info("Override this clean method %s", self)
        dict = {}
        return dict

    class Meta:
        abstract = True


class NamedBase(Base):
    metrics = []
    initial_usage_recorded = models.BooleanField(default=False)
    name = models.CharField(max_length=200)
    usages = models.ManyToManyField("Usage")
    reportnum = models.IntegerField(default=1)

    def save(self):
        super(NamedBase, self).save()
        if not self.initial_usage_recorded:
            logging.info("Processing %s ", self)
            import usage_store as usage_store
            startusages = []
            for metric in self.metrics:
                #logging.info("Processing metric %s" %metric)
                #  Recored Initial Values
                v = self.get_value_for_metric(metric)
                if v is not None:
                    logging.info("Value for %s is %s", metric, v)
                    logging.info("Recording usage for metric %s value= %s",
                                    metric, v)
                    usage = usage_store.record(self.id, metric, v)
                    startusages.append(usage)
                # Start recording initial rates
                r = self.get_rate_for_metric(metric)
                if r is not None:
                    logging.info("Rate for %s is %s", metric, r)
                    logging.info("Recording usage rate for metric %s value %s",
                                    metric, r)
                    usage = usage_store.startrecording(self.id, metric, r)
                    startusages.append(usage)

            self.usages = startusages
            self.reportnum = 1
            self.initial_usage_recorded = True
            super(NamedBase, self).save()
        else:
            self.update_usage()

    def update_usage(self):
        import usage_store as usage_store
        for metric in self.metrics:
            #logging.info("Processing metric %s" %metric)
            #  Recorded updated values
            v = self.get_updated_value_for_metric(metric)

            if v is not None:
                logging.info("Value for %s is %s", metric, v)
                logging.info("Recording usage for metric %s value= %s", \
                                metric, v)
                usage = usage_store.update(self.id, metric, v)
            # recording updated rates
            r = self.get_updated_rate_for_metric(metric)
            if r is not None:
                logging.info("Rate for %s is %s", metric, r)
                logging.info("Recording usage rate for metric %s value= %s",
                                metric, r)
                usage = usage_store.updaterecording(self.id, metric, r)

        super(NamedBase, self).save()

    def get_value_for_metric(self, metric):
        '''Override this method to report usage for metric'''
        return None

    def get_rate_for_metric(self, metric):
        '''Override this method to report usage for metric'''
        return None

    def get_updated_value_for_metric(self, metric):
        '''Override this method to report usage for metric'''
        return None

    def get_updated_rate_for_metric(self, metric):
        '''Override this method to report usage for metric'''
        return None

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)

    def __unicode__(self):
        return self.name


class HostingContainer(NamedBase):
    status = models.CharField(max_length=200)
    default_profile = models.CharField(max_length=200, blank=True, null=True)
    default_path = models.CharField(max_length=200, blank=True, null=True)

    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {"auths": ["GET", "PUT", "POST", "DELETE"],
        "properties": ["GET", "PUT"],
        "usages": ["GET"],
        "services": ["GET", "POST"]}

    def __init__(self, *args, **kwargs):
        super(HostingContainer, self).__init__(*args, **kwargs)
        self.metrics = CONTAINER_METRICS

    def thumbs(self):
        thumbs = []
        for service in self.dataservice_set.all()[:4]:
            for mfile in service.mfile_set.exclude(thumb__exact='')[:4]:
                thumbs.append(mfile.thumburl())
        for i in range(len(thumbs), 16):
            thumbs.append(os.path.join(settings.MEDIA_URL,
                            "images", "package-x-generic.png"))
        return thumbs

    def get(self, url, *args, **kwargs):
        if url == "services":
            return self.dataservice_set.all()
        if not url:
            return self

    def post(self, url, *args, **kwargs):
        if url == "services":
            return self.create_data_service(kwargs['name'])
        else:
            return None

    def put(self, url, *args, **kwargs):
        logging.info("PUT CONTAINER %s %s", url, args)
        if url == None:
            from forms import HostingContainerForm
            form = HostingContainerForm(kwargs["request"].POST,instance=self)
            if form.is_valid():
                hostingcontainer = form.save()
                return hostingcontainer
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request! ")
                return r
        return HttpResponseNotFound()

    def get_usage(self):
        serviceids = [service.id for service in self.dataservice_set.all()]
        mfileids = [mfile.id for service in self.dataservice_set.all()
                            for mfile in service.mfile_set.all()]
        jobids = [job.id for service in self.dataservice_set.all()
                            for job in service.jobs()]
        ids = serviceids + mfileids + jobids + [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return usages

    def get_usage_summary(self):
        from jobservice.models import Job
        serviceids = [service.id for service in self.dataservice_set.all()]
        mfileids = [mfile.id for service in self.dataservice_set.all()
                            for mfile in service.mfile_set.all()]
        jobids = [job.id for service in self.dataservice_set.all()
                            for job in service.jobs()]
        ids = serviceids + mfileids + jobids + [self.id]
        usages = Usage.objects.filter(base__in=ids)
        summary = self._usages_to_summary(usages)
        summary.extend(Usage.get_job_usagesummary(
                    Job.objects.filter(id__in=jobids)))
        return summary

    def jobs(self):
        from jobservice.models import Job
        dataservices = self.dataservice_set.all()
        mfiles = MFile.objects.filter(service__in=dataservices).all()
        return Job.objects.filter(mfile__in=mfiles)

    @staticmethod
    def create_container(name):
        hostingcontainer = HostingContainer(name=name)
        hostingcontainer.save()
        managementproperty = ManagementProperty(property="accessspeed", \
                base=hostingcontainer, value=settings.DEFAULT_ACCESS_SPEED)
        managementproperty.save()

        hostingcontainerauth = Auth(base=hostingcontainer, authname="full")
        hostingcontainerauth.setroles(['containeradmin'])
        hostingcontainerauth.save()

        return hostingcontainer

    def create_data_service(self, name):

        dataservice = DataService(name=name, container=self)
        dataservice.save()

        serviceauth = Auth(base=dataservice, authname="full")
        serviceauth.setroles(["serviceadmin"])
        serviceauth.save()

        customerauth = Auth(base=dataservice, authname="customer")
        customerauth.setroles(["servicecustomer"])
        customerauth.save()

        managementproperty = ManagementProperty(property="accessspeed",
                                        base=dataservice,
                                        value=settings.DEFAULT_ACCESS_SPEED)
        managementproperty.save()

        pr = DEFAULT_PROFILE
        if self.default_profile != None and self.default_profile != "":
            pr = self.default_profile

        managementproperty = ManagementProperty(property="profile",
                                                base=dataservice, value=pr)
        managementproperty.save()

        for profile_name in static.default_profiles.keys():
            profile = static.default_profiles[profile_name]
            dsp = DataServiceProfile(service=dataservice, name=profile_name)
            dsp.save()

            ks = profile.keys()
            ks.sort()
            for workflow_name in ks:
                workflow = profile[workflow_name]
                wf = DataServiceWorkflow(profile=dsp, name=workflow_name)
                wf.save()

                tasksets = workflow['tasksets']
                workflow['tasksets']

                dstaskset = None
                prev = None
                order = 0
                for taskset in tasksets:
                    tsname = taskset['name']
                    dstaskset = DataServiceTaskSet(name=tsname, workflow=wf, order=order)
                    dstaskset.save()
                    order = order +1
                    if prev:
                        prev.next = dstaskset
                        prev.save()

                    tasks = taskset['tasks']
                    for task in tasks:
                        task_name = task['task']
                        name = task['name']
                        condition = ""
                        if 'condition' in task:
                            condition = task['condition']
                        args = ""
                        if 'args' in task:
                            args = task['args']
                        dst = DataServiceTask(name=name, taskset=dstaskset,
                                                task_name=task_name,
                                                condition=condition, args=args)
                        dst.save()
                        logging.info(dst)
                    prev = dstaskset


        return dataservice

    def get_rate_for_metric(self, metric):
        if metric == METRIC_CONTAINER:
            return 1

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(HostingContainer, self).save()

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)


class DataServiceProfile(models.Model):
    service = models.ForeignKey('DataService', related_name="profiles")
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return "Profile %s for %s" % (self.name, self.service.name)


class DataServiceWorkflow(models.Model):
    profile = models.ForeignKey(DataServiceProfile, related_name="workflows")
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "Workflow %s for %s" % (self.name, self.profile.name)

    def create_workflow_job(self, mfileid):
        initial = self.tasksets.get(order=0)
        if initial is None:
            raise Exception("Workflow has no initial taskset to run")
        return self.continue_workflow_job(mfileid, initial.id)

    def continue_workflow_job(self, mfileid, taskid):

        task = self.tasksets.get(id=taskid)
        if task is None:
            raise Exception("Workflow %s has no taskset to run", self.name)

        mfile = MFile.objects.get(id=mfileid)
        from mserve.jobservice.models import Job
        jobname = "Workflow %s - Task %s" % (self.name, task.name)
        job = Job(name=jobname, mfile=mfile)
        job.save()
        tsr = task.create_workflow_taskset(mfileid, job)
        job.taskset_id = tsr.taskset_id
        job.save()

        try:
            nexttask = self.tasksets.filter(order__gt=task.order).order_by("order")[0]
            continue_workflow_taskset.delay(mfileid, job.id, nexttask.id )
        except ObjectDoesNotExist:
            logging.info("Last job %s in workflow running", task.order)
        return job


class DataServiceTaskSet(models.Model):
    name = models.CharField(max_length=200)
    workflow = models.ForeignKey(DataServiceWorkflow, related_name="tasksets")
    order = models.IntegerField()

    class Meta:
        ordering = ["order"]

    def create_workflow_taskset(self, mfileid, job):
        in_tasks = filter(lambda t : t != None , [task.create_workflow_task(mfileid, job) for task in self.tasks.all()])
        ts = TaskSet(tasks=in_tasks)
        tsr = ts.apply_async()
        tsr.save()
        return tsr


class DataServiceTask(models.Model):
    name = models.CharField(max_length=200)
    taskset = models.ForeignKey(DataServiceTaskSet, related_name="tasks")
    task_name = models.CharField(max_length=200, choices=TASK_CHOICES)
    condition = models.CharField(max_length=200, blank=True, null=True)
    args = models.TextField(blank=True, null=True)

    def create_workflow_task(self, mfileid, job):
        task_name = self.task_name
        logging.debug("Processing task %s ", task_name)
        mfile = MFile.objects.get(id=mfileid)

        if self.condition != None \
                and self.condition != "":
            condition = self.condition
            logging.debug("Task has condition %s ", condition)

            passed = eval(condition, {"mfile": mfile})
            if not passed:
                return None

        args = {}
        if self.args is not None \
                and self.args != "":
            args = eval(self.args)

        args["taskid"] = self.id

        output_arr = []

        from jobservice.static import job_descriptions

        if task_name in job_descriptions:
            job_description = job_descriptions[task_name]
            nboutputs = job_description['nboutputs']
            for i in range(0, nboutputs):
                outputmimetype = \
                    job_description["output-%s" % i]["mimetype"]
                output = JobOutput(name="Output%s-%s" % (i, task_name),
                                    job=job, mimetype=outputmimetype)
                output.save()
                output_arr.append(output.id)

        prioritise = job.mfile.service.priority
        q = "normal.%s" % (task_name)
        if prioritise:
            q = "priority.%s" % (task_name)
        options = {"routing_key": q}
        task = subtask(task=task_name,
                        args=[[mfileid], output_arr, args],
                        options=options)
        logging.info("Task created %s ", task)

        return task

    def __unicode__(self):
        return "Task %s for %s" % (self.task_name, self.taskset.name)

# Chunk Size - 50Mb
CHUNK_SIZE = 1024 * 1024 * 50

def fbuffer(f, length, chunk_size=CHUNK_SIZE):
    to_read = int(length)
    while to_read > 0:
        chunk = f.read(chunk_size)
        to_read = to_read - chunk_size
        if not chunk:
            break
        yield chunk


class DataService(NamedBase):
    container = models.ForeignKey(HostingContainer, blank=True, null=True)
    parent = models.ForeignKey('DataService', blank=True, null=True,
                                    related_name="subservices")
    status = models.CharField(max_length=200)
    starttime = models.DateTimeField(blank=True, null=True)
    endtime = models.DateTimeField(blank=True, null=True)
    priority = models.BooleanField(default=False)
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {
        "auths": ["GET", "PUT", "POST", "DELETE"],
        "properties": ["GET", "PUT"],
        "usages": ["GET"],
        "mfiles": ["GET", "POST"],
        "mfolders": ["GET", "POST"],
        "jobs": ["GET"],
        "profiles": ["GET"],
        }

    def folder_structure(self):
        return self._folder_structure(self.id)

    def _folder_structure(self, id=None):
        structure = self.__subfolder_structure(None, id=id)
        return {"data": structure}

    def __subfolder_structure(self, mfolder, id=None):

        thisid = id or self.id

        dict = {}
        if mfolder:
            dict["data"] = mfolder.name
            dict["attr"] = {"id": mfolder.id}
        else:
            dict["data"] = self.name
            dict["attr"] = {"id": thisid, "class": "service"}

        children = []

        for _mfolder in self.mfolder_set.filter(parent=mfolder):
            children.append(self.__subfolder_structure(_mfolder))

        for mfile in self.mfile_set.filter(folder=mfolder):
            children.append(
                {"data": {
                    "title": mfile.name,
                    "icon": mfile.thumburl()},
                    "attr": {"id": mfile.id,
                    "class": "mfile"}})

        dict["children"] = children
        return dict

    def __init__(self, *args, **kwargs):
        super(DataService, self).__init__(*args, **kwargs)
        self.metrics = SERVICE_METRICS

    def get_usage(self):

        ids = [mfile.id for mfile in self.mfile_set.all()] \
                + [job.id for job in self.jobs()] + [self.id]
        thisusage = Usage.objects.filter(base__in=ids)
        return thisusage

        from jobservice.models import JobASyncResult
        asyncs = JobASyncResult.objects.filter(job__in=self.jobs()).values_list("async_id",flat=True)
        taskstates = [taskstate for taskstate in TaskState.objects
                            .filter(task_id__in=asyncs)
                            .filter(state="SUCCESS")]
        usages = [Usage(base=self, metric=taskstate.name,
                                total=taskstate.runtime, rate=0,
                                rateCumulative=0, rateTime=taskstate.tstamp,
                                nInProgress=0, reports=1,
                                squares=(
                                    taskstate.runtime * taskstate.runtime))
                                for taskstate in taskstates]

        combine = Usage.objects.none()
        for usa in usages:
            combine = combine & usa
        
        ids = [mfile.id for mfile in self.mfile_set.all()] \
                + [job.id for job in self.jobs()] + [self.id]
        thisusage = Usage.objects.filter(base__in=ids)
        return combine | thisusage

    def get_usage_summary(self):
        ids = [mfile.id for mfile in self.mfile_set.all()] \
                + [job.id for job in self.jobs()] + [self.id]
        usages = Usage.objects.filter(base__in=ids)
        summary = self._usages_to_summary(usages)
        summary.extend(Usage.get_job_usagesummary(self.jobs()))
        return summary

    def subservices_url(self):
        return reverse('dataservice_subservices', args=[self.id])

    def create_subservice(self, name, save=True):
        if self.parent:
            service = self.parent.create_subservice(name, save=False)
            service.parent = self
            service.save()
            return service
        elif self.container:
            service = self.container.create_data_service(name)
            service.parent = self
            service.save()
            for mfile in self.mfile_set.all():
                newmfile = mfile.duplicate(save=False, service=service)
                newmfile.service = service
                newmfile.save()
            return service
        else:
            return HttpResponseBadRequest()

    def thumbs(self):
        thumbs = []
        for mfile in self.mfile_set.exclude(thumb__exact='')[:4]:
            thumbs.append(mfile.thumburl())
        for i in range(len(thumbs), 4):
            thumbs.append(os.path.join(settings.MEDIA_URL,
                            "images", "package-x-generic.png"))
        return thumbs

    def get(self, url, *args, **kwargs):
        if url == "mfiles":
            return self.mfile_set.all()
        if url == "mfolders":
            return self.mfolder_set.all()
        if url == "jobs":
            from jobservice.models import Job
            mfiles = MFile.objects.filter(service=self).all()
            jobs = Job.objects.filter(mfile__in=mfiles)
            return jobs
        if url == "profiles":
            return self.profiles.all()

            # TODO: Return any service specific workflow
            ret = []
            for k in profiles.keys():
                r = {}
                r['name'] = k
                r['workflows'] = profiles[k]
                ret.append(r)
            return ret
        if not url:
            return self

    def jobs(self):
        from jobservice.models import Job
        mfiles = MFile.objects.filter(service=self).all()
        return Job.objects.filter(mfile__in=mfiles)

    def check_times(self):
        now = datetime.datetime.now()
        if (self.starttime and now < self.starttime) or (self.endtime and now > self.endtime):
            _json = {"error" : "The service is only avaliable between %s and %s " % (self.starttime, self.endtime) }
            return HttpResponseForbidden(_json, mimetype="application/json" )
        return None

    def post(self, url, *args, **kwargs):
        # TODO : Jobs
        logging.info("%s %s ", args, kwargs)

        if url == "mfiles":

            check = self.check_times()
            if check:
                return check

            if self.parent:
                return self.parent.post(url, *args, **kwargs)
            mfile = self.create_mfile(kwargs['name'], file=kwargs['file'])
            for subservice in self.subservices.all():
                subservice.__duplicate__(mfile)
            return mfile
        if url == "mfolders":

            check = self.check_times()
            if check:
                return check

            return self.create_mfolder(kwargs['name'])
        return HttpResponseNotFound()

    def __duplicate__(self, mfile):
        newmfile = mfile.duplicate(save=False, service=self)
        newmfile.service = self
        newmfile.save()
        for subservice in self.subservices.all():
            subservice.__duplicate__(mfile)

    def put(self, url, *args, **kwargs):
        if self.parent:
            return self.parent.put(url, *args, **kwargs)
        logging.info("PUT SERVICE %s %s %s ", url, args, kwargs)
        if "request" in kwargs:
            request = kwargs["request"]
            if "name" in request.POST:
                    self.name = request.POST["name"]
            if "priority" in request.POST:
                if request.POST['priority'] == "True" or request.POST['priority'] == "true":
                    self.priority = True
                if request.POST['priority'] == "False" or request.POST['priority'] == "false":
                    self.priority = False
            self.save()
        return self

    def get_rate_for_metric(self, metric):
        if self.parent:
            return self.parent.get_rate_for_metric(metric)
        if metric == METRIC_SERVICE:
            return 1

    def get_profile(self):
        if self.parent:
            return self.parent.get_profile()
        try:
            mp = self.managementproperty_set.get(property="profile")
            return mp.value
        except ManagementProperty.DoesNotExist:
            return DEFAULT_PROFILE

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(DataService, self).save()

    def clean_base(self, authid):
        servicedict = {}
        servicedict["name"] = self.name
        servicedict["mfile_set"] = self.mfile_set
        servicedict["mfolder_set"] = self.mfolder_set
        servicedict["folder_structure"] = self._folder_structure(id=authid)

        jobs = []
        for j in self.jobs():
            jobs.append(j.clean_base(authid))
        servicedict["job_set"] = jobs

        return servicedict

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage, obj=self.container)

    def create_mfolder(self, name, parent=None):
        if self.parent:
            return self.parent.create_mfolder(name, parent=None)
        try:
            MFolder.objects.get(name=name, service=self, parent=parent)
            r = rc.DUPLICATE_ENTRY
            return r
        except MFolder.DoesNotExist:
            folder = MFolder(name=name, service=self, parent=parent)
            folder.save()
            return folder

    def create_mfile(self, name, file=None, request=None,
                        post_process=True, folder=None, duplicate_of=None):

        logging.info("Create Mfile %s", self)
        service = self

        # Check for duplicate name
        done = False
        n = 0
        fn, ext = os.path.splitext(name)
        while not done:
            existing_files = MFile.objects.filter(name=name, folder=folder,
                                                    service=service)
            if len(existing_files) == 0:
                done = True
            else:
                n = n + 1
                name = "%s-%s%s" % (fn, str(n), ext)

        length = 0

        if request:
            rangestart = -1
            rangeend = -1

            if 'CONTENT_LENGTH' in request.META:
                length = request.META['CONTENT_LENGTH']
            elif 'HTTP_CONTENT_LENGTH' in request.META:
                length = request.META['HTTP_CONTENT_LENGTH']

            if 'RANGE' in request.META:
                range_header = request.META['RANGE']
                byte, range = range_header.split('=')
                ranges = range.split('-')

                if len(ranges) != 2:
                    return HttpResponseBadRequest(
                            "Do not support range '%s' ", range_header)

                rangestart = int(ranges[0])
                rangeend = int(ranges[1])
                length = rangeend - rangestart
            elif 'HTTP_RANGE' in request.META:
                range_header = request.META['HTTP_RANGE']
                byte, range = range_header.split('=')
                ranges = range.split('-')

                if len(ranges) != 2:
                    return HttpResponseBadRequest(
                            "Do not support range '%s' ", range_header)

                rangestart = int(ranges[0])
                rangeend = int(ranges[1])
                length = rangeend - rangestart
            input = request.META['wsgi.input']
            emptyfile = ContentFile('')
            temp = NamedTemporaryFile()

            if rangestart != -1:
                try:
                    mf = open(temp.name, 'r+b')
                    try:
                        mf.seek(rangestart)
                        for chunk in fbuffer(input, length):
                            mf.write(chunk)
                    finally:
                        mf.close()
                except IOError:
                    logging.error(
                        "Error writing partial content to MFile '%s'",
                            temp.name)
                    pass
            else:
                try:
                    mf = open(temp.name, 'wb')
                    logging.info(temp.name)
                    try:
                        for chunk in fbuffer(input, length):
                            mf.write(chunk)
                    finally:
                        mf.close()
                except IOError:
                    logging.error(
                        "Error writing content to MFile '%s'", temp.name)
                    pass
            mfile = MFile(name=name, service=service, empty=True)
            mfile.file.save(name, File(temp))

        elif file == None:
            emptyfile = ContentFile('')
            mfile = MFile(name=name, service=service, empty=True)
            mfile.file.save(name, emptyfile)
        else:
            if type(file) == django.core.files.base.ContentFile:
                mfile = MFile(name=name, service=service)
                mfile.file.save(name, file)
                length = mfile.file.size
            else:
                mfile = MFile(name=name, service=service, file=file,
                                empty=False)
                mfile.save()
                length = mfile.file.size

        if duplicate_of:
            mfile.duplicate_of = duplicate_of

        mfile.folder = folder
        mfile.size = length
        mfile.mimetype = mimefile([mfile.id], [], {})["mimetype"]
        mfile.save()

        import usage_store as usage_store
        usage_store.record(mfile.id, METRIC_INGEST, int(length))

        logging.debug("MFile creation started '%s' ", mfile.name)
        logging.debug("Creating roles for '%s' ", mfile.name)

        mfileauth_owner = Auth(base=mfile, authname="owner")
        mfileauth_owner.setroles(['mfileowner'])
        mfileauth_owner.save()
        if post_process:
            mfile.create_workflow_job("ingest")

        return mfile


class RemoteMServeService(models.Model):
    url = models.URLField()
    name = models.CharField(max_length=200)

    def __unicode__(self):
        return "MServe : %s" % (self.name)


class MFolder(NamedBase):
    service = models.ForeignKey(DataService)
    parent = models.ForeignKey('self', null=True)

    def duplicate(self, name, parent):

        new_mfolder = MFolder(name=name, service=self.service, parent=parent)
        new_mfolder.save()

        for mfile in self.mfile_set.all():
            new_mfile = MFile(name=mfile.name, file=mfile.file,
                                folder=new_mfolder, mimetype=mfile.mimetype,
                                empty=False, service=mfile.service)
            new_mfile.save()

        for submfolder in self.mfolder_set.all():
            new_submfolder = submfolder.duplicate(submfolder.name, new_mfolder)
            new_submfolder.save()

        new_mfolder.save()
        return new_mfolder

    def __unicode__(self):
        return "MFolder: %s " % self.name

    def get_rel_path(self):
        if self.parent is not None:
            return os.path.join(self.parent.get_rel_path(), self.name)
        else:
            return self.name

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(MFolder, self).save()


class MFile(NamedBase):
    # TODO : Add bitmask to MFile for deleted,remote,input,output, etc
    empty = models.BooleanField(default=False)
    service = models.ForeignKey(DataService)
    folder = models.ForeignKey(MFolder, null=True)
    file = models.FileField(upload_to=utils.mfile_upload_to,
                        blank=True, null=True, max_length=FILE_FIELD_LENGTH,
                        storage=storage.getdiscstorage())
    mimetype = models.CharField(max_length=200, blank=True, null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)
    size = models.BigIntegerField(default=0)
    thumb = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getthumbstorage())
    poster = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getposterstorage())
    proxy = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getproxystorage())
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    duplicate_of = models.ForeignKey('MFile', null=True)

    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {
            "auths": ["GET", "PUT", "POST", "DELETE"],
            "properties": [],
            "usages": ["GET"],
            "file": ["GET", "PUT", "DELETE"],
            "workflows": ["GET", "POST"],
            "jobs": ["GET", "POST"],
            }

    class Meta:
        ordering = ('-created', 'name')

    def __unicode__(self):
        return "MFile  %s" % (self.name.encode("utf-8"))

    def __str__(self):
        return "MFile  %s" % (self.name.encode("utf-8"))

    def get_download_path(self):
        return reverse('mfile_download', args=[self.id])

    def get_upload_thumb_path(self):
        return reverse('mfile_upload_thumb', args=[self.id])

    def get_upload_poster_path(self):
        return reverse('mfile_upload_poster', args=[self.id])

    def get_upload_proxy_path(self):
        return reverse('mfile_upload_proxy', args=[self.id])

    def delete(self):
        if self.duplicate_of:
            self.duplicate_of.delete()
        else:
            super(MFile, self).delete()

    def __init__(self, *args, **kwargs):
        super(MFile, self).__init__(*args, **kwargs)
        self.metrics = MFILE_METRICS

    def get_usage(self):
        ids = [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return usages

    def get_usage_summary(self):
        ids = [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return self._usages_to_summary(usages)

    def get(self, url, *args, **kwargs):
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

    def post(self, url, *args, **kwargs):
        if url == "jobs":
            if 'name' in kwargs:
                name = kwargs['name']
                job = self.create_job(name)
                return job
            return HttpResponseBadRequest()
        if url == "workflows":
            if 'name' in kwargs:
                name = kwargs['name']
                job = self.create_workflow_job(name)
                return job
            return HttpResponseBadRequest("No workflow name specified")
        return HttpResponseBadRequest()

    def put(self, url, *args, **kwargs):
        if url == None:
            if 'file' in kwargs:
                file = kwargs['file']
                self.update_mfile(self.name, file=file, post_process=True,
                                    folder=self.folder)
                return self
            return HttpResponseBadRequest()
        return HttpResponseNotFound()

    def clean_base(self, authid):
        mfiledict = {}
        mfiledict["name"] = self.name
        mfiledict["file"] = self.file
        mfiledict["mimetype"] = self.mimetype
        mfiledict["updated"] = self.updated
        mfiledict["thumburl"] = self.thumburl()
        mfiledict["thumb"] = self.thumb
        mfiledict["created"] = self.created
        mfiledict["checksum"] = self.checksum
        mfiledict["posterurl"] = self.posterurl()
        mfiledict["poster"] = self.poster
        mfiledict["reportnum"] = self.reportnum
        mfiledict["size"] = self.size
        return mfiledict

    def __get_file(self):
        mfile = self

        # Access Speed default is unlimited
        accessspeed = ""

        service = mfile.service
        container = service.container
        logging.info("Finding limit for %s ", mfile.name)
        accessspeed = DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,
                                                    property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s",
                            accessspeed, mfile.name)
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,
                            property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s",
                                accessspeed, mfile.name)
            except ObjectDoesNotExist:
                pass

        file = mfile.file

        sigret = MFILE_GET_SIGNAL.send(sender=self, mfile=mfile)

        for k, v in sigret:
            logging.info("Signal %s returned %s ", k, v)

        import usage_store as usage_store

        check1 = mfile.checksum

        if check1 == "" or check1 == None:
            logging.warn("Mfile %s has no checksum - will return file \
                            without check", self)
        else:
            check2 = utils.md5_for_file(mfile.file)
            if check1 == check2:
                logging.info("Verification of %s on read ok", mfile)
            else:
                logging.info("Verification of %s on read FAILED", mfile)
                usage_store.record(mfile.id, metric_corruption, 1)
                try:
                    backup = BackupFile.objects.get(mfile=mfile)
                    check3 = mfile.checksum
                    if os.path.exists(backup.file.path):
                        check4 = utils.md5_for_file(backup.file)
                        if(check3 == check4):
                            shutil.copy(backup.file.path, mfile.file.path)
                            file = backup.file
                        else:
                            logging.info("The file %s has been lost", mfile)
                            usage_store.record(mfile.id,
                                                METRIC_DATALOSS, mfile.size)
                            return rc.NOT_HERE
                except BackupFile.DoesNotExist as e:
                    logging.info("There is no backup file for %s ", mfile)
                    return rc.NOT_HERE

        file = mfile.file

        MFILE_GET_SIGNAL.send(sender=self, mfile=mfile)

        if accessspeed == "unlimited":
            dlfoldername = "dl"
        else:
            dlfoldername = os.path.join("dl", accessspeed)

        path = unicode(file)

        redirecturl = utils.gen_sec_link_orig(file.name, dlfoldername)
        logging.info("%s %s ", file.name, dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT, dlfoldername, path)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = file.path

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            logging.info("Linking ")
            logging.info("   %s ", mfilefilepath)
            logging.info("to %s ", fullfilepath)
            try:
                os.link(mfilefilepath, fullfilepath)
            except Exception as e:
                logging.info("Caught error linking file, trying copy. %s", \
                                str(e))
                shutil.copy(mfilefilepath, fullfilepath)

        import dataservice.models as models

        usage_store.record(mfile.id, METRIC_ACCESS, mfile.size)

        redirecturl = os.path.join("/", redirecturl)
        return HttpResponseRedirect(redirecturl)

    def update_mfile(self, name, file=None, request=None, post_process=True,
                        folder=None, duplicate_of=None):
        logging.info("Update Mfile %s", self)
        length = 0

        if request:
            chunked = False
            ranged = False
            rangestart = -1
            rangeend = -1

            if 'CONTENT_LENGTH' in request.META:
                length = request.META['CONTENT_LENGTH']
            elif 'HTTP_CONTENT_LENGTH' in request.META:
                length = request.META['HTTP_CONTENT_LENGTH']

            if 'RANGE' in request.META:
                range_header = request.META['RANGE']
                byte, range = range_header.split('=')
                ranges = range.split('-')

                if len(ranges) != 2:
                    return HttpResponseBadRequest(
                            "Do not support range '%s' ", range_header)

                rangestart = int(ranges[0])
                rangeend = int(ranges[1])
                length = rangeend - rangestart
                ranged = true
            elif 'HTTP_RANGE' in request.META:
                range_header = request.META['HTTP_RANGE']
                byte, range = range_header.split('=')
                ranges = range.split('-')

                if len(ranges) != 2:
                    return HttpResponseBadRequest(
                            "Do not support range '%s' ", range_header)

                rangestart = int(ranges[0])
                rangeend = int(ranges[1])
                length = rangeend - rangestart
                ranged = True

            if 'TRANSFER_ENCODING' in request.META:
                encoding_header = request.META['TRANSFER_ENCODING']
                if encoding_header.find('chunked') != -1:
                    chunked = True

            if 'HTTP_TRANSFER_ENCODING' in request.META:
                encoding_header = request.META['HTTP_TRANSFER_ENCODING']
                if encoding_header.find('chunked') != -1:
                    chunked = True

            if chunked:
                return HttpResponseBadRequest("Chunking Not Supported")

            input = request.META['wsgi.input']

            if rangestart != -1:
                try:
                    mf = open(self.file.path, 'r+b')
                    try:
                        mf.seek(rangestart)
                        for chunk in fbuffer(input, length):
                            mf.write(chunk)
                    finally:
                        mf.close()
                except IOError:
                    logging.error(
                        "Error writing partial content to MFile '%s'",
                                    self.file.path)
                    pass
            else:
                try:
                    mf = open(self.file.path, 'wb')
                    logging.info(self.file.path)
                    try:
                        for chunk in fbuffer(input, length):
                            mf.write(chunk)
                    finally:
                        mf.close()
                except IOError:
                    logging.error("Error writing content to MFile '%s'",
                                    self.file.path)
                    pass

            self.save()

        else:
            if type(file) == django.core.files.base.ContentFile:
                self.file.save(name, file)
                length = file.size
            else:
                self.file.save(name, File(file))
                length = file.size

        if duplicate_of:
            self.duplicate_of = duplicate_of

        self.name = name
        self.folder = folder
        self.size = length
        self.mimetype = mimefile([self.id], [], {})["mimetype"]
        self.save()

        import usage_store as usage_store
        usage_store.record(self.id, METRIC_INGEST, int(length))

        logging.info("MFile update '%s' ", self.name)
        logging.info("MFile PATH %s ", self.file.path)
        logging.info("MFile size %s ", self.size)

        if post_process:
            self.create_workflow_job("update")

        return self

    def create_job(self, name):
        from jobservice.models import Job
        job = Job(name=name, mfile=self)
        job.save()
        return job

    def duplicate(self, save=True, service=None):
        if service:
            new_mfile = service.create_mfile(self.name, file=self.file,
                                            folder=self.folder,
                                            duplicate_of=self)
        else:
            new_mfile = self.service.create_mfile(self.name, file=self.file,
                                            folder=self.folder,
                                            duplicate_of=self)
        if save:
            new_mfile.save()
        return new_mfile

    def create_read_only_auth(self):
        mfileauth_ro = Auth(base=self, authname="%s Read Only" % self)
        mfileauth_ro.setroles(["mfilereadonly"])
        mfileauth_ro.save()
        return mfileauth_ro

    def create_workflow_job(self, name):
        if self.file:

            if not self.mimetype:
                self.mimetype = mimefile([self.id], [], {})["mimetype"]
            self.save()

            profile_name = self.service.get_profile()
            logging.info("Create workflow with profile %s ", profile_name)

            profile = self.service.profiles.get(service=self.service,
                                                    name=profile_name)
            return profile.workflows.get(name=name).create_workflow_job(self.id)
        else:
            return None

    def post_process(self):
        return self.create_workflow_job("ingest")

    def get_rel_path(self):
        if self.folder is not None:
            return os.path.join(self.folder.get_rel_path(), self.name)
        else:
            return self.name

    def get_rate_for_metric(self, metric):
        if metric == METRIC_MFILE:
            return 1
        if not self.empty:
            if metric == METRIC_DISC:
                return self.size

    def get_value_for_metric(self, metric):
        if not self.empty:
            if metric == METRIC_DISC_SPACE:
                return self.size

    def get_updated_value_for_metric(self, metric):
        if not self.empty:
            if metric == METRIC_DISC_SPACE:
                return self.size

    def get_updated_rate_for_metric(self, metric):
        if metric == METRIC_MFILE:
            return 1
        if not self.empty:
            if metric == METRIC_DISC:
                return self.size

    def thumburl(self):
        if self.thumb and self.thumb != "":
            return "%s%s" % (settings.THUMB_PATH, self.thumb)
        elif self.mimetype:
            if self.name.endswith(".blend"):
                return os.path.join(settings.MEDIA_URL, "images/blender.png")
            if self.mimetype.startswith("image"):
                return os.path.join(settings.MEDIA_URL, "images", "image-x-generic.png")
            if self.mimetype.startswith("text"):
                return os.path.join(settings.MEDIA_URL, "images", "text-x-generic.png")
        return os.path.join(settings.MEDIA_URL, "images", "package-x-generic.png")

    def posterurl(self):
        if self.poster and self.poster != "":
            return "%s%s" % (settings.THUMB_PATH, self.poster)
        else:
            if self.mimetype:
                if self.mimetype.startswith("image"):
                    return os.path.join(settings.MEDIA_URL,
                                        "images", "image-x-generic.png")
                if self.mimetype.startswith("text"):
                    return os.path.join(settings.MEDIA_URL,
                                        "images", "text-x-generic.png")
        return os.path.join(settings.MEDIA_URL, "images", "package-x-generic.png")

    def proxyurl(self):
        if self.proxy and self.proxy != "":
            return "%s%s" % (settings.THUMB_PATH, self.proxy)
        else:
            return ""
            if self.mimetype:
                if self.mimetype.startswith("image"):
                    return os.path.join(settings.MEDIA_URL,
                            "images", "image-x-generic.png")
                if self.mimetype.startswith("text"):
                    return os.path.join(settings.MEDIA_URL,
                            "images", "text-x-generic.png")
        return os.path.join(settings.MEDIA_URL, "images", "package-x-generic.png")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        self.updated = datetime.datetime.now()
        if self.file:
            if os.path.exists(self.file.path):
                self.size = self.file.size
            self.empty = False
        super(MFile, self).save()

    def _delete_usage_(self):
        import usage_store as usage_store
        for usage in self.usages.all():
            usage_store._stoprecording_(usage, obj=self.service)


def pre_delete_handler_mfile(sender, instance=False, **kwargs):
    mfiles = MFile.objects.filter(duplicate_of=instance.pk)
    logging.info("%s %s Has duplicates %s", instance, instance.id, mfiles)
    if instance.duplicate_of:
        dup = MFile.objects.filter(duplicate_of=instance.duplicate_of.pk)
        #dup.delete()
    instance._delete_usage_()


def pre_delete_handler(sender, instance=False, **kwargs):
    instance._delete_usage_()

pre_delete.connect(pre_delete_handler_mfile, sender=MFile,
                    dispatch_uid="dataservice.models")
pre_delete.connect(pre_delete_handler, sender=DataService,
                    dispatch_uid="dataservice.models")
pre_delete.connect(pre_delete_handler, sender=HostingContainer,
                    dispatch_uid="dataservice.models")


def post_init_handler(sender, instance=False, **kwargs):
    pass

post_init.connect(post_init_handler, sender=MFile,
                    dispatch_uid="dataservice.models")


def post_save_handler(sender, instance=False, **kwargs):
    pass

post_save.connect(post_save_handler, sender=MFile,
                    dispatch_uid="dataservice.models")


class BackupFile(NamedBase):
    mfile = models.ForeignKey(MFile)
    file = models.FileField(upload_to=utils.create_filename,
                            max_length=FILE_FIELD_LENGTH,
                            storage=storage.gettapestorage())
    mimetype = models.CharField(max_length=200, blank=True, null=True)
    checksum = models.CharField(max_length=32, blank=True, null=True)

    def __init__(self, *args, **kwargs):
        super(BackupFile, self).__init__(*args, **kwargs)
        self.metrics = BACKUPFILE_METRICS

    def get_upload_path(self):
        return reverse('backup_upload', args=[self.id])

    def get_value_for_metric(self, metric):
        if metric == METRIC_BACKUPFILE:
            return 1
        if self.file:
            if metric == METRIC_DISC_SPACE:
                return self.file.size

    def get_rate_for_metric(self, metric):
        if self.file:
            if metric == METRIC_DISC:
                return self.file.size

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        super(BackupFile, self).save()


class ManagementProperty(models.Model):
    base = models.ForeignKey(NamedBase)
    property = models.CharField(max_length=200)
    value = models.CharField(max_length=200)

    def __unicode__(self):
        return "Management Property %s:%s" % (self.property, self.value)

    def values(self):
        if self.property == "accessspeed":
            return {
                "type": "enum",
                "choices":
                    ["100", "1000", "10000",
                        "100000", "1000000", "100000000", "unlimited"]}
        elif self.property == "profile":
            return {"type": "enum",
                    "choices": static.default_profiles.keys()}
        else:
            return {}


class Auth(Base):
    authname = models.CharField(max_length=50)
    base = models.ForeignKey(NamedBase, blank=True, null=True)
    parent = models.ForeignKey('Auth', blank=True, null=True)
    usages = models.ManyToManyField("Usage")
    roles_csv = models.CharField(max_length=200)

    def __init__(self, *args, **kwargs):
        super(Auth, self).__init__(*args, **kwargs)

    def geturls(self):
        urls = {}
        for rolename in self.getroles():
            urls.update(static.default_roles[rolename]['urls'])
        return urls

    def urls(self):
        urls = {}
        for rolename in self.getroles():
            urls.update(static.default_roles[rolename]['urls'])
        return urls

    def basename(self):
        return self.base.name

    def thumburl(self):
        if utils.is_service(self.base):
            ds = DataService.objects.get(id=self.base.id)
            if len(ds.mfile_set.all()) > 0:
                return list(ds.mfile_set.all())[0].thumburl()
        return os.path.join(settings.MEDIA_URL, "images", "package-x-generic.png")

    def getroles(self):
        return self.roles_csv.split(",")

    def roles(self):
        return self.roles_csv.split(",")

    def setroles(self, new_roles):
        for rolename in new_roles:
            if rolename not in static.default_roles.keys():
                raise Exception("Rolename '%s' not valid " % rolename)
        self.roles_csv = ",".join(new_roles)

    def getmethods(self):
        methods = []
        for rolename in self.getroles():
            methods = methods + static.default_roles[rolename]['methods']
        return methods

    def check(self, url, method):
        if url == None:
            if self.base:
                if method in self.getmethods() and self.base.get_real_base()\
                        .check(url, method):
                    return True, None
                else:
                    return False, HttpResponseForbidden()
            else:
                if method in self.getmethods() and self.parent.get_real_base()\
                        .check(url, method):
                    return True, None
                else:
                    return False, HttpResponseForbidden()
        else:

            if self.base:
                passed = False
                if url != "base":
                    passed, error = self.base.get_real_base()\
                                        .check(url, method)
                else:
                    passed = True

                if url in self.geturls()\
                        and method in self.geturls()[url]\
                        and passed:
                    return True, None
                else:
                    return False, HttpResponseForbidden()
            else:
                passed, error = self.parent.get_real_base().check(url, method)

                if url in  self.geturls()\
                        and method in self.geturls()[url]\
                        and passed:
                    return True, None
                else:
                    return False, HttpResponseForbidden()

    def get_usage(self):
        base = self.get_real_base()
        return base.get_usage()

    def get_usage_summary(self):
        base = self.get_real_base()
        return base.get_usage_summary()

    def get(self, url, *args, **kwargs):
        logging.info("AUTH %s %s ", self.authname, url)
        if not url:
            return self
        if url == "base":
            return self.get_real_base().clean_base(self.id)
        return self.base.get_real_base().do("GET", url)

    def put(self, url, *args, **kwargs):
        return self.get_real_base().do("PUT", url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        return self.get_real_base().do("POST", url, *args, **kwargs)

    def save(self):
        if not self.id:
            self.id = utils.random_id()
        if not self.roles_csv:
            self.roles_csv = ""
        super(Auth, self).save()

    def __unicode__(self):
        return "Auth: authname=%s base=%s roles=%s " % (self.authname, self.base, ",".join(self.getroles()))
