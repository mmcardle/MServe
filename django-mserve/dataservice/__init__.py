"""The Mserve dataservice module """

task_descriptions = {}
task_descriptions['dataservice.tasks.backup_mfile'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "application/octet-stream" },
        "options":[],
        "results" : []
}

from jobservice import *
if 'task_descriptions' in task_descriptions:
    for k in struct.task_descriptions.keys():
        register_task_description(k, task_descriptions[k])