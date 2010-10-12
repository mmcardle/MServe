from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import Usage
from dataservice.models import UsageRate
from dataservice.models import UsageSummary
from dataservice.models import UsageReport
from dataservice.models import NamedBase
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import ManagementProperty
from django.core.exceptions import ObjectDoesNotExist
import datetime
import time
import sys
import logging

# Metrics for objects
metric_stager = "http://prestoprime/stager"
metric_container = "http://prestoprime/container"
metric_service = "http://prestoprime/service"

# Metrics for Stagers
metric_disc = "http://prestoprime/disc"

metrics = [metric_stager,metric_service,metric_container,metric_disc]
byte_metrics = [metric_disc]

def record(id,metric,value):
    base = NamedBase.objects.get(pk=id)
    usage = Usage(base=base,metric=metric,value=value)
    usage.save()

def startrecording(id,metric,rate):
    base = NamedBase.objects.get(pk=id)
    usagerate = UsageRate(base=base,metric=metric,rate=rate,usageSoFar=0.0)
    usagerate.save()

def stoprecording(id,metric):
    base = NamedBase.objects.get(pk=id)
    usagerate = UsageRate.objects.get(base=base,metric=metric)
    lastRateTime, lastRate, lastUsage = usagerate.current,usagerate.rate,usagerate.usageSoFar

    now = datetime.datetime.now()

    t2 = time.mktime(now.timetuple())+float("0.%s"%now.microsecond)
    t1 = time.mktime(lastRateTime.timetuple())+float("0.%s"%lastRateTime.microsecond)

    usage = float(lastUsage) + float(lastRate) * (t2 - t1)
    print "Stop Recording Usage = %s" % usage
    record(id, metric, usage)
    usagerate.delete()
    
def stager_usagesummary(stagerid):
    summary = []
    stager = DataStager.objects.get(pk=stagerid)
    ss = __usagesummary_by_base(stager)
    for s in ss:
        summary.append(s)
    dict = {}
    for s in summary:
        m = s.metric
        aggregate = None
        if dict.has_key(m):
            aggregate = dict[m]
        else:
            aggregate = UsageSummary()
            aggregate.metric = m
            aggregate.min = sys.float_info.max
            dict[m] = aggregate

        aggregate.n    += s.n
        aggregate.sum  += s.sum
        aggregate.max  = max(s.max,aggregate.max )
        aggregate.min  = min(s.min,aggregate.min )
        aggregate.sums += s.sums

    return dict.values()
    
def service_usagesummary(serviceid):

    summary = []
    service  = DataService.objects.get(pk=serviceid)

    stagers = DataStager.objects.filter(service=service)
    for stager in stagers:
        ss = stager_usagesummary(stager.id)
        for s in ss:
            summary.append(s)
    ss = __usagesummary_by_base(service)
    for s in ss:
        summary.append(s)

    dict = {}
    for s in summary:
        m = s.metric
        aggregate = None
        if dict.has_key(m):
            aggregate = dict[m]
        else:
            aggregate = UsageSummary()
            aggregate.metric = m
            aggregate.min = sys.float_info.max
            dict[m] = aggregate

        aggregate.n    += s.n
        aggregate.sum  += s.sum
        aggregate.max  = max(s.max,aggregate.max )
        aggregate.min  = min(s.min,aggregate.min )
        aggregate.sums += s.sums

    return dict.values()

def container_usagesummary(containerid):
    summary = []
    container = HostingContainer.objects.get(pk=containerid)

    services  = DataService.objects.filter(container=container)
    for service in services:
        ss = service_usagesummary(service.id)
        for s in ss:
            summary.append(s)
    ss = __usagesummary_by_base(container)
    for s in ss:
        summary.append(s)

    dict = {}
    for s in summary:
        m = s.metric
        aggregate = None
        if dict.has_key(m):
            aggregate = dict[m]
        else:
            aggregate = UsageSummary()
            aggregate.metric = m
            aggregate.min = sys.float_info.max
            dict[m] = aggregate

        aggregate.n    += s.n
        aggregate.sum  += s.sum
        aggregate.max  = max(s.max,aggregate.max )
        aggregate.min  = min(s.min,aggregate.min )
        aggregate.sums += s.sums

    return dict.values()

def __usagesummary_by_base(base):
    
    summary = []
    for metric in metrics:
        s = usagesummary_by_metric_base(metric,base)
        if s is not None:
            summary.append(s)
    return summary

def usage_to_summary(usages):
    if len(usages) == 0:
        return None

    metric = None
    n,sum,umax,sums = 0,0,0,0
    umin  = sys.float_info.max
    for u in usages:
        n = n + 1
        metric = u.metric
        sum = sum + u.value
        umax = max(umax,u.value)
        umin = min(umin,u.value)
        sums = sums + (u.value*u.value)
        
    summary = UsageSummary(metric=metric,n=n,sum=sum,min=umin,max=umax,sums=sums)
    return summary

def usagesummary_by_metric_base(metric,base):
    usages = Usage.objects.filter(metric=metric,base=base)
    return usage_to_summary(usages)

def usagesummary_by_metric(metric):
    usages = Usage.objects.filter(metric=metric)
    return usage_to_summary(usages)

def usagesummary():
    summary = []
    for metric in metrics:
        summary.append(usagesummary_by_metric(metric))
    return summary