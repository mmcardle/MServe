import os.path

from celery.decorators import task
import logging
import subprocess
from subprocess import Popen, PIPE
import tempfile

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

    f = open(outputfile, 'w')
    f.close()

    for callback in callbacks:
        subtask(callback).delay()

    return {}

@task
def mxfframecount(inputs,outputs,options={},callbacks=[]):
    inputfile = inputs[0]
    f = tempfile.NamedTemporaryFile()
    outputfile = f.name
    logging.info("Processing d10mxfchecksum job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["d10sumchecker","-i",inputfile,"-o",outputfile]
    subprocess.call(args)
    lines = 0
    for line in open(outputfile):
        lines += 1

    for callback in callbacks:
        subtask(callback).delay()

    return { "lines": lines }