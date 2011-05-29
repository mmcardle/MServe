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
from django.core.files import File
from subprocess import Popen, PIPE
import logging
import subprocess
import urllib
import hashlib
import Image
import pycurl
import tempfile
import magic
import os
import os.path

@task
def create_mfile_task(inputs,outputs,options={},callbacks=[]):

    input = inputs[0]
    service = options["service"]
    name = options["name"]

    mfile = service.create_mfile(name,post_process=False)
    
    logging.info("input to Mfile '%s' " % input)
    logging.info("created Mfile '%s' " % mfile)

    if not os.path.exists(input):
        logging.info("Input for Mfile %s does not exist" % (input))
        dir = os.path.dirname(path)
        if os.path.exists(dir):
            logging.info("Dir %s",os.path.listdir(dir))
        return False

    f = open(input, 'rb' ,chunk_size)


    mfile.file.save(name, File(f))

    mfile.save()

    f.close()

    mfile.post_process()

    for callback in callbacks:
        subtask(callback).delay()

    return {  }

@task
def update_mfile_task(inputs,outputs,options={},callbacks=[]):
    input = inputs[0]
    name = options["name"]
    mfile = options['mfile']

    logging.info("input to Mfile '%s' " % input)
    logging.info("updating Mfile '%s' " % mfile)

    f = open(input, 'rb' ,chunk_size)

    mfile.file.save(name, File(f))

    mfile.save()

    f.close()

    mfile.post_process()

    for callback in callbacks:
        subtask(callback).delay()

    return {  }

@task
def thumbvideo(videopath,thumbpath,width,height):
    logging.info("Processing video thumb %sx%s for %s to %s" % (width,height,videopath,thumbpath))
    if not os.path.exists(videopath):
        logging.info("Video %s does not exist" % (videopath))
        return False
    args = ["ffmpegthumbnailer","-t","20","-s","%sx%s"%(width,height),"-i",videopath,"-o",thumbpath]
    
    logging.info(args)
    ret = subprocess.call(args)
    return ret

@task
def proxyvideo(infile,proxypath,width="420",height="256"):

        logfile = open('/var/mserve/mserve.log','a')
	errfile = open('/var/mserve/mserve.log','a')

	tfile = tempfile.NamedTemporaryFile(delete=False,suffix=".mp4")

	try:
            tmpfile=tfile.name
            vidfifo="stream.yuv"
            audfifo="stream.wav"
            outfile=proxypath

            options= ["-vcodec","libx264","-vpre","lossless_max"]

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

            ffmpeg_args = ["ffmpeg","-y","-i",vidfilename,"-i",audfilename,"-acodec","libfaac","-ac","2","-ab","64","-ar","44100","-vf","scale=480:272"]

            ffmpeg_args.extend(options)
            ffmpeg_args.append(tmpfile)

            logging.info(" ".join(ffmpeg_args))
            p = Popen(ffmpeg_args, stdin=PIPE, stdout=logfile, close_fds=True)
            p.communicate()

            qt_args = ["qt-faststart", tmpfile, outfile]
            qt = Popen(qt_args, stdin=PIPE, close_fds=True)
            qt.communicate()

        except Exception as e:
            logging.info("Error encoding video %s" % e)
            os.unlink(tmpfile)
            tfile.close()
        else:
            logging.info("Proxy Video '%s' Done"% infile)
            os.unlink(tmpfile)
            tfile.close()

@task
def proxyvideo2(videopath,proxypath,width="420",height="256"):
    logging.info("Processing video proxy for %s to %s" % (videopath,proxypath))
    if not os.path.exists(videopath):
        logging.info("Video %s does not exist" % (videopath))
        return False
    args = ["ffmpeg","-s","%sx%s"%(width,height),"-i",videopath,"-f","ogg","-vcodec","libtheora","-b","800k","-g","300","-acodec","libvorbis","-ab","128k",proxypath]
    logging.info(args)
    ret = subprocess.call(args)
    return ret

@task
def mimefile(mfilepath):
    m = magic.open(magic.MAGIC_MIME)
    m.load()
    result = m.file(mfilepath)
    mimetype = result.split(';')[0]
    logging.info("Mime for file %s is %s" % (mfilepath,mimetype))
    return mimetype

@task
def md5file(inputs,outputs,options={},callbacks=[]):
    """Return hex md5 digest for a Django FieldFile"""
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
    return md5string

@task
def thumbimage(mfilepath,thumbpath,options={},callback=None):

    logging.info("thumbimage %s to %s with options %s " % (mfilepath,thumbpath,options) )

    widthS = options["width"]
    heightS = options["height"]
    height = int(heightS)
    width  = int(widthS)

    logging.info("Creating %sx%s image for %s to %s" % (width,height,mfilepath,thumbpath))
    if not os.path.exists(mfilepath):
        logging.info("Image %s does not exist" % (mfilepath))
        return False

    im = Image.open(mfilepath)

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
    im.save(thumbpath, "PNG")
    logging.info("Thumnail created %s" % (thumbpath))

    if callback:
        subtask(callback).delay()

    return True


@task
def thumbimage_async_remote(dataurl,mfileid,thumburl,size):

    tmpfile = tempfile.NamedTemporaryFile()
    try:
        #im = Image.fromstring(mode,size,imstring)
        imageurl = urllib.urlretrieve(dataurl)
        im = Image.open(imageurl[0])
        im.thumbnail(size)
        im.save(tmpfile.name, "JPEG")

        logging.info("Thumnail created uploading to %s" % (thumburl))

        pf = [  ('mfileid', mfileid),
                ('file', (pycurl.FORM_FILE, tmpfile.name)), ]

        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, thumburl)
        #c.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        c.setopt(c.HTTPHEADER, [ 'Expect:' ] )
        c.setopt(c.HTTPPOST, pf)
        #c.setopt(c.VERBOSE, 1)
        c.perform()
        c.close()

        return True
    
    except IOError:
        print "cannot create thumbnail for", mfileid
        return False
    return False
