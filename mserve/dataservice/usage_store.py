from mserve.dataservice.models import NamedBase
from dataservice.models import *
import utils as utils
import datetime
import time
import logging
from django.db.models import Count,Max,Min,Avg,Sum,StdDev,Variance

def record(id,metric,total,report=True):
    base = NamedBase.objects.get(pk=id)
    usage = Usage(base=base,metric=metric,total=total,rate=0,rateCumulative=0,rateTime=datetime.datetime.now(),nInProgress=0,reports=1,squares=(total*total))
    usage.save()
    base.usages.add(usage)
    base.save()
    if report:
        reportusage(base)
    return usage

def startrecording(id,metric,rate,report=True):
    base = NamedBase.objects.get(pk=id)
    logging.info("base %s "% base)

    try:
        usage = Usage.objects.get(base=base,metric=metric)
        if rate == usage.rate:
            logging.info("Usage allready exists for %s at current rate %s " % (usage.metric,rate))
        else:
            logging.info("Usage allready exists for %s at rate %s, changing rate to %s " % (usage.metric, usage.rate, rate))

            now = datetime.datetime.now()
            td = now-usage.rateTime
            dif = (td.days*24*60*60)+ td.seconds + (td.microseconds/1000000.0)

            amount = dif*usage.rate

            usage.rateCumulative = usage.rateCumulative + amount
            usage.rateTime = now
            usage.rate = rate
            usage.save()
            if report:
                reportusage(base)
            return usage
    except Usage.DoesNotExist:
        logging.info("Usage DoesNotExist  ")
        usage = Usage(base=base,metric=metric,rate=rate,total=0.0,reports=1,nInProgress=1,rateCumulative=0,rateTime=datetime.datetime.now())
        logging.info("created %s " % usage)
        usage.save()
        if report:
            reportusage(base)
        return usage

def _stoprecording_(usage, obj=None):

    now = datetime.datetime.now()
    lastRateTime, lastRate, lastUsage = usage.rateTime,usage.rate,usage.rateCumulative

    t2 = time.mktime(now.timetuple())+float("0.%s"%now.microsecond)
    t1 = time.mktime(lastRateTime.timetuple())+float("0.%s"%lastRateTime.microsecond)

    usagedelta = float(lastUsage) + float(lastRate) * (t2 - t1)

    if obj is not None:
        obj.usages.add(usage)
        obj.save()

    usage.rateTime = now
    usage.rateCumulative = usage.rateCumulative + usagedelta
    usage.rate = 0
    usage.nInProgress = 0
    usage.save()


def stoprecording(id,metric,report=True):
    logging.debug("Stop Recording "+id)

    base = NamedBase.objects.get(id=id)

    try:
        usages = Usage.objects.filter(base=str(base))
        logging.info("Usages %s" % usages)
        usage = Usage.objects.get(base=base,metric=metric)

        _stoprecording_(usage)

    except Usage.DoesNotExist:
        logging.error("ERROR : Usage Rate does not exist to stop recording %s metric=%s" % (base,metric) )
    
def reportusage(base):
    toreport = []

    if utils.is_container(base):
        toreport =  [base]

    if utils.is_service(base):
        container = HostingContainer.objects.get(dataservice=base)
        toreport =  [container,base]

    if utils.is_mfile(base):
        service   = DataService.objects.get(mfile=base)
        toreport =  [service.container,service,base]

    for ob in toreport:
        logging.info("Reporting usage for %s "%ob)
        ob.reportnum += 1
        ob.save()

def get_usage(id=None):
    if id==None:
        usages = Usage.objects.all()
        return usages
    else:
        try:
            base = NamedBase.objects.get(pk=id)
            ids = []
            if utils.is_container(base):
                hc = HostingContainer.objects.get(id=id)
                serviceids = [service.id for service in hc.dataservice_set.all()  ]
                mfileids   = [mfile.id for service in hc.dataservice_set.all() for mfile in service.mfile_set.all() ]
                ids = serviceids + mfileids + [base.id]

            if utils.is_service(base):
                service   = DataService.objects.get(id=id)
                ids = [mfile.id for mfile in service.mfile_set.all()] + [base.id]

            if utils.is_mfile(base):
                ids=[base.id]

            usages = Usage.objects.filter(base__in=ids)
            return usages
        except NamedBase.DoesNotExist:

            auth = Auth.objects.get(pk=id)
            logging.info("Getting usage for auth %s " % auth)

            base = utils.get_base_for_auth(auth)

            return get_usage(id=base.id)

def get_usage_summary(id=None):
    
    summary = []
    usages = None
    if id==None:
        usages = Usage.objects.all()
        
    else:
        try:
            base = NamedBase.objects.get(pk=id)

            ids = []

            if utils.is_container(base):
                hc = HostingContainer.objects.get(id=id)
                serviceids = [service.id for service in hc.dataservice_set.all()  ]
                mfileids   = [mfile.id for service in hc.dataservice_set.all() for mfile in service.mfile_set.all() ]
                ids = serviceids + mfileids + [base.id]

            if utils.is_service(base):
                service   = DataService.objects.get(id=id)
                ids = [mfile.id for mfile in service.mfile_set.all()] + [base.id]

            if utils.is_mfile(base):
                ids=[base.id]

            usages = Usage.objects.filter(base__in=ids)
        except NamedBase.DoesNotExist:

            auth = Auth.objects.get(pk=id)
            logging.info("Getting usage summary for auth %s " % auth)

            base = utils.get_base_for_auth(auth)

            return get_usage_summary(id=base.id)
    
    if settings.DATABASE_ENGINE != "sqlite3":
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
            .annotate(sum=Total('rateCumulative'))

    return summary