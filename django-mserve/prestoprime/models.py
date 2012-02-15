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
from dataservice.models import MFile
from jobservice.models import Job
from jobservice.models import JobOutput
from django.db import models
from django.db.models.signals import post_save
from dataservice.tasks import thumbimage
from prestoprime.tasks import mxfframecount
from prestoprime.tasks import d10mxfchecksum
from prestoprime.tasks import extractd10frame
from celery.task.sets import TaskSet
import dataservice.usage_store as usage_store
import logging
import filecmp
import tempfile
import os
import settings as settings
import dataservice.utils as utils
import dataservice.storage as storage
from dataservice.models import MFILE_GET_SIGNAL
from cStringIO import StringIO
from django.core.files.uploadedfile import SimpleUploadedFile

pp_mxfframe_ingested_metric = "http://prestoprime/mxf_frames_ingested"
pp_mxfframe_corrupted_metric = "http://prestoprime/mxf_frames_corrupted"

class MFileD10Check(models.Model):
    mfile       = models.ForeignKey(MFile)
    checkfile   = models.FileField(upload_to=utils.create_filename,storage=storage.getdiscstorage())

    def __unicode__(self):
        if self.mfile:
            return "MFileD10Check (%s) %s" % (self.pk, self.mfile.name );
        else:
            return "MFileD10Check (%s) empty" % (self.pk);
        
def mfile_get_handler( sender, mfile=False, **kwargs):
    logging.info("In Prestoprime handler"  )
    try:
        if mfile.file.name.endswith(".mxf"):
            mfiled10check=MFileD10Check.objects.get(mfile=mfile)
            tmpfile = tempfile.NamedTemporaryFile(mode="w")
            d10mxfchecksum([mfile.file.path],[tmpfile.name])
            
            if not filecmp.cmp(tmpfile.name,mfiled10check.checkfile.path):
                lines1 = open(tmpfile.name).readlines()
                lines2 = open(mfiled10check.checkfile.path).readlines()

                # TODO: Make this a celery task
                corrupted = 0
                i = 0
                frames = []
                job = Job(name="Extract Corrupted Frames",service=mfile.service)
                job.save()
                tasks = []
                for line1 in lines1:
                    line2 = lines2[i]
                    if line1 != line2:
                        split = line1.split("\t")
                        frameS = split[0]
                        try:
                            frame = int(frameS)
                            frames.append(frame)
                            logging.info("frame %s corrupted " % frame )

                            output = JobOutput(name="Job 'Corrupted Frame %s'"%frame,job=job,mimetype="image/png")
                            output.save()
                            fname = "%s.%s" % ("corruptedframe","png")
                            outputpath = os.path.join( str(job.id) , fname)
                            output.file = outputpath
                            thumbfolder = os.path.join( settings.THUMB_ROOT, str(job.id))
                            if not os.path.exists(thumbfolder):
                                os.makedirs(thumbfolder)

                            (head,tail) = os.path.split(output.file.path)
                            if not os.path.isdir(head):
                                os.makedirs(head)

                            thumbfile= os.path.join( thumbfolder , "%s%s" % (fname,".thumb.png"))
                            thumbpath = os.path.join( str(job.id) , "%s%s" % (fname,".thumb.png"))
                            output.thumb = thumbpath
                            output.save()
                            thumboptions = {"width":settings.thumbsize[0],"height":settings.thumbsize[1]}
                            callback = thumbimage.subtask([output,thumbfile,thumboptions])

                            logging.info("Creating task %s %s " % (mfile.file.path,output.file.path))
                            inputs    = [mfile.file.path]
                            outputs   = [output.file.path]
                            options   = {"frame":frame}
                            callbacks = [callback]
                            task = extractd10frame.subtask([inputs,outputs,options],callbacks=callbacks)
                            tasks.append(task)
                            
                            logging.info("task created %s" % task)

                            corrupted += 1
                        except ValueError as e:
                            logging.info("PP handler %s " % e)

                    i = i+1

                if len(tasks) > 0:


                    logging.info("tasks to execute created %s" % task)

                    job.save()
                    ts = TaskSet(tasks=tasks)
                    tsr = ts.apply_async()
                    tsr.save()

                    job.taskset_id=tsr.taskset_id
                    job.name="Extract Corrupted Frames %s" % frames
                    job.save()
                else:
                    job.delete()

                if corrupted > 0:
                    usage_store.record(mfile.id,pp_mxfframe_corrupted_metric,corrupted)

                logging.info("Lines Corrupted = %s " % corrupted)
            else:
                logging.info("Files are same")

    except MFileD10Check.DoesNotExist:
        logging.info("Prestoprime mfile_get_handler ")
    except Exception as e:
        logging.info("Prestoprime mfile get handler failed %s " % e)
    logging.info("Done Prestoprime handler"  )
    return 

MFILE_GET_SIGNAL.connect(mfile_get_handler, dispatch_uid="prestoprime.models")

def post_save_handler( sender, instance=False, **kwargs):
    try:
        logging.debug("Prestoprime POST save handler %s %s" % (instance, instance.file))

        # Record Additional Usage
        if instance.name is not None and not instance.initial_usage_recorded and instance.name.endswith(".mxf"):
            logging.debug("Prestoprime POST save handler %s id:'%s' " % (instance,instance.id))

            mxfframecounttask = mxfframecount.subtask([[instance.id],[]])

            #count = result["frames"]
            #logging.info("Recording ingest usage %s " % (count))
            #usage_store.record(instance.id,pp_mxfframe_ingested_metric,count)

            job = Job(name="Prestoprime Tasks",mfile=instance)
            job.save()

            output = JobOutput(name="Job Output",job=job,mimetype="text/plain")
            output.save()

            ## Do Post Processing
            mfiled10check = MFileD10Check(mfile=instance)
            
            temp_handle = StringIO()
            temp_handle.seek(0)

            suf = SimpleUploadedFile("checkfile", temp_handle.read())
            mfiled10check.checkfile.save(suf.name+'.txt', suf, save=False)
            mfiled10check.save()

            d10mxfchecksumtask = d10mxfchecksum.subtask([[instance.id],[output]])

            ts = TaskSet(tasks=[d10mxfchecksumtask,mxfframecounttask])
            tsr = ts.apply_async()
            tsr.save()

            
            job.taskset_id=tsr.taskset_id
            job.save()
            
            logging.debug("Prestoprime task %s  " % task  )

    except Exception as e:
        logging.error("Prestoprime POST save handler failed %s " % e)

post_save.connect(post_save_handler, sender=MFile, dispatch_uid="prestoprime.models")