from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.conf import settings
import time

class SimulateTapeFileSystemStorage(FileSystemStorage):

    def __init__(self,location):
        super(SimulateTapeFileSystemStorage, self).__init__(location=location);

    def _open(self,name,mode='rb'):
        time.sleep(10)
        return super(SimulateTapeFileSystemStorage, self)._open(name,mode);

def gettapestorage():
    return SimulateTapeFileSystemStorage(location='%s/backup/'%settings.MEDIA_ROOT)


class DiskSystemStorage(FileSystemStorage):

    def __init__(self,location,base_url=None):
        super(DiskSystemStorage, self).__init__(location=location,base_url=base_url);

def getdiscstorage():
    return DiskSystemStorage(location=settings.MEDIA_ROOT)

def getthumbstorage():
    return DiskSystemStorage(location=settings.THUMB_ROOT,base_url="/mservethumbs/")