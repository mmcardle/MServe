"""

MServe Models
---------------

::

 This class defines all the MServe dataservice django models

https://docs.djangoproject.com/en/dev/topics/db/models/

"""
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
import logging
import datetime
import time
import os
import shutil
import settings as settings
import utils as utils
import static as static
import storage as storage
import usage_store as usage_store
from django.dispatch import Signal
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
from django.db.models import Q
from django.core.urlresolvers import reverse
from django.core.files import File
from django.db.models import Count, Max, Min, Avg, Sum, StdDev, Variance
from dataservice.tasks import mimefile


# Declare Signals
MFILE_GET_SIGNAL = Signal(providing_args=["mfile"])

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
    '''A Profile for a MServe user, holding objects this user has access to'''
    user = models.ForeignKey(User, unique=True)
    bases = models.ManyToManyField('NamedBase', related_name='bases',
        null=True, blank=True)
    auths = models.ManyToManyField('Auth', related_name='profileauths',
        null=True, blank=True)

    def myauths(self):
        '''Returns auths this user has access to'''
        ret = []
        for auth in self.auths.all():
            ret.append(Auth.objects.get(id=auth.id))
        return set(ret)

    def mfiles(self):
        '''Returns mfiles this user has access to'''
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
        '''Returns data services this user has access to'''
        ret = []
        for base in self.bases.all():
            if utils.is_service(base):
                ret.append(DataService.objects.get(id=base.id))
        return set(ret)

    def mfolders(self):
        '''Returns mfolders this user has access to'''
        ret = []
        for base in self.bases.all():
            if utils.is_mfolder(base):
                ret.append(MFolder.objects.get(id=base.id))
        for auth in self.auths.all():
            if utils.is_service(auth.base):
                ret.append(DataService.objects.get(id=auth.base.id))
        return set(ret)

    def containers(self):
        '''Returns containers this user has access to'''
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
    ''' A request for a service from a user '''
    name = models.CharField(max_length=200)
    """Requested name of the service"""
    reason = models.TextField()
    """Reason for the request"""
    profile = models.ForeignKey('MServeProfile', null=True, blank=True,
                                        related_name="servicerequests")
    """Profile of the user making the request"""
    state = models.CharField(max_length=1, choices=SERVICEREQUEST_STATES,
        default='P')
    """Current state of the request"""
    time = models.DateTimeField(auto_now_add=True)
    """Time the request was made"""

    class Meta:
        '''set ordering to time'''
        ordering = ["-time"]

    def url(self):
        """The REST API url for this Service Request"""
        return reverse('user_request', args=[self.id])

    def ctime(self):
        ''' Return the time for this request was made'''
        return self.time.ctime()

    def status(self):
        '''Returns the long version of the status '''
        for index, word in SERVICEREQUEST_STATES:
            if index == self.state:
                return word
        return "unknown"

    def __unicode__(self):
        return self.name


class Usage(models.Model):
    """A django model to record usage of a resource"""
    base = models.ForeignKey('NamedBase', null=True, blank=True)
    "The base object this report refers to"
    metric = models.CharField(max_length=4096)
    "The metric this report is recording"
    time = models.DateTimeField(auto_now_add=True)
    "Time first recorded (shouldnt change)"
    reports = models.BigIntegerField(default=0)
    "Number of reports"
    total = models.FloatField(default=0)
    "Sum of report values"
    squares = models.FloatField(default=0)
    nInProgress = models.BigIntegerField(default=0)
    rateTime = models.DateTimeField()
    "Time the rate last changed"
    rate = models.FloatField()
    "The current rate (change in value per second)"
    rateCumulative = models.FloatField()
    "Cumulative unreported usage before rateTime"

    @staticmethod
    def get_usage_plots(request, baseid=None):
        ''' Return jqplot json for usage - used by html views '''
        request_types = request.GET
        plots = []
        base = None
        try:
            base = NamedBase.objects.get(id=baseid)
        except NamedBase.DoesNotExist:
            try:
                auth = Auth.objects.get(id=baseid)
                base = auth.get_real_base()
            except Auth.DoesNotExist:
                pass

        if base == None:
            usages = Usage.objects.all()
        else:
            usages = base.get_real_base().get_usage()

        for request_type in request_types:
            if request_type == "http://mserve/deliverySuccess":
                plot = {}
                plot["type"] = "pie"
                plot["size"] = "large"
                plot["label"] = "Delivery Success"
                success = usages.filter(
                    metric=settings.DELIVERY_SUCCESS_METRIC)\
                    .aggregate(success=Sum('total'))["success"]
                total = usages.filter(
                    metric=settings.DELIVERY_SUCCESS_METRIC)\
                    .aggregate(total=Count('reports'))["total"]
                if success == None:
                    success = 0
                failure = total - success

                if total == 0:
                    data = []
                    data.append({
                        "label" : "No Data" ,
                        "data" : 1,
                        "color" : "#CCCCCC"})
                    plot["data"] = data
                    plots.append(plot)
                else:
                    data = []
                    data.append({
                        "label" : "Failed" ,
                        "data" : failure,
                        "color" : "#CC0000"})
                    data.append({
                        "label" : "Success" ,
                        "data" : success,
                        "color" : "#00CC00"})
                    plot["data"] = data
                    plots.append(plot)

        return plots
    
    @staticmethod
    def get_full_usagesummary():
        ''' Return all the usage for the whole service - expensive '''
        usages = Usage.objects.all()
        usagesummary = Usage.usages_to_summary(usages)
        from jobservice.models import Job
        usagesummary.extend(Usage.get_job_usagesummary(Job.objects.all()))
        return usagesummary

    @staticmethod
    def aggregate(usages):
        ''' Aggregate a set of usage objects '''
        for usage in usages:
            if usage.nInProgress > 0:
                usage_store.update_usage(usage)

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
        ''' Convert usages to a summary'''
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
        ''' Get usages for all Jobs '''
        from jobservice.models import JobASyncResult
        asyncs = JobASyncResult.objects.filter(job__in=jobs)\
                                    .values_list("async_id",flat=True)
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

    def save(self, *args, **kwargs):
        super(Usage, self).save(*args, **kwargs)

    def fmt_ctime(self):
        """Returns the ctime of the time field"""
        return self.time.ctime()

    def fmt_rtime(self):
        """Returns the ctime of the rateTime field"""
        return self.rateTime.ctime()

    def copy(self, base, save=False):
        """Make a new copy of this usage object"""
        newusage = Usage(base=base, metric=self.metric, total=self.total,
                    reports=self.reports, nInProgress=self.nInProgress,
                    rate=self.rate, rateTime=self.rateTime,
                    rateCumulative=self.rateCumulative)
        if save:
            newusage.save()
        return newusage

    def __unicode__(self):
        return "Usage: metric=%s total=%f reports=%s nInProgress=%s rate=%s \
                    rateTime=%s rateCumulative=%s" % (self.metric, self.total,
                        self.reports, self.nInProgress, self.rate,
                        self.rateTime, self.rateCumulative)


class Base(models.Model):
    """

    The Base object is an abstract objects that hold functionality common to
    any resource

    """
    id = models.CharField(primary_key=True, max_length=ID_FIELD_LENGTH)
    """The unique unguessable id for the resource"""
    methods = []
    urls = {
        "auths": [],
        "properties": [],
        "usages": []}

    def getmethods(self):
        """Returns the allowed methods for this object - default []"""
        return self.methods

    def geturls(self):
        """Returns the allowed urls for this object"""
        return self.urls

    def get_real_base(self):
        """Gets the super object that this base refers to"""
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
        """
        Validation check to make sure this base allows the method 'method'
        against the url 'url'
        """
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
        """
        Main method called by the handlers to perform operations of objects
        Must pass the 'check' method in order for the operation to continue
        """
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
                    manage_prop = self.get_real_base()\
                        .managementproperty_set.get(
                            base=self, property=k)
                    manage_prop.value = kwargs[k]
                    manage_prop.save()
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
                return rc.DELETED
            if url == "auths":
                if 'request' in kwargs:
                    if 'name' in kwargs["request"].POST:
                        name = kwargs["request"].POST["name"]
                        auth = self.auth_set.get(authname=name)
                        logging.info("DELETE AUTH %s", auth.authname)
                        auth.delete()
                        response = rc.DELETED
                        response.write("Deleted '%s'" % name)
                        return response
                    else:
                        return HttpResponseBadRequest()
                else:
                    return HttpResponseBadRequest()
            return HttpResponseNotFound()

        logging.info("ERROR: 404 Pattern not matched "
                            "for %s on %s", method, url)
        return rc.NOT_FOUND

    def clean_base(self, authid):
        """
        Method should be overriden to return a 'cleaned' version of this
        object for serialization to the user, removing any ids.
        """
        logging.info("Override this clean method %s", self)
        return {}

    class Meta:
        abstract = True


class NamedBase(Base):
    """
    NamedBase is a concrete class that all resources inheirit from. It hold the
    usage field where all usage against a resource is recorded.
    """
    metrics = []
    """A list of metric to report - default [] """
    initial_usage_recorded = models.BooleanField(default=False)
    """Boolean to record if initial usage has been recorded"""
    name = models.CharField(max_length=200)
    """The name of the resource"""
    usages = models.ManyToManyField("Usage")
    """A django many-to-many field to hold :class:`.Usage` """
    reportnum = models.IntegerField(default=1)
    """A counter for the report number, incremented every report"""
    created = models.DateTimeField(auto_now_add=True)
    """When this object was created"""

    class Meta:
        ordering = ["-created"]

    def save(self, *args, **kwargs):
        super(NamedBase, self).save(*args, **kwargs)
        if not self.initial_usage_recorded:
            startusages = []
            for metric in self.metrics:
                #logging.info("Processing metric %s" %metric)
                #  Recored Initial Values
                val = self.get_value_for_metric(metric)
                if val is not None:
                    logging.debug("Value for %s is %s", metric, val)
                    logging.debug("Recording usage for metric %s value= %s",
                                    metric, val)
                    usage = usage_store.record(self.id, metric, val)
                    startusages.append(usage)
                # Start recording initial rates
                rate = self.get_rate_for_metric(metric)
                if rate is not None:
                    logging.debug("Rate for %s is %s", metric, rate)
                    logging.debug("Recording usage rate for metric %s value %s",
                                    metric, rate)
                    usage = usage_store.startrecording(self.id, metric, rate)
                    startusages.append(usage)

            self.usages = startusages
            self.reportnum = 1
            self.initial_usage_recorded = True
            super(NamedBase, self).save(*args, **kwargs)
        else:
            self.update_usage()

    def update_usage(self):
        """Trigger usage has changed, updated usage reports"""
        for metric in self.metrics:
            #  Recorded updated values
            val = self.get_updated_value_for_metric(metric)

            if val is not None:
                logging.debug("Value for %s is %s", metric, val)
                logging.debug("Recording usage for metric %s value= %s", \
                                metric, val)
                usage_store.update(self.id, metric, val)
            # recording updated rates
            rate = self.get_updated_rate_for_metric(metric)
            if rate is not None:
                logging.debug("Rate for %s is %s", metric, rate)
                logging.debug("Recording usage rate for metric %s value= %s",
                                metric, rate)
                usage_store.updaterecording(self.id, metric, rate)

        super(NamedBase, self).save()

    def get_value_for_metric(self, metric):
        '''Override this method to report value for metric'''
        return None

    def get_rate_for_metric(self, metric):
        '''Override this method to report rate for metric'''
        return None

    def get_updated_value_for_metric(self, metric):
        '''Override this method to report updated value for metric'''
        return None

    def get_updated_rate_for_metric(self, metric):
        '''Override this method to report updated rate for metric'''
        return None

    def _delete_usage_(self):
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)

    def __unicode__(self):
        return self.name


class HostingContainer(NamedBase):
    """

    A Hosting Container is an object to hold groups of services in a
    manageable container. It provides defaults for profiles and storage
    locations

    """
    default_profile = models.CharField(max_length=200, blank=True, null=True)
    """The default profile to create services with"""
    default_path = models.CharField(max_length=200, blank=True, null=True)
    """The default path to store data"""
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {"auths": ["GET", "PUT", "POST", "DELETE"],
        "properties": ["GET", "PUT"],
        "usages": ["GET"],
        "services": ["GET", "POST"]}

    def __init__(self, *args, **kwargs):
        super(HostingContainer, self).__init__(*args, **kwargs)
        self.metrics = CONTAINER_METRICS

    def url(self):
        """The REST API url for this Container"""
        return reverse('hostingcontainer', args=[self.id])

    def stats_url(self):
        """The REST API url for stats for this container - used by html views"""
        return reverse('stats', args=[self.id])

    def services_url(self):
        """The REST API url for usage for this container"""
        return reverse('hostingcontainer_services', args=[self.id])

    def usage_url(self):
        """The REST API url for usage for this container"""
        return reverse('hostingcontainer_usagesummary', args=[self.id])

    def properties_url(self):
        """The REST API url for properties for this container"""
        return reverse('hostingcontainer_props', args=[self.id])

    def thumbs(self):
        """A list of thumbnail images representing this container"""
        thumbs = []
        for service in self.dataservice_set.all()[:4]:
            for mfile in service.mfile_set.exclude(thumb__exact='')[:4]:
                thumbs.append(mfile.thumburl())
        for i in range(len(thumbs), 16):
            thumbs.append(os.path.join(settings.MEDIA_URL,
                            "images", "package-x-generic.png"))
        return thumbs

    def get(self, url, *args, **kwargs):
        """Perform a GET on this container"""
        if url == "services":
            return self.dataservice_set.all()
        if not url:
            return self

    def post(self, url, *args, **kwargs):
        """Perform a POST on this container"""
        if url == "services":
            return self.create_data_service(kwargs['name'])
        else:
            return None

    def put(self, url, *args, **kwargs):
        """Perform a PUT on this container"""
        logging.info("PUT CONTAINER %s %s", url, args)
        if url == None:
            from forms import HostingContainerForm
            form = HostingContainerForm(
                        kwargs["request"].POST, instance=self)
            if form.is_valid():
                hostingcontainer = form.save()
                return hostingcontainer
            else:
                response = rc.BAD_REQUEST
                response.write("Invalid Request! ")
                return response
        return HttpResponseNotFound()

    def get_usage(self):
        """Get all usage for this container, including child resources"""
        serviceids = [service.id for service in self.dataservice_set.all()]
        mfileids = [mfile.id for service in self.dataservice_set.all()
                            for mfile in service.mfile_set.all()]
        jobids = [job.id for service in self.dataservice_set.all()
                            for job in service.jobs()]
        ids = serviceids + mfileids + jobids + [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return usages

    def get_usage_summary(self):
        """Get a usage summary for this container, including child resources"""
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
        """Get all jobs under this container"""
        from jobservice.models import Job
        dataservices = self.dataservice_set.all()
        mfiles = MFile.objects.filter(service__in=dataservices).all()
        return Job.objects.filter(mfile__in=mfiles)

    def mfiles(self):
        """Get all mfiles under this container"""
        dataservices = self.dataservice_set.all()
        mfiles = MFile.objects.filter(service__in=dataservices).all()
        return mfiles

    @staticmethod
    def create_container(name):
        """Create a new HostingContainer"""
        hostingcontainer = HostingContainer(name=name)
        hostingcontainer.save()
        return hostingcontainer

    def create_data_service(self, name, duplicate_of=None,
                                    starttime=None, endtime=None):
        """Create a new dataservice under this container"""

        dataservice = DataService(name=name, container=self,
                                    starttime=starttime, endtime=endtime)
        dataservice.save()

        if duplicate_of:
            dataservice.parent = duplicate_of
            dataservice.save()
            for mfile in duplicate_of.mfile_set.all():
                newmfile = mfile.duplicate(save=False, service=dataservice)
                newmfile.service = dataservice
                newmfile.save()
            for mfolder in duplicate_of.mfolder_set.all():
                newmfolder= mfolder.duplicate(mfolder.name,save=False,
                                                service=dataservice)
                newmfolder.service = dataservice
                newmfolder.save()

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

        if settings.PRESTOPRIME:
            mp_delivery_multi = ManagementProperty(
                    property="deliverySuccessMultiplier_GB",
                    base=dataservice,
                    value=settings.DEFAULT_DELIVERY_SUCCESS_MULTIPLIER_GB)
            mp_delivery_multi.save()
            mp_delivery_const = ManagementProperty(
                    property="deliverySuccessConstant_Minutes",
                    base=dataservice,
                    value=settings.DEFAULT_DELIVERY_SUCCESS_CONSTANT_MIN)
            mp_delivery_const.save()

        defprofile = DEFAULT_PROFILE
        if self.default_profile != None and self.default_profile != "":
            defprofile = self.default_profile

        managementproperty = ManagementProperty(property="profile",
                                                base=dataservice, value=defprofile)
        managementproperty.save()

        for profile_name in static.default_profiles.keys():
            profile = static.default_profiles[profile_name]
            dsp = DataServiceProfile(service=dataservice, name=profile_name)
            dsp.save()

            keys = profile.keys()
            keys.sort()
            for workflow_name in keys:
                workflow = profile[workflow_name]
                wflow = DataServiceWorkflow(profile=dsp, name=workflow_name)
                wflow.save()

                tasksets = workflow['tasksets']
                dstaskset = None
                prev = None
                order = 0
                for taskset in tasksets:
                    tsname = taskset['name']
                    dstaskset = DataServiceTaskSet(name=tsname,
                                                workflow=wflow, order=order)
                    dstaskset.save()
                    order = order +1
                    if prev:
                        prev.next = dstaskset
                        prev.save()

                    _tasks = taskset['tasks']
                    for task in _tasks:
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
                    prev = dstaskset
        return dataservice

    def get_rate_for_metric(self, metric):
        if metric == METRIC_CONTAINER:
            return 1

    def save(self, *args, **kwargs):
        initial = not self.id
        if initial:
            self.id = utils.random_id()
        super(HostingContainer, self).save(*args, **kwargs)
        if initial:
            managementproperty = ManagementProperty(property="accessspeed", \
                    base=self, value=settings.DEFAULT_ACCESS_SPEED)
            managementproperty.save()

            hostingcontainerauth = Auth(base=self, authname="full")
            hostingcontainerauth.setroles(['containeradmin'])
            hostingcontainerauth.save()

    def _delete_usage_(self):
        for usage in self.usages.all():
            usage_store._stoprecording_(usage)


class DataServiceProfile(models.Model):
    """A DataServiceProfile holds workflows for a dataservice"""
    service = models.ForeignKey('DataService', related_name="profiles")
    """The :class:`.DataService` that this profile relates to"""
    name = models.CharField(max_length=200)
    """The name of the profile"""

    def tasksets_url(self):
        """The REST API url for the tasksets this DataServiceProfile"""
        return reverse('dataservice_profiles_tasksets',
                        args=[self.service.id, self.id])

    def tasks_url(self):
        """The REST API url for the tasks this DataServiceProfile"""
        return reverse('dataservice_profiles_tasks',
                        args=[self.service.id, self.id])

    def __unicode__(self):
        return "Profile %s for %s" % (self.name, self.service.name)


class DataServiceWorkflow(models.Model):
    """A DataServiceWorkflow holds an ordered set of tasksets to be executed"""
    profile = models.ForeignKey(DataServiceProfile, related_name="workflows")
    """The :class:`.DataServiceProfile` that this workflow relates to"""
    name = models.CharField(max_length=200)
    """The name of the workflow"""

    def __unicode__(self):
        return "Workflow %s for %s" % (self.name, self.profile.name)

    def create_workflow_job(self, mfileid):
        """Start a workflow job with the initial task of this workflow"""
        # TODO - Rename Method
        initial = self.tasksets.get(order=0)
        if initial is None:
            raise Exception("Workflow has no initial taskset to run")
        return self.continue_workflow_job(mfileid, initial.id)

    def continue_workflow_job(self, mfileid, taskid):
        """Continue workflow job with the next task of this workflow,taskid"""
        thistask = self.tasksets.get(id=taskid)
        if thistask is None:
            raise Exception("Workflow %s has no taskset to run", self.name)

        mfile = MFile.objects.get(id=mfileid)
        from jobservice.models import Job
        jobname = "Workflow %s - %s" % (self.name, thistask.name)
        job = Job(name=jobname, mfile=mfile)
        job.save()
        tsr = thistask.create_workflow_taskset(mfileid, job)
        job.taskset_id = tsr.taskset_id
        job.save()

        _tasks = self.tasksets.filter(order__gt=thistask.order)\
                                                .order_by("order")
        if len(_tasks) > 0:
            continue_workflow_taskset.delay(mfileid, job.id, _tasks[0].id )
        else:
            logging.info("Last job %s in workflow running", thistask.order)
        return job


class DataServiceTaskSet(models.Model):
    """A DataServiceTaskSet holds a set of tasks to be executed"""
    name = models.CharField(max_length=200)
    """The name of the taskset"""
    workflow = models.ForeignKey(DataServiceWorkflow, related_name="tasksets")
    """The :class:`.DataServiceWorkflow` that this task set relates to"""
    order = models.IntegerField()
    """The order of the task set"""

    class Meta:
        ordering = ["order"]

    def url(self):
        """The REST API url for this DataServiceTaskSet"""
        return reverse('dataservice_profiles_tasksets',
                        args=[self.workflow.profile.service.id,
                            self.workflow.profile.id, self.id])

    def create_workflow_taskset(self, mfileid, job):
        """Create a set of tasks, add them to the queue to be executed"""
        in_tasks = filter(lambda t : t != None ,
                    [_task.create_workflow_task(mfileid, job)
                        for _task in self.tasks.all()])
        ts = TaskSet(tasks=in_tasks)
        tsr = ts.apply_async()
        tsr.save()
        return tsr


class DataServiceTask(models.Model):
    """A DataServiceTask holds a description of a single task to be executed"""
    name = models.CharField(max_length=200)
    """The name of the task"""
    taskset = models.ForeignKey(DataServiceTaskSet, related_name="tasks")
    """The :class:`.DataServiceTaskSet` that this task relates to"""
    task_name = models.CharField(max_length=200, choices=TASK_CHOICES)
    """The name of the celery registered task"""
    condition = models.CharField(max_length=200, blank=True, null=True)
    """A condition to evaluate to see if the task is run"""
    args = models.TextField(blank=True, null=True)
    """Arguments to be passed to the task execution"""

    def url(self):
        """The REST API url for this DataServiceTask"""
        return reverse('dataservice_profiles_tasks',
                        args=[  self.taskset.workflow.profile.service.id,
                                self.taskset.workflow.profile.id, self.id])
                            
    def create_workflow_task(self, mfileid, job):
        """Creates a celery executable task for this DataServiceTask"""
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

        from jobservice import get_task_description

        job_description = get_task_description(task_name)
        nboutputs = job_description['nboutputs']
        for i in range(0, nboutputs):
            outputmimetype = \
                job_description["output-%s" % i]["mimetype"]
            from jobservice.models import JobOutput
            output = JobOutput(name="Output%s-%s" % (i, task_name),
                                job=job, mimetype=outputmimetype)
            output.save()
            output_arr.append(output.id)

        prioritise = job.mfile.service.priority
        queue = "normal.%s" % (task_name)
        if prioritise:
            queue = "priority.%s" % (task_name)
        options = {"routing_key": queue}
        task = subtask(task=task_name,
                        args=[[mfileid], output_arr, args],
                        options=options)
        logging.info("Task created %s ", task)

        return task

    def __unicode__(self):
        return "Task %s for %s" % (self.task_name, self.taskset.name)

class DataService(NamedBase):
    """
    A DataService hold a logic structure of :class:`.MFile` objects and
    :class:`.MFolder` objects that represent a file system.

    A DataService can be in one of many :class:`DataServiceProfile`,
    each of which has different tasks that are run upon ingest, update and
    access of Mfiles

    """
    container = models.ForeignKey(HostingContainer, blank=True, null=True)
    """The :class:`.HostingContainer` that this task relates to"""
    parent = models.ForeignKey('DataService', blank=True, null=True,
                                    related_name="subservices")
    """The :class:`.DataService` that is this services parent if this a subservice"""
    starttime = models.DateTimeField(blank=True, null=True)
    """Start time of the service"""
    endtime = models.DateTimeField(blank=True, null=True)
    """End time of the service"""
    priority = models.BooleanField(default=False)
    """If the service is in priority mode"""
    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {
        "auths": ["GET", "PUT", "POST", "DELETE"],
        "properties": ["GET", "PUT"],
        "usages": ["GET"],
        "mfiles": ["GET","PUT", "POST","DELETE"],
        "mfolders": ["GET", "POST","PUT","DELETE"],
        "jobs": ["GET"],
        "profiles": ["GET"],
        }

    def url(self):
        """The REST API url for this DataService"""
        return reverse('dataservice', args=[self.id])

    def webdav_url(self):
        """The WebDAVurl for this Container"""
        return reverse('webdav', args=[self.id])

    def stats_url(self):
        """The REST API url for stats for this service, used by html views"""
        return reverse('stats', args=[self.id])

    def usage_url(self):
        """The REST API url for usage for this service"""
        return reverse('dataservice_usagesummary', args=[self.id])

    def properties_url(self):
        """The REST API url for properties for this service"""
        return reverse('dataservice_props', args=[self.id])

    def profiles_url(self):
        """The REST API url for properties for this service"""
        return reverse('dataservice_profiles', args=[self.id])

    def subservices_url(self):
        """The REST API url for subservice for this service"""
        return reverse('dataservice_subservices', args=[self.id])

    def mfiles_url(self):
        """The REST API url for mfiles for this service"""
        return reverse('dataservice_mfiles', args=[self.id])

    def get_folder_for_paths(self, paths):
        """Tries to find a folder at the specified paths ['path','to','folder'] """
        try:
            if len(paths) > 0:
                foldername = paths[0]
                folder = self.mfolder_set.get(name=foldername, parent=None)
                if len(paths[1:]) == 0:
                    return folder
                else:
                    return folder.get_folder_for_paths(paths[1:])
            else:
                return None
        except:
            raise e

    def get_file_for_paths(self, paths):
        """Tries to find a file at the specified paths ['path','to','file'] """
        try:
            if len(paths) > 0:
                name = paths[0]
                try:
                    mfile = self.mfile_set.get(name=name, folder=None)
                    return mfile
                except MFile.DoesNotExist:
                    folder = self.mfolder_set.get(name=name, parent=None)
                    if folder:
                        return folder.get_file_for_paths(paths[1:])
            else:
                return None
        except:
            raise e

    def folder_structure(self):
        """Returns the folder structure for the UI to display"""
        return self._folder_structure(self.id)

    def _folder_structure(self, id=None):
        structure = self.__subfolder_structure(None, id=id)
        return {"data": structure}

    def __subfolder_structure(self, mfolder, id=None):

        thisid = id or self.id

        _dict = {}
        if mfolder:
            _dict["data"] = mfolder.name
            _dict["attr"] = {"id": mfolder.id}
        else:
            _dict["data"] = self.name
            _dict["attr"] = {"id": thisid, "class": "service"}

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

        _dict["children"] = children
        return _dict

    def __init__(self, *args, **kwargs):
        super(DataService, self).__init__(*args, **kwargs)
        self.metrics = SERVICE_METRICS

    def get_usage(self):
        """Returns all usage for this service, including child resources"""
        ids = [mfile.id for mfile in self.mfile_set.all()] \
                + [job.id for job in self.jobs()] + [self.id]
        thisusage = Usage.objects.filter(base__in=ids)
        return thisusage

        from jobservice.models import JobASyncResult
        asyncs = JobASyncResult.objects.filter(job__in=self.jobs())\
                                        .values_list("async_id",flat=True)
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
        """Returns a usage summary for this service, including child resources"""
        ids = [mfile.id for mfile in self.mfile_set.all()] \
                + [job.id for job in self.jobs()] + [self.id]
        usages = Usage.objects.filter(base__in=ids)
        summary = self._usages_to_summary(usages)
        summary.extend(Usage.get_job_usagesummary(self.jobs()))
        return summary


    def create_subservice(self, name, save=True):
        """Create a subservice with this service as the parent"""
        if self.parent:
            service = self.parent.create_subservice(name, save=False)
            service.parent = self
            service.save()
            return service
        elif self.container:
            service = self.container.create_data_service(name,
                                                        duplicate_of=self)
            return service
        else:
            return HttpResponseBadRequest()

    def thumbs(self):
        """A list of 4 thumbnail images representing this service"""
        thumbs = []
        for mfile in self.mfile_set.exclude(thumb__exact='')[:4]:
            thumbs.append(mfile.thumburl())
        for i in range(len(thumbs), 4):
            thumbs.append(os.path.join(settings.MEDIA_URL,
                            "images", "package-x-generic.png"))
        return thumbs

    def get(self, url, *args, **kwargs):
        """Perform a GET on this service"""
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
        if not url:
            return self

    def jobs(self):
        """Returns all jobs for this service"""
        from jobservice.models import Job
        mfiles = MFile.objects.filter(service=self).all()
        return Job.objects.filter(mfile__in=mfiles)

    def mfiles(self):
        """Returns all MFiles for this service"""
        return self.mfile_set.all()

    def check_times(self):
        """Check if now() is in this service start and end times"""
        now = datetime.datetime.now()
        if (self.starttime and now < self.starttime)\
                or (self.endtime and now > self.endtime):
            _json = {"error" : "The service is only avaliable between %s and %s"
                            % (self.starttime, self.endtime) }
            return HttpResponseForbidden(_json, mimetype="application/json" )
        return None

    def post(self, url, *args, **kwargs):
        """Perform a POST on this service"""
        # TODO : Jobs
        logging.info("%s %s ", args, kwargs)

        if url == "mfiles":

            check = self.check_times()
            if check:
                return check

            if self.parent:
                mfile = self.create_mfile(kwargs['name'], file=kwargs['file'])
                self.parent.__duplicate__(mfile, ignore_services=[self.id])
                return mfile
            else:
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

    def __duplicate__(self, mfile, ignore_services=[]):
        newmfile = mfile.duplicate(save=False, service=self)
        newmfile.service = self
        newmfile.save()
        for subservice in self.subservices.all():
            if subservice.id not in ignore_services:
                subservice.__duplicate__(mfile)

    def put(self, url, *args, **kwargs):
        """Perform a PUT on this service"""
        if self.parent:
            return self.parent.put(url, *args, **kwargs)
        if "request" in kwargs:
            request = kwargs["request"]
            if "name" in request.POST:
                self.name = request.POST["name"]
            if "priority" in request.POST:
                if request.POST['priority'] == "True"\
                        or request.POST['priority'] == "true":
                    self.priority = True
                if request.POST['priority'] == "False"\
                        or request.POST['priority'] == "false":
                    self.priority = False
            self.save()
        return self

    def get_rate_for_metric(self, metric):
        if self.parent:
            return self.parent.get_rate_for_metric(metric)
        if metric == METRIC_SERVICE:
            return 1

    def get_profile(self):
        """Get the current profile for this service"""
        if self.parent:
            return self.parent.get_profile()
        try:
            manage_prop = self.managementproperty_set.get(property="profile")
            return manage_prop.value
        except ManagementProperty.DoesNotExist:
            return DEFAULT_PROFILE

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        super(DataService, self).save(*args, **kwargs)

    def clean_base(self, authid):
        """Called by an Auth to return a cleaned version of this service"""
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
        for usage in self.usages.all():
            usage_store._stoprecording_(usage, obj=self.container)

    def create_mfolder(self, name, parent=None, duplicate_of=None):
        """Create a MFolder at this service with optional parent"""
        if self.parent:
            return self.parent.create_mfolder(name, parent=None,
                                duplicate_of=duplicate_of)
        try:
            MFolder.objects.get(name=name, service=self, parent=parent,
                                duplicate_of=duplicate_of)
            return rc.DUPLICATE_ENTRY
        except MFolder.DoesNotExist:
            folder = MFolder(name=name, service=self, parent=parent,
                                duplicate_of=duplicate_of)
            folder.save()
            return folder

    def get_unique_name(self, name, folder=None):
        """Get a unique name for an new MFile object"""
        # TODO: get race conditions here?
        # Check for duplicate name
        fn, ext = os.path.splitext(name)
        done = False
        num = 0
        while not done:
            existing_files = MFile.objects.filter(name=name, folder=folder,
                                                    service=self)
            if len(existing_files) == 0:
                done = True
            else:
                num = num + 1
                name = "%s-%s%s" % (fn, str(num), ext)
        return name

    def create_mfile(self, name, file=None, request=None, response=None,
                        post_process=True, folder=None, duplicate_of=None):
        """

        Create a MFile at this service from the file object or the request
        object. The boolean post_process will make the 'ingest' workflow
        run or not, which can be used for partial content uploads. The folder
        objects will create the file in a specific MFolder.

        """
        logging.info("Create Mfile %s", self)
        service = self
        name = self.get_unique_name(name, folder)
        length = 0

        if request:
            mfile = MFile(name=name, service=service, empty=True,
                          duplicate_of=duplicate_of)
            utils.write_request_to_field(request, mfile.file, name)
        elif file == None:
            emptyfile = ContentFile('')
            mfile = MFile(name=name, service=service, empty=True,
                          duplicate_of=duplicate_of)
            mfile.file.save(name, emptyfile)
        else:
            if type(file) == ContentFile:
                mfile = MFile(name=name, service=service,
                                duplicate_of=duplicate_of)
                mfile.file.save(name, file)
                length = mfile.file.size
            else:
                mfile = MFile(name=name, service=service, file=file,
                                empty=False, duplicate_of=duplicate_of)
                mfile.save()
                length = mfile.file.size

        mfile.folder = folder
        mfile.size = length
        mfile.mimetype = mimefile([mfile.id], [], {})["mimetype"]
        mfile.save()

        if not duplicate_of:
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
    """

    A RemoteMServeService is a link to another MServe that a user can use with
    the OAuth protocol to transfer files.

    """
    url = models.URLField()
    """The url of the remote MServe service"""
    name = models.CharField(max_length=200)
    """The name of the remote MServe service"""

    def __unicode__(self):
        return "MServe : %s" % (self.name)


class MFolder(NamedBase):
    """A MFolder is a representation of a file system folder in a service"""
    service = models.ForeignKey(DataService)
    """The :class:`.DataService` that this folder belongs to"""
    parent = models.ForeignKey('self', null=True, blank=True)
    """The parent :class:`.MFolder`"""
    duplicate_of = models.ForeignKey('MFolder', null=True,
                                    blank=True, related_name='duplicated_from')
    """The :class:`.MFolder` if this folder is a duplicate of another"""

    def get_folder_for_paths(self, paths):
        """Tries to find a folder at the specified paths ['path','to','folder'] """
        try:
            if len(paths) > 0:
                foldername = paths[0]
                folder = self.mfolder_set.get(name=foldername, parent=self)
                if len(paths[1:]) == 0:
                    return folder
                else:
                    return folder.get_folder_for_paths(paths[1:])
            else:
                return None
        except Exception as e:
            raise e
            return None

    def get_file_for_paths(self, paths):
        """Tries to find a file at the specified paths ['path','to','file'] """
        try:
            if len(paths) > 0:
                name = paths[0]
                try:
                    mfile = self.mfile_set.get(name=name, folder=self)
                    return mfile
                except MFile.DoesNotExist:
                    folder = self.mfolder_set.get(name=name, parent=self)
                    if folder:
                        return folder.get_file_for_paths(paths[1:])
            else:
                return None
        except Exception as e:
            raise e
            return None

    def duplicate(self, name, save=True, service=None):
        """Make a duplicate of the MFolder and sub folder structure"""
        if service:
            new_mfolder = service.create_mfolder(name,
                                            duplicate_of=self)
        else:
            new_mfolder = self.service.create_mfolder(name,
                                            duplicate_of=self)
        if save:
            new_mfolder.save()

        return new_mfolder

    def make_copy(self, name, parent):
        """Makes a copy of the MFolder anf entire sub folder structure"""
        if name == None:
            name = self.name

        new_mfolder = MFolder(name=name, service=self.service, parent=parent)
        new_mfolder.save()

        for mfile in self.mfile_set.all():
            new_mfile = MFile(name=mfile.name, file=mfile.file,
                                folder=new_mfolder, mimetype=mfile.mimetype,
                                empty=False, service=mfile.service)
            new_mfile.save()

        for submfolder in self.mfolder_set.all():
            new_submfolder = submfolder.make_copy(submfolder.name, new_mfolder)
            new_submfolder.save()

        new_mfolder.save()
        return new_mfolder

    def __unicode__(self):
        return "MFolder: %s " % self.name

    def get_rel_path(self):
        """Gets the relative path for the mfolder in the current hierarchy"""
        if self.parent is not None:
            return os.path.join(self.parent.get_rel_path(), self.name)
        else:
            return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        super(MFolder, self).save(*args, **kwargs)


class Relationship(models.Model):
    ''' A relationship between two MFiles '''
    name = models.CharField(max_length=200)
    """Name of the relationship"""
    entity1 = models.ForeignKey('MFile', related_name="related_left")
    """The :class:`.Mfile` of the first entity in the relationship"""
    entity2 = models.ForeignKey('MFile', related_name="related_right")
    """The :class:`.Mfile` of the second entity in the relationship"""

    def left(self):
        return self.entity1.serialize()

    def right(self):
        return self.entity2.serialize()

class MFile(NamedBase):
    """
    An MFile represents a single file on the system at a service
    """
    # TODO : Add bitmask to MFile for deleted,remote,input,output, etc
    empty = models.BooleanField(default=False)
    """If the file is empty"""
    service = models.ForeignKey(DataService)
    """The :class:`.DataService` that this file belongs to"""
    folder = models.ForeignKey(MFolder, null=True)
    """The :class:`.MFolder` that contains this MFile"""
    file = models.FileField(upload_to=utils.mfile_upload_to,
                        blank=True, null=True, max_length=FILE_FIELD_LENGTH,
                        storage=storage.getdiscstorage())
    mimetype = models.CharField(max_length=200, blank=True, null=True)
    """The mimetype of the file"""
    checksum = models.CharField(max_length=32, blank=True, null=True)
    """The md5 checksum of the file"""
    size = models.BigIntegerField(default=0)
    """The size of the file in bytes"""
    thumb = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getthumbstorage())
    poster = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getposterstorage())
    proxy = models.ImageField(upload_to=utils.create_filename,
                            null=True, storage=storage.getproxystorage())
    updated = models.DateTimeField(auto_now=True)
    """The last time the file was updated"""
    duplicate_of = models.ForeignKey('MFile', null=True)
    """The duplicate of this file. Not the same as :class:`BackupFile`"""

    methods = ["GET", "POST", "PUT", "DELETE"]
    urls = {
            "auths": ["GET", "PUT", "POST", "DELETE"],
            "properties": [],
            "usages": ["GET"],
            "file": ["GET", "PUT", "DELETE"],
            "workflows": ["GET", "POST"],
            "jobs": ["GET", "POST"],
            }

    def url(self):
        """The REST API url for this MFile"""
        return reverse('mfile', args=[self.id])

    def relations(self):
        return Relationship.objects.filter(Q(entity1=self)|Q(entity2=self))

    def stats_url(self):
        """The REST API url for stats for this MFile, used by html views"""
        return reverse('stats', args=[self.id])

    def jobs_url(self):
        """The REST API url for jobs for this MFile"""
        return reverse('mfile_jobs', args=[self.id])

    def usage_url(self):
        """The REST API url for usage for this MFile"""
        return reverse('mfile_usagesummary', args=[self.id])

    def get_download_path(self):
        """The REST API url for downloading this MFile"""
        return reverse('mfile_download', args=[self.id])

    def get_upload_thumb_path(self):
        """The REST API url for uploading a new thumbnail"""
        return reverse('mfile_upload_thumb', args=[self.id])

    def get_upload_poster_path(self):
        """The REST API url for uploading a new poster"""
        return reverse('mfile_upload_poster', args=[self.id])

    def get_upload_proxy_path(self):
        """The REST API url for uploading a new proxy"""
        return reverse('mfile_upload_proxy', args=[self.id])

    @staticmethod
    def get_mfile_plots(request, baseid=None):
        """Get any plots to be charted in the GUI, currently return []"""
        return []

    class Meta:
        ordering = ('-created', 'name')

    def __unicode__(self):
        return "MFile  %s" % (self.name.encode("utf-8"))

    def __str__(self):
        return "MFile  %s" % (self.name.encode("utf-8"))


    def delete(self):
        """Delete this MFile and any duplicates"""
        if self.duplicate_of:
            self.duplicate_of.delete()
        else:
            super(MFile, self).delete()

    def __init__(self, *args, **kwargs):
        super(MFile, self).__init__(*args, **kwargs)
        self.metrics = MFILE_METRICS

    def get_usage(self):
        """Returns all usage for this MFile, including child resources"""
        ids = [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return usages

    def get_usage_summary(self):
        """Returns a usage summary for this MFile, including child resources"""
        ids = [self.id]
        usages = Usage.objects.filter(base__in=ids)
        return self._usages_to_summary(usages)

    def get(self, url, *args, **kwargs):
        """Perform a GET on this MFile"""
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
        """Perform a POST on this MFile"""
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
        """Perform a PUT on this MFile"""
        if url == None:
            if 'file' in kwargs:
                file = kwargs['file']
                self.update_mfile(self.name, file=file, post_process=True,
                                    folder=self.folder)
                return self
            return HttpResponseBadRequest()
        return HttpResponseNotFound()

    def serialize(self):
        """Called by piston handlers to return a flat version of the model """
        mfiledict = {}
        mfiledict["id"] = self.id
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

    def clean_base(self, authid):
        """Called by an Auth to return a cleaned version of this mfile"""
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

        thisfile = mfile.file

        sigret = MFILE_GET_SIGNAL.send(sender=self, mfile=mfile)

        for k, v in sigret:
            logging.info("Signal %s returned %s ", k, v)

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
                usage_store.record(mfile.id, METRIC_CORRUPTION, 1)
                try:
                    backup = BackupFile.objects.get(mfile=mfile)
                    check3 = mfile.checksum
                    if os.path.exists(backup.file.path):
                        check4 = utils.md5_for_file(backup.file)
                        if(check3 == check4):
                            shutil.copy(backup.file.path, mfile.file.path)
                            thisfile = backup.file
                        else:
                            logging.info("The file %s has been lost", mfile)
                            usage_store.record(mfile.id,
                                                METRIC_DATALOSS, mfile.size)
                            return rc.NOT_HERE
                except BackupFile.DoesNotExist as e:
                    logging.info("There is no backup file for %s ", mfile)
                    return rc.NOT_HERE

        thisfile = mfile.file

        MFILE_GET_SIGNAL.send(sender=self, mfile=mfile)

        if accessspeed == "unlimited":
            dlfoldername = "dl"
        else:
            dlfoldername = os.path.join("dl", accessspeed)

        path = unicode(thisfile)

        redirecturl = utils.gen_sec_link_orig(thisfile.name, dlfoldername)
        logging.info("%s %s ", thisfile.name, dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT, dlfoldername, path)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = thisfile.path

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            logging.info("Linking ")
            logging.info("   %s ", mfilefilepath)
            logging.info("to %s ", fullfilepath)
            try:
                os.link(mfilefilepath, fullfilepath)
            except:
                logging.info("Caught error linking file, trying copy.")
                shutil.copy(mfilefilepath, fullfilepath)

        usage_store.record(mfile.id, METRIC_ACCESS, mfile.size)

        redirecturl = os.path.join("/", redirecturl)
        return HttpResponseRedirect(redirecturl)

    def update_mfile(self, name=None, file=None, request=None,
                        post_process=True, folder=None,
                        duplicate_of=None,  response=None):
        """

        Update an MFile at this service from the file object or the request
        object. The boolean post_process will make the 'update' workflow
        run or not, which can be used for partial content uploads. The folder
        objects will update the file to the specificed MFolder.

        """
        logging.info("Update Mfile %s", self)

        if name == None:
            name = self.name

        if request:
            utils.write_request_to_field(request, self.file , self.name)
        elif file != None:
            if type(file) == ContentFile:
                self.file.save(name, file)
            else:
                self.file.save(name, File(file))

        if duplicate_of:
            self.duplicate_of = duplicate_of

        self.name = name

        if folder:
            self.folder = folder

        self.mimetype = mimefile([self.id], [], {})["mimetype"]

        if file:
            self.size = os.stat(self.file.path).st_size
            usage_store.record(self.id, METRIC_INGEST, int(self.size))
        
        self.save()

        logging.info("MFile update '%s' ", self.name)
        logging.info("MFile PATH %s ", self.file.path)
        logging.info("MFile size %s ", self.size)

        if post_process:
            self.create_workflow_job("update")

        return self

    def create_job(self, name):
        """Create a Job Object with this MFile as a parameter"""
        from jobservice.models import Job
        job = Job(name=name, mfile=self)
        job.save()
        return job

    def duplicate(self, save=True, service=None):
        """Create a duplicate MFile with this file as input"""
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
        """Create a read only authority to this MFile"""
        mfileauth_ro = Auth(base=self, authname="%s Read Only" % self)
        mfileauth_ro.setroles(["mfilereadonly"])
        mfileauth_ro.save()
        return mfileauth_ro

    def create_workflow_job(self, name):
        """Create a workflow job from the workflow named 'name' with this MFile
        as input"""
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
        """Post process this MFile, i.e. run the 'ingest' task"""
        return self.create_workflow_job("ingest")

    def get_rel_path(self):
        """Gets the relative path for the mfile in the current hierarchy"""
        if self.folder is not None:
            return os.path.join(self.folder.get_rel_path(), self.name)
        else:
            return self.name

    def get_rate_for_metric(self, metric):
        if not self.duplicate_of:
            if metric == METRIC_MFILE:
                return 1
            if not self.empty:
                if metric == METRIC_DISC:
                    return self.size

    def get_value_for_metric(self, metric):
        if not self.empty and not self.duplicate_of:
            if metric == METRIC_DISC_SPACE:
                return self.size

    def get_updated_value_for_metric(self, metric):
        if not self.duplicate_of:
            if not self.empty:
                if metric == METRIC_DISC_SPACE:
                    return self.size

    def get_updated_rate_for_metric(self, metric):
        if not self.duplicate_of:
            if metric == METRIC_MFILE:
                return 1
            if not self.empty:
                if metric == METRIC_DISC:
                    return self.size

    def thumburl(self):
        """Return the url for the thumbnail of this file. either from the
        thumbnail field or a sensible default"""
        if self.thumb and self.thumb != "":
            return "%s%s" % (settings.THUMB_PATH, self.thumb)
        elif self.mimetype:
            if self.name.endswith(".blend"):
                return os.path.join(settings.MEDIA_URL, "images/blender.png")
            if self.mimetype.startswith("image"):
                return os.path.join(settings.MEDIA_URL,
                    "images", "image-x-generic.png")
            if self.mimetype.startswith("text"):
                return os.path.join(settings.MEDIA_URL,
                    "images", "text-x-generic.png")
        return os.path.join(settings.MEDIA_URL, "images",
                    "package-x-generic.png")

    def posterurl(self):
        """Return the url for the poster of this file. either from the
        poster field or a sensible default"""
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
        return os.path.join(settings.MEDIA_URL,
                                        "images", "package-x-generic.png")

    def proxyurl(self):
        """Return the url for the proxy of this file. either from the
        thumbnail field or a sensible default"""
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
        return os.path.join(settings.MEDIA_URL,
                            "images", "package-x-generic.png")

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        self.updated = datetime.datetime.now()
        if self.file:
            if os.path.exists(self.file.path):
                self.size = self.file.size
            self.empty = False
        super(MFile, self).save(*args, **kwargs)

    def _delete_usage_(self):
        for usage in self.usages.all():
            usage_store._stoprecording_(usage, obj=self.service)


def pre_delete_handler_mfile(sender, instance=None, **kwargs):
    """Handler to catch deletion of mfiles"""
    if instance:
        instance._delete_usage_()

def pre_delete_handler(sender, instance=None, **kwargs):
    """Handler to catch deletion of objects"""
    if instance:
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
    """
    A BackupFile is an internal object to manage replication
    """
    mfile = models.ForeignKey(MFile)
    """The :class:`MFile` this is a backup of"""
    file = models.FileField(upload_to=utils.create_filename,
                            max_length=FILE_FIELD_LENGTH,
                            storage=storage.gettapestorage())
    mimetype = models.CharField(max_length=200, blank=True, null=True)
    """The mimetype of the backup"""
    checksum = models.CharField(max_length=32, blank=True, null=True)
    """The md5sum of the backup"""

    def __init__(self, *args, **kwargs):
        super(BackupFile, self).__init__(*args, **kwargs)
        self.metrics = BACKUPFILE_METRICS

    def get_upload_path(self):
        """The REST API url for uploading a backup file"""
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

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        super(BackupFile, self).save(*args, **kwargs)


class ManagementProperty(models.Model):
    """
    A Management Property holds configuration parameters for HostingContainers
    DataServices and MFiles
    """
    base = models.ForeignKey(NamedBase)
    """The resource this Property relates to"""
    property = models.CharField(max_length=200)
    """The property name"""
    value = models.CharField(max_length=200)
    """The property value"""

    def __unicode__(self):
        return "Management Property %s:%s" % (self.property, self.value)

    def values(self):
        """The possible values for the property"""
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
            return {"type": "string"}


class Auth(Base):
    """
    An Auth object is a capability to access a HostingContainer, DataService
    or MFile
    """
    authname = models.CharField(max_length=50)
    """Name for the Auth"""
    base = models.ForeignKey(NamedBase, blank=True, null=True)
    """The resource this Property relates to"""
    parent = models.ForeignKey('Auth', blank=True, null=True)
    """The parent Auth of this Auth"""
    usages = models.ManyToManyField("Usage")
    """A django many-to-many field to hold :class:`.Usage` """
    roles_csv = models.CharField(max_length=200)
    """A comma separated list of valid roles"""

    def browse_url(self):
        """The REST API url for browsing this Auth"""
        return reverse('browse', args=[self.id])

    def stats_url(self):
        """The REST API url for stats about this auth - used by html views"""
        return reverse('stats', args=[self.id])

    def usage_url(self):
        """The REST API url for usage"""
        return reverse('auth_usagesummary', args=[self.id])

    def base_url(self):
        """The REST API url for the base object this auth is for"""
        return reverse('auth_base', args=[self.id])

    def jobs_url(self):
        """The REST API url for the jobs for this auth"""
        return reverse('auth_jobs', args=[self.id])

    def mfiles_url(self):
        """The REST API url for the jobs for this auth"""
        return reverse('auth_mfiles', args=[self.id])

    def __init__(self, *args, **kwargs):
        super(Auth, self).__init__(*args, **kwargs)

    def geturls(self):
        """Return valid the urls for this Auth"""
        urls = {}
        for rolename in self.getroles():
            urls.update(static.default_roles[rolename]['urls'])
        return urls

    def urls(self):
        """Return valid the urls for this Auth"""
        # TODO: duplicate of above method?
        urls = {}
        for rolename in self.getroles():
            urls.update(static.default_roles[rolename]['urls'])
        return urls

    def basename(self):
        """Return name of the base object"""
        return self.base.name

    def thumburl(self):
        """Return a thumbnail for this Auth"""
        if utils.is_service(self.base):
            dservice = DataService.objects.get(id=self.base.id)
            if len(dservice.mfile_set.all()) > 0:
                return list(dservice.mfile_set.all())[0].thumburl()
        return os.path.join(settings.MEDIA_URL,
                    "images", "package-x-generic.png")

    def getroles(self):
        """Return a list of valid roles"""
        return self.roles_csv.split(",")

    def roles(self):
        """Return a list of valid roles"""
        # TODO: duplicate of above method?
        return self.roles_csv.split(",")

    def setroles(self, new_roles):
        """Set the valid roles for this Auth"""
        for rolename in new_roles:
            if rolename not in static.default_roles.keys():
                raise Exception("Rolename '%s' not valid " % rolename)
        self.roles_csv = ",".join(new_roles)

    def getmethods(self):
        """Get the valid methods for this Auth"""
        methods = []
        for rolename in self.getroles():
            methods = methods + static.default_roles[rolename]['methods']
        return methods

    def check(self, url, method):
        """Check Method 'method' on url 'url' is allowed by this Auth"""
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
        """Get usage for the base object"""
        base = self.get_real_base()
        return base.get_usage()

    def get_usage_summary(self):
        """Get usage summary for the base object"""
        base = self.get_real_base()
        return base.get_usage_summary()

    def get(self, url, *args, **kwargs):
        """Perform a GET on this Auth"""
        logging.info("AUTH %s %s ", self.authname, url)
        if not url:
            return self
        if url == "base":
            return self.get_real_base().clean_base(self.id)
        return self.base.get_real_base().do("GET", url)

    def put(self, url, *args, **kwargs):
        """Perform a PUT on this Auth"""
        return self.get_real_base().do("PUT", url, *args, **kwargs)

    def post(self, url, *args, **kwargs):
        """Perform a POST on this Auth"""
        return self.get_real_base().do("POST", url, *args, **kwargs)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = utils.random_id()
        if not self.roles_csv:
            self.roles_csv = ""
        super(Auth, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Auth: authname=%s base=%s roles=%s "\
                % (self.authname, self.base, ",".join(self.getroles()))
