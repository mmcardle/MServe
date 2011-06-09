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

from celery.decorators import task
import logging
import subprocess
import tempfile
from subprocess import Popen, PIPE
from celery.task.sets import subtask
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

@task
def mxftechmdextractor(inputs,outputs,options={},callbacks=[]):
    inputfile = inputs[0]
    outputfile = outputs[0]
    logging.info("Processing mxftechmdextractor job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["/home/mm/dev/MXFTechMDExtractorPlugin/bin/run.sh",inputfile]
    cmd = " ".join(args)
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE, close_fds=True)
    output = p.stdout.read()
    f = open(outputfile, 'w')
    f.write(output)

    for callback in callbacks:
        subtask(callback).delay()

    return {"success":True,"message":"MXFTechMDExtractorPlugin successful"}

@task
def d10mxfchecksum(inputs,outputs,options={},callbacks=[]):

    mfile = inputs[0]
    joboutput = outputs[0]

    inputfile = mfile.file.path
    outputfile = tempfile.NamedTemporaryFile()

    logging.info("Processing d10mxfchecksum job on %s" % (inputfile))

    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False

    args = ["d10sumchecker","-i",inputfile,"-o",outputfile.name]

    subprocess.call(args)

    outputfile.seek(0)
    suf = SimpleUploadedFile(os.path.split(mfile.name)[-1],outputfile.read(), content_type='text/plain')

    from mserve.jobservice.models import JobOutput
    jo = JobOutput.objects.get(id=joboutput.pk)
    jo.file.save(suf.name+'_d10mxfchecksum.txt', suf, save=True)

    for callback in callbacks:
        subtask(callback).delay()

    return {"success":True,"message":"d10mxfchecksum successful"}

@task
def mxfframecount(inputs,outputs,options={},callbacks=[]):

    mfile = inputs[0]
    inputfile = mfile.file.path

    outputfile = tempfile.NamedTemporaryFile()
    logging.info("Processing mxfframecount job on %s" % (inputfile))

    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False

    args = ["d10sumchecker","-i",inputfile,"-o",outputfile.name]
    logging.info(args)
    subprocess.call(args)
    frames = 0
    for line in open(outputfile.name):
        frames += 1

    # TODO: subtract 1 for additional output
    frames = frames -1
    
    import dataservice.usage_store as usage_store
    usage_store.record(mfile.id,"http://prestoprime/mxf_frames_ingested",frames)

    for callback in callbacks:
        subtask(callback).delay()

    return {"success":True,"message":"mxfframecount successful", "frames": frames }

@task(max_retries=3)
def extractd10frame(inputs,outputs,options={},callbacks=[],**kwargs):
    inputfile = str(inputs[0])
    outputfile = str(outputs[0])
    frame = str(options['frame'])
    logging.info("Processing extractd10frame job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False

    import pyffmpeg

    stream = pyffmpeg.VideoStream()
    stream.open(inputfile)
    image = stream.GetFrameNo(frame)
    image.save(outputfile)

    for callback in callbacks:
            subtask(callback).delay()

    return {"success":True,"message":"extractd10frame successful"}



