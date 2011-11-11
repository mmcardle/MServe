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
import json
import logging
import subprocess
import hashlib
import Image
import tempfile
import magic
import urlparse
import os
import os.path
import time
import shutil
import pycurl
import StringIO
import PythonMagick
import settings as settings
from celery.task import task
from celery.task.sets import subtask
from subprocess import Popen, PIPE
from datetime import timedelta
from celery.task.sets import TaskSet
from settings import HOSTNAME
from django.core.files import File

'''
from celery.task import periodic_task
@periodic_task(run_every=timedelta(minutes=15))
def service_scrubber():
    logging.info("Running service scrubber")
    from dataservice.models import DataService
    from dataservice.models import MFile
    for ds in DataService.objects.all():
        try:
            mfiles = list(ds.mfile_set.all().order_by('updated'))
            for mfile in mfiles:
                job = mfile.create_workflow_job("periodic")
                if job:
                    logging.info("Created workflow job %s " % (job) )
        except Exception, e:
            logging.info("Exception while scurbbing service %s , %s " % (ds, e))
'''
def _get_mfile(mfileid):
    from models import MFile
    mf = MFile.objects.get(id=mfileid)
    if os.path.exists(mf.file.path):
        return mf.file.path
    else:
        return _get_path(mf.get_download_path(),suffix=mf.name)

def _get_path(path,suffix=""):
    for name in settings.FILE_TRANSPORTS.keys():
        transport = settings.FILE_TRANSPORTS[name]
        logging.debug("Trying transport %s" % name)
        try:
            mfileresp = tempfile.NamedTemporaryFile('wb',suffix=suffix,delete=False)
            f = open(mfileresp.name,'w')
            remotemfile = '%s://%s:%s%s' % (transport["schema"],transport["netloc"],transport["port"],path)
            logging.debug("remotemfile %s" % remotemfile)

            c = pycurl.Curl()
            c.setopt(c.URL, str(remotemfile))
            c.setopt(pycurl.FOLLOWLOCATION, 1)
            c.setopt(c.WRITEFUNCTION, f.write)
            c.perform()
            status = c.getinfo(c.HTTP_CODE)
            c.close()
            f.close()

            if status > 400:
                logging.warn("Transport %s return error status code '%s' " % (name,status))
            else:
                return mfileresp.name
        except Exception as e:
            logging.warn("Could not get MFile from transport '%s'"%name)
            logging.warn(e)
    raise Exception("Could not get MFile any transports")

def _save_joboutput_thumb(outputid,image):
    from mserve.jobservice.models import JobOutput
    joboutput = JobOutput.objects.get(id=outputid)
    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    return _save_topath(tfile, joboutput.get_upload_thumb_path(), field=joboutput.thumb )

def _save_joboutput(outputid,file):
    from mserve.jobservice.models import JobOutput
    joboutput = JobOutput.objects.get(id=outputid)
    return _save_topath(file, joboutput.get_upload_path(), field=joboutput.file)

def _save_backupfile(backupid,file):
    from mserve.dataservice.models import BackupFile
    backupfile = BackupFile.objects.get(id=backupid)
    return _save_topath(file, backupfile.get_upload_path(), field=backupfile.file)

def _save_thumb(mfileid,image):
    from mserve.dataservice.models import MFile
    mfile = MFile.objects.get(id=mfileid)
    path = mfile.get_upload_thumb_path()
    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    return _save_topath(tfile, path, field=mfile.thumb)

def _save_poster(mfileid,image):
    from mserve.dataservice.models import MFile
    mfile = MFile.objects.get(id=mfileid)
    path = mfile.get_upload_poster_path()
    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    return _save_topath(tfile,path, field=mfile.poster)

def _save_proxy(mfileid,proxy):
    from mserve.dataservice.models import MFile
    mfile = MFile.objects.get(id=mfileid)
    path = mfile.get_upload_proxy_path()
    return _save_topath(proxy, path, field=mfile.proxy)

def _save_topath(file, path, field=None):
    for name in settings.FILE_TRANSPORTS.keys():
        transport = settings.FILE_TRANSPORTS[name]
        logging.debug("Trying transport %s" % name)
        if transport["schema"] == "http" or transport["schema"] == "https":
            try:
                resp = StringIO.StringIO()

                remotemfile = '%s://%s:%s%s' % (transport["schema"],transport["netloc"],transport["port"],path)
                logging.debug("remotemfile %s" % remotemfile)
                resp = StringIO.StringIO()

                f = open(file.name)
                c = pycurl.Curl()
                c.setopt(c.URL, str(remotemfile))
                c.setopt(c.PUT, 1)
                c.setopt(c.INFILE, f)
                c.setopt(c.INFILESIZE, os.path.getsize(f.name))
                c.setopt(c.WRITEFUNCTION, resp.write)
                c.perform()
                status = c.getinfo(c.HTTP_CODE)
                c.close()

                if status > 400:
                    logging.warn("Transport %s return error status code '%s' " % (name,status))
                else:
                    return f.name
            except Exception as e:
                logging.warn("Could not put MFile to transport '%s'"%name)
                logging.warn(e)
        elif transport["schema"] == "direct":
            if field != None:
                field.save(os.path.basename(file.name), File(file))
                return field.path
            else:
                logging.error("Transport Schema set to direct, but no field object provided")
    raise Exception("Could not put Mfile to any transports")

def _transcode_ffmpeg(videopath, options):

    if "width" in options:
        widthS = options["width"]
        width  = int(widthS)
    else:
        width = settings.postersize[0]

    if "height" in options:
        heightS = options["height"]
        height  = int(heightS)
    else:
        height = settings.postersize[1]

    if "ffmpeg_args" in options:
        _ffmpeg_args=options["ffmpeg_args"]
    else:
        _ffmpeg_args = ["-vcodec","libx264","-vpre","lossless_fast","-vf","scale=%s:%s"%(width,height),"-acodec","libfaac","-ac","2","-ab","64","-ar","44100"]

    # TODO: Replace with Job Logs
    nulfp = open(os.devnull, "w")
    _stdout = nulfp.fileno()
    _stderr = nulfp.fileno()

    tfile = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
    outfile = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")

    try:
        tmpfile=tfile.name
        vidfifo="stream.yuv"
        audfifo="stream.wav"

        tmpdir = tempfile.mkdtemp()
        vidfilename = os.path.join(tmpdir, vidfifo)
        try:
            os.mkfifo(vidfilename)
        except OSError, e:
            logging.info("Failed to create Video FIFO: %s" % e)

        audfilename = os.path.join(tmpdir, audfifo)
        try:
            os.mkfifo(audfilename)
        except OSError, e:
            logging.info("Failed to create Audio FIFO: %s" % e)

        ffmpeg_args_rawvid = ["ffmpeg","-y","-i",videopath,"-an","-f","yuv4mpegpipe",vidfilename]
        ffmpeg_args_rawwav = ["ffmpeg","-y","-i",videopath,"-f","wav","-acodec","pcm_s16le",audfilename]

        Popen(ffmpeg_args_rawvid,stdout=_stdout,stderr=_stderr)
        Popen(ffmpeg_args_rawwav,stdout=_stdout,stderr=_stderr)

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=_stdout, stderr=_stderr, close_fds=True)
        p.communicate()

        if os.path.getsize(tmpfile) == 0:
            raise Exception("ffmpeg produced 0 size output")

        qt_args = ["qt-faststart", tmpfile, outfile.name]
        qt = Popen(qt_args, stdin=PIPE, stdout=_stdout, stderr=_stderr, close_fds=True)
        qt.communicate()

        return outfile

    except:
        logging.info("Error encoding video")
        os.unlink(tmpfile)
        tfile.close()
        raise


def _thumbvideo_ffmpegthumbnailer(videopath,width,height,tiled=False):

    tfile = tempfile.NamedTemporaryFile(suffix=".png")
    tfile1 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile2 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile3 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile4 = tempfile.NamedTemporaryFile(suffix=".png")

    logging.info("Processing video thumb %sx%s for %s to %s" % (width,height,videopath,tfile.name))
    if not os.path.exists(videopath):
        logging.info("Video %s does not exist" % (videopath))
        return False

    if tiled:
        hw = float(int(width)/2)
        hh = float(int(height)/2)

        subprocess.call(["ffmpegthumbnailer","-t","10","-s","%sx%s"%(width,height),"-i",videopath,"-o",tfile.name])
        subprocess.call(["ffmpegthumbnailer","-t","20","-s","%sx%s"%(hw,hh),"-i",videopath,"-o",tfile1.name])
        subprocess.call(["ffmpegthumbnailer","-t","40","-s","%sx%s"%(hw,hh),"-i",videopath,"-o",tfile2.name])
        subprocess.call(["ffmpegthumbnailer","-t","60","-s","%sx%s"%(hw,hh),"-i",videopath,"-o",tfile3.name])
        subprocess.call(["ffmpegthumbnailer","-t","80","-s","%sx%s"%(hw,hh),"-i",videopath,"-o",tfile4.name])

        image = Image.open(tfile.name)
        image1 = Image.open(tfile1.name)
        image2 = Image.open(tfile2.name)
        image3 = Image.open(tfile3.name)
        image4 = Image.open(tfile4.name)

        image.paste(image1, (0,0))
        image.paste(image2, (int(hw),0))
        image.paste(image3, (0,int(hh)))
        image.paste(image4, (int(hw),int(hh)))

        return image
    else:
        subprocess.call(["ffmpegthumbnailer","-t","10","-s","%sx%s"%(width,height),"-i",videopath,"-o",tfile.name])
        image = Image.open(tfile.name)
        return image

def _thumbvideo(videopath,width,height,tiled=False):

    try:
        import pyffmpeg

        if tiled:
            hw = float(int(width)/2)
            hh = float(int(height)/2)

            try:

                reader = pyffmpeg.FFMpegReader(False)
                reader.open(videopath,pyffmpeg.TS_VIDEO_PIL)
                vt=reader.get_tracks()[0]

                vt.seek_to_frame(0)
                image = vt.get_current_frame()[2]
                image = _thumbimageinstance(image,width,height)

                rdrdurtime=reader.duration_time()
                cdcdurtime=vt.duration_time()
                mt=max(cdcdurtime,rdrdurtime)
                nframes=min(mt*vt.get_fps(),1000)

                frames = range(0,nframes,nframes/5)[-4:]

                vt.seek_to_frame(frames[0])
                image2 = vt.get_current_frame()[2]
                image2 = _thumbimageinstance(image2,hw,hh)
                image.paste(image2, (0, 0))

                vt.seek_to_frame(frames[1])
                image3 = vt.get_current_frame()[2]
                image3 = _thumbimageinstance(image3,hw,hh)
                image.paste(image3, (hw, 0))

                vt.seek_to_frame(frames[2])
                image4 = vt.get_current_frame()[2]
                image4 = _thumbimageinstance(image4,hw,hh)
                image.paste(image4, (0, hh))

                vt.seek_to_frame(frames[3])
                image5 = vt.get_current_frame()[2]
                image5 = _thumbimageinstance(image5,hw,hh)
                image.paste(image5, (hw,hh))

                reader.close()

                logging.info("Reader Done")

                return image

            except IOError as e:
                logging.info("IOError seeking pyffmeg, trying ffmpegthumbnailer")

            return _thumbvideo_ffmpegthumbnailer(videopath,width,height,tiled=tiled)
        else:
            try:
                reader = pyffmpeg.FFMpegReader(False)
                reader.open(videopath,pyffmpeg.TS_VIDEO_PIL)
                vt=reader.get_tracks()[0]
                vt.seek_to_frame(0)
                image = vt.get_current_frame()[2]
                image = _thumbimageinstance(image,width,height)
                reader.close()
                logging.info("Reader Done")
                return image

            except IOError as e:
                logging.info("IOError seeking pyffmeg, trying ffmpegthumbnailer")

            return _thumbvideo_ffmpegthumbnailer(videopath,width,height,tiled=tiled)
    except ImportError:
        logging.error("Could not import pyffmpeg, failing back to ffmpegthumbnailer")
        return _thumbvideo_ffmpegthumbnailer(videopath,width,height,tiled=tiled)

@task(default_retry_delay=15,max_retries=3,name="thumbvideo")
def thumbvideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        videopath = _get_mfile(mfileid)

        width=options["width"]
        height=options["height"]

        tiled=False
        if "tiled" in options:
            tiledS = options["tiled"]
            if tiledS == "True" or tiledS == "true":
                tiled = True

        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height,tiled=tiled)

        if not _save_thumb(mfileid,image):
            thumbvideo.retry([inputs,outputs,options,callbacks])

        return {"success":True,"message":"Thumbnail '%sx%s' of video successful"%(width,height)}
    except Exception as e:
        logging.info("Error with thumbvideo %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3,name="postervideo")
def postervideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        videopath = _get_mfile(mfileid)

        width=options["width"]
        height=options["height"]

        tiled=False
        if "tiled" in options:
            tiledS = options["tiled"]
            if tiledS == "True" or tiledS == "true":
                tiled = True

        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height,tiled=tiled)

        if not _save_poster(mfileid,image):
            postervideo.retry([inputs,outputs,options,callbacks])

        return {"success":True,"message":"Poster '%sx%s' of video successful"%(width,height)}
    except Exception, e:
        logging.info("Error with postervideo %s : %s" % (type(e),e))
        raise

@task(default_retry_delay=15,max_retries=3,name="transcodevideo")
def transcodevideo(inputs,outputs,options={},callbacks=[]):

    mfileid = inputs[0]
    infile = _get_mfile(mfileid)
    joboutput = outputs[0]

    transcode = _transcode_ffmpeg(infile, options)
    
    if os.path.getsize(transcode.name) == 0:
        raise Exception("Transcode produced a 0 byte file")

    transcode.close()

    upload = open(transcode.name,'r')
    _save_joboutput(joboutput, upload)
    upload.close()

    return {"success":True, "message": "Transcode Successful"}


@task(default_retry_delay=15,max_retries=3,name="proxyvideo")
def proxyvideo(inputs,outputs,options={},callbacks=[]):

    mfileid = inputs[0]
    infile = _get_mfile(mfileid)

    transcode = _transcode_ffmpeg(infile, options)

    if os.path.getsize(transcode.name) == 0:
        raise Exception("Proxy Transcode produced a 0 byte file")
    
    transcode.close()

    upload = open(transcode.name,'r')
    _save_proxy(mfileid, upload)
    upload.close()

    return {"success":True, "message": "Proxy Successful"}


@task(default_retry_delay=15,max_retries=3,name="mimefile")
def mimefile(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]
        path = _get_mfile(mfileid)
        m = magic.open(magic.MAGIC_MIME)
        m.load()

        upath = path.encode("utf-8")
        result = m.file(upath)
        mimetype = result.split(';')[0]

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        mf.mimetype = mimetype
        mf.save()

        for callback in callbacks:
            logging.info("Mimefile callback - "% callback)
            subtask(callback).delay()

        return {"success":True,"message":"Mime detection successful", "mimetype" : mimetype}
    except Exception as e:
        logging.info("Error with mime %s" % e)
        import sys
        import traceback
        traceback.print_exc(file=sys.stdout)
        raise e

@task
def backup_mfile(inputs,outputs,options={},callbacks=[]):
    """Backup MFile """
    try:
        mfileid = inputs[0]

        from mserve.dataservice.models import MFile
        from mserve.dataservice.models import BackupFile

        mf = MFile.objects.get(id=mfileid)
        path = _get_mfile(mfileid)
        file = open(path,'r')

        backup = BackupFile(name="backup_%s"%mf.name,mfile=mf,mimetype=mf.mimetype,checksum=mf.checksum)
        backup.save()

        _save_backupfile(backup.id, file)

        return {"success":True,"message":"Backup of '%s' successful"%mf.name}
    except Exception, e:
        logging.info("Error with backup_mfile %s" % e)
        raise

@task(default_retry_delay=15,max_retries=3,name="email")
def email(inputs,outputs,options={},callbacks=[]):
    try:
        from django.core.mail import send_mail

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=inputs[0])

        message = "Your workflow on file '%s' has succedded\n" % (mf.name)

        send_mail('MServe Workflow', message, 'mserve@'+HOSTNAME,
            ['mm@it-innovation.soton.ac.uk'], fail_silently=False)

        return { "message":"Email sent" }
    except Exception as e:
        logging.info("Error with email %s" % e)
        raise e


@task
def continue_workflow_taskset(mfileid, jobid, nexttasksetid):
    try:
        from mserve.jobservice.models import Job
        from mserve.dataservice.models import MFile, DataServiceTaskSet
        prevjob = Job.objects.get(id=jobid)
        nexttaskset = DataServiceTaskSet.objects.get(id=nexttasksetid)

        if prevjob.successful():
            nexttaskset.workflow.continue_workflow_job(mfileid, nexttasksetid)
        elif prevjob.failed():
            raise Exception("Workflow task failed")
        else:
            logging.info("Job %s not complete yet", prevjob)
            continue_workflow_taskset.apply_async(args=[mfileid, jobid, nexttasksetid], countdown=5)
    except Exception as e:
        logging.info("Error with continue_workflow_task %s" % e)
        raise e


@task
def mfilefetch(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        path = _get_mfile(mfileid)
        file = open(path,'r')
        outputid = outputs[0]
        _save_joboutput(outputid, file)
        return {"message":"Retrieval of '%s' successful"%mf.name}
    except Exception as e:
        logging.info("Error with mfilefetch %s" % e)
        raise e

@task
def md5fileverify(inputs,outputs,options={},callbacks=[]):

    """Return hex md5 digest for a Django FieldFile"""
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        path = _get_mfile(mfileid)
        file = open(path,'r')
        md5 = hashlib.md5()
        while True:
            data = file.read(8192)  # multiple of 128 bytes is best
            if not data:
                break
            md5.update(data)
        file.close()
        calculated_md5 = md5.hexdigest()

        logging.info("Verify MD5 calclated %s" % calculated_md5)

        from mserve.dataservice.models import MFile
        _mf = MFile.objects.get(id=mfileid)
        db_md5 = _mf.checksum

        if db_md5 != calculated_md5:
            raise Exception("MD5 Verification Failed")

        for callback in callbacks:
            subtask(callback).delay()

        return {"message":"Verification of '%s' successful %s=%s" % (mf,db_md5,calculated_md5), "md5" : calculated_md5  }

    except Exception as e:
        logging.info("Error with mime %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3,name="md5file")
def md5file(inputs,outputs,options={},callbacks=[]):

    """Return hex md5 digest for a Django FieldFile"""
    try:
        mfileid = inputs[0]
        path = _get_mfile(mfileid)
        file = open(path,'r')
        md5 = hashlib.md5()
        while True:
            data = file.read(8192)  # multiple of 128 bytes is best
            if not data:
                break
            md5.update(data)
        file.close()
        md5string = md5.hexdigest()
        logging.info("MD5 calclated %s" % (md5string ))

        from mserve.dataservice.models import MFile
        _mf = MFile.objects.get(id=mfileid)
        _mf.checksum = md5string
        _mf.save()

        for callback in callbacks:
            logging.info("Running Callback %s" % callback)
            subtask(callback).delay()

        return {"success":True,"message":"MD5 successful", "md5" : md5string}
    except Exception, e:
        logging.info("Error with md5 %s" % e)
        raise

@task(default_retry_delay=15,max_retries=3,name="posterimage_remote")
def posterimage_remote(inputs,outputs,options={},callbacks=[]):

    try:
        print inputs
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)

        remoteservice = "http://jester/services/CpNP8KcttY9D4vunctgSRPIfZOdstOkUAVAl0tNKs/mfiles/"

        #response = cStringIO.StringIO()
        resp = StringIO.StringIO()

        pf = [  ('file', (pycurl.FORM_FILE, str(mf.file.path))), ]
        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, remoteservice)
        c.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        #c.setopt(c.HTTPHEADER, [ 'Expect:' ] )
        c.setopt(c.WRITEFUNCTION, resp.write)

        c.setopt(c.HTTPPOST, pf)
        #c.setopt(c.VERBOSE, 1)

        c.perform()
        c.close()

        print resp

    except Exception as e:
        logging.info("Error with posterimage %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3,name="posterimage")
def posterimage(inputs,outputs,options={},callbacks=[]):

    try:

        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        logging.info("Creating %sx%s image for %s" % (width,height,input))
        
        path = _get_mfile(mfileid)
        image = _thumbimage(path,width,height)

        if image:

            if not _save_poster(mfileid,image):
                posterimage.retry([inputs,outputs,options,callbacks])

            logging.info("Poster created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Poster '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")
    except Exception ,e:
        #logging.info("Error with posterimage %s" % e)
        raise

@task(default_retry_delay=15,max_retries=3,name="thumbimage")
def thumbimage(inputs,outputs,options={},callbacks=[]):
    
    try:
        inputid = inputs[0]       

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        path = _get_mfile(inputid)

        logging.info("Creating %sx%s image for %s" % (width,height,inputid))

        image = _thumbimage(path, width,height)

        if image:

            if not _save_thumb(inputid,image):
                thumbimage.retry([inputs,outputs,options,callbacks])

            logging.info("Thumbnail created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Thumbnail '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")

    except:# Exception as e:
        #logging.info("Error with thumbimage %s" % e)
        raise

@task(default_retry_delay=15,max_retries=3)
def thumboutput(inputs,outputs,options={},callbacks=[]):

    try:
        inputid = inputs[0]

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        from mserve.jobservice.models import JobOutput
        jo = JobOutput.objects.get(pk=inputid)
        path = jo.file.path

        logging.info("Creating %sx%s image for %s" % (width,height,inputid))

        image = _thumbimage(path,width,height)

        if image:

            if not _save_joboutput_thumb(inputid,image):
                thumboutput.retry([inputs,outputs,options,callbacks])

            logging.info("Thumbnail created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Thumbnail '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")

    except Exception as e:
        logging.info("Error with thumbimage %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3)
def thumbvideooutput(inputs,outputs,options={},callbacks=[]):

    try:
        inputid = inputs[0]

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        tiled=False
        if "tiled" in options:
            tiledS = options["tiled"]
            if tiledS == "True" or tiledS == "true":
                tiled = True

        from mserve.jobservice.models import JobOutput
        jo = JobOutput.objects.get(pk=inputid)
        path = jo.file.path

        logging.info("Creating %sx%s image for %s" % (width,height,inputid))

        image = _thumbvideo(path,width,height,tiled=tiled)

        if image:

            if not _save_joboutput_thumb(inputid,image):
                thumbvideooutput.retry([inputs,outputs,options,callbacks])

            logging.info("Thumbnail created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Thumbnail '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")

    except Exception as e:
        logging.info("Error with thumbimage %s" % e)
        raise e

def _thumbimage(input,width,height):
    if not os.path.exists(input):
        raise Exception("Image %s does not exist" % input)
    try:
        im = Image.open(input)
        return _thumbimageinstance(im,width,height)
    except Exception as e:
        logging.info("Error thumnailing image, trying ImageMagick, Error was : %s" %e)
        img = PythonMagick.Image()
        img.read(str(input))
        tfile = tempfile.NamedTemporaryFile('wb',suffix=".png")
        img.write(tfile.name)
        im = Image.open(tfile.name)
        return _thumbimageinstance(im,width,height)

def _thumbimageinstance(im,width,height):

    width = int(width)
    height = int(height)

    w, h = im.size

    if float(w)/h < float(width)/float(height):
            im = im.resize((width, h*width/w), Image.ANTIALIAS)
    else:
            im = im.resize((w*int(height)/h, int(height)), Image.ANTIALIAS)
    w, h = im.size

    im = im.crop(((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height))

    im.thumbnail((width,height))

    return im

def _thumb_file_remote(filename,remoteservice,width,height):

        logging.info("Calling remote service %s " % remoteservice)

        scheme, netloc, path, query, fragid = urlparse.urlsplit(remoteservice)

        logging.info("%s %s %s %s %s "% (scheme, netloc, path, query, fragid ))

        remotemfile = '%s://%s/%s/mfiles/' % (scheme,netloc,path)

        resp = StringIO.StringIO()

        pf = [  ('file', (pycurl.FORM_FILE, str(filename))), ]
        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, str(remotemfile))
        c.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        c.setopt(c.WRITEFUNCTION, resp.write)
        c.setopt(c.HTTPPOST, pf)
        c.perform()
        c.close()

        logging.info(resp.getvalue())

        js = json.loads(resp.getvalue())

        id = js['id']

        remotejob = '%s://%s/mfiles/%s/jobs/' % (scheme,netloc,id)

        jobresp = StringIO.StringIO()

        jobpf = [  ('jobtype', (pycurl.FORM_CONTENTS, "dataservice.tasks.posterimage") ),
                    ('width', (pycurl.FORM_CONTENTS, str(width)) ),
                    ('height', (pycurl.FORM_CONTENTS, str(height)) ),
                    ]
        c2 = pycurl.Curl()
        c2.setopt(c2.POST, 1)
        c2.setopt(c2.URL, str(remotejob))
        c2.setopt(c2.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        c2.setopt(c2.WRITEFUNCTION, jobresp.write)
        c2.setopt(c2.HTTPPOST, jobpf)
        c2.perform()
        c2.close()

        print "Job Resp - %s" % jobresp.getvalue()

        jobjs = json.loads(jobresp.getvalue())

        jobid = jobjs['id']

        remotejob = '%s://%s/jobs/%s/' % (scheme,netloc,jobid)

        jobstatusresp = StringIO.StringIO()
        c3 = pycurl.Curl()
        c3.setopt(c3.URL, str(remotejob))
        c3.setopt(c3.WRITEFUNCTION, jobstatusresp.write)

        status = False
        while True:
            time.sleep(3)

            c3.perform()

            print "Job Resp - %s" % jobstatusresp.getvalue()

            jobjs = json.loads(jobstatusresp.getvalue())

            status = jobjs['tasks']['successful']

            print status

            if status:
                break

        c3.close()

        import tempfile
        if status:

            outfile = tempfile.NamedTemporaryFile()
            f = open(outfile.name,'w')

            remotemfile= "%s://%s/mfiles/%s/" % (scheme,netloc,id)

            print remotemfile
            mfileresp = StringIO.StringIO()
            c4 = pycurl.Curl()
            c4.setopt(c4.URL, str(remotemfile))
            c4.setopt(c4.WRITEFUNCTION, mfileresp.write)
            c4.perform()
            c4.close()

            print "Mfile Resp - %s" % mfileresp.getvalue()

            mfilejs = json.loads(mfileresp.getvalue())

            posterpath = mfilejs['thumburl']

            posterurl = "%s://%s/%s/"% (scheme,netloc,posterpath)

            c5 = pycurl.Curl()
            c5.setopt(c5.URL, str(posterurl))
            c5.setopt(c5.WRITEFUNCTION, f.write)
            c5.perform()
            c5.close()

            print outfile

            mfiledelresp = StringIO.StringIO()
            c6 = pycurl.Curl()
            c6.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            c6.setopt(c6.URL, str(remotemfile))
            c6.setopt(c6.WRITEFUNCTION, mfiledelresp.write)
            c6.perform()

            print mfiledelresp.getvalue()

            image = Image.open(outfile.name)

            return image