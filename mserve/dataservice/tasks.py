import os.path

# We can register as a class ....

#from celery.task import Task
#from celery.registry import tasks
#class ProcessVideoTask(Task):
#    def run(self, object_id, **kwargs):
#        logger = self.get_logger(**kwargs)
#        logger.info("Processed video for %s." % object_id)
#        return True
#tasks.register(ProcessVideoTask)

# .... or use the @task decorator

from celery.decorators import task
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
def thumbimage(mfilepath,thumbpath,width,height):
    logging.info("Creating %sx%s image for %s to %s" % (width,height,mfilepath,thumbpath))
    if not os.path.exists(mfilepath):
        logging.info("Image %s does not exist" % (mfilepath))
        return False

    im = Image.open(mfilepath)

    w, h = im.size
    if float(w)/h < float(width)/height:
            im = im.resize((width, h*width/w), Image.ANTIALIAS)
    else:
            im = im.resize((w*height/h, height), Image.ANTIALIAS)
    w, h = im.size
    im = im.crop( ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height))

    im.thumbnail((width,height))
    im.save(thumbpath, "JPEG")
    logging.info("Thumnail created %s" % (thumbpath))

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
