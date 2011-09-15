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
import logging
import os
import shutil
import os.path
import time
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
import dataservice.utils as utils
import settings as settings
import paramiko
import os
import uuid
from ssh import MultiSSHClient
from dataservice.models import MFile
from jobservice.models import JobOutput

def _ssh_r3d(left_eye_file,right_eye_file,tmpimage):

    ssh = MultiSSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(settings.R3D_HOST, username=settings.R3D_USER, password=settings.R3D_PASS)

    export_file_path = ""
    start_frame = ""
    end_frame = ""
    clip_settings_file = ""
    output_file_dir,output_file_name = os.path.split(tmpimage)

    command = "redline %s %s %s %s %s %s %s %s" % (left_eye_file,right_eye_file,output_file_dir,output_file_name,export_file_path,start_frame,end_frame,clip_settings_file)
    command = "composite -blend 40 %s %s -alpha Set %s" % (left_eye_file,right_eye_file,tmpimage)

    logging.info(command)

    stdin, stdout, stderr = ssh.exec_command(command)

    result = {}
    result["stdout"] = stdout.readlines()
    result["sdterr"] = stderr.readlines()

    return result


@task(name="r3d")
def r3d(inputs,outputs,options={},callbacks=[]):

    logging.info("Inputs %s"% (inputs))
    if len(inputs) > 0:
        left  = MFile.objects.get(id=inputs[0])
        logging.info("Left %s" % left)
        if len(inputs) > 1:
            right = MFile.objects.get(id=inputs[1])
            logging.info("Right %s" % right)

            remote_mount = "/tmp"
            local_mount = settings.MSERVE_DATA

            tfile_uuid = "r3d-image-"+str(uuid.uuid4())
            remoteimage = os.path.join(remote_mount,tfile_uuid)
            localimage = os.path.join(local_mount,tfile_uuid)

            result = _ssh_r3d(left.file.path,right.file.path,remoteimage)

            logging.info(result)

            # TODO: Change to local in deployment
            #outputfile = open(localimage,'r')
            outputfile = open(remoteimage,'r')

            suf = SimpleUploadedFile("mfile",outputfile.read(), content_type='image/tiff')

            if len(outputs)>0:
                jo = JobOutput.objects.get(id=outputs[0])
                jo.file.save('image.jpg', suf, save=True)
            else:
                logging.error("Nowhere to save output")

            outputfile.close()

            return {"message":"R3D successful"}
        else:
            logging.error("No right eye input given")
    else:
        logging.error("No left eye input given")
    raise

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
