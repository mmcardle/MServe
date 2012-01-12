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
from django.db import models
from dataservice.models import *
import base64
import pickle

class WebDavLock(models.Model):
    base = models.ForeignKey(NamedBase)
    owner = models.CharField(max_length=200)
    timeout = models.CharField(max_length=200)
    token = models.CharField(max_length=200)
    depth = models.CharField(max_length=200)
    lockscope = models.CharField(max_length=200)
    locktype = models.CharField(max_length=200)

    def __unicode__(self):
        return "WebDavLock %s %s %s %s " % (self.owner, self.token, self.lockscope, self.locktype )
    
class WebDavProperty(models.Model):
    base            = models.ForeignKey(NamedBase)
    name            = models.CharField(max_length=200)
    ns              = models.CharField(max_length=200)
    _encoded_value  = models.TextField()

    def set_value(self,val):
        self._encoded_value = base64.b64encode(pickle.dumps(val))

    def get_value(self):
        return pickle.loads(base64.b64decode(self._encoded_value))