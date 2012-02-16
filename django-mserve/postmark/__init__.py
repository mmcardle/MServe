########################################################################
#
# University of Southampton IT Innovation Centre, 2012
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
#	Created Date :			2012-01-04
#	Created for Project :		PrestoPrime
#
########################################################################

task_descriptions = {}

task_descriptions['postmark.tasks.digitalrapids'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "video/mp4" },
        "options":[],
        "results" : []
}
task_descriptions['postmark.tasks.red3dmux'] = {
        "nbinputs" : 2,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "input-1" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "image/tiff" },
        "options":["start_frame","end_frame"],
        "results" : []
}
task_descriptions['postmark.tasks.red2dtranscode'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "video" },
        "input-1" : { "mimetype" : "video" },
        "output-0" : { "mimetype" : "application/octet-stream" },
        "options":["export_type","start_frame","end_frame"],
        "results" : []
}

import settings
if settings.POSTMARK:
    from jobservice import *
    if 'task_descriptions' in task_descriptions:
        for k in struct.task_descriptions.keys():
            register_task_description(k, task_descriptions[k])