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
import os.path

# We can register as a class ....

#from celery.task import Task
#from celery.registry import tasks
#class ProcessVideoTask(Task):
#    def run(self, object_id, **kwargs):
#        logger = self.get_logger(**kwargs)
#        logger.info("Processed video for %s." % object_id)
#        return True
#tasks.register(ProcessVideoTask)

# .... or use the @task decorator

from celery.decorators import task
from celery.task.sets import subtask
import logging
import subprocess
import string
import shutil
import urllib2

@task
def copyfromurl(inputs,outputs,options={},callbacks=[]):

    url = options["url"]
    output = outputs[0]

    u = urllib2.urlopen(url)
    localFile = open(output, 'w')
    localFile.write(u.read())
    localFile.close()

    if options["mfile"]:
        mfile = options['mfile']
        mfile.name= "Imported File"
        mfile.save()
        mfile.post_process() 

    for callback in callbacks:
        subtask(callback).delay()
        
    return {  }

# Blender Commnad Line API
#
# Render a Picture
# blender -b file.blend -o //file -F JPEG -x 1 -f 1
#
# Render a movie
# blender -b file.blend -x 1 -o //file -F MOVIE -s 003 -e 005 -a
#
# Render a Series
# blender -b file.blend -x 1 -o //file -F "PNG" -s ss -e ee -a

@task
def render_blender(inputs,outputs,options={},callbacks=[]):

    padding = 4
    frame = options["frame"]
    if options.has_key("fname"):
        fname = options["format"]
    else:
        fname="image"
    if options.has_key("format"):
        format = options["format"]
    else:
        format="PNG"

    mfileid = inputs[0]
    from mserve.dataservice.models import MFile
    mf = MFile.objects.get(id=mfileid)
    inputfile = mf.file.path

    outputfile = outputs[0]

    logging.info("Processing render job %s frame: %s " % (inputfile,frame))

    if not os.path.exists(inputfile):
        logging.info("Scene %s does not exist" % inputfile)
        return False

    [outputdir,ffff]= os.path.split(outputfile)

    hashes = "#" * padding
    outputformat = "%s/%s.%s" % (outputdir,fname,hashes)
    ss= string.zfill(str(frame), padding)
    args = ["blender","-b",inputfile,"-x","1","-o",outputformat,"-F",format.upper(),"-s",ss,"-e",ss,"-a"]
    logging.info(args)

    n = str(frame).zfill(padding)
    resultfile = os.path.join(outputdir,"%s.%s.%s"%(fname,n,format.lower()))

    ret = subprocess.call(args)

    if resultfile != outputfile:
        logging.debug("result file %s is not outputfile %s ... Moving" % (resultfile, outputfile))
        shutil.move(resultfile, outputfile)


    for callback in callbacks:
        subtask(callback).delay()

    return ret
