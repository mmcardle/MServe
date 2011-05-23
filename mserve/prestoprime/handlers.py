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
from piston.handler import BaseHandler
from piston.utils import rc
from django.http import HttpResponse
from dataservice.models import NamedBase
from dataservice.models import Usage
from dataservice.models import DataService
from dataservice.models import HostingContainer
from dataservice.handlers import ResourcesHandler
from anyjson import serialize as JSON_dump
import dataservice.utils as utils
import logging
import time
import datetime
from django.db.models import Count,Max,Min,Avg,Sum,StdDev,Variance

sleeptime = 10

class PPManagedResourcesHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, id, last=-1):
        rh = ResourcesHandler()

        ret = rh.read(request, id, last_known=last)

        logging.info(ret)

        return ret

class PPUsageHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, id, last=-1):
        try:
            base = NamedBase.objects.get(pk=id)
        except NamedBase.DoesNotExist:
            auth = Auth.objects.get(pk=id)
            base = auth.base

        if last is not -1:
            while str(last) == str(base.reportnum):
                time.sleep(sleeptime)
                base = NamedBase.objects.get(id=id)

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

        #usageSummary = base.usages.values('metric').filter(nInProgress=0)\
        usageSummary = Usage.objects.filter(base__in=ids).values('metric').filter(nInProgress=0)\
            .annotate(n=Count('total')) \
            .annotate(avg=Avg('total')) \
            .annotate(max=Max('total')) \
            .annotate(min=Min('total')) \
            .annotate(sum=Sum('total')) \
            .annotate(sums=Sum('total')) \
            .annotate(stddev=StdDev('total'))\
            .annotate(variance=Variance('total'))

        logging.info("Getting usage for metrics %s " %  base.usages.values('metric'))
        logging.info("Getting usage for metrics %s " %  base.usages.values('metric').filter(nInProgress=0))

        inprogress = Usage.objects.filter(base__in=ids).values('metric').filter(nInProgress__gte=1)\
            .annotate(nRates=Count('total')) \
            .annotate(rateTime=Avg('rateTime')) \
            .annotate(rate=Avg('rate')) \
            .annotate(usageSoFar=Sum('rateCumulative')) \
            .annotate(count=Count('total'))

        inprogressMap = {}
        for inp in inprogress:
            # TODO : This should be datetime.datetime.now().isoformat() But ting will not accept it currently
            inp["current"] = datetime.datetime.now()
            inprogressMap[inp["metric"]] = inp

        usageSummaryMap = {}
        for us in usageSummary:
            #us["sums"] = float('%.f'% (us['sum']*us['sum']))
            us["sums"] = int(us['sum']*us['sum'])
            usageSummaryMap[us["metric"]] =  us

        dict = {}
        dict["inprogress"] = inprogressMap
        dict["summarys"] = usageSummaryMap
        dict["reportnum"] = base.reportnum

        # TODO : This should be JSON_dump and dates formatted with isoformat
        # But ting will not accept it currently (see above)
        #return HttpResponse(JSON_dump(dict),mimetype="application/json")
        return dict