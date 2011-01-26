from mserve.dataservice.models import NamedBase
from dataservice.models import *
import utils as utils
import datetime
import time
import sys
import logging

# Metrics for objects
metric_mfile = "http://prestoprime/file"
metric_backupfile = "http://prestoprime/backupfile"
metric_container = "http://prestoprime/container"
metric_service = "http://prestoprime/service"

# Metrics for mfiles
metric_disc = "http://prestoprime/disc"
metric_disc_space = "http://prestoprime/disc_space"
metric_ingest = "http://prestoprime/ingest"
metric_access = "http://prestoprime/access"
metric_archived = "http://prestoprime/archived"
metric_dataloss = "http://prestoprime/dataloss"
metric_corruption = "http://prestoprime/corruption"
metric_responsetime = "http://prestoprime/responsetime"

metrics = [metric_mfile,metric_service,metric_container,metric_disc,metric_disc_space,metric_ingest,metric_access,metric_archived,metric_dataloss,metric_corruption,metric_responsetime]

# What metric are reported fro each type
container_metrics = metrics
service_metrics = [metric_mfile,metric_service,metric_disc,metric_archived,metric_dataloss,metric_corruption,metric_responsetime,metric_disc_space]
mfile_metrics = [metric_mfile,metric_disc,metric_ingest,metric_access,metric_archived,metric_dataloss,metric_corruption,metric_responsetime,metric_disc_space]
backupfile_metrics = [metric_archived,metric_backupfile,metric_disc_space]

# Other Metric groups
byte_metrics = [metric_disc_space]

def record(id,metric,value,report=True):
    base = NamedBase.objects.get(pk=id)
    usage = Usage(base=base,metric=metric,value=value)
    usage.save()
    if report:
        reportusage(base)

def startrecording(id,metric,rate,report=True):
    base = NamedBase.objects.get(pk=id)
    logging.info("base %s "% base)

    #obj, created = UsageRate.objects.get_or_create(base=base,metric=metric,rate=rate,usageSoFar=0.0,current=datetime.datetime.now())
    #if created:
    #    logging.info("created %s "% obj)
    #else:
    #    logging.info("existing %s " % obj)

    try:
        usagereport = UsageRate.objects.get(base=base,metric=metric)
        logging.info("usagereport %s "% usagereport)
        if rate == usagereport.rate:
            logging.info("Usage allready exists for %s at current rate %s " % (usagereport.metric,rate))
        else:
            logging.info("Usage allready exists for %s at rate %s, changing rate %s " % (usagereport.metric, usagereport.rate, rate))
            c = usagereport.current

            todate = datetime.datetime.now()
            td = todate-usagereport.current
            dif = (td.days*24*60*60)+ td.seconds + (td.microseconds/1000000.0)

            amount = dif*usagereport.rate

            usagereport.usageSoFar = usagereport.usageSoFar + amount
            usagereport.current = todate
            usagereport.rate = rate
            usagereport.save()

    except UsageRate.DoesNotExist:
        logging.info("DoesNotExist  ")
        usagereport = UsageRate(base=base,metric=metric,rate=rate,usageSoFar=0.0,current=datetime.datetime.now())
        logging.info("created %s " % usagereport)
        usagereport.save()

    if report:
        reportusage(base)

def stoprecording(id,metric,report=True):
    logging.debug("Stop Recording "+id)
    base = NamedBase.objects.get(pk=id)
    usagerates = UsageRate.objects.filter(base=base,metric=metric)

    if len(usagerates)>1:
        for ur in usagerates:
            logging.debug("XXX Found duplicate usage - %s" % ur)
    usagerate = UsageRate.objects.get(base=base,metric=metric)
    lastRateTime, lastRate, lastUsage = usagerate.current,usagerate.rate,usagerate.usageSoFar

    now = datetime.datetime.now()

    t2 = time.mktime(now.timetuple())+float("0.%s"%now.microsecond)
    t1 = time.mktime(lastRateTime.timetuple())+float("0.%s"%lastRateTime.microsecond)

    usage = float(lastUsage) + float(lastRate) * (t2 - t1)
    print "Stop Recording Usage = %s" % usage
    record(id, metric, usage)
    usagerate.delete()
    if report:
        reportusage(base)
    
def reportusage(base):
    #logging.info("Report usage %s" % base)
    toreport = []

    if utils.is_container(base):
        logging.info("Base %s "%base)
        toreport =  [base]

    if utils.is_service(base):
        container = HostingContainer.objects.get(dataservice=base)
        container.reportnum += 1
        container.save()

        toreport =  [container,base]

    if utils.is_mfile(base):
        service   = DataService.objects.get(mfile=base)
        service.reportnum += 1
        service.save()
        container = HostingContainer.objects.get(dataservice=service)
        container.reportnum += 1
        container.save()

        toreport =  [container,service,base]

    for ob in toreport:
        #logging.info("Reporting usage for %s "%ob)
        reports = UsageReport.objects.filter(base=ob)
        for r in reports:
            #logging.info("\tReport %s "%r)
            r.reportnum = r.reportnum + 1
            r.save()

def mfile_usagesummary(mfileid):
    summary = []
    mfile = MFile.objects.get(pk=mfileid)
    ss = __usagesummary_by_base(mfile)
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

    logging.info("Getting usagesummary for %s " % service)

    mfiles = MFile.objects.filter(service=service)

    for mfile in mfiles:
        logging.info("Getting usagesummary for %s " % mfile)
        ss = mfile_usagesummary(mfile.id)
        for s in ss:
            summary.append(s)
    ss = __usagesummary_by_base(service)
    for s in ss:
        summary.append(s)

    logging.info("Usagesummarys  %s " % summary)

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

    logging.info("Usagesummarys  %s " % dict.values())

    return dict.values()


def mfile_inprogresssummary(mfile):
    s = MFile.objects.get(pk=mfile)
    inprogress = []
    for p in UsageRate.objects.filter(base=mfile):
        logging.info("mfile_inprogresssummary %s " % p)
        inprogress.append(p)

    if len(inprogress)==0:
        return []

    return inprogress_to_aggregates(s, inprogress, mfile_metrics)

def __mfile_inprogresssummary__(mfile):
    inprogress = []
    for p in UsageRate.objects.filter(base=mfile):
        inprogress.append(p)
    return inprogress


def service_inprogresssummary(service):
    ser = DataService.objects.get(pk=service)
    mfiles = MFile.objects.filter(service=service)
    inprogress = []
    for mfile in mfiles:
        for s in __mfile_inprogresssummary__(mfile):
            inprogress.append(s)

    for p in UsageRate.objects.filter(base=service):
        inprogress.append(p)

    if len(inprogress)==0:
        return []

    return inprogress_to_aggregates(ser, inprogress, service_metrics)

def __service_inprogresssummary__(service):
    inprogress = []
    mfiles = MFile.objects.filter(service=service)
    for mfile in mfiles:
        for s in __mfile_inprogresssummary__(mfile):
            inprogress.append(s)

    for p in UsageRate.objects.filter(base=service):
        inprogress.append(p)

    return inprogress

def container_inprogresssummary(container):
    c = HostingContainer.objects.get(pk=container)
    services = DataService.objects.filter(container=container)
    inprogress = []
    for service in services:
        for s in __service_inprogresssummary__(service):
            inprogress.append(s)

    for p in UsageRate.objects.filter(base=container):
        inprogress.append(p)

    if len(inprogress)==0:
        return []

    return inprogress_to_aggregates(c, inprogress, container_metrics)

def inprogress_to_aggregates(base,inprogress,base_metrics):
    maxdate = None
    for inp in inprogress:
        if maxdate == None:
            maxdate = inp.current
        else:
            maxdate = max(maxdate,inp.current)

    for ur in inprogress:
        __update_usagereport__(ur,maxdate)

    aggregates = {}

    for metric in base_metrics:
        aggregates[metric] = agg = AggregateUsageRate(base=base,current=maxdate)
        agg.usageSoFar = 0.0
        agg.rate = 0.0 
        agg.metric=metric

    for usage in inprogress:
        if aggregates.has_key(usage.metric):
            agg_ur = aggregates[usage.metric]
            agg_ur.rate = agg_ur.rate + usage.rate
            agg_ur.usageSoFar = agg_ur.usageSoFar + usage.usageSoFar
            agg_ur.count = agg_ur.count+1

    logging.info(aggregates)

    return aggregates.values()

def __update_usagereport__(usagereport,todate):
    c = usagereport.current
    if c == todate:
        return

    td = todate-usagereport.current
    dif = (td.days*24*60*60)+ td.seconds + (td.microseconds/1000000.0)

    amount = dif*usagereport.rate

    usagereport.usageSoFar = usagereport.usageSoFar + amount
    usagereport.current = todate
    usagereport.save()

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

    return [] + dict.values()

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