import hashlib

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