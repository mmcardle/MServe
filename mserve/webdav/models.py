from django.db import models
from dataservice.models import *
import base64
import pickle

class WebDavProperty(models.Model):
    base            = models.ForeignKey(NamedBase)
    name            = models.CharField(max_length=200)
    ns              = models.CharField(max_length=200)
    _encoded_value  = models.TextField()

    def set_value(self,val):
        self._encoded_value = base64.b64encode(pickle.dumps(val))

    def get_value(self):
        return pickle.loads(base64.b64decode(self._encoded_value))