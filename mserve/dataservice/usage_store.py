from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import Usage
from dataservice.models import UsageRate
from dataservice.models import UsageSummary
from dataservice.models import NamedBase
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import ManagementProperty
from django.core.exceptions import ObjectDoesNotExist
import datetime
import time
import sys

# Metrics for objects
metric_stager = "http://prestoprime/stager"
metric_container = "http://prestoprime/container"
metric_service = "http://prestoprime/service"

# Metrics for Stagers
metric_disc = "http://prestoprime/disc"

metrics = [metric_stager,metric_service,metric_container,metric_disc]

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
    summary.extend(usagesummary_by_base(stager))
    return summary
    
def service_usagesummary(serviceid):
    summary = []
    service  = DataService.objects.get(pk=serviceid)
    stagers = DataStager.objects.filter(service=service)
    for stager in stagers:
        summary.extend(stager_usagesummary(stager.id))
    summary.extend(usagesummary_by_base(service))
    return summary

def container_usagesummary(containerid):
    summary = []
    container = HostingContainer.objects.get(pk=containerid)
    services  = DataService.objects.filter(container=container)
    for service in services:
        summary.extend(service_usagesummary(service.id))
    summary.extend(usagesummary_by_base(container))
    return summary

def usagesummary_by_base(base):
    summary = []
    for metric in metrics:
        summary.extend(usagesummary_by_metric_base(metric,base))
    return summary

def usage_to_summary(usages,metric):
    n,sum,umax,sums = 0,0,0,0
    umin  = sys.float_info.max
    for u in usages:
        n = n + 1
        sum = sum + u.value
        umax = max(umax,u.value)
        umin = min(min,u.value)
        sums = sums + (u.value*u.value)

    summary = UsageSummary(metric=metric,n=n,sum=sum,min=umin,max=umax,sums=sums)
    return summary

def usagesummary_by_metric_base(metric,base):
    print "find usage %s %s" % (metric,base)
    usages = Usage.objects.filter(metric=metric,base=base)
    if len(usages) ==0 :
        return []
    return usage_to_summary(usages,metric)

def usagesummary_by_metric(metric):
    usages = Usage.objects.filter(metric=metric)
    if len(usages) ==0 :
        return []
    return usage_to_summary(usages,metric)

def usagesummary():
    summary = []
    for metric in metrics:
        summary.append(usagesummary_by_metric(metric))
    return summary

def container_progress(containerid):
    return []