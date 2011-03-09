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
