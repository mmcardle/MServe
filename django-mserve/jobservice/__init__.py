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
from django.core.cache import cache
from models import *
import base64
import pickle

def get_task_description(task_name):
    task_description = cache.get(task_name)
    if task_description:
        return pickle.loads(base64.b64decode(task_description))
    else:
        try:
            td = TaskDescription.objects.get(task_name=task_name)
            task_description = td.get_json()
            cache.set(task_name, base64.b64encode(pickle.dumps(task_description)))
            return task_description
        except TaskDescription.DoesNotExist:
            raise Exception("No such job description '%s'" % task_name)

def register_task_description(task_name, task_description):
    cache.set(task_name, base64.b64encode(pickle.dumps(task_description)))
    save_task_description(task_name, task_description)

def save_task_description(task_name, task_description):
    td = TaskDescription.objects.get_or_create(task_name=task_name)[0]
    for i in range(0,task_description['nbinputs']):
        TaskInput.objects.get_or_create(taskdescription=td, num=i, mimetype=task_description['input-%s'%i]["mimetype"])
    for i in range(0,task_description['nboutputs']):
        TaskOutput.objects.get_or_create(taskdescription=td, num=i, mimetype=task_description['output-%s'%i]["mimetype"])
    for o in task_description['options']:
        TaskOption.objects.get_or_create(taskdescription=td, name=o)
    for r in task_description['results']:
        TaskResult.objects.get_or_create(taskdescription=td, name=r)

for td in TaskDescription.objects.all():
    register_task_description(td.task_name, td.get_json())