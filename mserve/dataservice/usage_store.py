from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import Usage
from dataservice.models import UsageSummary
from dataservice.models import NamedBase
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import ManagementProperty
from django.core.exceptions import ObjectDoesNotExist

# Metrics for objects
metric_stager = "http://prestoprime/stager"
metric_container = "http://prestoprime/container"
metric_service = "http://prestoprime/service"

# Metrics for Stagers
metric_discspace = "http://prestoprime/discspace"

def record(id,metric,value):
    print "Recording %s for metric %s value=%s" % (id,metric,value)
    base = NamedBase.objects.get(pk=id)
    print base
    print Usage.objects.filter(base=base)
    
    print Usage.objects.filter(base=base,metric=metric)
    a = Usage.objects.filter(base=base,metric=metric).update(value=value)
    print Usage.objects.filter(base=base,metric=metric)

def usage_summary():

    stager_summary = UsageSummary(metric=metric_stager,n=DataStager.objects.count,min=0,max=DataStager.objects.count,sums=0)
    service_summary = UsageSummary(metric=metric_service,n=DataService.objects.count,min=0,max=DataService.objects.count,sums=0)
    container_summary = UsageSummary(metric=metric_container,n=HostingContainer.objects.count,min=0,max=HostingContainer.objects.count,sums=0)

    return [stager_summary,service_summary,container_summary]

def container_usage(id):
    print "Container Usage - %s" % id
    usagelist = None
    try:
        usagelist = Usage.objects.filter(base=id)
        print "Usage - %s" % usagelist
        if len(usagelist) == 0:
            print "Usage = 0"
            return __init_container_usage(id)
    except ObjectDoesNotExist:
        return __init_container_usage(id)

    return usagelist

def __init_container_usage(id):
    print "Init Usage for container - %s" % id
    base = NamedBase.objects.get(pk=id)
    serviceusage = Usage(metric=metric_service,base=base)
    serviceusage.save()
    print "Service Usage- %s" % serviceusage
    usagelist = [serviceusage]
    print "created new usage %s" % usagelist
    return usagelist

def service_usage(id):
    print "service usage"
    usagelist = None
    try:
        usagelist = Usage.objects.filter(base=id)
        print "usage list %s"  % usagelist
        if len(usagelist) == 0:
            return __init_service_usage(id)
    except ObjectDoesNotExist:
        return __init_service_usage(id)
    print "usage list %s"  % usagelist
    return usagelist

def __init_service_usage(id):
    base = NamedBase.objects.get(pk=id)
    serviceusage = Usage(metric=metric_stager,base=base)
    serviceusage.save()
    usagelist = [serviceusage]
    print "init usage %s"  % usagelist
    return usagelist

def stager_usage(id):   
    usagelist = None
    try:
        usagelist = Usage.objects.filter(base=id)
        if len(usagelist) == 0:
            return __init_stager_usage(id)
    except ObjectDoesNotExist:
        return __init_stager_usage(id)

    return usagelist

def __init_stager_usage(id):
    base = NamedBase.objects.get(pk=id)
    discusage = Usage(metric=metric_discspace,base=base)
    discusage.save()
    usagelist = [discusage]
    return usagelist