import hashlib
import hashlib
import time
import uuid
import os
import pickle
import base64
import logging

fmt = "%3.2f"

def get_methods_for_auth(auth):
    methodslist = [ pickle.loads(base64.b64decode(method_enc)) for method_enc in auth.roles.all().values_list('methods_encoded',flat=True) ]
    methods = [item for sublist in methodslist for item in sublist]
    return set(methods)

def get_methods_for_base(baseid):
    from dataservice.models import NamedBase
    base = NamedBase.objects.get(id=baseid)
    methods = []
    for auth in base.auth_set.all():
         ms = get_methods_for_auth(auth)
         methods += ms
    return set(methods)
  
def check_method_for_auth(authid,method):
    from dataservice.models import Auth
    from dataservice.models import NamedBase
    # Find the Authority with id
    auth = Auth.objects.get(id=authid)

    # Find the methods this auth has
    methods = get_methods_for_auth(auth)

    if auth.base is not None:
        # This auth is a direct sub auth of a base class
        basemethods = get_methods_for_base(auth.base.id)
        if method in methods and method in basemethods:
            logging.info("Authority Check OK for method '%s' in auth methods '%s' and basemethods '%s' " % (method,methods,basemethods)  )
            return True
        else:
            logging.info("Authority Check Failed for method '%s'  not in auth methods '%s' and not in base methods '%s'" % (method,methods,basemethods)  )
    else:
        # This auth is a sub authority of another auth
        authparent = auth.parent
        return check_method_for_auth(authparent.id,method) and method in methods

    logging.info("Authority Check Failed for method '%s'  not in auth methods '%s'" % (method,methods)  )
    return False


def clean_mfile(mfile):
    mfiledict = {}
    mfiledict["name"] = mfile.name
    mfiledict["file"] = mfile.file
    mfiledict["mimetype"] = mfile.mimetype
    mfiledict["updated"] = mfile.updated
    mfiledict["thumburl"] = mfile.thumburl()
    mfiledict["thumb"] = mfile.thumb
    mfiledict["created"] = mfile.created
    mfiledict["checksum"] = mfile.checksum
    mfiledict["posterurl"] = mfile.posterurl()
    mfiledict["poster"] = mfile.poster
    mfiledict["reportnum"] = mfile.reportnum
    mfiledict["size"] = mfile.size
    return mfiledict

def create_filename(instance, filename):
    timeformat = time.strftime("%Y/%m/%d/")
    return os.path.join(timeformat , random_id() ,filename)

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

def get_base_for_auth(auth):
    try:
        base = auth.base
        auth = auth
        while base is None:
            auth = auth.parent
            base = auth.base

        return base
    except Auth.DoesNotExist:
        return None
