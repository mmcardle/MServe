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
import Image
import pycurl
import time
import tempfile

@task
def add(x, y):
    return x + y

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

def thumbimage(stagerpath,thumbpath,width,height):
    logging.info("Creating %s%s image for %s to %s" % (width,height,stagerpath,thumbpath))
    if not os.path.exists(stagerpath):
        logging.info("Image %s does not exist" % (stagerpath))
        return False

    im = Image.open(stagerpath)

    w, h = im.size
    if float(w)/h < float(width)/height:
            im = im.resize((width, h*width/w), Image.ANTIALIAS)
    else:
            im = im.resize((w*height/h, height), Image.ANTIALIAS)
    w, h = im.size
    im = im.crop( ((w-width)/2, (h-height)/4, (w-width)/2+width, (h-height)/4+height))

    im.thumbnail((width,height))
    im.save(thumbpath, "JPEG")
    logging.info("Thumnail created %s" % (stagerpath))

    return True


@task
def thumbimage_async_remote(dataurl,stagerid,thumburl,size):

    tmpfile = tempfile.NamedTemporaryFile()
    try:
        #im = Image.fromstring(mode,size,imstring)
        imageurl = urllib.urlretrieve(dataurl)
        im = Image.open(imageurl[0])
        im.thumbnail(size)
        im.save(tmpfile.name, "JPEG")

        logging.info("Thumnail created uploading to %s" % (thumburl))

        pf = [  ('stagerid', stagerid),
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
        print "cannot create thumbnail for", stagerid
        return False
    return False