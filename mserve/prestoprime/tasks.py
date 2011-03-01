import os.path

from celery.decorators import task
import logging
import subprocess
from subprocess import Popen, PIPE

@task
def mxftechmdextractor(inputfile,outputfile,options={},callback=None):
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
    return None

@task
def d10mxfchecksum(inputfile,outputfile,options={},callback=None):
    logging.info("Processing d10mxfchecksum job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["d10sumchecker","-i",inputfile,"-o",outputfile]
    ret = subprocess.call(args)
    return ret

@task
def mxfframecount(inputfile,outputfile,options={},callback=None):
    logging.info("Processing d10mxfchecksum job on %s" % (inputfile))
    if not os.path.exists(inputfile):
        logging.info("Inputfile  %s does not exist" % (inputfile))
        return False
    args = ["d10sumchecker","-i",inputfile,"-o",outputfile]
    subprocess.call(args)
    lines = 0
    for line in open(outputfile):
        lines += 1
    return lines