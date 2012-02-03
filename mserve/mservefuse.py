#!/usr/bin/python
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
#	Created Date :			2012-01-25
#	Created for Project :		POSTMARK
#
########################################################################

from __future__ import with_statement

import os
import errno
from sys import argv
from threading import Lock
from errno import EACCES
from errno import EEXIST
from errno import ENOTEMPTY
from errno import ENOENT


from mservefuse.fuse import FUSE
from mservefuse.fuse import FuseOSError
from mservefuse.fuse import Operations
from mservefuse.fuse import ENOTSUP

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory\
            containing %r. It appears you've customized things.\nYou'll have to\
            run django-admin.py, passing it your settings module.\n \
            (If the file settings.py does indeed exist, \
            it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

from django.core.management import setup_environ
setup_environ(settings)
import logging

from dataservice.models import MFolder
from dataservice.models import MFile
from dataservice.models import Auth
from dataservice.models import METRIC_INGEST
from dataservice.models import METRIC_ACCESS
from dataservice import usage_store as usage_store
from django.core.files.base import ContentFile

class MServeLoggingMixIn:
    
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, operation, path, *args):
        if operation == "write":
            logging.info("MServeFUSE -> %s %s", operation, path)
        else:
            logging.info("MServeFUSE -> %s %s %s ", operation, path, repr(args))
        ret = '[Unhandled Exception]'
        try:
            ret = getattr(self, operation)(path, *args)
            return ret
        except OSError, error:
            ret = str(error)
            raise
        finally:
            if operation == "read":
                logging.info("MServeFUSE <- %s", operation)
            else:
                logging.info("MServeFUSE <- %s %s", operation, repr(ret))

def _get_auth_from_path(path):
    paths = path.split(os.path.sep)
    paths = [part for part in paths if part != '']
    auth = paths[0]
    rest = paths[1:]
    return auth, rest

def _stat_to_dict(fstats, override=dict()):
    stats = dict((key, getattr(fstats, key)) for key in ('st_atime', 'st_ctime',
        'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))
    stats.update(override)
    return stats


class MServeFUSE(Operations):

    def __init__(self, *args, **kwargs):
        self.uid = kwargs.get("uid", 65534)
        self.gid = kwargs.get("gid", 65534)
        self.authcache = {}
        self.usagecache = {}
        self.rwlock = Lock()
        self.usagelock = Lock()
        self.ops = ["access", "create", "fsync", "fsyncdir", "getattr", "mkdir",
                "open", "opendir", "read", "readdir", "rename",
                "rmdir", "truncate", "unlink"]
        super(MServeFUSE, self).__init__()

    def _getvars(self, path):
        if not path:
            return (None, None, None, None, None)
        authid, restpath = _get_auth_from_path(path)
        auth, realbase, validops, deniedops = self.authcache.get(authid, (None, None, None, None))
        return auth, realbase, restpath, validops, deniedops

    def __report_usage(self, authid, mfileid):
        with self.usagelock:
            usages = self.usagecache[authid][mfileid]
            for metric in usages:
                logging.info("reporting %s = %s " , metric, usages[metric])
                usage_store.record(mfileid, metric, usages[metric], report=False)
            self.usagecache[authid][mfileid] = {}

    def __get_usage(self, authid, mfileid):
        if authid in self.usagecache:
            if mfileid in self.usagecache[authid]:
                return self.usagecache[authid][mfileid]
        return None

    def _update_usage_cache(self, authid, mfileid, metric, usage):
        if not authid in self.usagecache:
            self.usagecache[authid] = {}
        if not mfileid in self.usagecache[authid]:
            self.usagecache[authid][mfileid] = {}
        if not metric in self.usagecache[authid][mfileid]:
            self.usagecache[authid][mfileid][metric] = 0
        self.usagecache[authid][mfileid][metric] += usage

    def __call__(self, operation, path, *args):
        if path == '/' or path == "/*" or path == "./":
            path = "./"
            return super(MServeFUSE, self).__call__(operation, path, *args)
        else:
            try:
                authid, restpath = _get_auth_from_path(path)
                auth, realbase, validops, deniedops \
                            = self.authcache.get(authid,
                                                 (None, None, None, None))

                if not auth:
                    auth = Auth.objects.get(id=authid)
                    realbase = auth.get_real_base()
                    validops = []
                    deniedops = []

                    for _op in self.ops:
                        check = False
                        if _op == "access":
                            check, err = auth.check("mfolders", "GET") \
                                and auth.check("mfiles", "GET")
                        elif _op == "create":
                            check, err = auth.check("mfiles", "POST")
                        elif _op == "fsync":
                            check, err = auth.check("mfiles", "PUT")
                        elif _op == "fsyncdir":
                            check, err = auth.check("mfolders", "PUT")
                        elif _op == "getattr":
                            check1, err1 = auth.check("mfolders", "GET")
                            check2, err2 = auth.check("mfiles", "GET")
                            check = check1 and check2
                        elif _op == "mkdir":
                            check, err = auth.check("mfolders", "POST")
                        elif _op == "open":
                            check, err = auth.check("mfiles", "GET")
                        elif _op == "opendir":
                            check, err = auth.check("mfolders", "GET")
                        elif _op == "read":
                            check, err = auth.check("mfiles", "GET")
                        elif _op == "readdir":
                            check, err = auth.check("mfolders", "GET")
                        elif _op == "rename":
                            logging.debug("rename check done in-method")
                            check = True
                        elif _op == "rmdir":
                            check, err = auth.check("mfolders", "DELETE")
                        elif _op == "truncate":
                            check, err = auth.check("mfiles", "PUT")
                        elif _op == "unlink":
                            check, err = auth.check("mfiles", "DELETE")
                        else:
                            msg = "CHECK for operation %s not done" % _op
                            logging.debug(msg)
                            
                        if check:
                            validops.append(_op)
                        else:
                            deniedops.append(_op)

                        self.usagecache[authid] = {}

                self.authcache[authid] = (auth, realbase, validops, deniedops)

                if operation in deniedops:
                    raise FuseOSError(EACCES)

                return super(MServeFUSE, self)\
                        .__call__(operation, path, *args)
            except Auth.DoesNotExist:
                raise FuseOSError(errno.ENOENT)
    
    def access(self, path, mode):
        pass

    def chmod(self, path, mode):
        raise FuseOSError(ENOTSUP)

    def chown(self, path, uid, gid):
        raise FuseOSError(ENOTSUP)

    def create(self, path, mode, _fi=None):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        if auth:
            try:
                mfile = realbase.get_file_for_paths(restpath)
                if mfile:
                    raise FuseOSError(EEXIST)
            except Exception as exception:
                logging.info(exception)
            try:
                parentmfolder = realbase.get_folder_for_paths(
                                                        restpath[:-1])
                name = os.path.basename(path)
                mfile = realbase.create_mfile(name, folder=parentmfolder,
                                                file=ContentFile(''),
                                                post_process=False)
                return os.open(mfile.file.path, os.O_WRONLY | os.O_CREAT, mode)
            except Exception as exception:
                logging.info(exception)
                raise exception
        else:
            raise FuseOSError(errno.EACCES)

    def flush(self, path, fileh):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            mfile = realbase.get_file_for_paths(restpath)
            usage = self.__get_usage(auth.id, mfile.id)
            if mfile and usage and len(usage) > 0:
                mfile.update_mfile()
        except Exception as exception:
            logging.info(exception)

        return os.fsync(fileh)

    def fsync(self, path, datasync, fileh):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        self.usagecache[auth.id]
        try:
            mfile = realbase.get_file_for_paths(restpath)
            usage = self.__get_usage(auth.id, mfile.id)
            if mfile and len(usage) > 0:
                mfile.update_mfile()
        except Exception as exception:
            logging.info(exception)

        return os.fsync(fileh)
                
    def getattr(self, path, fileh=None):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        if auth == None:
            stats = os.lstat(settings.MSERVE_DATA)
            return _stat_to_dict(stats,
                            {"st_uid":self.uid, "st_gid":self.gid})
        else:
            if len(path) == 0:
                stats = os.lstat(settings.MSERVE_DATA)
                return _stat_to_dict(stats,
                            {"st_uid":self.uid, "st_gid":self.gid})
            else:
                try:
                    mfile = realbase.get_file_for_paths(restpath)
                    stats = os.stat(mfile.file.path)
                    return _stat_to_dict(stats)
                except Exception as exception:
                    logging.info(exception)
                try:
                    realbase.get_folder_for_paths(restpath)
                    # TODO - Check this is secure to return stat for ./
                    stats = os.lstat(settings.MSERVE_DATA)
                    return _stat_to_dict(stats,
                        {"st_uid":self.uid, "st_gid":self.gid, "st_size":5000})
                except Exception as exception:
                    logging.info(exception)
        raise FuseOSError(ENOENT)
    
    getxattr = None
    
    def link(self, target, source):
        raise FuseOSError(ENOTSUP)

    def open(self, path, fip):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            mfile = realbase.get_file_for_paths(restpath)
            handle = os.open( mfile.file.path, os.O_RDWR )
            return handle
        except Exception as exception:
            logging.info(exception)
            raise exception

    listxattr = None

    def mkdir(self, path, mode):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            # First get the folder from the path
            parentfolder = realbase.get_folder_for_paths(restpath[:-1])
            realbase.create_mfolder(
                    restpath[-1], parent=parentfolder)
        except Exception as exception:
            logging.info(exception)
            raise exception

    def read(self, path, size, offset, fileh):
        with self.rwlock:
            auth, realbase, restpath, validops, deniedops = self._getvars(path)
            mfile = realbase.get_file_for_paths(restpath)
            try:
                os.lseek(fileh, offset, 0)
                return os.read(fileh, size)
            finally:
                self._update_usage_cache(auth.id, mfile.id, METRIC_ACCESS, size)
    
    def readdir(self, path, fileh):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        if auth == None:
            return ['.','..']
        else:
            try:
                # First get the folder from the path
                mfolder = realbase.get_folder_for_paths(restpath)
                # Get all folders in that folder
                folderlist = list(realbase.mfolder_set\
                        .filter(parent=mfolder).values_list('name',flat=True))
                # Get all files in that folder
                filelist = list(realbase.mfile_set
                        .filter(folder=mfolder).values_list('name',flat=True))
                # return files and folder as str
                return ['.', '..'] + map(str, folderlist +filelist)
            except Exception as exception:
                logging.info(exception)
                raise exception


    readlink = os.readlink
    
    def release(self, path, fileh):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        mfile = realbase.get_file_for_paths(restpath)
        if mfile:
            self.__report_usage(auth.id, mfile.id)
        return os.close(fileh)
        
    def rename(self, path, new):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            # Check if trying to move file
            mfile = realbase.get_file_for_paths(restpath)
            if mfile:
                check = "rename" in validops
                if not check:
                    raise FuseOSError(EACCES)
                authid, newrestpath = _get_auth_from_path(new)
                if authid == auth.id:
                    try:
                        realbase.get_file_for_paths(newrestpath)
                    except MFolder.DoesNotExist as exception:
                        newmfolder = realbase\
                                        .get_folder_for_paths(newrestpath[:-1])
                        mfile.name = os.path.basename(new)
                        mfile.folder = newmfolder
                        mfile.save()
                    except MFile.DoesNotExist as exception:
                        mfile.name = os.path.basename(new)
                        mfile.save()
            else:
                # Check if trying to move folder
                mfolder = realbase.get_folder_for_paths(restpath)
                if mfolder:
                    check = auth.check("mfolders", "PUT")
                    if not check:
                        raise FuseOSError(EACCES)
                    authid, newrestpath = _get_auth_from_path(new)
                    if authid == auth.id:
                        try:
                            realbase.get_folder_for_paths(newrestpath)
                        except MFolder.DoesNotExist as exception:
                            mfolder.name = os.path.basename(new)
                            mfolder.save()
                        except MFile.DoesNotExist as exception:
                            mfolder.name = os.path.basename(new)
                            mfolder.save()

        except Exception as exception:
            logging.info(exception)
            raise exception

    def rmdir(self, path):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            # First get the folder from the path
            folder = realbase.get_folder_for_paths(restpath)
            num_mfiles = folder.mfile_set.count()
            num_mfolders = folder.mfolder_set.count()
            if num_mfiles + num_mfolders == 0:
                folder.delete()
            else:
                raise FuseOSError(ENOTEMPTY)
        except Exception as exception:
            logging.info(exception)
            raise exception

    def statfs(self, path):
        stv = os.statvfs(settings.MSERVE_DATA)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
    
    def symlink(self, target, source):
        raise FuseOSError(ENOTSUP)

    def truncate(self, path, length, fileh=None):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            mfile = realbase.get_file_for_paths(restpath)
            if mfile:
                fileh = open( mfile.file.path, 'r+')
                return os.ftruncate(fileh.fileno(), length)
            else:
                raise FuseOSError(ENOTSUP)
        except Exception as exception:
            logging.info(exception)
            raise exception
    
    def unlink(self, path):
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            mfile = realbase.get_file_for_paths(restpath)
            mfile.delete()
        except Exception as exception:
            logging.info(exception)
            raise exception

    def utimens(self, path, times=None):
        """Times is a (atime, mtime) tuple. If None use current time."""
        auth, realbase, restpath, validops, deniedops = self._getvars(path)
        try:
            # Check if trying to move file
            mfile = realbase.get_file_for_paths(restpath)
            if mfile:
                check = auth.check("mfiles", "PUT")
                if not check:
                    raise FuseOSError(EACCES)
                return os.utime(mfile.file.path, times)

            mfolder = realbase.get_folder_for_paths(restpath)
            if mfolder:
                raise FuseOSError(ENOTSUP)

        except Exception as exception:
            logging.info(exception)
            raise exception

    def write(self, path, data, offset, fileh):
        with self.rwlock:
            auth, realbase, restpath, validops, deniedops = self._getvars(path)
            authid, rest = _get_auth_from_path(path)
            os.lseek(fileh, offset, 0)
            bytes_written = os.write(fileh, data)
            mfile = realbase.get_file_for_paths(restpath)
            self._update_usage_cache(authid, mfile.id, METRIC_INGEST, bytes_written)
            return bytes_written


if __name__ == "__main__":
    if len(argv) != 2:
        print 'usage: %s <mountpoint>' % argv[0]
        sys.exit(1)
    kwargs = {}
    kwargs["allow_other"] = True
    kwargs["uid"] = 65534
    kwargs["gid"] = 65534
    kwargs["foreground"] = True
    #keyargs["noforget"] = True
    if settings.DEBUG:
        MServeFUSE.__bases__ = (MServeLoggingMixIn,Operations,)
    fuse = FUSE(MServeFUSE(**kwargs), argv[1], **kwargs)