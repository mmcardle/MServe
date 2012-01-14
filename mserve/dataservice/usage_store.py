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
from models import NamedBase
from dataservice.models import *
import utils as utils
import datetime
import time
import logging

def record(id,metric,total,report=True):
    base = NamedBase.objects.get(pk=id)
    usage = Usage(base=base,metric=metric,total=total,rate=0,rateCumulative=0,rateTime=datetime.datetime.now(),nInProgress=0,reports=1,squares=(total*total))
    usage.save()
    base.usages.add(usage)
    base.save()
    if report:
        reportusage(base)
    return usage

def update(id,metric,total,report=True):
    base = NamedBase.objects.get(pk=id)
    try:
        usage = Usage.objects.get(base=base,metric=metric)
        usage.total=total
        usage.squares=total*total
        usage.save()
        base.usages.add(usage)
        base.save()
        if report:
            reportusage(base)
        return usage
    except Usage.DoesNotExist:
        logging.debug("Usage DoesNotExist  ")

def startrecording(id,metric,rate,report=True):
    base = NamedBase.objects.get(pk=id)
    logging.debug("Start Recording base %s "% base)

    try:
        usage = Usage.objects.get(base=base,metric=metric)
        if rate == usage.rate:
            logging.debug("Usage allready exists for %s at current rate %s " % (usage.metric,rate))
        else:
            logging.debug("Usage allready exists for %s at rate %s, changing rate to %s " % (usage.metric, usage.rate, rate))
            update_usage(usage,rate=rate)
            if report:
                reportusage(base)
            return usage
    except Usage.DoesNotExist:
        usage = Usage(base=base,metric=metric,rate=rate,total=0.0,reports=1,nInProgress=1,rateCumulative=0,rateTime=datetime.datetime.now())
        logging.debug("created %s " % usage)
        usage.save()
        if report:
            reportusage(base)
        return usage

def update_usage(usage,rate=None):
    if rate == None:
        rate = usage.rate
    now = datetime.datetime.now()
    td = now-usage.rateTime
    dif = (td.days*24*60*60)+ td.seconds + (td.microseconds/1000000.0)

    amount = dif*rate*usage.nInProgress

    usage.rateCumulative = usage.rateCumulative + amount
    usage.rateTime = now
    usage.rate = rate
    usage.squares = usage.rateCumulative*usage.rateCumulative
    usage.save()
    return usage

def updaterecording(id,metric,rate,report=True):
    base = NamedBase.objects.get(pk=id)

    try:
        usage = Usage.objects.get(base=base,metric=metric)
        if rate == usage.rate:
            logging.debug("Usage allready exists for %s at current rate %s " % (usage.metric,rate))
        else:
            logging.debug("Usage allready exists for %s at rate %s, changing rate to %s " % (usage.metric, usage.rate, rate))
            update_usage(usage,rate=rate)
            if report:
                reportusage(base)
            return usage
    except Usage.DoesNotExist:
        usage = Usage(base=base,metric=metric,rate=rate,total=0.0,reports=1,nInProgress=1,rateCumulative=0,rateTime=datetime.datetime.now())
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

    finalTotal = usage.total + usage.rateCumulative + usagedelta

    usage.rateTime = now
    usage.rateCumulative = 0
    usage.total = finalTotal
    usage.rate = 0
    usage.nInProgress = 0
    usage.base=None
    u = usage.copy(obj,save=True)

    if obj is not None:
        obj.usages.add(u)
        obj.save()

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
        ob.reportnum += 1
        ob.save()