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
#	Created Date :			2012-01-06
#	Created for Project :		RASCC
#
########################################################################

task_descriptions = {}

task_descriptions['dumbtask'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "image/jpeg" },
        "output-0" : { "mimetype" : "text/plain" },
        "options" : [],
        "results" :[]
    }
task_descriptions['dataservice.tasks.dumbtask'] = task_descriptions['dumbtask']
task_descriptions['swirl'] = {
        "nbinputs" : 1,
        "nboutputs" : 1,
        "input-0" : { "mimetype" : "image/jpg" },
        "output-0" : { "mimetype" : "image/jpg" },
        "options" : [],
        "results" :[]
    }
task_descriptions['dataservice.tasks.swirl'] =  task_descriptions['swirl']
task_descriptions['imodel'] = {
        "nbinputs" : 1,
        "nboutputs" : 2,
        "input-0" : { "mimetype" : "application/json" },
        "output-0" : { "mimetype" : "text/csv" },
        "output-1" : { "mimetype" : "text/plain" },
        "options" : [],
        "results" :[]
    }
task_descriptions['dataservice.tasks.imodel'] =  task_descriptions['imodel']
task_descriptions['thumbimage'] = {
        "nbinputs" : 1,
        "nboutputs" : 0,
        "input-0" : { "mimetype" : "image/png" },
        "options" : ['width','height'],
        "results" :[]
    }