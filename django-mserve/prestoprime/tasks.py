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

from celery.task import task
import logging
import subprocess
import tempfile
from subprocess import Popen, PIPE
from celery.task.sets import subtask
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.base import ContentFile

@task
def mxftechmdextractor(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]

        from dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        inputfile = mf.file.path

        joboutput = outputs[0]

        logging.info("Processing mxftechmdextractor job on %s" % (inputfile))
        if not os.path.exists(inputfile):
            logging.info("Inputfile  %s does not exist" % (inputfile))
            return False

        args = ["/home/mm/dev/MXFTechMDExtractorPlugin/bin/run.sh",inputfile]
        cmd = " ".join(args)
        p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)

        from jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput)
        jo.file.save('mxftechmdextractor.txt', ContentFile(p.stdout.read()), save=True)

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"MXFTechMDExtractorPlugin successful"}
    except Exception as e:
        logging.info("Error with mxftechmdextractor %s" % e)
        raise e
@task
def d10mxfchecksum(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]
        joboutput = outputs[0]

        from dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        inputfile = mf.file.path
        outputfile = tempfile.NamedTemporaryFile()

        logging.info("Processing d10mxfchecksum job on %s" % (inputfile))

        if not os.path.exists(inputfile):
            logging.info("Inputfile  %s does not exist" % (inputfile))
            return False

        args = ["d10sumchecker","-i",inputfile,"-o",outputfile.name]

        ret = subprocess.call(args)

        if ret != 0:
            raise Exception("d10mxfchecksum failed")

        outputfile.seek(0)
        suf = SimpleUploadedFile("mfile",outputfile.read(), content_type='text/plain')

        from jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput)
        jo.file.save('d10mxfchecksum.txt', suf, save=True)

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"d10mxfchecksum successful"}
    except Exception as e:
        logging.info("Error with d10mxfchecksum %s" % e)
        raise e
    
@task
def mxfframecount(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        from dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        inputfile = mf.file.path

        outputfile = tempfile.NamedTemporaryFile()
        logging.info("Processing mxfframecount job on %s" % (inputfile))

        if not os.path.exists(inputfile):
            logging.info("Inputfile  %s does not exist" % (inputfile))
            return False

        args = ["d10sumchecker","-i",inputfile,"-o",outputfile.name]
        logging.info(args)
        ret = subprocess.call(args)

        if ret != 0:
            raise Exception("mxfframecount failed")

        frames = 0
        for line in open(outputfile.name):
            frames += 1

        # TODO: subtract 1 for additional output
        frames = frames -1

        import dataservice.usage_store as usage_store
        usage_store.record(mf.id,"http://prestoprime/mxf_frames_ingested",frames)

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"mxfframecount successful", "frames": frames }
    except Exception as e:
        logging.info("Error with mxfframecount %s" % e)
        raise e

@task(max_retries=3)
def extractd10frame(inputs,outputs,options={},callbacks=[],**kwargs):
    try:
        mfileid = inputs[0]
        from dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        inputfile = mf.file.path

        joboutput = outputs[0]
        frame = str(options['frame'])

        logging.info("Processing extractd10frame job on %s" % (inputfile))
        if not os.path.exists(inputfile):
            logging.info("Inputfile  %s does not exist" % (inputfile))
            return False

        import pyffmpeg

        stream = pyffmpeg.VideoStream()
        stream.open(inputfile)
        image = stream.GetFrameNo(frame)

        # Save the thumbnail
        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile("mfile",temp_handle.read(), content_type='image/png')

        from jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput.pk)
        jo.file.save('extractd10frame.png', suf , save=False)
        jo.save()

        for callback in callbacks:
                subtask(callback).delay()

        return {"success":True,"message":"extractd10frame successful"}
    except Exception as e:
        logging.info("Error with extractd10frame %s" % e)
        raise e


