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
from django.http import HttpResponse
from anyjson import serialize as JSON_dump
from celery.registry import tasks
from django.core.cache import cache
import jobservice as js
import logging

def list_jobs(request):
    """
    A view returning all defined tasks as a JSON object.
    """

    reg = tasks.regular().keys()
    per = tasks.periodic().keys()

    regfilter = []
    perfilter = []

    for k in reg:
        if not k.startswith("celery."):
            regfilter.append(k)

    for k in per:
        if not k.startswith("celery."):
            perfilter.append(k)

    regfilter.sort()
    perfilter.sort()

    descriptions = {}
    
    for jobtype in regfilter:
        try:
            #desc = cache.get(jobtype)
            desc = js.handlers.cache[jobtype]
            descriptions[jobtype] = desc
        except Exception as e:
            logging.debug("No job description for job type '%s' %s" % (jobtype,e) )
    
    response_data = {"regular": regfilter,
                     "periodic": perfilter,
                     "descriptions": descriptions
                     }
    return HttpResponse(JSON_dump(response_data), mimetype="application/json")
