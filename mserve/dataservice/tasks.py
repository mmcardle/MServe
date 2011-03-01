import os.path
from celery.decorators import task
from celery.task.sets import subtask
import logging
import subprocess
import urllib
import hashlib
import Image
import pycurl
import tempfile
import magic

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
def proxyvideo(videopath,proxypath,width="420",height="256"):
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
    mimetype = m.file(mfilepath)
    logging.info("Mime for file %s is %s" % (mfilepath,mimetype))
    return mimetype

@task
def md5file(mfilepath):
    """Return hex md5 digest for a Django FieldFile"""
    file = open(mfilepath,'r')
    md5 = hashlib.md5()
    while True:
        data = file.read(8192)  # multiple of 128 bytes is best
        if not data:
            break
        md5.update(data)
    file.close()
    md5string = md5.hexdigest()
    logging.info("MD5 calclated %s" % (md5string ))

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
