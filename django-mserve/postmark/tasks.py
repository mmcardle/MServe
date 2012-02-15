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
import re
import tempfile
import datetime
import shutil
import os.path
import time
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
import dataservice.utils as utils
import settings as settings
import paramiko
import uuid
from ssh import MultiSSHClient
from dataservice.models import MFile
from jobservice.models import JobOutput
import tarfile

def tar_files(temp_tarfile, files):
    tar = tarfile.open(temp_tarfile, "w:gz")
    for name in files:
        (head,tail) = os.path.split(name)
        tar.add(name,arcname=tail)
    tar.close()


def get_files(directory, prefix=None, suffix=None, after=None):
    _files=[]
    for fname in os.listdir(directory):
        file = os.path.join(directory,fname)
        if not os.path.isfile(file):
            continue
        if after:
            mtime = os.path.getmtime(file)
            if datetime.datetime.fromtimestamp(mtime) <= after:
                continue
        if prefix:
            if not re.match(prefix,fname):
                continue
        if suffix:
            if not re.search(suffix+"$",fname):
                continue
        _files.append(file)
    return _files


def _ssh_r2d(file, export_type, tmpimage, start_frame=1, end_frame=2):

    ssh = MultiSSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(settings.R3D_HOST, username=settings.R3D_USER, password=settings.R3D_PASS)
    output_file_dir,output_file_name = os.path.split(tmpimage)

    command = "redline --i %s --outDir %s -o %s --exportPreset %s -s %s -e %s" % (file, output_file_dir, output_file_name, export_type, start_frame, end_frame)
    logging.info(command)

    stdin, stdout, stderr = ssh.exec_command(command)

    result = {}
    result["stdout"] = stdout.readlines()
    result["sdterr"] = stderr.readlines()

    return result

@task(name="red2dtranscode")
def red2dtranscode(inputs,outputs,options={},callbacks=[]):

    started = datetime.datetime.now()

    logging.info("Inputs %s"% (inputs))
    if len(inputs) > 0:
        input_mfile  = MFile.objects.get(id=inputs[0])
        logging.info("R2D input file %s" % input_mfile)
        remote_mount = "/Volumes/ifs/mserve/"

        start_frame = 1
        if "start_frame" in options:
            start_frame = options["start_frame"]

        end_frame = 2
        if "end_frame" in options:
            end_frame = options["end_frame"]

        export_type = "tiff"
        if "export_type" in options and options["export_type"] != "":
            export_type = options["export_type"]
        
        file_local_mount = os.path.join(settings.STORAGE_ROOT)
        if input_mfile.service.container.default_path:
            file_local_mount = os.path.join(settings.STORAGE_ROOT, input_mfile.service.container.default_path)

        file_path=input_mfile.file.path
        file_relative= os.path.join(file_path.replace(file_local_mount,remote_mount))
        tfile_uuid = "r2d-image-"+str(uuid.uuid4())
        remoteimage = os.path.join(remote_mount,tfile_uuid)

        if export_type == "tiff":
            suffix = "."+("0".zfill(6))+".tif"
            localimage = os.path.join(file_local_mount,tfile_uuid,tfile_uuid+suffix)
        elif export_type == "avid":
            input_name = input_mfile.name.split(".")[0]
            fname = input_name+".mxf"
            localimage = os.path.join(file_local_mount,"MXF",fname)
        elif export_type == "fcp":
            fname = tfile_uuid+".mov"
            localimage = os.path.join(file_local_mount,fname)
        else:
            raise Exception("Unknown export type '%s'" % export_type)

        logging.info("file_local_mount %s" % file_local_mount)
        logging.info("file_path %s" % file_path)
        logging.info("file_relative %s" % file_relative)
        logging.info("remoteimage %s" % remoteimage)
        logging.info("localimage %s" % localimage)

        result = _ssh_r2d(file_relative,export_type,remoteimage,start_frame=start_frame,end_frame=end_frame)
        outputfile = None

        if export_type == "tiff":
            localdir = os.path.join(file_local_mount,tfile_uuid)
            temp_tarfile = tempfile.NamedTemporaryFile('wb')
            tar_files(temp_tarfile.name, [localdir] )
            outputfile = open(temp_tarfile.name, 'r')

        if export_type == "avid":
            localdir = os.path.join(file_local_mount,"MXF")
            files = get_files(localdir, prefix=input_mfile.name[:8], after=started)
            logging.info(files)
            temp_tarfile = tempfile.NamedTemporaryFile('wb')
            tar_files(temp_tarfile.name, files )
            outputfile = open(temp_tarfile.name, 'r')

        if export_type == "fcp":
            files = [localimage]
            logging.info(files)
            temp_tarfile = tempfile.NamedTemporaryFile('wb')
            tar_files(temp_tarfile.name, files )
            outputfile = open(temp_tarfile.name, 'r')

        logging.info("outputfile %s", outputfile)

        if outputfile:
            suf = SimpleUploadedFile("mfile",outputfile.read(), content_type='image/tiff')

            if len(outputs)>0:
                jo = JobOutput.objects.get(id=outputs[0])
                jo.file.save('results.tar.gz', suf, save=True)
            else:
                logging.error("Nowhere to save output")

            outputfile.close()
        else:
            raise Exception("Unable to get outputfile location")

        return {"message":"R2D successful"}
    else:
        logging.error("No input given")
    raise

def _ssh_r3d(left_eye_file,right_eye_file,tmpimage, start_frame=1, end_frame=2):

    ssh = MultiSSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(settings.R3D_HOST, username=settings.R3D_USER, password=settings.R3D_PASS)
    clip_settings_file = "/Volumes/Media/masterRMD"
    output_file_dir,output_file_name = os.path.split(tmpimage)

    command = "redline -i3d %s %s -outDir %s -o %s --exportPreset 3Dtiff --makeSubDir --s  %s --e  %s --masterRMDFolder %s " % (left_eye_file,right_eye_file,output_file_dir,output_file_name,start_frame,end_frame,clip_settings_file)

    logging.info(command)

    stdin, stdout, stderr = ssh.exec_command(command)

    result = {}
    result["stdout"] = stdout.readlines()
    result["sdterr"] = stderr.readlines()

    return result


@task(name="red3dmux")
def red3dmux(inputs,outputs,options={},callbacks=[]):

    logging.info("Inputs %s"% (inputs))
    if len(inputs) > 0:
        left  = MFile.objects.get(id=inputs[0])
        logging.info("Left %s" % left)
        if len(inputs) > 1:
            right = MFile.objects.get(id=inputs[1])
            logging.info("Right %s" % right)
            remote_mount = "/Volumes/ifs/mserve/"

            start_frame = 1
            if "start_frame" in options:
                start_frame = options["start_frame"]

            end_frame = 2
            if "end_frame" in options:
                end_frame = options["end_frame"]

            left_local_mount = os.path.join(settings.STORAGE_ROOT,left.service.container.default_path)
            right_local_mount = os.path.join(settings.STORAGE_ROOT,right.service.container.default_path)

            left_path=left.file.path
            right_path=right.file.path

            left_relative=left_path.replace(left_local_mount,remote_mount)
            right_relative=right_path.replace(right_local_mount,remote_mount)

            tfile_uuid = "r3d-image-"+str(uuid.uuid4())
            remoteimage = os.path.join(remote_mount,tfile_uuid)

            localimage = os.path.join(settings.STORAGE_ROOT,left.service.container.default_path,tfile_uuid,tfile_uuid+".000004.tif")

            logging.info("left_local_mount %s" % left_local_mount)
            logging.info("right_local_mount %s" % right_local_mount)
            logging.info("left_path %s" % left_path)
            logging.info("right_path %s" % right_path)
            logging.info("left_relative %s" % left_relative)
            logging.info("right_relative %s" % right_relative)
            logging.info("remoteimage %s" % remoteimage)
            logging.info("localimage %s" % localimage)

            result = _ssh_r3d(left_relative,right_relative,remoteimage,start_frame=start_frame,end_frame=end_frame)

            logging.info(result)

            # TODO: Change to local in deployment
            outputfile = open(localimage,'r')
            #outputfile = open(remoteimage,'r')

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
        from dataservice.models import MFile
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

        from jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput)
        jo.file.save('transcode.mov', File(videofile), save=True)

        videofile.close()

        return {"success":True,"message":"Digital Rapids transcode of video successful"}

    except Exception as e:
        logging.info("Error with digitalrapids %s" % e)
        raise e
