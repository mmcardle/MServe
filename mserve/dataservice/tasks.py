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
from celery.decorators import task
from celery.task.sets import subtask
from subprocess import Popen, PIPE
import logging
import subprocess
import hashlib
import Image
import tempfile
import magic
import os
import os.path
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

def _thumbvideo_ffmpegthumbnailer(videopath,width,height):

    tfile = tempfile.NamedTemporaryFile(suffix=".png")
    tfile1 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile2 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile3 = tempfile.NamedTemporaryFile(suffix=".png")
    tfile4 = tempfile.NamedTemporaryFile(suffix=".png")

    logging.info("Processing video thumb %sx%s for %s to %s" % (width,height,videopath,tfile.name))
    if not os.path.exists(videopath):
        logging.info("Video %s does not exist" % (videopath))
        return False

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
    image.paste(image2, (hw,0))
    image.paste(image3, (0,hh))
    image.paste(image4, (hw,hh))

    return image


def _thumbvideo(videopath,width,height):

    try:
        import pyffmpeg

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

        return _thumbvideo_ffmpegthumbnailer(videopath,width,height)
    except ImportError:
        logging.error("Could not import pyffmpeg, failing back to ffmpegthumbnailer")
        return _thumbvideo_ffmpegthumbnailer(videopath,width,height)

@task
def thumbvideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        videopath = mf.file.path

        width=options["width"]
        height=options["height"]
        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height)

        if not _save_thumb(mfileid,image):
            thumbvideo.retry([inputs,outputs,options,callbacks])

        return {"success":True,"message":"Thumbnail '%sx%s' of video successful"%(width,height)}
    except Exception as e:
        logging.info("Error with thumbvideo %s" % e)
        raise e

@task
def postervideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        videopath = mf.file.path

        width=options["width"]
        height=options["height"]
        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height)

        if not _save_poster(mfileid,image):
            postervideo.retry([inputs,outputs,options,callbacks])

        return {"success":True,"message":"Poster '%sx%s' of video successful"%(width,height)}
    except Exception as e:
        logging.info("Error with postervideo %s : %s" % (type(e),e))
        raise e

@task
def transcodevideo(inputs,outputs,options={},callbacks=[]):

    mfileid = inputs[0]
    from mserve.dataservice.models import MFile
    mf = MFile.objects.get(id=mfileid)
    infile = mf.file.path
    _ffmpeg_args=options["ffmpeg_args"]

    _stdin = None
    _stderr = None

    tfile = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
    toutfile = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")
    joboutput = outputs[0]

    try:
        tmpfile=tfile.name
        tmpoutfile=toutfile.name
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

        ffmpeg_args_rawvid = ["ffmpeg","-y","-i",infile,"-an","-f","yuv4mpegpipe",vidfilename]
        ffmpeg_args_rawwav = ["ffmpeg","-y","-i",infile,"-f","wav","-acodec","pcm_s16le",audfilename]

        Popen(ffmpeg_args_rawvid,stdout=_stdin,stderr=_stderr)
        Popen(ffmpeg_args_rawwav,stdout=_stdin,stderr=_stderr)

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=_stdin, close_fds=True)
        p.communicate()

        qt_args = ["qt-faststart", tmpfile, tmpoutfile]
        qt = Popen(qt_args, stdin=PIPE, close_fds=True)
        qt.communicate()

        from mserve.jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput.pk)
        jo.file.save('transcode.mp4', File(toutfile), save=True)

        logging.info("Created file at : %s" % jo.file.path)

    except Exception as e:
        logging.info("Error encoding video %s" % e)
        os.unlink(tmpfile)
        tfile.close()
        raise e
    else:
        logging.info("Proxy Video '%s' Done"% infile)
        os.unlink(tmpfile)
        tfile.close()

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"Transcode  successful"}

@task
def proxyvideo(inputs,outputs,options={},callbacks=[]):

    mfileid = inputs[0]
    from mserve.dataservice.models import MFile
    mf = MFile.objects.get(id=mfileid)
    infile = mf.file.path
    _ffmpeg_args=options["ffmpeg_args"]

    #_stdout = open('/var/mserve/mserve.log','a')
    #_stderr = open('/var/mserve/mserve.log','a')
    _stdout = PIPE
    _stderr = PIPE

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

        ffmpeg_args_rawvid = ["ffmpeg","-y","-i",infile,"-an","-f","yuv4mpegpipe",vidfilename]
        ffmpeg_args_rawwav = ["ffmpeg","-y","-i",infile,"-f","wav","-acodec","pcm_s16le",audfilename]

        Popen(ffmpeg_args_rawvid,stdout=_stdout,stderr=_stderr)
        Popen(ffmpeg_args_rawwav,stdout=_stdout,stderr=_stderr)

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=_stdout, close_fds=True)
        p.communicate()

        qt_args = ["qt-faststart", tmpfile, outfile.name]
        qt = Popen(qt_args, stdin=PIPE, close_fds=True)
        qt.communicate()

        # Save to the thumbnail field
        outfile.seek(0)
        suf = SimpleUploadedFile("mfile",
                outfile.read(), content_type='image/png')

        _mf = MFile.objects.get(id=mfileid)
        _mf.proxy.save(suf.name+'_proxy.mp4', suf, save=True)

    except Exception as e:
        logging.info("Error encoding video %s" % e)
        os.unlink(tmpfile)
        tfile.close()
        raise e
    else:
        logging.info("Proxy Video '%s' Done"% infile)
        os.unlink(tmpfile)
        tfile.close()

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"Transcode successful"}

@task
def mimefile(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)

        m = magic.open(magic.MAGIC_MIME)
        m.load()
        result = m.file(mf.file.path)
        mimetype = result.split(';')[0]
        logging.info("Mime for file %s is %s" % (mf,mimetype))

        mf.mimetype = mimetype
        mf.save()

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"Mime detection successful", "mimetype" : mimetype}
    except Exception as e:
        logging.info("Error with mime %s" % e)
        raise e
@task
def backup_mfile(inputs,outputs,options={},callbacks=[]):
    """Backup MFile """
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        file = mf.file

        from dataservice.models import BackupFile

        backup = BackupFile(name="backup_%s"%file.name,mfile=mf,mimetype=mf.mimetype,checksum=mf.checksum,file=file)
        backup.save()

        return {"success":True,"message":"Backup of '%s' successful"%mf.name}
    except Exception as e:
        logging.info("Error with backup_mfile %s" % e)
        raise e

@task
def mfilefetch(inputs,outputs,options={},callbacks=[]):
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        file = mf.file

        outputid = outputs[0]

        from jobservice.models import JobOutput
        output = JobOutput.objects.get(id=outputid)
        output.file.save("JobOutput",File(file))
        output.mimetype = mf.mimetype
        output.save()

        return {"message":"Retrieval of '%s' successful"%mf.name}
    except Exception as e:
        logging.info("Error with backup_mfile %s" % e)
        raise e


@task
def md5fileverify(inputs,outputs,options={},callbacks=[]):

    """Return hex md5 digest for a Django FieldFile"""
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        file = open(mf.file.path,'r')
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

        return {"message":"Verification of '%s' successful %s=%s" % (mf,db_md5,calculated_md5) }

    except Exception as e:
        logging.info("Error with mime %s" % e)
        raise e

@task
def md5file(inputs,outputs,options={},callbacks=[]):

    """Return hex md5 digest for a Django FieldFile"""
    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        file = open(mf.file.path,'r')
        md5 = hashlib.md5()
        while True:
            data = file.read(8192)  # multiple of 128 bytes is best
            if not data:
                break
            md5.update(data)
        file.close()
        md5string = md5.hexdigest()
        logging.info("MD5 calclated %s" % (md5string ))

        _mf = MFile.objects.get(id=mfileid)
        _mf.checksum = md5string
        _mf.save()

        for callback in callbacks:
            logging.info("Running Callback %s" % callback)
            subtask(callback).delay()

        return {"success":True,"message":"MD5 of '%s' successful"%mf, "md5" : md5string}
    except Exception as e:
        logging.info("Error with mime %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3)
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

        image = _thumbimage(mf.file.path,width,height)

        if image:

            if not _save_poster(mfileid,image):
                posterimage.retry([inputs,outputs,options,callbacks])

            logging.info("Poster created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Poster '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")
    except Exception as e:
        logging.info("Error with posterimage %s" % e)
        raise e

@task
def thumbvideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfileid = inputs[0]
        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfileid)
        videopath = mf.file.path

        width=options["width"]
        height=options["height"]
        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height)

        if image:
            if not _save_thumb(mfileid,image):
                thumbvideo.retry([inputs,outputs,options,callbacks])

            return {"success":True,"message":"Thumbnail '%sx%s' of video successful"%(width,height)}
        else:
            raise Exception("Could not create video thumb image")
        
    except Exception as e:
        logging.info("Error with thumbvideo %s" % e)
        raise e

@task(default_retry_delay=15,max_retries=3)
def thumbimage(inputs,outputs,options={},callbacks=[]):
    
    try:
        inputid = inputs[0]       

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(pk=inputid)
        path = mf.file.path

        logging.info("Creating %sx%s image for %s" % (width,height,inputid))

        image = _thumbimage(path,width,height)

        if image:

            if not _save_thumb(inputid,image):
                thumbimage.retry([inputs,outputs,options,callbacks])

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

            if not _save_output_thumb(inputid,image):
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

def _save_poster(mfileid,image):

    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    dfile = File(open(tfile.name))

    from mserve.dataservice.models import MFile
    _mf = MFile.objects.get(id=mfileid)
    _mf.poster.save('poster.png', dfile, save=True)

    mfcheck = MFile.objects.get(id=mfileid)

    if mfcheck.poster == "":
        return False

    logging.info("MFile Check poster %s "%mfcheck.poster)
    return True

def _save_thumb(mfileid,image):

    try:
        tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
        image.save(tfile.name)
        dfile = File(open(tfile.name))

        from mserve.dataservice.models import MFile
        _mf = MFile.objects.get(pk=mfileid)
        _mf.thumb.save('thumb.png', dfile, save=True)

        mfcheck = MFile.objects.get(id=mfileid)

        if mfcheck.thumb == "":
            return False

        return True
    except IOError as e:
        logging.info("MFile Check thumb error %s "%e)
        raise e
    except Exception as e:
        logging.info("MFile Check thumb error %s "%e)
        raise e

def _save_output_thumb(outputid,image):

    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    dfile = File(open(tfile.name))

    from mserve.jobservice.models import JobOutput
    _jo = JobOutput.objects.get(pk=outputid)
    _jo.thumb.save('thumb.png', dfile, save=True)

    logging.info("JobOutput thumb %s "%_jo.thumb)

    jocheck = JobOutput.objects.get(id=outputid)

    if jocheck.thumb == "":
        return False

    logging.info("JobOutput Check thumb %s "%jocheck.thumb)
    return True


def _thumbimage(input,width,height):
    if not os.path.exists(input):
        raise Exception("Image %s does not exist" % input)
    im = Image.open(input)
    return _thumbimageinstance(im,width,height)

def _thumbimageinstance(im,width,height):

    width = int(width)
    height = int(height)

    w, h = im.size

    if float(w)/h < float(width)/float(height):
            im = im.resize((width, h*width/w), Image.ANTIALIAS)
    else:
            logging.info("Thumbnail 3 %s %s" % (w,h))
            im = im.resize((w*int(height)/h, int(height)), Image.ANTIALIAS)
            logging.info("Thumbnail 3.5 %s %s" % (w,h))
    w, h = im.size

    im = im.crop(((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height))

    im.thumbnail((width,height))

    return im