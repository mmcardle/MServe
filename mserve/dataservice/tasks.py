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

def _thumbvideo_XX(videopath,width,height):

    tfile = tempfile.NamedTemporaryFile(suffix=".png")
    thumbpath = tfile.name

    args = ["ffmpegthumbnailer","-t","20","-s","%sx%s"%(width,height),"-i",videopath,"-o",thumbpath]

    logging.info(args)
    ret = subprocess.call(args)

    logging.info("Created thumb from video RET = %s" % ret )

    image = Image.open(tfile.name)

    image = _thumbimageinstance(image,width,height)

    return image

def _thumbvideo(videopath,width,height):

    import pyffmpeg

    stream = pyffmpeg.VideoStream()
    stream2 = pyffmpeg.VideoStream()
    stream3 = pyffmpeg.VideoStream()
    stream4 = pyffmpeg.VideoStream()
    stream5 = pyffmpeg.VideoStream()
    stream.open(videopath)
    stream2.open(videopath)
    stream3.open(videopath)
    stream4.open(videopath)
    stream5.open(videopath)

    hw = float(int(width)/2)
    hh = float(int(height)/2)

    image = stream.GetFrameNo(0)
    image = _thumbimageinstance(image,width,height)

    try:
        image2 = stream2.GetFrameNo(0)
        image3 = stream3.GetFrameNo(333)
        image4 = stream4.GetFrameNo(666)
        image5 = stream5.GetFrameNo(1000)

        image2 = _thumbimageinstance(image2,hw,hh)
        image.paste(image2, (0, 0))

        image3 = _thumbimageinstance(image3,hw,hh)
        image.paste(image3, (hw, 0))

        image4 = _thumbimageinstance(image4,hw,hh)
        image.paste(image4, (0, hh))

        image5 = _thumbimageinstance(image5,hw,hh)
        image.paste(image5, (hw,hh))
    except IOError:
        logging.info("Unable to get frames for composite thumb")
        pass

    return image

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
        logging.info("Error with postervideo %s" % e)
        raise e

@task
def transcodevideo(inputs,outputs,options={},callbacks=[]):

    mfileid = inputs[0]
    from mserve.dataservice.models import MFile
    mf = MFile.objects.get(id=mfileid)
    infile = mf.file.path
    _ffmpeg_args=options["ffmpeg_args"]

    logfile = open('/var/mserve/mserve.log','a')
    errfile = open('/var/mserve/mserve.log','a')

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

        Popen(ffmpeg_args_rawvid,stdout=logfile,stderr=errfile)
        Popen(ffmpeg_args_rawwav,stdout=logfile,stderr=errfile)

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=logfile, close_fds=True)
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

    logfile = open('/var/mserve/mserve.log','a')
    errfile = open('/var/mserve/mserve.log','a')

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

        Popen(ffmpeg_args_rawvid,stdout=logfile,stderr=errfile)
        Popen(ffmpeg_args_rawwav,stdout=logfile,stderr=errfile)

        #vid_options= ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(width,height)]
        #aud_options= ["-acodec","libfaac","-ac","2","-ab","64","-ar","44100"]

        # TODO: Fix audio for mxf
        # if infile.endswith(".mxf"):
        #    aud_options= ["-acodec","libfaac","-ac","1","-ab","64","-ar","44100"]

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        #ffmpeg_args.extend(aud_options)
        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=logfile, close_fds=True)
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

        from mserve.dataservice.models import MFile
        _mf = MFile.objects.get(id=mfileid)
        _mf.checksum = md5string
        _mf.save()

        for callback in callbacks:
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

    tfile = tempfile.NamedTemporaryFile(delete=True,suffix=".png")
    image.save(tfile.name)
    dfile = File(open(tfile.name))
    
    from mserve.dataservice.models import MFile
    _mf = MFile.objects.get(pk=mfileid)
    _mf.thumb.save('thumb.png', dfile, save=True)

    logging.info("MFile thumb %s "%_mf.thumb)

    mfcheck = MFile.objects.get(id=mfileid)

    if mfcheck.thumb == "":
        return False

    logging.info("MFile Check thumb %s "%mfcheck.thumb)
    return True

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