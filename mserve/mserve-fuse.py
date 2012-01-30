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

from sys import argv
from sys import exit
from threading import Lock
from errno import *
import os
import errno

from mservefuse.fuse import FUSE, FuseOSError, Operations, LoggingMixIn, ENOTSUP

try:
    import settings # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n(If the file settings.py does indeed exist, it's causing an ImportError somehow.)\n" % __file__)
    sys.exit(1)

from django.core.management import setup_environ
import settings
setup_environ(settings)
import logging

from dataservice.models import *
from django.core.files.base import ContentFile

class Loopback(LoggingMixIn, Operations):

    def __init__(self):
        self.rwlock = Lock()

    def _stat_to_dict(self, st):
        return dict((key, getattr(st, key)) for key in ('st_atime', 'st_ctime',
                'st_gid', 'st_mode', 'st_mtime', 'st_nlink', 'st_size', 'st_uid'))

    def _get_auth_from_path(self, path):
        paths = path.split(os.path.sep)
        paths.remove('')
        auth = paths[0]
        rest = paths[1:]
        return auth, rest

    def __call__(self, op, path, *args):
        if path == '/' or path == "/*" or path == "./":
            self.auth = None
            self.restpath = None
            path = "./"
            restpath = path
            return super(Loopback, self).__call__(op, path, *args)
        else:
            authid, restpath = self._get_auth_from_path(path)
            self.restpath = restpath
            auth = Auth.objects.get(id=authid)
            self.auth = auth
            print "Auth = ", auth
            return super(Loopback, self).__call__(op, "/".join(restpath), *args)
    
    def access(self, path, mode):
        pass

    def chmod(self, path, mode):
        raise FuseOSError(ENOTSUP)

    def chown(self, path, uid, gid):
        raise FuseOSError(ENOTSUP)

    def create(self, path, mode):
        if self.auth:
            try:
                mf = self.auth.get_real_base().get_file_for_paths(self.restpath)
                if mf:
                    raise FuseOSError(EEXIST)
            except Exception as e:
                logging.info(e)
            try:
                parentmfolder = self.auth.get_real_base().get_folder_for_paths(self.restpath[:-1])
                name = os.path.basename(path)
                mfile = self.auth.get_real_base().create_mfile(name,folder=parentmfolder, file=ContentFile(''))
                return os.open(mfile.file.path, os.O_WRONLY | os.O_CREAT, mode)
            except Exception as e:
                logging.info(e)
                raise e
        else:
            raise FuseOSError(errno.EACCES)

    def flush(self, path, fh):
        return os.fsync(fh)

    def fsync(self, path, datasync, fh):
        try:
            mf = self.auth.get_real_base().get_file_for_paths(self.restpath)
            if mf:
                mf.update_mfile()
        except Exception as e:
            logging.info(e)

        return os.fsync(fh)
                
    def getattr(self, path, fh=None):
        if self.auth == None:
            st = os.lstat("./")
            return self._stat_to_dict(st)
        else:
            if len(path) == 0:
                st = os.lstat("./")
                return self._stat_to_dict(st)
            else:
                try:
                    mf = self.auth.get_real_base().get_file_for_paths(self.restpath)
                    st = os.stat(mf.file.path)
                    return self._stat_to_dict(st)
                except Exception as e:
                    logging.info(e)
                try:
                    mfolder = self.auth.get_real_base().get_folder_for_paths(self.restpath)
                    # TODO - Check this is secure to return stat for ./
                    st = os.lstat(".")
                    return self._stat_to_dict(st)
                except Exception as e:
                    logging.info(e)
                    #raise e
        raise FuseOSError(ENOENT)
    
    getxattr = None
    
    def link(self, target, source):
        return os.link(source, target)

    def open(self, path, fip):
        try:
            mfile = self.auth.get_real_base().get_file_for_paths(self.restpath)
            r = os.open( mfile.file.path, os.O_RDWR )
            return r
        except Exception as e:
            logging.info(e)
            raise e

    listxattr = None

    def mkdir(self, path, mode):
        try:
            # First get the folder from the path
            parentfolder = self.auth.get_real_base().get_folder_for_paths(self.restpath[:-1])
            self.auth.get_real_base().create_mfolder(self.restpath[-1], parent=parentfolder)
        except Exception as e:
            logging.info(e)
            raise e

    def read(self, path, size, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.read(fh, size)
    
    def readdir(self, path, fh):
        if self.auth == None:
            return ['.','..']
        else:
            try:
                # First get the folder from the path
                mfolder = self.auth.get_real_base().get_folder_for_paths(self.restpath)
                # Get all folders in that folder
                folderlist = list(self.auth.get_real_base().mfolder_set.filter(parent=mfolder).values_list('name',flat=True))
                # Get all files in that folder
                filelist = list(self.auth.get_real_base().mfile_set.filter(folder=mfolder).values_list('name',flat=True))
                # return files and folder as str
                return ['.', '..'] + map(lambda x: str(x) , folderlist + filelist)
            except Exception as e:
                logging.info(e)
                raise e


    readlink = os.readlink
    
    def release(self, path, fh):
        return os.close(fh)
        
    def rename(self, old, new):
        try:
            # Check if trying to move file
            mfile = self.auth.get_real_base().get_file_for_paths(self.restpath)
            if mfile:
                authid, newrestpath = self._get_auth_from_path(new)
                if authid == self.auth.id:
                    try:
                        self.auth.get_real_base().get_file_for_paths(newrestpath)
                    except MFolder.DoesNotExist as e:
                        mfile.name = os.path.basename(new)
                        mfile.save()
                    except MFile.DoesNotExist as e:
                        mfile.name = os.path.basename(new)
                        mfile.save()
                
            # Check if trying to move folder
            mfolder = self.auth.get_real_base().get_folder_for_paths(self.restpath)
            if mfolder:
                authid, newrestpath = self._get_auth_from_path(new)
                print authid, newrestpath
                if authid == self.auth.id:
                    try:
                        self.auth.get_real_base().get_folder_for_paths(newrestpath)
                    except MFolder.DoesNotExist as e:
                        mfolder.name = os.path.basename(new)
                        mfolder.save()
                    except MFile.DoesNotExist as e:
                        mfolder.name = os.path.basename(new)
                        mfolder.save()

        except Exception as e:
            logging.info(e)
            raise e

    def rmdir(self, path):
        try:
            # First get the folder from the path
            folder = self.auth.get_real_base().get_folder_for_paths(self.restpath)
            folder.delete()
        except Exception as e:
            logging.info(e)
            raise e

    def statfs(self, path):
        stv = os.statvfs(path)
        return dict((key, getattr(stv, key)) for key in ('f_bavail', 'f_bfree',
            'f_blocks', 'f_bsize', 'f_favail', 'f_ffree', 'f_files', 'f_flag',
            'f_frsize', 'f_namemax'))
    
    def symlink(self, target, source):
        return os.symlink(source, target)

    def truncate(self, path, length, fh=None):
        try:
            mfile = self.auth.get_real_base().get_file_for_paths(self.restpath)
            f = open( mfile.file.path, 'r+')
            return os.ftruncate(f.fileno(), length)
        except Exception as e:
            logging.info(e)
            raise e
    
    def unlink(self, path):
        try:
            mfile = self.auth.get_real_base().get_file_for_paths(self.restpath)
            mfile.delete()
        except Exception as e:
            logging.info(e)
            raise e

    utimens = os.utime
    
    def write(self, path, data, offset, fh):
        with self.rwlock:
            os.lseek(fh, offset, 0)
            return os.write(fh, data)
    

if __name__ == "__main__":
    if len(argv) != 2:
        print 'usage: %s <mountpoint>' % argv[0]
        exit(1)
    fuse = FUSE(Loopback(), argv[1], foreground=True)