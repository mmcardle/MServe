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
import hashlib
import hashlib
import time
import uuid
import os
import pickle
import base64
import logging
from Crypto.Cipher import AES
import base64
import urllib
import random
import os
import sys


fmt = "%3.2f"

def get_class( kls ):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m

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

def unique_id():
    return str(uuid.uuid4())

def random_id():
    mode = AES.MODE_CBC
    short_key1 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key2 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key3 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key4 = base64.b64encode(str(random.randint(0,sys.maxint)))

    aeskey = (short_key1 + short_key2 + short_key3 + short_key4)[:32]

    short_key5 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key6 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key7 = base64.b64encode(str(random.randint(0,sys.maxint)))
    short_key8 = base64.b64encode(str(random.randint(0,sys.maxint)))
    key = (short_key5 + short_key6 + short_key7 + short_key8)[:32]

    aes = AES.new(aeskey, mode)
    padded_key = key
    encrypted_key = aes.encrypt(padded_key)
    encoded_key = encrypted_key
    encoded_key = base64.b64encode(encrypted_key)

    encoded_key = encoded_key.translate(None,"//\\+=")

    return encoded_key


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
    try:
        logging.info("content 5.2 %s " % file)
        file.open()
        logging.info("content 5.4 %s " % file)
        md5 = hashlib.md5()
        logging.info("content 5.5 %s " % file)
        while True:
            data = file.read(8192)  # multiple of 128 bytes is best
            if not data:
                break
            md5.update(data)
        logging.info("content 6 %s " % md5.hexdigest())
        file.close()
        return md5.hexdigest()
    except Exception as e:
        raise e

def is_container(base):
    return hasattr(base,"hostingcontainer")

def is_service(base):
    return hasattr(base,"dataservice")

def is_mfile(base):
    return hasattr(base,"mfile")

def is_mfolder(base):
    return hasattr(base,"mfolder")

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
