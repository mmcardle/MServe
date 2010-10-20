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