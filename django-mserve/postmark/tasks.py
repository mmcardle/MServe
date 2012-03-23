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
import pycurl
import logging
import os
import re
import tempfile
import datetime
import shutil
import os.path
import time
import dataservice.utils as utils
import settings as settings
import paramiko
import uuid
import tarfile
import simplejson as json
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from ssh import MultiSSHClient
from dataservice.models import MFile
from jobservice.models import JobOutput
from django.shortcuts import render_to_response

def tar_files(temp_tarfile, base_dir, files):
    tar = tarfile.open(temp_tarfile, "w:gz")
    for name in files:
        fname = os.path.join(base_dir, name)
        aname = os.path.relpath(fname, base_dir)
        tar.add(fname, arcname=aname)
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


def _ssh_r2d(file, export_type, tmp_folder, start_frame=1, end_frame=2):

    ssh = MultiSSHClient()

    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(settings.R3D_HOST, username=settings.R3D_USER, password=settings.R3D_PASS)
    #output_file_dir,output_file_name = os.path.split(tmpimage)

    command = "redline --i %s --outDir %s/%s --exportPreset %s -s %s -e %s" % (file, tmp_folder, export_type, start_frame, end_frame)
    logging.info(command)

    stdin, stdout, stderr = ssh.exec_command(command)

    result = {}
    result["stdout"] = stdout.readlines()
    result["sdterr"] = stderr.readlines()

    return result

@task
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
        tfile_uuid = "r2d-transcode-"+str(uuid.uuid4())
        remoteimage = os.path.join(remote_mount,tfile_uuid)
        localimage = os.path.join(file_local_mount,tfile_uuid)

        logging.info("file_local_mount %s" % file_local_mount)
        logging.info("file_path %s" % file_path)
        logging.info("file_relative %s" % file_relative)
        logging.info("remoteimage %s" % remoteimage)
        logging.info("localimage %s" % localimage)

        result = _ssh_r2d(file_relative,export_type,remoteimage,start_frame=start_frame,end_frame=end_frame)

        localdir = os.path.join(file_local_mount,tfile_uuid)
        files = os.listdir(localdir)
        temp_tarfile = tempfile.NamedTemporaryFile('wb')
        tar_files(temp_tarfile.name, localdir, files)
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


@task
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


@task
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


class RequestReader:

    def __init__(self, tmpl, vars):
        self.finished = False
        self.POSTSTRING = str(render_to_response(tmpl,vars,
                mimetype='text/xml'))

    def read_cb(self, size):
        assert len(self.POSTSTRING) <= size
        if not self.finished:
            self.finished = True
            return self.POSTSTRING
        else:
            # Nothing more to read
            return ""

    def __len__(self):
        return  len(self.POSTSTRING)

class ResponseWriter:
   def __init__(self):
       self.contents = ''

   def body_callback(self, buf):
       self.contents = self.contents + buf


def fims_transformrequest(url, vars):
    transformRequestReader = RequestReader("transformRequest.tmpl.xml", vars)
    transformResponseWriter = ResponseWriter()

    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.POST, 1)
    c.setopt(c.POSTFIELDSIZE, len(transformRequestReader))
    c.setopt(c.READFUNCTION, transformRequestReader.read_cb)
    c.setopt(c.WRITEFUNCTION, transformResponseWriter.body_callback)
    if settings.DEBUG:
        c.setopt(c.VERBOSE, 1)
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    if status>=400:
        raise Exception("FIMS MEWS service returned an error %s " % status)
    c.close()
    transformjs = json.loads(transformResponseWriter.contents)
    return transformjs


def fims_job_queryrequest(url):
    jobQueryResponseWriter = ResponseWriter()
    c = pycurl.Curl()
    c.setopt(c.URL, url)
    c.setopt(c.WRITEFUNCTION, jobQueryResponseWriter.body_callback)
    if settings.DEBUG:
        c.setopt(c.VERBOSE, 1)
    c.perform()
    status = c.getinfo(c.HTTP_CODE)
    if status>=400:
        raise Exception("FIMS MEWS service returned an error %s " % status)
    c.close()
    jobjs = json.loads(jobQueryResponseWriter.contents)
    return jobjs


@task
def fims_mews(inputs, outputs, options={}, callbacks=[]):

    # TODO: Create the correct paths for the FIMS MEWS service to be able to
    # see the MFile content

    bmcontent_locator = ""
    jobguid = utils.unique_id()
    transfer_locator = ""
    transfer_destination = ""

    transform_vars = {'bmcontent_locator': bmcontent_locator,
            'jobguid': jobguid,
            'transfer_locator':transfer_locator,
            'transfer_destination':transfer_destination }

    js = fims_transformrequest(settings.FIMS_MEWS_URL_TRANSFORM, transform_vars)
    jobGUID = js["transformAck"]["operationInfo"]["jobID"]["jobGUID"]

    # TODO: instead of having max_polls use the status field to break
    # when the job fails (dont know what these statuses are yet)
    max_polls=5
    js_resp = fims_job_queryrequest(settings.FIMS_MEWS_URL_JOBQUERY+jobGUID)
    status = js_resp ["queryJobRequest"]["queryJobInfo"]["jobInfo"]["status"]\
                    ["code"]
                    
    while status == "running" and max_polls >= 0:
        time.sleep(5)
        js_resp = fims_job_queryrequest(settings.FIMS_MEWS_URL_JOBQUERY+jobGUID)
        print js_resp
        status = js_resp ["queryJobRequest"]["queryJobInfo"]["jobInfo"]["status"]\
                    ["code"]
        max_polls = max_polls -1

    # TODO: Save the result from transfer_destination and transfer_locator?

    return js_resp
