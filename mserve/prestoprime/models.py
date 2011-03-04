from dataservice.models import MFile
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from prestoprime.tasks import mxfframecount
import dataservice.usage_store as usage_store
import logging
import tempfile


pp_mxfframe_metric = "http://prestoprime/mxf_frames_ingested"

def post_save_handler( sender, instance=False, **kwargs):
    try:
        logging.info("Prestoprime POST save handler %s %s" % (instance, instance.file))
        if not instance.initial_usage_recorded and instance.file.name.endswith(".mxf"):
            logging.info("Prestoprime POST save handler %s id:'%s' " % (instance,instance.id))
            tmpfile = tempfile.NamedTemporaryFile(mode="w")
            result = mxfframecount([instance.file.path],[tmpfile.name])
            count = result["lines"]
            logging.info("Recording ingest usage %s " % (count))
            usage_store.record(instance.id,pp_mxfframe_metric,count)
    except e:
        logging.info("Prestoprime POST save handler failed %s " % e)

post_save.connect(post_save_handler, sender=MFile, dispatch_uid="prestoprime.models")