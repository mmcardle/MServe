from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from django.conf import settings
import time

class SimulateFileSystemStorage(FileSystemStorage):

    def __init__(self,location):
        super(SimulateFileSystemStorage, self).__init__(location=location);

    def _open(self,name,mode='rb'):
        time.sleep(10)
        return super(SimulateFileSystemStorage, self)._open(name,mode);

def gettapestorage():
    return SimulateFileSystemStorage(location='%s/backup/'%settings.MEDIA_ROOT)

def getdiscstorage():
    return default_storage