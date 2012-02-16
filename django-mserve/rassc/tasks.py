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
import logging
import subprocess
import tempfile
import os
import os.path
import shutil
import PythonMagick
import settings as settings
from celery.task import task
from dataservice.tasks import _get_mfile
from dataservice.tasks import _save_joboutput

@task(default_retry_delay=5,max_retries=1)
def dumbtask(inputs,outputs,options={},callbacks=[]):
    logging.info("Processing dumb task")
    try:
        mfileid = inputs[0]
        filepath = _get_mfile(mfileid)

        toutfile = tempfile.NamedTemporaryFile(delete=False,suffix=".txt")
        joboutput = outputs[0]

        retcode = subprocess.call(["wc",filepath,toutfile.name])
        _save_joboutput(joboutput,toutfile)

        return {"success":True,"message":"Dumb task successful"}

    except Exception as e:
        logging.info("Error with dumb task %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3)
def swirl(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]

        path = _get_mfile(mfileid)

        logging.info("Swirling image for %s (%s)" % (input, path))
        img = PythonMagick.Image()
        img.read(str(path))
        img.swirl(90)

        # Create swirled image as job output
        toutfile = tempfile.NamedTemporaryFile(delete=False,suffix=".jpg")
        img.write(toutfile.name)
        joboutput = outputs[0]
        _save_joboutput(joboutput,toutfile)

        return {"success":True,"message":"Swirl successful"}
    except Exception ,e:
        logging.info("Error with swirl %s" % e)

@task(default_retry_delay=15,max_retries=3)
def imodel(inputs,outputs,options={},callbacks=[]):
        mfileid = inputs[0]
        path = _get_mfile(mfileid)
        logging.info("CWD: %s" % os.getcwd())
        logging.info("Running imodel on %s" % (path))

	# Run iModel in a temporary directory
	logging.info(os.environ)
        #imodel_home = "/opt/iModel-1.0-beta-3-SNAPSHOT"
        #imodel_home = os.environ["IMODEL_HOME"]
	imodel_home = settings.IMODEL_HOME
        logging.info("Running iModel from %s" % imodel_home)
	(mfile_dir, mfile_name) = os.path.split(path)
        # XXX: configuration.txt must be in CWD
        # XXX: Runtime arguments should not be provided in a file
	tempdir = tempfile.mkdtemp()
	logging.info("iModel temp dir: %s" % (tempdir))
        shutil.copy("imodel/configuration.txt", tempdir)
        shutil.copy(path, tempdir)
        p = subprocess.Popen(["java", "-cp", imodel_home + ":" + imodel_home+"/lib/*:" + imodel_home+"/bin", "uk.ac.soton.itinnovation.prestoprime.imodel.batch.start.StartArchiveSystemModel", mfile_name], cwd=tempdir, stdout=subprocess.PIPE)

        # save stdout
	stdoutfile = open(tempdir+"/stdout", 'w')
        logging.info("Temp file for stdout: %s" % (stdoutfile.name))
        (stdout, stderr) = p.communicate()
        stdoutfile.write(stdout)
        stdoutfile.close()
        _save_joboutput(outputs[1], stdoutfile)

	# Process results
	import sys
	sys.path.append("imodel")
	import parseimodel
	processedresultsfilename = tempdir+"/data.csv"
	parseimodel.parse(tempdir+"/outputSystemPerformance.log", processedresultsfilename)
        joboutput = outputs[0]
	processedresultsfile = open(processedresultsfilename, 'r')
        _save_joboutput(joboutput, processedresultsfile)

        return {"success":True,"message":"iModel simulation successful"}
