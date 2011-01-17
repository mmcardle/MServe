import hashlib
import hashlib
import time
import uuid
import os

fmt = "%3.2f"

def create_filename(instance, filename):
    timeformat = time.strftime("%Y/%m/%d/")
    return os.path.join(timeformat ,instance.id ,filename)

def random_id():
    return str(uuid.uuid4())

def gen_sec_link_orig(rel_path,prefix):
      if not rel_path.startswith("/"):
        rel_path = "%s%s" % ("/", rel_path)
      secret = 'ugeaptuk6'
      uri_prefix = '/%s/' % prefix
      hextime = "%08x" % time.time()
      token = hashlib.md5(secret + rel_path + hextime).hexdigest()
      return '%s%s/%s%s' % (uri_prefix, token, hextime, rel_path)

def md5_for_file(file):
    """Return hex md5 digest for a Django FieldFile"""
    file.open()
    md5 = hashlib.md5()
    while True:
        data = file.read(8192)  # multiple of 128 bytes is best
        if not data:
            break
        md5.update(data)
    file.close()
    return md5.hexdigest()

def is_container(base):
    return hasattr(base,"hostingcontainer")

def is_service(base):
    return hasattr(base,"dataservice")

def is_mfile(base):
    return hasattr(base,"mfile")

def is_containerauth(base):
    return hasattr(base,"hostingcontainerauth")

def is_serviceauth(base):
    return hasattr(base,"dataserviceauth")

def is_mfileauth(base):
    return hasattr(base,"mfileauth")