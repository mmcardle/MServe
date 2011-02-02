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
def render_blender(scenepath,s,e,outputdir,fname,thumbpath,thumbsize=(210,128),padding=4,format="PNG",callback=None):
    logging.info("Processing render job %s start %s to end %s" % (scenepath,s,e))
    if not os.path.exists(scenepath):
        logging.info("Scene %s does not exist" % (scenepath))
        return False
    hashes = "#" * padding
    outputformat = "%s/%s.%s" % (outputdir,fname,hashes)
    ss= string.zfill(str(s), padding)
    ee= string.zfill(str(e), padding)
    args = ["blender","-b",scenepath,"-x","1","-o",outputformat,"-F",format.upper(),"-s",ss,"-e",ee,"-a"]
    logging.info(args)
    n = str(s).zfill(padding)
    ifile = os.path.join(outputdir,"%s.%s.%s"%(fname,n,format.lower()))

    ret = subprocess.call(args)
    if callback:
        # The callback may have been serialized with JSON,
        # so best practice is to convert the subtask dict back
        # into a subtask object.

        #ofile = os.path.join(outputdir,"%s.%s.thumb.png"%(fname,n))
        subtask(callback).delay( ifile ,thumbpath ,thumbsize[0], thumbsize[1] )
    return ret
