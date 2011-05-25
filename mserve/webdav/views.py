################################################################################
#
# (C) University of Southampton IT Innovation Centre, 2011
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
#    Created By :             Mark McArdle
#    Created Date :           2011-04-28
#    Created for Project :    Postmark
#
################################################################################
#
# Dependencies : none
#
################################################################################

from mserve.dataservice.models import *
from mserve.webdav.models import *
import logging
import datetime
import time
import os.path
import os
import urllib2
from copy import deepcopy
from datetime import datetime,timedelta,tzinfo
from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from lxml import etree

def webdav(request,id):

    try:
        logging.info("%s id:%s %s" % (request.method, id, request.path_info));

        response = None
        try:
            dataservice = DataService.objects.get(id=id)
            dav_server = DavServer(dataservice,id)
            response = dav_server.handle(request)
        except DataService.DoesNotExist:
            #logging.info("%s Data Service %s doesnt exists" % (request.method, id));
            pass

        try:
            auth = Auth.objects.get(id=id)
            import dataservice.utils as utils
            base = utils.get_base_for_auth(auth)
            if utils.is_service(base):
                dataservice = DataService.objects.get(id=auth.base.id)
                dav_server = DavServer(dataservice,id)
                #logging.info("%s Auth:%s %s" % (request.method, dataservice, request.path_info));
                response = dav_server.handle(request)
        except Auth.DoesNotExist:
            pass

        #if response == None:
        #    logging.info("Response NOT FOUND")
        #    return HttpResponseNotFound()

        #logging.info("Response for %s : %s " % (request.method,response.status_code))

        if response['Content-Type'] == 'text/xml':
            pass#logging.info(response.content)
        else:
            pass#logging.info('<non-xml response data> %s ' % (response['Content-Type']))
        return response
    except Exception as e:
        logging.exception(e)

# Chunk Size - 50Mb
chunk_size=1024*1024*50

def fbuffer(f, length , chunk_size=chunk_size):

    #logging.info("reading %s in chunks of  %s "% (length,chunk_size))

    to_read = int(length)
    while to_read > 0 :
        chunk = f.read(chunk_size)
        to_read = to_read - chunk_size
        #logging.info("read chunk - %s to go "% (to_read))
        if not chunk:
            break
        yield chunk

class DavServer(object):

    SUPPORTED_PROPERTIES = [
        'creationdate',
        'displayname',
        'getcontentlength',
        'getcontenttype',
        'getetag',
        'getlastmodified',
        'resourcetype'
    ]

    def __init__(self,service,id):
        self.service = service
        self.id = id

    def handle(self, request):
        if request.method == 'COPY':
            return self._handle_copy(request)
        elif request.method == 'DELETE':
            return self._handle_delete(request)
        elif request.method == 'GET':
            return self._handle_get(request)
        elif request.method == 'HEAD':
            return self._handle_head(request)
        elif request.method == 'OPTIONS':
            return self._handle_options(request)
        elif request.method == 'MKCOL':
            return self._handle_mkcol(request)
        elif request.method == 'MOVE':
            return self._handle_move(request)
        elif request.method == 'POST':
            return self._handle_post(request)
        elif request.method == 'PROPFIND':
            return self._handle_propfind(request)
        elif request.method == 'PROPPATCH':
            return self._handle_proppatch(request)
        elif request.method == 'PUT':
            return self._handle_put(request)
        else:
            return HttpResponseBadRequest()

    def _handle_copy(self, request):
        # NOTE This assumes same-host destination
        # TODO Handle other host destination to allow remote copy
        dest_path = request.META['HTTP_DESTINATION'][
            request.META['HTTP_DESTINATION'].find(
                request.META['HTTP_HOST'])+len(request.META['HTTP_HOST']):]

        overwrite = True
        if request.META.has_key('HTTP_OVERWRITE') and request.META['HTTP_OVERWRITE'] == 'F':
            overwrite = False

        if dest_path == request.path_info and overwrite == False:
            return HttpResponseForbidden()

        return self.__do_copy(request, self.service, dest_path, overwrite)

    def _handle_delete(self, request):
        # TODO : Handle Recovery undelete
        logging.info("DELETE on %s" % self.service)

        request_uri = request.META['REQUEST_URI']
        if request_uri.find('#') != -1:
            logging.info("Bad Request, URI contains fragment %s " %request.META['REQUEST_URI'])
            return HttpResponseBadRequest()

        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)

        if isFo or isFi:
            object.delete()
            return HttpResponseNoContent()

        return HttpResponseNotFound()


    def _handle_get(self, request):
        logging.info("GET on %s" % self.service)
        response = self._handle_head(request)
        if response.status_code != 404:

            isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)

            if isFi:
                return object.do("GET","file")

        else:
            return HttpResponseNotFound()

    def _handle_head(self, request):
        # TODO Configure response headers for HEAD request
        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)
        response = HttpResponse()
        if isFi:
            response = HttpResponse(mimetype=object.mimetype)
            response['Content-Length'] = object.file.size
            fstat = os.stat(object.file.path)
            response['Last-Modified'] = self.__get_localized_datetime(fstat.st_mtime).strftime("%a, %d %b %Y %H:%M:%S %Z")
            response['ETag'] = "%s-%s" % (hex(int(fstat.st_mtime))[2:], fstat.st_size)
            return response
        elif isFo:
            response['Content-Length'] = "4096"
            return response
        elif _get_path(request,self.id) == '/' :
            return response
        else:
            return HttpResponseNotFound()

    def _handle_mkcol(self, request):
        logging.info("MKCOL on %s" % self.service)

        # We don't support bodies for MKCOL requests
        if hasattr(request,"raw_post_data") and request.raw_post_data != '':
            return HttpResponseUnsupportedMediaType()

        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)

        if isFi:
            return HttpResponseMethodNotAllowed()

        if isFo:
            return HttpResponseMethodNotAllowed()


        is_folder,ancestors,name,fname = _get_path_info_request(request,self.id)

        foldername = ancestors.pop()
        
        ancestors_exist,parentfolder = self.__ancestors_exist(self.service, ancestors)

        if not ancestors_exist:
            return HttpResponseConflict()

        try:
            MFolder.objects.get(name=foldername,service=self.service,parent=parentfolder)
            return HttpResponseMethodNotAllowed()
        except MFolder.DoesNotExist:

            try:
                existingmfile = MFile.objects.get(service=self.service,name=foldername,folder=parentfolder)
                return HttpResponseMethodNotAllowed()
            except MFile.DoesNotExist:
                pass

            mfolder = MFolder(name=foldername,service=self.service,parent=parentfolder)
            mfolder.save()
            r = HttpResponseCreated()
            return r
            

    def _handle_move(self, request):
        logging.info("MOVE on %s" % self.service)

        # NOTE This assumes same-host destination
        # TODO Handle other host destination to allow remote move
        dest_path = request.META['HTTP_DESTINATION'][
            request.META['HTTP_DESTINATION'].find(
                request.META['HTTP_HOST'])+len(request.META['HTTP_HOST']):]

        overwrite = True
        if request.META['HTTP_OVERWRITE'] == 'F':
            overwrite = False

        # Move file(s)
        response = self.__do_move(request, self.service, dest_path, overwrite)

        return response

    def _handle_options(self, request):
        logging.info("OPTIONS on %s" % self.service)
        response = MultiValueHttpResponse()
        response['Content-Length'] = 0
        response.add_header_value('DAV', '1')
        #response.add_header_value('DAV', '<http://apache.org/dav/propset/fs/1>')

        response['MS-Author-Via'] = "DAV"
        
        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)

        if isFi:
            response['Allow'] = "COPY, DELETE, GET, HEAD, MOVE, OPTIONS, POST, PROPFIND, PROPPATCH, PUT"
            response['Content-Type'] = object.mimetype
        elif isFo:
            response['Content-Type'] = 'httpd/unix-directory'
            response['Allow'] = "COPY, DELETE, GET, HEAD, MKCOL, MOVE, OPTIONS, POST, PROPFIND, PROPPATCH"
        else:
            response['Content-Type'] = 'httpd/unix-directory'
            response['Allow'] = "COPY, DELETE, GET, HEAD, MKCOL, MOVE, OPTIONS, POST, PROPFIND, PROPPATCH"

        return response

    def _handle_post(self, request):
        logging.info("POST on %s" % self.service)
        # POST handling is actually the same as PUT for a non-existent resource
        return self._handle_put(request)

    def _handle_propfind(self, request):
        logging.info("PROPFIND on %s" % self.service)
        # Handle Depth header
        depth = '1'
        if request.META.has_key('HTTP_DEPTH'):
            depth = request.META['HTTP_DEPTH']


        # First, find out what properties were requested
        props = []

        if hasattr(request,"raw_post_data") and request.raw_post_data != '':
            try:
                xmltree = etree.fromstring(request.raw_post_data)
                allprop_nodes = xmltree.xpath('*[local-name() = "allprop"]')
                if allprop_nodes:
                    for p in self.SUPPORTED_PROPERTIES:
                        props.append(DavProperty(name=p, ns='DAV:'))
                prop_nodes = xmltree.xpath('*[local-name() = "prop"]/*')
                for p in prop_nodes:
                    name = p.xpath('local-name()')
                    ns = p.xpath('namespace-uri()')
                    props.append(DavProperty(name=name, ns=ns))
            except:
                # Request body not valid XML
                return HttpResponseBadRequest()
        else:
            for p in self.SUPPORTED_PROPERTIES:
                props.append(DavProperty(name=p, ns='DAV:'))


        # Next, get all the files that we want to return properties for

        files = []
        mfiles = []

        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)
        real_path = request.path_info.split(self.id)[-1:][0]

        if isFi:
            finfo = self.__get_file_info(request, self.service, object, props=props)
            if finfo:
                files.append(finfo)

        elif isFo :
            finfo = self.__get_folder_info(request, self.service, object, props=props)
            files.append(finfo)

            if depth != '0':

                mfiles.extend(list(object.mfile_set.all()))
                for mfile in mfiles:
                    finfo = self.__get_file_info(request, self.service, mfile, props=props)
                    if finfo:
                        files.append(finfo)

                folders = list(MFolder.objects.filter(parent=object,service=self.service))
                for mfolder in folders:
                    finfo = self.__get_folder_info(request, self.service, mfolder, props=props)
                    files.append(finfo)
        elif real_path == '' or real_path == '/':
            finfo = self.__get_service_info( request, self.service, props)
            files.append(finfo)

            if depth != '0':
                service_mfiles = list(MFile.objects.filter(folder=None,service=self.service))
                for mfile in service_mfiles:
                    finfo = self.__get_file_info(request, self.service, mfile, props=props)
                    if finfo:
                        files.append(finfo)

                folders = list(MFolder.objects.filter(parent=None,service=self.service))
                for mfolder in folders:
                    finfo = self.__get_folder_info(request, self.service, mfolder, props=props)
                    files.append(finfo)
        else:
            return HttpResponseNotFound()
        
        # Finally, build the response using a django template
        response = render_to_response("multistatus.djt.xml",
            {'files': files, 'props': props},
            context_instance=RequestContext(request),
            mimetype='text/xml')


        if response.status_code == 200:
            response.status_code = 207
        return response

    def _handle_proppatch(self, request):
        logging.info("PROPPATCH on %s" % self.service)

        props = []
        if request.raw_post_data != '':
            try:
                xmltree = etree.fromstring(request.raw_post_data)
                set_prop_nodes = xmltree.xpath('*[local-name() = "set" or local-name() = "remove"]/*[local-name() = "prop"]/*')
                for p in set_prop_nodes:
                    ns = p.xpath('namespace-uri()')
                    name = p.xpath('local-name()')
                    # TODO: Handle other than text in value
                    value = ''.join(p.xpath('text()'))
                    action = p.xpath('local-name(../..)')
                    props.append(DavProperty(name=name, value=value, ns=ns, action=action))
            except:
                # Request body not valid XML
                return HttpResponseBadRequest()

        path = request.path_info
        # Set/remove properties as requested
        for p in props:
            if p.action == 'set':
                logging.info("PROPPATCH set '%s' on %s" % (p,path))
                self.__set_property(path=path, property=p)
            elif p.action == 'remove':
                logging.info("PROPPATCH remove '%s' on %s" % (p,path))
                self.__remove_property(path=path, property=p)
                p.removed = True


        files = []

        isFo,isFi,object = _get_resource_for_path(path,self.service,self.id)
        
        if isFi:
            finfo = self.__get_file_info(request, self.service, object, props=props)
            if finfo:
                files.append(finfo)

        response = render_to_response("multistatus.djt.xml", {'files': files, 'props': props},
            context_instance=RequestContext(request), mimetype='text/xml')

        # Default response is 200 for django
        if response.status_code == 200:
            # Needs to be 207 for multistatus response
            response.status_code = 207

        return response

    def __remove_property(self, path=None, property=None):
        if path and property:

            isFo,isFi,object = _get_resource_for_path(path,self.service,self.id)

            if isFi or isFo:
                try:
                    existing_dav_property = WebDavProperty.objects.get(base=object,name=property.name,ns=property.namespace)
                    existing_dav_property.delete()
                    
                except WebDavProperty.DoesNotExist:
                    logging.info("PROPPATCH Asked to remove non-existant property '%s' on %s" % (property,path))
                    pass

    def __set_property(self, path=None, property=None):
        if path and property:

            isFo,isFi,object = _get_resource_for_path(path,self.service,self.id)

            if isFi or isFo:
                try:
                    existing_dav_property = WebDavProperty.objects.get(base=object,name=property.name,ns=property.namespace)
                    existing_dav_property.set_value(property.value)
                    existing_dav_property.save()

                except WebDavProperty.DoesNotExist:
                    new_dav_property = WebDavProperty(base=object,name=property.name,ns=property.namespace)
                    new_dav_property.set_value(property.value)
                    new_dav_property.save()

    def _handle_put(self, request):
        logging.info("PUT on %s" % self.service)
        response = self.__handle_upload_service(request)
        return response

    def __mfile_exists(self, service, ancestors, filename):
        # Check Folders exists

        folder = None
        try:
            for foldername in ancestors:
                if ancestors[0] == foldername:
                    folder = service.mfolder_set.get(name=foldername)
                else:
                    folder = folder.mfolder_set.get(name=foldername)

        except MFolder.DoesNotExist:
            return False,None

        mfile = None
        try:
            mfile = MFile.objects.get(name=filename,folder=folder)
        except MFile.DoesNotExist:
            return False,None

        return True,mfile

    def __ancestors_exist(self, service, ancestors):
        # Check Folders exists
        folder = None
        try:
            for foldername in ancestors:
                if ancestors[0] == foldername:

                    folder = service.mfolder_set.get(name=foldername,parent=None)

                else:
                    folder = folder.mfolder_set.get(name=foldername)

        except MFolder.DoesNotExist:
            return False,None

        return True,folder

    def __do_move(self, request, service, dest_path, overwrite):

        created = True

        # Check Destination
        isDestFo,isDestFi,dest_object = _get_resource_for_path(dest_path,service,self.id)

        if (isDestFi or isDestFo) and not overwrite:
            return HttpResponsePreconditionFailed()

        isFo,isFi,object = _get_resource_for_path(request.path_info,service,self.id)

        if not isFi and not isFo:
            # Source doesn't exist, nothing to copy
            return HttpResponseNotFound()

        # The OPTIONS
        # 1 src is file therefore rename file and change parent folder, delete dest file
        # 2 src is folder therefore rename folder and change parent folder, delete dest folder

        created = True

        #1
        if isFi:
            real_dest_path = dest_path.split(self.id)[-1:][0]
            norm_path = os.path.normpath(real_dest_path)
            norm_path_split = norm_path.split('/')
            ancs = norm_path_split[0:-1]

            if ancs[0] == '':
                ancs.remove('')

            file_or_folder = norm_path_split[-1]
            isDestParentFo,parentFo = self.__ancestors_exist(service, ancs)

            if not isDestParentFo:
                return HttpResponseConflict()
            
            mfile = object
            mfile.name = file_or_folder
            mfile.folder = parentFo
            if dest_object is not None:
                created = False
                dest_object.delete()
            mfile.save()


        #2
        if isFo:
            real_dest_path = dest_path.split(self.id)[-1:][0]
            norm_path = os.path.normpath(real_dest_path)
            norm_path_split = norm_path.split('/')
            ancs = norm_path_split[0:-1]
            
            if ancs[0] == '':
                ancs.remove('')

            file_or_folder = norm_path_split[-1]
            isDestParentFo,parentFo = self.__ancestors_exist(service, ancs)

            if not isDestParentFo:
                return HttpResponseConflict()
            
            mfolder = object
            mfolder.name = file_or_folder
            mfolder.parent = parentFo
            if dest_object is not None:
                created = False
                dest_object.delete()
            mfolder.save()

        if created:
            return HttpResponseCreated()
        else:
            return HttpResponseNoContent()

    def __do_copy(self, request, service, dest_path, overwrite):

        isFo,isFi,object = _get_resource_for_path(request.path_info,service,self.id)

        if not isFi and not isFo:
            # Source doesn't exist, nothing to copy
            return HttpResponseNotFound()

        # Check Destination
        isDestFo,isDestFi,dest_object = _get_resource_for_path(dest_path,service,self.id)

        created = True

        if (isDestFi or isDestFo):
            created = False
            if not overwrite:
                return HttpResponsePreconditionFailed()

        # The OPTIONS
        # 1 src is file therefore create new mfile, copy contents
        # 2 src is folder therefore create new mfolder, copy files and folders

        #1
        if isFi:

            real_dest_path = dest_path.split(self.id)[-1:][0]
            norm_path = os.path.normpath(real_dest_path)
            norm_path_split = norm_path.split('/')
            ancs = norm_path_split[0:-1]

            if ancs[0] == '':
                ancs.remove('')

            file_or_folder = norm_path_split[-1]
            isDestParentFo,parentFo = self.__ancestors_exist(service, ancs)

            if not isDestParentFo:
                return HttpResponseConflict()

            #if isDestFi and dest_object.name == file_or_folder:
            #    created = False

            mfile = object

            if not isDestFi:
                new_mfile = MFile(name=file_or_folder, file=mfile.file, folder=parentFo, mimetype=mfile.mimetype, empty=False, service=mfile.service )
                new_mfile.save()
            else:
                created = False
                dest_object.file = mfile.file
                dest_object.save()

            #created = True

        #2
        if isFo:
            real_dest_path = dest_path.split(self.id)[-1:][0]
            norm_path = os.path.normpath(real_dest_path)
            norm_path_split = norm_path.split('/')
            ancs = norm_path_split[0:-1]

            if ancs[0] == '':
                ancs.remove('')

            file_or_folder = norm_path_split[-1]
            isDestParentFo,parentFo = self.__ancestors_exist(service, ancs)

            if not isDestParentFo:
                return HttpResponseConflict()

            isDestFo,isDestFi,dest_object = _get_resource_for_path(dest_path,self.service,self.id)

            if not isDestFo:
                new_mfolder = object.duplicate(file_or_folder,parentFo)
                new_mfolder.save()
            else:
                dest_object.delete()
                new_mfolder = object.duplicate(file_or_folder,parentFo)
                new_mfolder.save()
                created = False

        if created:
            return HttpResponseCreated()
        else:
            return HttpResponseNoContent()

    def __get_service_info(self, request, service, props=[]):
        rel_path = "/%s/%s/" % ("webdav",self.id)

        finfo = DavFileInfo(href=rel_path)
        f_props = deepcopy(props)

        while len(f_props) != 0:
            p = f_props.pop(0)
            if p.name in self.SUPPORTED_PROPERTIES:
                if p.name == 'creationdate':
                    dt = datetime.today()
                    p.value = dt.isoformat()
                elif p.name == 'displayname':
                    p.value = self.id
                elif p.name == 'getcontentlength':
                    p.value = 4096
                elif p.name == 'getcontenttype':
                    p.value = "application/x-directory"
                elif p.name == 'getetag':
                    dt = datetime.today()
                    epoch_seconds = time.mktime(dt.timetuple())
                    p.value = "%s-%s" % (hex(int(epoch_seconds))[2:], 4096)
                elif p.name == 'getlastmodified':
                    dt = datetime.today()
                    p.value = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
                elif p.name == 'resourcetype':
                    p.value = '<D:collection/>'
            elif p.status == '200 OK' and not p.removed:
                # TODO: Custom properties
                # See if we have a value for the custom property
                #custom_prop = self.__get_property(abs_path, p.name)
                #if custom_prop:
                #    p.value = custom_prop.value
                #else:
                    # No value found for the custom property
                p.status = '404 Not Found'
            finfo.add_property(property=p, status=p.status)

        return finfo

    def __get_folder_info(self, request, service, folder, props=[]):
        rel_path = "/%s/%s/%s/" % ("webdav",self.id,folder.get_rel_path())

        finfo = DavFileInfo(href=rel_path)
        f_props = deepcopy(props)

        # Check Source
        is_folder,ancestors,filename,foldername = _get_path_info_request(request,self.id)
        a,src_folder = self.__ancestors_exist(service,ancestors)

        while len(f_props) != 0:
            p = f_props.pop(0)
            if p.name in self.SUPPORTED_PROPERTIES:
                if p.name == 'creationdate':
                    dt = datetime.today()
                    p.value = dt.isoformat()
                elif p.name == 'displayname':
                    p.value = folder.name
                elif p.name == 'getcontentlength':
                    p.value = 4096
                elif p.name == 'getcontenttype':
                    p.value = "application/x-directory"
                elif p.name == 'getetag':
                    dt = datetime.today()
                    epoch_seconds = time.mktime(dt.timetuple())
                    p.value = "%s-%s" % (hex(int(epoch_seconds))[2:], 4096)
                elif p.name == 'getlastmodified':
                    dt = datetime.today()
                    p.value = dt.strftime("%a, %d %b %Y %H:%M:%S %Z")
                elif p.name == 'resourcetype':
                    p.value = '<D:collection/>'
            elif p.status == '200 OK' and not p.removed:
                # TODO: Custom properties
                # See if we have a value for the custom property
                custom_prop = self.__get_property(folder, p.name, p.namespace)
                if custom_prop:
                    p.value = custom_prop
                else:
                    # No value found for the custom property
                    p.status = '404 Not Found'
            finfo.add_property(property=p, status=p.status)

        return finfo

    def __get_file_info(self, request, service, mfile, props=[]):
        rel_path = "/%s/%s/%s" % ("webdav",self.id,mfile.get_rel_path())

        finfo = DavFileInfo(href=rel_path)

        if not mfile.file:
            return None

        fstat = os.stat(mfile.file.path)
        f_props = deepcopy(props)
        while len(f_props) != 0:
            p = f_props.pop(0)
            if p.name in self.SUPPORTED_PROPERTIES:
                if p.name == 'creationdate':
                    p.value = self.__get_localized_datetime(fstat.st_ctime).isoformat()
                elif p.name == 'displayname':
                    p.value = mfile.name
                elif p.name == 'getcontentlength':
                    p.value = fstat.st_size
                elif p.name == 'getcontenttype':
                    if mfile.mimetype != None:
                        # TODO : backwards compatible for mimetypes
                        p.value = mfile.mimetype.split(";")[0]
                    else:
                        p.value = "application/octet-stream"
                elif p.name == 'getetag':
                    p.value = "%s-%s" % (hex(int(fstat.st_mtime))[2:], fstat.st_size)
                elif p.name == 'getlastmodified':
                    p.value = self.__get_localized_datetime(fstat.st_mtime).strftime("%a, %d %b %Y %H:%M:%S %Z")
                elif p.name == 'resourcetype':
                    p.value = ''
            elif p.status == '200 OK' and not p.removed:
                # TODO : Get MFile Properites
                # See if we have a value for the custom property
                custom_prop = self.__get_property(mfile, p.name, p.namespace)
                if custom_prop:
                    p.value = custom_prop
                else:
                     #No value found for the custom property
                    p.status = '404 Not Found'
            finfo.add_property(property=p, status=p.status)

        return finfo

    def __get_property(self, base=None, property_name=None, property_namespace=None):
        if base and property_name:
            try:
                dav_property = WebDavProperty.objects.get(base=base,name=property_name,ns=property_namespace)
                return dav_property.get_value()
            except WebDavProperty.DoesNotExist:
                return None

    def __get_localized_datetime(self, timestamp):
        utc = datetime.utcfromtimestamp(timestamp)
        local = datetime.fromtimestamp(timestamp)
        delta = local - utc
        local -= delta
        localized_str = local.strftime("%d %b %Y %H:%M:%S UTC")
        localized = datetime.strptime(localized_str, "%d %b %Y %H:%M:%S %Z")
        localized = localized.replace(tzinfo=UTC())
        return localized

    def __handle_upload_service(self, request):

        isFo,isFi,object = _get_resource_for_path(request.path_info,self.service,self.id)

        if isFo:
            return HttpResponseBadRequest("File path specified is a directory")

        length = 0
        chunked = False
        ranged = False
        rangestart = -1
        rangeend = -1
        created = False

        if request.META.has_key('HTTP_CONTENT_LENGTH'):
            length = request.META['HTTP_CONTENT_LENGTH']

        if request.META.has_key('HTTP_RANGE'):
            range_header = request.META['HTTP_RANGE']
            byte,range=range_header.split('=')
            ranges = range.split('-')

            if len(ranges) != 2:
                return HttpResponseBadRequest("Do not support range '%s' "% range_header)

            rangestart = int(ranges[0])
            rangeend = int(ranges[1])
            length = rangeend - rangestart
            ranged = true

        if request.META.has_key('HTTP_TRANSFER_ENCODING'):
            encoding_header = request.META['HTTP_TRANSFER_ENCODING']
            if encoding_header.find('chunked') != -1:
                chunked = True

        if chunked:
            return HttpResponseBadRequest("Chunking Not Supported")

        is_folder,ancestors,name,fname = _get_path_info_request(request,self.id)
        ancestors_exist,parentfolder = self.__ancestors_exist(self.service, ancestors)

        mfile = None

        if isFi:
            mfile = object
        elif not is_folder and ancestors_exist:
            created = True
            mfile = self.service.create_mfile(name,post_process=False)
            mfile.folder=parentfolder
        else:
            return HttpResponseBadRequest("Error creating file")

        input = request.META['wsgi.input']

        if rangestart != -1:
            try:
                mf = open(mfile.file.path,'r+b')
                try:
                    mf.seek(rangestart)
                    for chunk in fbuffer(input,length):
                        mf.write(chunk)
                finally:
                    mf.close()
            except IOError:
                logging.error("Error writing partial content to MFile '%s'" % mfile)
                pass
        else:
            try:
                mf = open(mfile.file.path,'wb')
                try:
                    for chunk in fbuffer(input,length):
                        mf.write(chunk)
                finally:
                    mf.close()
            except IOError:
                logging.error("Error writing content to MFile '%s'" % mfile)
                pass

        if chunked:
            if request.META.has_key('HTTP_TRAILER'):
                trailer = input.readline()
                trailersplit= trailer.split(':')
                if len(trailersplit)>1:
                    header = trailersplit[0]
                    md5value = trailersplit[1]
                    logging.info("Found Trailer header %s with value %s " % (header,md5value))

        mfile.save()

        # TODO : Need to check if file is done?
        # How? perhaps a special header is needed
        # X-MServe-Process
        if not ranged:
            mfile.post_process()
        if request.META.has_key('HTTP_X_MSERVE'):
            encoding_header = request.META['HTTP_X_MSERVE']
            if encoding_header.find('post-process') != -1:
                logging.info("X-MServe header found - post processing content")
                mfile.post_process()

        if created:
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=204)

class DavFileInfo(object):

    def __init__(self, href=None, responsedescription=None):
        self.href = href
        self.properties = {}
        self.responsedescription = responsedescription

    def add_property(self, property=None, status='200 OK'):
        if property:
            if not self.properties.has_key(status):
                self.properties[status] = []
            self.properties[status].append(property)

    def __repr__(self):
        return "%s" % (self.href)

    def __unicode__(self):
        return "%s %s " % (self.href, self.properties)

class DavProperty(object):

    def __init__(self, name=None, value=None, status=None, ns=None, action=None):
        self.name = name
        self.value = value
        self.status = status or '200 OK'
        self.namespace = ns or ''
        self.action  = action or 'get'
        self.removed = False

    def __repr__(self):
        return "%s:%s" % (self.name,self.value)

    def __unicode__(self):
        return self.name

class HttpResponseConflict(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseConflict, self).__init__(*args, **kwargs)
        self.status_code = 409

class HttpResponseContinue(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseContinue, self).__init__(*args, **kwargs)
        self.status_code = 100

class HttpResponseCreated(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseCreated, self).__init__(*args, **kwargs)
        self.status_code = 201

class HttpResponseMethodNotAllowed(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseMethodNotAllowed, self).__init__(*args, **kwargs)
        self.status_code = 405

class HttpResponseNoContent(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseNoContent, self).__init__(*args, **kwargs)
        self.status_code = 204

class HttpResponsePreconditionFailed(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponsePreconditionFailed, self).__init__(*args, **kwargs)
        self.status_code = 412

class HttpResponseUnsupportedMediaType(HttpResponse):
    def __init__(self, *args, **kwargs):
        super(HttpResponseUnsupportedMediaType, self).__init__(*args, **kwargs)
        self.status_code = 415

class MultiValueHttpResponse(HttpResponse):
    '''
    A subclass of HttpResponse that is capable of representing multiple instances of a header.
    Use 'add_header_value' to set or add a value for a header.
    Use 'get_header_values' to get all values for a header.
    'items' returns an array containing each value for each header.
    'get' and '__getitem__' return the first value for the requested header.
    '__setitem__' replaces all values for a header with the provided value.
    '''

    # See http://djangosnippets.org/snippets/1871/

    _multi_value_headers = {}

    def __init__(self, *args, **kwargs):
        super(MultiValueHttpResponse, self).__init__(*args, **kwargs)
        # the constructor may set some headers already
        for item in super(MultiValueHttpResponse, self).items():
            self[item[0]] = item[1]

    def __str__(self):
        return '\n'.join(['%s: %s' % (key, value)
                          for key, value in self.items()]) + '\n\n' + self.content

    def __setitem__(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        self._multi_value_headers[header.lower()] = [(header, value)]

    def __getitem__(self, header):
        return self._multi_value_headers[header.lower()][0][1]

    def items(self):
        items = []
        for header_values in self._multi_value_headers.values():
            for entry in header_values:
                items.append((entry[0], entry[1]))

        return items

    def get(self, header, alternate):
        return self._multi_value_headers.get(header.lower(), [(None, alternate)])[0][1]

    def add_header_value(self, header, value):
        header, value = self._convert_to_ascii(header, value)
        lower_header = header.lower()
        if not lower_header in self._multi_value_headers:
            self._multi_value_headers[lower_header] = []
        self._multi_value_headers[lower_header].append((header, value))

    def get_header_values(self, header):
        header = self._convert_to_ascii(header)

        return [header[1] for header in self._multi_value_headers.get(header.lower(), [])]

class UTC(tzinfo):
    def utcoffset(self, dt):
        return timedelta(0) + self.dst(dt)
    def dst(self, dt):
        return timedelta(0)
    def tzname(self,dt):
        return "UTC"

def _get_path(request,id):
    # format : /webdav/{id}/{ancestors}/{folder or file}/
    # Remove /webdav/{id}/
    pathlist = request.path_info.split(id)[-1:]
    return pathlist[-1]

def _get_path_info_request(request,id):
    return _get_path_info(request.path_info,id)

def _get_path_info(path,id):
    # format : /webdav/{id}/{ancestors}/{folder or file}/
    # Remove /webdav/{id}/
    pathlist = path.split(id)[-1:]
    return __get_path_info(pathlist[-1])

def __get_path_info(path):

    paths = path.split('/')
    foldername = None
    if paths[0] == '':
        paths.remove('')
    if paths[-1] == '' and len(paths)>2:
        foldername = paths[-2]
    ancestors = paths[0:-1]
    name = paths[-1:][0]

    folder = (name=='')

    return folder,ancestors,name,foldername

def _get_resource_for_path(pathlist,service,id):
    p = pathlist.split(id)[-1:]
    path = p[-1]
    # format : /{ancestors}/{folder or file}/

    norm_path = os.path.normpath(path)
    norm_path_split = norm_path.split('/')
    ancs = norm_path_split[0:-1]

    if ancs[0] == '':
        ancs.remove('')

    file_or_folder = norm_path_split[-1]

    if ancs == [] and (file_or_folder == None or file_or_folder == ''):
        return False,False,None

    if ancs == []:
        try:
            mfolder = service.mfolder_set.get(name=file_or_folder,parent=None)
            return True,False,mfolder
        except MFolder.DoesNotExist:
            pass
        try:
            mfile = service.mfile_set.get(name=file_or_folder,folder=None)
            return False,True,mfile
        except MFile.DoesNotExist:
            pass

    if file_or_folder == None or file_or_folder == '':
        return False,False,None

    folder_exists,folder_ob = _get_folder(service, ancs)

    if folder_exists:
        try:
            mfolder = folder_ob.mfolder_set.get(name=file_or_folder,parent=folder_ob)
            return True,False,mfolder
        except MFolder.DoesNotExist:
            pass
        try:
            mfile = folder_ob.mfile_set.get(name=file_or_folder,folder=folder_ob)
            return False,True,mfile
        except MFile.DoesNotExist:
            pass

    return False,False,None

def _get_folder(service, ancestors):
    # Check Folders exists
    folder = None
    try:
        for foldername in ancestors:
            if ancestors[0] == foldername:
                folder = service.mfolder_set.get(name=foldername,parent=None)
            else:
                folder = folder.mfolder_set.get(name=foldername)
    except MFolder.DoesNotExist:
        return False,None

    if folder is None:
        return False,None
    
    return True,folder