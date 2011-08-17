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
from django.core.files.storage import FileSystemStorage
import settings

class SimulateTapeFileSystemStorage(FileSystemStorage):

    def __init__(self,location):
        super(SimulateTapeFileSystemStorage, self).__init__(location=location);

    def _open(self,name,mode='rb'):
        return super(SimulateTapeFileSystemStorage, self)._open(name,mode);

def gettapestorage():
    return SimulateTapeFileSystemStorage(location='%s/backup/'%settings.STORAGE_ROOT)


class DiskSystemStorage(FileSystemStorage):

    def __init__(self,location,base_url=None):
        super(DiskSystemStorage, self).__init__(location=location,base_url=base_url);

def getdiscstorage():
    return DiskSystemStorage(location=settings.STORAGE_ROOT)

def getthumbstorage():
    return DiskSystemStorage(location=settings.THUMB_ROOT,base_url="/mservethumbs/")

def getposterstorage():
    return DiskSystemStorage(location=settings.THUMB_ROOT,base_url="/mservethumbs/")

def getproxystorage():
    return DiskSystemStorage(location=settings.THUMB_ROOT,base_url="/mserveproxy/")