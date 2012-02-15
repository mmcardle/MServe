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
from jobservice.models import TaskDescription

def list_tasks(request):
    """
    A view returning all defined tasks as a JSON object.
    """

    task_descriptions = TaskDescription.objects.values_list("task_name",flat=True)
    reg = tasks.regular().keys()
    per = tasks.periodic().keys()

    regfilter = []
    perfilter = []

    regfilter.extend(task_descriptions)
    #for k in reg:
    #    #if not k.startswith("celery."):
    #    if k in task_descriptions:
    #        regfilter.append(k)
    #for k in per:
    #    if not k.startswith("celery."):
    #        perfilter.append(k)

    regfilter.sort()
    perfilter.sort()

    descriptions = {}
    from jobservice import get_task_description

    for jobtype in regfilter:
        try:
            t = get_task_description(jobtype)
            descriptions[jobtype] = t
        except Exception as e:
            print "No job description for job type '%s' %s" % (jobtype,e)
            #logging.debug("No job description for job type '%s' %s" % (jobtype,e) )
            pass

    response_data = {"regular": regfilter,
                     "periodic": perfilter,
                     "descriptions": descriptions
                     }
    try:
        return HttpResponse(JSON_dump(response_data), mimetype="application/json")
    except:
        raise
