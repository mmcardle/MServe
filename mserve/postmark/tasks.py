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
#	Created Date :			2011-07-26
#	Created for Project :		Postmark
#
########################################################################
from celery.task import task
from celery.task.sets import subtask
from subprocess import Popen, PIPE
import json
import logging
import hashlib
import Image
import tempfile
import magic
import urlparse
import os
import shutil
import os.path
import time
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File
import pycurl
import StringIO
import dataservice.utils as utils
import settings as settings

def _drop_folder(filepath,inputfolder,outputfolder):

    try:
        uid = utils.unique_id()
        name = "%s_%s" % (uid,os.path.basename(filepath))
        inputfile = os.path.join(inputfolder,name)
        outputfile = os.path.join(outputfolder,name)
        shutil.copy(filepath, inputfile)

        exists = os.path.exists(outputfile)

        # Wait till file exists
        while not exists:
            logging.info("Output file %s doesnt exist, sleeping" % outputfile)
            time.sleep(10)
            exists = os.path.exists(outputfile)

        # Wait until file stops growing
        growing = True
        size = os.path.getsize(outputfile)
        logging.info("Size is %s"%str(size))
        while growing:
            time.sleep(10)
            newsize = os.path.getsize(outputfile)
            logging.info("Size is now %s"%str(newsize))
            growing = (size!=newsize)
            size = newsize
            logging.info("File Growing  %s"% growing)

        return outputfile


    except Exception as e:
        logging.info("Error with watching drop folder %s" % e)
        raise e


@task(name="digitalrapids")
def digitalrapids(inputs,outputs,options={},callbacks=[]):

    baseinputdir    = settings.DIGITAL_RAPIDS_INPUT_DIR
    baseoutputdir   = settings.DIGITAL_RAPIDS_OUTPUT_DIR

    inputdir    = os.path.join(baseinputdir)
    outputdir   = os.path.join(baseoutputdir)
    
    try:
    
        mfileid = inputs[0]
        joboutput = outputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        videopath = mf.file.path

        logging.info("Processing video Digital Rapids %s" % (videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        video = _drop_folder(videopath,inputdir,outputdir)

        from dataservice import usage_store
        inputfilesize = os.path.getsize(videopath)
        usage_store.record(mfileid,"http://mserve/digitalrapids",inputfilesize)

        videofile = open(video,'r')

        from mserve.jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput)
        jo.file.save('transcode.mov', File(videofile), save=True)

        videofile.close()

        return {"success":True,"message":"Digital Rapids transcode of video successful"}

    except Exception as e:
        logging.info("Error with digitalrapids %s" % e)
        raise e
