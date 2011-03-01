from dataservice.models import MFile
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from prestoprime.tasks import mxfframecount
import dataservice.usage_store as usage_store
import logging
import tempfile

pp_mxfframe_metric = "http://prestoprime/mxf_frames_ingested"

def post_save_handler( sender, instance=False, **kwargs):
    if not instance.initial_usage_recorded and instance.file.name.endswith(".mxf"):
        logging.info("Prestoprime POST save handler %s id:'%s' " % (instance,instance.id))
        # TODO Not working yet
        tmpfile = tempfile.NamedTemporaryFile(mode="w")
        count = mxfframecount(instance.file.path,tmpfile.name)
        usage_store.record(instance.id,pp_mxfframe_metric,count)

post_save.connect(post_save_handler, sender=MFile, dispatch_uid="prestoprime.models")