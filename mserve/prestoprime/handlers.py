from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import NamedBase
from dataservice.models import Usage
from dataservice.models import DataService
from dataservice.models import HostingContainer
import dataservice.utils as utils
import logging
import time
from django.db.models import Count,Max,Min,Avg,Sum,StdDev,Variance

class PPUsageHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, id, last=-1):
        try:
            base = NamedBase.objects.get(pk=id)
        except NamedBase.DoesNotExist:
            auth = Auth.objects.get(pk=id)
            base = auth.base

        if last is not -1:
            while last == base.reportnum:
                logging.debug("Waiting for new usage lastreport=%s" % last)
                time.sleep(sleeptime)
                base = NamedBase.objects.get(id=id)

        usageSummary = base.usages.filter(nInProgress=0).values('metric')\
            .annotate(n=Count('total')) \
            .annotate(avg=Avg('total')) \
            .annotate(max=Max('total')) \
            .annotate(min=Min('total')) \
            .annotate(sum=Sum('total')) \
            .annotate(stddev=StdDev('total'))\
            .annotate(variance=Variance('total'))

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

        inprogress = Usage.objects.filter(base__in=ids).filter(nInProgress__gte=1).values('metric')\
            .annotate(nRates=Count('total')) \
            .annotate(rateTime=Avg('rateTime')) \
            .annotate(rate=Avg('rate')) \
            .annotate(rate=Sum('rateCumulative'))

        inprogressMap = {}
        for inp in inprogress:
            inprogressMap[inp["metric"]] = inp

        usageSummaryMap = {}
        for us in usageSummary:
            usageSummaryMap[us["metric"]] = us

        dict = {}
        dict["inprogressUsage"] = inprogressMap
        dict["usageSummary"] = usageSummaryMap

        return dict