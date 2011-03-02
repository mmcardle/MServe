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
def render_blender(inputfile,outputfile,options={},callback=None):

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

    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.

        #ofile = os.path.join(outputdir,"%s.%s.thumb.png"%(fname,n))
        #subtask(callback).delay( outputfile ,thumbpath ,thumbsize[0], thumbsize[1] )
        subtask(callback).delay(  )
    return ret
