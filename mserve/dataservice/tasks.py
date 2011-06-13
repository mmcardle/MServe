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
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

def _thumbvideo(videopath,width,height):

    tfile = tempfile.NamedTemporaryFile(suffix=".png")
    thumbpath = tfile.name

    args = ["ffmpegthumbnailer","-t","20","-s","%sx%s"%(width,height),"-i",videopath,"-o",thumbpath]

    logging.info(args)
    ret = subprocess.call(args)

    logging.info("Created thumb from video RET = %s" % ret )

    image = Image.open(tfile.name)

    image.thumbnail((width,height))

    return image


@task
def thumbvideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfile = inputs[0]
        videopath = mfile.file.path

        width=options["width"]
        height=options["height"]
        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height)
        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile("mfile_thumb",temp_handle.read(), content_type='image/png')

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfile.pk)
        #mf.thumb.save(suf.name+'.png', suf, save=True)
        mfile.thumb.save(suf.name+'.png', suf, save=True)

        logging.info("Thumb Video %s" % (mfile.thumb))
        logging.info("Thumb Video %s" % (mf.thumb))

        return {"success":True,"message":"Thumbnail '%sx%s' of video successful"%(width,height)}
    except Exception as e:
        logging.info("Error with thumbvideo %s" % e)
        raise e

@task
def postervideo(inputs,outputs,options={},callbacks=[]):

    try:
        mfile = inputs[0]
        videopath = mfile.file.path

        width=options["width"]
        height=options["height"]
        logging.info("Processing video thumb %sx%s for %s" % (width,height,videopath))
        if not os.path.exists(videopath):
            logging.info("Video %s does not exist" % (videopath))
            return False

        image = _thumbvideo(videopath,width,height)
        temp_handle = StringIO()
        image.save(temp_handle, 'png')
        temp_handle.seek(0)

        # Save to the thumbnail field
        suf = SimpleUploadedFile('mfile_poster',temp_handle.read(), content_type='image/png')

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfile.pk)
        mf.poster.save(suf.name+'.png', suf, save=True)

        logging.info("Poster Video %s" % (mf.poster.path))

        return {"success":True,"message":"Poster '%sx%s' of video successful"%(width,height)}
    except Exception as e:
        logging.info("Error with postervideo %s" % e)
        raise e

@task
def transcodevideo(inputs,outputs,options={},callbacks=[]):

    mfile = inputs[0]
    infile = mfile.file.path
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

        #vid_options= ["-vcodec","libx264","-vpre","baseline","-vf","scale=%s:%s"%(width,height)]
        #aud_options= ["-acodec","libfaac","-ac","2","-ab","64","-ar","44100"]

        # TODO: Fix audio for mxf
        #if infile.endswith(".mxf"):
        #    aud_options= ["-acodec","libfaac","-ac","1","-ab","64","-ar","44100"]

        ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename]

        logging.info("Transcode 0 ")

        #ffmpeg_args.extend(aud_options)
        ffmpeg_args.extend(_ffmpeg_args)
        ffmpeg_args.append(tmpfile)

        logging.info("Transcode 1 ")

        logging.info(" ".join(ffmpeg_args))
        p = Popen(ffmpeg_args, stdin=PIPE, stdout=logfile, close_fds=True)
        p.communicate()

        logging.info("Transcode 2 ")

        qt_args = ["qt-faststart", tmpfile, tmpoutfile]
        qt = Popen(qt_args, stdin=PIPE, close_fds=True)
        qt.communicate()

        from mserve.jobservice.models import JobOutput
        jo = JobOutput.objects.get(id=joboutput.pk)
        jo.file.save(mfile.name+'_transcode.mp4', File(toutfile), save=True)

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

    mfile = inputs[0]
    infile = mfile.file.path
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
        #if infile.endswith(".mxf"):
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

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfile.pk)
        mf.proxy.save(suf.name+'_proxy.mp4', suf, save=True)

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
        mfile = inputs[0]
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        result = m.file(mfile.file.path)
        mimetype = result.split(';')[0]
        logging.info("Mime for file %s is %s" % (mfile,mimetype))

        from mserve.dataservice.models import MFile
        mf = MFile.objects.get(id=mfile.pk)
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
        mfile = inputs[0]
        file = mfile.file

        from dataservice.models import BackupFile

        backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
        backup.save()

        return {"success":True,"message":"Backup of '%s' successful"%mfile.name}
    except Exception as e:
        logging.info("Error with backup_mfile %s" % e)
        raise e

@task
def md5file(inputs,outputs,options={},callbacks=[]):

    """Return hex md5 digest for a Django FieldFile"""
    try:
        mfile = inputs[0]
        file = open(mfile.file.path,'r')
        md5 = hashlib.md5()
        while True:
            data = file.read(8192)  # multiple of 128 bytes is best
            if not data:
                break
            md5.update(data)
        file.close()
        md5string = md5.hexdigest()
        logging.info("MD5 calclated %s" % (md5string ))
        mfile.checksum = md5string
        mfile.save()

        for callback in callbacks:
            subtask(callback).delay()

        return {"success":True,"message":"MD5 of '%s' successful"%mfile, "md5" : md5string}
    except Exception as e:
        logging.info("Error with mime %s" % e)
        raise e

@task
def posterimage(inputs,outputs,options={},callbacks=[]):

    try:
        mfile = inputs[0]
        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        logging.info("Creating %sx%s image for %s" % (width,height,input))

        image = _thumbimage(mfile.file.path,width,height)

        if image:
            # Save the thumbnail
            temp_handle = StringIO()
            image.save(temp_handle, 'png')
            temp_handle.seek(0)

            # Save to the poster field
            suf = SimpleUploadedFile("mfile",
                    temp_handle.read(), content_type='image/png')

            from mserve.dataservice.models import MFile
            mf = MFile.objects.get(id=mfile.pk)
            mf.poster.save(suf.name+'_poster.png', suf, save=True)

            logging.info("Poster created %s" % (image))

            for callback in callbacks:
                subtask(callback).delay()

            return {"success":True,"message":"Poster '%sx%s' successful"%(width,height)}
        else:
            raise Exception("Could not create image")
    except Exception as e:
        logging.info("Error with posterimage %s" % e)
        raise e


@task(max_retries=3)
def thumbimage(inputs,outputs,options={},callbacks=[]):

    from mserve.dataservice.models import MFile
    from mserve.jobservice.models import JobOutput
    
    try:
        input = inputs[0]

        if type(input) == MFile:
            model = inputs[0]
            path = model.file.path
            name = "mfile"
        elif type(input) == JobOutput:
            model = inputs[0]
            path = model.file.path
            name = "output"
        elif type(input) == str:
            path = input
            name = os.path.basename(path)
        else:
            raise Exception("thumbimage cant handle input '%s' of type '%s' "% (input[0],type(input[0])) )

        widthS = options["width"]
        heightS = options["height"]
        height = int(heightS)
        width  = int(widthS)

        logging.info("Creating %sx%s image for %s" % (width,height,input))

        image = _thumbimage(path,width,height)

        if image:

            if type(input) == MFile:
                # Save the thumbnail
                temp_handle = StringIO()
                image.save(temp_handle, 'png')
                temp_handle.seek(0)

                # Save to the thumbnail field
                suf = SimpleUploadedFile(name,
                        temp_handle.read(), content_type='image/png')

                mf = MFile.objects.get(id=model.pk)
                mf.thumb.save(suf.name+'_thumb.png', suf, save=True)
            elif type(input) == JobOutput:
                # Save the thumbnail
                temp_handle = StringIO()
                image.save(temp_handle, 'png')
                temp_handle.seek(0)

                # Save to the thumbnail field
                suf = SimpleUploadedFile(name,
                        temp_handle.read(), content_type='image/png')

                jo = JobOutput.objects.get(id=model.pk)
                jo.thumb.save(suf.name+'_thumb.png', suf, save=True)
            elif type(input) == str:
                im.save(path)


            if len(outputs) > 0:
                temp_handle.seek(0)
                joboutput = outputs[0]
                from mserve.jobservice.models import JobOutput
                jo = JobOutput.objects.get(id=joboutput.pk)
                suf2 = SimpleUploadedFile("output",
                    temp_handle.read(), content_type='image/png')
                jo.file.save(name+'_thumb.png', suf2, save=True)

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
        logging.info("Image %s does not exist" % input)
        return False

    im = Image.open(input)

    w, h = im.size
    logging.info("Thumbnail 1 %s %s" % (w,h))
    if float(w)/h < float(width)/float(height):
            logging.info("Thumbnail 2 %s %s" % (w,h))
            im = im.resize((width, h*width/w), Image.ANTIALIAS)
    else:
            logging.info("Thumbnail 3 %s %s" % (w,h))
            im = im.resize((w*int(height)/h, int(height)), Image.ANTIALIAS)
            logging.info("Thumbnail 3.5 %s %s" % (w,h))
    w, h = im.size
    logging.info("Thumbnail  4 %s %s" % (w,h))

    im = im.crop(((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height))

    im.thumbnail((width,height))

    return im