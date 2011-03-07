import os.path

from celery.decorators import task
import logging
import subprocess
from subprocess import Popen, PIPE
from celery.task.sets import subtask

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

    return {}

@task
def d10mxfchecksum(inputs,outputs,options={},callbacks=[]):
    inputfile = inputs[0]
    outputfile = outputs[0]
    logging.info("Processing d10mxfchecksum job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["d10sumchecker","-i",inputfile,"-o",outputfile]
    ret = subprocess.call(args)

    for callback in callbacks:
        subtask(callback).delay()

    return {}

@task
def mxfframecount(inputs,outputs,options={},callbacks=[]):
    inputfile = inputs[0]
    outputfile = outputs[0]
    logging.info("Processing mxfframecount job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["d10sumchecker","-i",inputfile,"-o",outputfile]
    subprocess.call(args)
    lines = 0
    for line in open(outputfile):
        lines += 1

    # TODO: subtract 1 for additional output
    lines = lines -1

    for callback in callbacks:
        subtask(callback).delay()

    return { "lines": lines }

@task(max_retries=3)
def extractd10frame(inputs,outputs,options={},callbacks=[],**kwargs):
    inputfile = str(inputs[0])
    outputfile = str(outputs[0])
    frame = str(options['frame'])
    logging.info("Processing extractd10frame job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False

    try:
        args = ["ffmpeg","-vframes",frame,"-i",inputfile,"-f","image2",outputfile]
        logging.info("Processing  %s" % (args))
        ret = subprocess.call(args)

        if ret != 0:
            raise Exception("error")

        for callback in callbacks:
            subtask(callback).delay()

        return {}
    except Exception, e:
            extractd10frame.retry(args=[inputs,outputs,options,callbacks], exc=e, countdown=20, kwargs=kwargs)


