"""

MServe Handlers
---------------

::

 This class defines the piston handlers for the dataservice module
 
All the handlers follow the same basic pattern. Each handler is attached to a
Django Model, defined in models.py. Each handler maps the four basic HTTP
methods onto CRUD methods

+------------+------------+
| HTTP       | CRUD       |
+============+============+
| GET        | read       |
+------------+------------+
| PUT        | update     |
+------------+------------+
| POST       | create     |
+------------+------------+
| DELETE     | delete     |
+------------+------------+

The methods that are allowed in a handler are specified in the 'allowed_methods'
field. If a method is specified in 'allowed_methods' but is not implemented
in the class, it will be handled by the BaseHandler piston class.

A handler is called when a pattern in urls.py is mapped onto a handler and the
variables from the pattern are passed to it e.g. (?P<containerid>[^/]+) would
pass the variable containerid to the handler
All handlers also recieve the request object which contains information about
the request, e.g. request.user
The 'fields' field in each handler defines which fields and methods from the
handlers model is serialized and returned as JSON

More info https://bitbucket.org/jespern/django-piston/wiki/Documentation

"""
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
from piston.handler import BaseHandler
from piston.utils import rc
from models import MServeProfile
from models import ServiceRequest
from models import Usage
from models import NamedBase
from models import HostingContainer
from models import DataServiceProfile
from models import DataServiceWorkflow
from models import DataServiceTaskSet
from models import DataServiceTask
from models import DataService
from models import RemoteMServeService
from models import MFolder
from models import MFile
from models import Relationship
from models import BackupFile
from models import ManagementProperty
from models import Auth
from forms import ServiceRequestForm
from forms import HostingContainerForm
from forms import SubServiceForm
from forms import DataServiceForm
from forms import UpdateMFileForm
from forms import MFileForm
from forms import ManagementPropertyForm
from forms import DataServiceTaskForm
from forms import DataServiceTaskSetForm
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
import utils as utils
import logging


class ProfileHandler(BaseHandler):
    """
    
    The piston handlers for the :class:`.MServeProfile` class
    
    This allows a user to get their MServeProfile, with contains references to
    auth capabilites for MFiles, MFolders, DataServices and auths owned by that
    user. 
    
    If a user does not have a MServeProfile this is caught via 'DoesNotExist'
    and one is created.

    """
    allowed_methods = ('GET', 'PUT')
    model = MServeProfile
    fields = (('user', ()), 'mfiles', 'mfolders', 'myauths', ('dataservices',
                ('id', 'name', 'mfile_set')), ('containers', ('id', 'name')),)

    def read(self, request):
        if not request.user.is_authenticated():
            return {}
        try:
            profile = MServeProfile.objects.get(user=request.user)
            return profile

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            mserve_profile = MServeProfile(user=request.user)
            mserve_profile.save()
            return mserve_profile


class ServiceRequestHandler(BaseHandler):
    """
    
    The piston handlers for the :class:`.ServiceRequest` class

    A ServiceRequest object is created by a regular user via POST.
    A User can check the status of the request with a GET.
    A staff member can update the request  to either approved 'A' or rejected
    'R' via a 'PUT'
    The user that made the request can delete it with a DELETE

    """
    allowed_methods = ('GET', 'POST', 'DELETE', 'PUT')
    model = ServiceRequest
    fields = ('id', 'name', 'reason', 'state', 'status', 'time', 'ctime', 'url',
             ('profile', ('id', 'user')))

    def update(self, request, servicerequestid=None):
        if request.user.is_staff:
            if "state" in request.POST:
                if request.POST['state'] == "A":

                    if "cid" in request.POST:

                        cid = request.POST['cid']
                        service_req = ServiceRequest.objects.get(
                                                    id=servicerequestid)

                        service_req.state = "A"
                        service_req.save()

                        dataservice = HostingContainer.objects.\
                            get(id=cid).create_data_service(service_req.name)

                        custauth = dataservice.auth_set.get(
                                                    authname="customer")

                        service_req.profile.auths.add(custauth)

                        return service_req
                    else:
                        response = rc.BAD_REQUEST
                        response.write("Invalid arguments - "\
                            "No Container id specified")
                        return response
                elif request.POST['state'] == "R":
                    service_req = ServiceRequest.objects.get(
                                                id=servicerequestid)
                    service_req.state = "R"
                    service_req.save()
                    return service_req
                else:
                    response = rc.BAD_REQUEST
                    response.write("Unknown state")
                    return response
            else:
                response = rc.BAD_REQUEST
                response.write("Invalid arguments")
                return response

        else:
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

    def delete(self, request, servicerequestid=None):
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response
        service_req = ServiceRequest.objects.get(id=servicerequestid)
        if request.user.get_profile() == service_req.profile:
            service_req.delete()
            return rc.DELETED
        else:
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

    def read(self, request, servicerequestid=None):

        if request.user.is_staff:
            if servicerequestid:
                return ServiceRequest.objects.get(id=servicerequestid)
            else:
                return ServiceRequest.objects.all()
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response
        try:
            profile = MServeProfile.objects.get(user=request.user)

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            profile = MServeProfile(user=request.user)
            profile.save()

        if servicerequestid:
            return ServiceRequest.objects.filter(
                            profile=profile, id=servicerequestid)
        else:
            return ServiceRequest.objects.filter(profile=profile)

    def create(self, request):
        if not request.user.is_authenticated():
            response = HttpResponse("Not Authorised.")
            response.status_code = 401
            return response

        try:
            profile = MServeProfile.objects.get(user=request.user)

        except MServeProfile.DoesNotExist:
            logging.info("PortalProfile Does not exist for this user!")
            profile = MServeProfile(user=request.user)
            profile.save()

        srform = ServiceRequestForm(request.POST)
        if srform.is_valid():
            servicerequest = srform.save()
            profile.servicerequests.add(servicerequest)
            profile.save()
            return servicerequest
        else:
            response = rc.BAD_REQUEST
            response.write(srform.as_p())
            return response


class HostingContainerHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.HostingContainer` class

    A HostingContainer object is created by a staff member with a POST.
    It can be updated with a PUT, read with a GET and deleted with DELETE.
    Only valid staff members can call any of the methods on hosting containers.

    """
    allowed_methods = ('GET', 'POST', 'DELETE', 'PUT')
    model = HostingContainer
    fields = ('name', 'id', 'created', 'default_profile', 'default_path',
                'reportnum', 'thumbs', 'services_url',
                ('dataservice_set',
                ('name', 'id', 'reportnum', 'starttime', 'endtime', 'thumbs',
                    'mfile_set')),
                ('properties', ('id', 'value', 'property', ), ), )
    exclude = ()

    def update(self, request, containerid):
        if request.user.is_staff:
            return HostingContainer.objects.get(id=containerid).do(
                                            "PUT", request=request)
        else:
            return HttpResponseForbidden()

    def read(self, request, containerid=None, murl=None):

        if containerid == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)

        if murl and containerid:
            hosting_con = get_object_or_404(HostingContainer, id=containerid)
            return hosting_con.do(request.method, murl)

        if containerid == None and not request.user.is_staff:
            return rc.FORBIDDEN

        if containerid:
            hosting_con = get_object_or_404(HostingContainer, id=containerid)
            return hosting_con.do("GET")
        else:
            return rc.FORBIDDEN

    def delete(self, request, containerid):
        logging.info("Deleting Container %s ", containerid)
        return HostingContainer.objects.get(id=str(containerid)).do("DELETE")

    def create(self, request):
        if request.user.is_staff:
            form = HostingContainerForm(request.POST)
            if form.is_valid():
                hostingcontainer = form.save()
                return hostingcontainer
            else:
                response = rc.BAD_REQUEST
                response.write("Invalid Request! %s " % (form))
                return response
        else:
            return HttpResponseForbidden()


class DataServiceHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.DataService` class

    A DataService object is created by a staff member with a POST.
    It can be updated with a PUT, read with a GET and deleted with DELETE.
    Only valid staff members can call any of the methods on data services.


    """
    allowed_methods = ('GET', 'POST', 'DELETE', 'PUT')
    model = DataService
    fields = ('name', 'id', 'created', 'reportnum', 'starttime', 'endtime',
                'mfile_set', 'job_set', 'mfolder_set', 'thumbs', 'mfiles_url',
                'folder_structure', 'subservices_url', 'url', 'stats_url',
                'usage_url', 'priority', 'properties_url', 'profiles_url',
                'mfolders_url', 'webdav_url', 'auth_set')
    exclude = ('pk')

    def read(self, request, serviceid=None, containerid=None, suburl=None):
        if suburl:
            return self.model.objects.get(id=serviceid).subservices.all()
        if containerid:
            return HostingContainer.objects.get(pk=containerid).do(
                                                        "GET", "services")
        if serviceid:
            dataservice = get_object_or_404(self.model, pk=serviceid)
            return dataservice.do("GET")
        return HttpResponseNotAllowed(['POST'])

    def update(self, request, serviceid, suburl=None):
        try:
            service = DataService.objects.get(pk=serviceid).do("PUT",
                                                        request=request)
            return service
        except DataService.DoesNotExist as excep:
            response = rc.BAD_REQUEST
            logging.info("Exception %s", excep)
            response.write("Invalid Request!")
            return response

    def delete(self, request, serviceid, suburl=None):
        logging.info("Deleting Service %s ", serviceid)
        return DataService.objects.get(id=serviceid).do("DELETE")

    def create(self, request, containerid=None, serviceid=None, suburl=None):
        service = None
        if serviceid:
            service = DataService.objects.get(id=serviceid)
            form = SubServiceForm(request.POST)
        else:
            form = DataServiceForm(request.POST)
        if form.is_valid():
            if 'name' in request.POST:
                name = request.POST['name']
                start = request.POST.get('starttime', None)
                end = request.POST.get('endtime', None)
                if start == '':
                    start = None
                if end == '':
                    end = None
                if service:
                    dataservice = service.create_subservice(name)
                else:
                    if containerid:
                        container = HostingContainer.objects.get(
                                                        id=containerid)
                        dataservice = container.create_data_service(
                                            name, starttime=start, endtime=end)
                    elif 'container' in request.POST:
                        containerid = request.POST['container']
                        container = HostingContainer.objects.get(
                                            id=containerid)
                        dataservice = container.create_data_service(
                                            name, starttime=start, endtime=end)
                    else:
                        response = rc.BAD_REQUEST
                        response.write("Invalid Request! - "
                            "No name in POST parameters")
                        return response
                return dataservice
            else:
                response = rc.BAD_REQUEST
                response.write("Invalid Request! - "
                            "No container in POST parameters")
                return response
        else:
            logging.info(form)
            response = rc.BAD_REQUEST
            response.write("Invalid Request!")
            return response


class SubServiceHandler(BaseHandler):
    """
    
    The piston handler for the subservices

    This handler is not tied to a class, but allows creation of a DataService
    object that shares data with another DataService. This relationship will be
    held via a parent relationship.

    """
    allowed_methods = ('GET', 'POST')

    def read(self, request, containerid=None):
        if containerid:
            return DataService.objects.filter(parent__container=containerid)
        else:
            response = rc.FORBIDDEN
            return response

    def create(self, request, containerid=None):
        if "serviceid" in request.POST and "name" in request.POST:
            serviceid = request.POST['serviceid']
            name = request.POST['name']
            container = HostingContainer.objects.get(id=containerid)
            service = container.dataservice_set.get(id=serviceid)
            subservice = service.create_subservice(name=name)
            if 'starttime' in request.POST:
                subservice.starttime = request.POST['starttime']
            if 'endtime' in request.POST:
                subservice.endtime = request.POST['endtime']
            subservice.save()
            return subservice
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid Request! %s not valid " % request.POST)
            return response


class DataServiceProfileHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.DataServiceProfile` class

    This handler allows the reading of the DataServiceProfile objects for a
    DataService. Profiles can be used to control how a service operates,
    examples are 'default' and 'transcode'

    """
    allowed_methods = ('GET')
    model = DataServiceProfile
    fields = ('name', 'id', 'workflows', 'tasksets_url', 'tasks_url')

    def read(self, request, serviceid):
        service = DataService.objects.get(id=serviceid)
        return service.do("GET", "profiles")


class DataServiceWorkflowHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.DataServiceWorkflow` class

    This allows data service workflows to be read with a 'GET' workflows
    examples are 'ingest', 'update' and 'access'.

    """
    allowed_methods = ('GET')
    model = DataServiceWorkflow
    fields = ('name', 'id', 'tasksets', )


class DataServiceTaskSetHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.DataServiceTaskSet` class

    DataServiceTaskSets can be created, updated, read and deleted with this
    handler.

    """
    allowed_methods = ('GET', 'PUT', 'POST', 'DELETE')
    model = DataServiceTaskSet
    fields = ('name', 'id', 'tasks', 'order', 'url')

    def read(self, request, serviceid, profileid, tasksetid=None):
        if tasksetid:
            dsts = DataServiceTaskSet.objects.get(
                workflow__profile__service=serviceid,
                workflow__profile=profileid,
                id=tasksetid)
            return dsts
        else:
            dsts = DataServiceTaskSet.objects.filter(
                workflow__profile__service=serviceid,
                workflow__profile=profileid)
            return dsts

    def delete(self, request, serviceid, profileid, tasksetid):
        dsts = DataServiceTaskSet.objects.get(id=tasksetid)
        dsts.delete()
        return rc.DELETED

    def update(self, request, serviceid, profileid, tasksetid):
        dsts = DataServiceTaskSet.objects.get(id=tasksetid)
        dstsf = DataServiceTaskSetForm(request.POST, instance=dsts)
        if dstsf.is_valid():
            dsts = dstsf.save()
            return dsts
        else:
            response = rc.BAD_REQUEST
            logging.info(dstsf)
            response.write("Invalid Request!")
            return response

    def create(self, request, serviceid, profileid):
        DataService.objects.get(id=serviceid).profiles.get(id=profileid)
        dstsf = DataServiceTaskSetForm(request.POST)
        if dstsf.is_valid():
            dst = dstsf.save()
            return dst
        else:
            response = rc.BAD_REQUEST
            logging.info(dstsf)
            response.write("Invalid Request!")
            return response


class DataServiceTaskHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.DataServiceTask` class

    DataServiceTasks can be created, updated, read and deleted with this
    handler.

    """
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = DataServiceTask
    fields = ('name', 'task_name', 'id', 'condition', 'args', 'url')

    def read(self, request, serviceid, profileid, taskid=None):
        if taskid:
            dst = DataServiceTask.objects.get(
                    taskset__workflow__profile__service=serviceid,
                    taskset__workflow__profile=profileid,
                    id=taskid)
            return dst
        else:
            dst = DataServiceTask.objects.filter(
                    taskset__workflow__profile__service=serviceid,
                    taskset__workflow__profile=profileid)
            return dst

    def delete(self, request, serviceid, profileid, taskid):
        dst = DataServiceTask.objects.get(id=taskid)
        dst.delete()
        return rc.DELETED

    def update(self, request, serviceid, profileid, taskid):
        dst = DataServiceTask.objects.get(id=taskid)
        dstf = DataServiceTaskForm(request.POST, instance=dst)
        if dstf.is_valid():
            dst = dstf.save()
            return dst
        else:
            response = rc.BAD_REQUEST
            logging.info(dstf)
            response.write("Invalid Request!")
            return response

    def create(self, request, serviceid, profileid):
        DataService.objects.get(id=serviceid).profiles.get(id=profileid)
        dstf = DataServiceTaskForm(request.POST)
        if dstf.is_valid():
            dst = dstf.save()
            return dst
        else:
            response = rc.BAD_REQUEST
            logging.info(dstf)
            response.write("Invalid Request!")
            return response


class BackupFileHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.BackupFile` class

    BackupFiles are used internally by MServe for replication. This handler
    allows saving, upodating and reading of a BackupFile object and the related
    file.

    """
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = BackupFile

    def read(self, request, backupid=None):
        if backupid:
            return BackupFile.objects.get(id=backupid)
        return {}

    def create(self, request, backupid):
        backupfile = BackupFile.objects.get(pk=backupid)
        if "file" in request.FILES:
            postfile = request.FILES["file"]
            backupfile.file.save(backupfile.name, postfile, save=True)
            return {"message": "updated backup file"}
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid Request! no file in request.")
            return response

    def update(self, request, backupid):
        backupfile = BackupFile.objects.get(pk=backupid)
        try:
            utils.write_request_to_field(
                request, backupfile.file,
                "%s_%s" % ("backup", backupfile.mfile.name)
               )
            return {"message": "updated backup file"}
        except:
            raise

class RelationshipHandler(BaseHandler):
    """

    The piston handler for the :class:`.Relationship` class

    This allows reading of Relationship objects

    """
    allowed_methods = ('GET', 'POST')
    model = Relationship
    fields = ('name', 'left', 'right')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(id=mfileid)
        return mfile.relations()

    def create(self, request, mfileid):

        mfileid_left = mfileid
        mfileid_right = request.POST.get("mfileid", None)
        relationship_name = request.POST.get("name", None)

        if mfileid_right == None:
            response = rc.BAD_REQUEST
            logging.info("Bad Request to relationship create handler %s", request.POST)
            response.write("Invalid Request! No mfileid in POST fields")
            return response
        elif relationship_name == None:
            response = rc.BAD_REQUEST
            logging.info("Bad Request to relationship create handler %s", request.POST)
            response.write("Invalid Request! No name in POST fields")
            return response
        else:
            mfile_left = MFile.objects.get(id=mfileid_left)
            mfile_right = MFile.objects.get(id=mfileid_right)
            relationship = Relationship(entity1=mfile_left,
                                entity2=mfile_right,
                                name=relationship_name)
            relationship.save()
            return relationship


class MFolderHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.MFolder` class

    This allows reading of a MFolder objects with a GET

    """
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = MFolder
    fields = ('name', 'id', 'parent', 'url')

    def delete(self, request, mfolderid=None):
        self.model.objects.get(id=mfolderid).delete()
        return rc.DELETED

    def read(self, request, mfolderid=None, serviceid=None, authid=None):
        if mfolderid:
            return self.model.objects.get(id=mfolderid).do("GET")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET", "mfolders")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET", "mfolders")
        return []

    def create(self, request, serviceid):

        parent_id = request.POST.get("parent", None)
        folder_name = request.POST.get("name", None)

        if folder_name == None:
            response = rc.BAD_REQUEST
            logging.info("Bad Request to mfolder create handler %s", request.POST)
            response.write("Invalid Request! No name in POST fields")
            return response
        else:
            parent_folder = None
            if parent_id:
                parent_folder = MFolder.objects.get(id=parent_id)

            service = DataService.objects.get(id=serviceid)
            mfolder = service.create_mfolder(folder_name, parent=parent_folder)
            return mfolder

class MFileHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.MFile` class
    
    MFile objects are created with a POST to this handler. This handler also
    manages creating and updating of the thumbnail, poster and proxy objects, 
    which are mainly called by the backend during the processing of workflows.
    
    Empty MFiles objects can also be created with an empty 'file' parameter 
    in the POST
    
    """
    # TODO: Check this logic - HttpResponseNotAllowed(['POST'])?
    allowed_methods = ('GET', 'POST', 'PUT', 'DELETE')
    model = MFile
    fields = ('name', 'id', 'file', 'checksum', 'size', 'mimetype', 'thumb',
                'poster', 'proxy', 'created', 'updated', 'thumburl', \
                'posterurl', 'proxyurl', 'reportnum', 'relations', 'url',
                'download_url', 'relationships_url',
                'jobs_url', ('folder', ('id', 'name') )
            )

    def read(self, request, mfileid=None, serviceid=None,
                authid=None, field=None):
        if field:
            # TODO: Check this logic
            return HttpResponseNotAllowed(['POST'])
        if mfileid:
            return self.model.objects.get(id=mfileid).do("GET")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET", "mfiles")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET", "mfiles")
        return HttpResponseNotAllowed(['POST'])

    def delete(self, request, mfileid, field=None):
        if field:
            return HttpResponseNotAllowed(['POST'])
        logging.info("Deleting mfile %s ", mfileid)
        MFile.objects.get(id=mfileid).do("DELETE")
        return rc.DELETED

    def update(self, request, mfileid):
        try:
            mfile = MFile.objects.get(pk=mfileid)
            mfile.name = request.POST.get("name", mfile.name)
            existing = MFile.objects.filter(name=mfile.name, 
                                folder=mfile.folder, service=mfile.service)\
                                .exclude(id=mfile.id)
            if existing:
                response = rc.BAD_REQUEST
                response.write("Invalid Request! Mfile with name %s already \
                                exists" % mfile.name)
                return response
            mfile.save()
            return mfile
        except:
            raise 
            response = rc.BAD_REQUEST
            response.write("Invalid Request!")
            return response

    def create(self, request, mfileid=None, serviceid=None,
                authid=None, field=None):

        if field:
            try:
                mfile = MFile.objects.get(pk=mfileid)
                if field == "thumb":
                    postfile = request.FILES[field]
                    mfile.thumb.save("thumb.png", postfile, save=True)
                    return {"message": "updated thumb"}
                if field == "poster":
                    postfile = request.FILES[field]
                    mfile.poster.save("poster.png", postfile, save=True)
                    return {"message": "updated poster"}
                if field == "proxy":
                    postfile = request.FILES[field]
                    mfile.proxy.save("proxy.mp4", postfile, save=True)
                    return {"message": "updated proxy"}
            except MFile.DoesNotExist:
                response = rc.BAD_REQUEST
                response.write("Invalid Request!")
                return response

        form = MFileForm(request.POST, request.FILES)
        if form.is_valid():

            name = ""
            postfile = None
            if "file" in request.FILES:
                postfile = request.FILES['file']
                name = postfile.name
            else:
                postfile = None
                name = "Empty File"
            if serviceid:
                service = DataService.objects.get(pk=serviceid)
                return service.do("POST", "mfiles", name=name, file=postfile)
            if authid:
                auth = Auth.objects.get(pk=authid)
                return auth.do("POST", "mfiles", name=name, file=postfile)
            else:
                response = rc.BAD_REQUEST
                response.write("Invalid Request when "
                                "submitting creating mfile")
                return response
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid Request! Submitted Form Invalid %s" % form)
            return response


class RemoteMServeServiceHandler(BaseHandler):
    """The piston handler for the :class:`.RemoteMServeService` class"""
    allowed_methods = ('GET')
    model = RemoteMServeService

    def read(self, request):
        if request.user.is_staff:
            return RemoteMServeService.objects.all()
        else:
            return []


class MFileContentsHandler(BaseHandler):
    """
    
    A piston handler to handle reading the file field of an MFile or an
    Auth capability

    """
    allowed_methods = ('GET')

    def read(self, request, mfileid=None, authid=None):
        if mfileid:
            logging.info("MFileContentsHandler mfile")
            return MFile.objects.get(pk=mfileid).do("GET", "file")
        elif authid:
            logging.info("MFileContentsHandler auth")
            return Auth.objects.get(pk=authid).do("GET", "file")
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid Request!")
            return response


class UsageHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.Usage` class

    This handler returns usage recorded against HostingContainers, DataServices
    MFiles or Auth capabilites.

    """
    allowed_methods = ('GET')
    model = Usage
    fields = ('squares', 'total', 'nInProgress', 'metric',
                'rate', 'reports', 'time', 'rateCumulative',
                'total', 'rateTime')

    def read(self, request, containerid=None, serviceid=None,
                 mfileid=None, authid=None):
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET", "usages", **request.GET)
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET", "usages", **request.GET)
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET", "usages", **request.GET)
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET", "usages", **request.GET)


class UsageSummaryHandler(BaseHandler):
    """

    The piston handler for the usage summarys, a usage summary os an aggregated
    report of usage for a particular object.

    """
    allowed_methods = ('GET')

    def read(self, request, containerid=None, serviceid=None,
                mfileid=None, authid=None):
        if containerid or serviceid or mfileid:
            base = NamedBase.objects.get(
                    id__in=[containerid, serviceid, mfileid])
            result = {}
            result["usages"] = base.get_real_base().get_usage_summary()
            result["reportnum"] = base.reportnum
            return result
        elif authid:
            auth = Auth.objects.get(pk=authid)
            base = utils.get_base_for_auth(auth)
            result = {}
            result["usages"] = base.get_real_base().get_usage_summary()
            result["reportnum"] = base.reportnum
            return result
        elif request.user.is_staff:
            result = {}
            result["usages"] = Usage.get_full_usagesummary()
            result["reportnum"] = -1
            return result
        else:
            response = rc.BAD_REQUEST
            response.write("Invalid Request!")
            return response


class ManagementPropertyHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.ManagementProperty` class

    Management properties can be created, updated and read using this handler.

    """
    allowed_methods = ('GET', 'PUT', 'POST')
    model = ManagementProperty
    fields = ("value", "property", "id", "values")
    exclude = ()

    def read(self, request, containerid=None, serviceid=None,
                mfileid=None, authid=None):
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET", "properties")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET", "properties")
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET", "properties")
        if authid:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET", "properties")
        return []

    def create(self, request, serviceid=None):
        form = ManagementPropertyForm(request.POST)
        if form.is_valid():
            manage_prop = form.save(commit=False)
            manage_prop.base = DataService.objects.get(id=serviceid)
            try:
                ManagementProperty.objects.get(
                            property=manage_prop.property,
                            base=manage_prop.base
                           )
                logging.info("Bad Form %s ", form)
                resp = rc.BAD_REQUEST
                resp.write(". A Management Property "
                    "called '%s' allready exists " % (manage_prop.property))
                return resp
            except ManagementProperty.DoesNotExist:
                pass
            manage_prop.save()
            return manage_prop
        else:
            logging.info("Bad Form %s ", form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def update(self, request, serviceid=None):
        form = ManagementPropertyForm(request.POST)
        if form.is_valid():
            try:
                manage_prop = form.cleaned_data['property']
                base = NamedBase.objects.get(id=serviceid)
                existingmanagementproperty = ManagementProperty.objects.get(
                                            property=manage_prop, base=base)
                form = ManagementPropertyForm(request.POST,
                                        instance=existingmanagementproperty)
                return form.save()
            except ObjectDoesNotExist:
                response = rc.BAD_REQUEST
                response.write(" The Management Property '%s' doesn't exist "
                            % manage_prop)
                return response
        else:
            logging.info("Bad Form %s ", form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])


class AuthHandler(BaseHandler):
    """
    
    The piston handler for the :class:`.Auth` class

    The Auth Handler returns a list of Auth capabilites for an HostingContainer
    DataService, MFile or another Auth object. For examples the handler would
    return "servicecustomer" and "serviceadmin" for a DataService object.

    """
    allowed_methods = ('GET', 'POST')
    model = Auth
    fields = ('authname', 'browse_url', 'id', 'auth_set', 'urls', 'methods',
            'basename', 'thumburl', 'base_url', 'jobs_url', 'usage_url',
            'mfiles_url',
            ('roles', ('id', 'rolename', 'description', 'methods')))

    def read(self, request, containerid=None, serviceid=None,
                mfileid=None, authid=None, murl=None):
        if authid and not murl:
            return self.model.objects.get(id=authid).do("GET")
        if containerid:
            container = HostingContainer.objects.get(pk=containerid)
            return container.do("GET", "auths")
        if serviceid:
            service = DataService.objects.get(pk=serviceid)
            return service.do("GET", "auths")
        if mfileid:
            mfile = MFile.objects.get(pk=mfileid)
            return mfile.do("GET", "auths")
        if authid and murl:
            auth = Auth.objects.get(pk=authid)
            return auth.do("GET", murl)
        return []

    def create(self, request, authid=None, containerid=None, serviceid=None,
                        mfileid=None):
        if containerid:
            container = HostingContainer.objects.get(id=containerid)
            return container.do("POST", "auths", request=request)
        elif serviceid:
            dataservice = DataService.objects.get(id=serviceid)
            return dataservice.do("POST", "auths", request=request)
        elif mfileid:
            mfile = MFile.objects.get(id=mfileid)
            return mfile.do("POST", "auths", request=request)
        elif authid:
            auth = Auth.objects.get(id=authid)
            return auth.do("POST", "auths", request=request)
        else:
            return rc.BAD_REQUEST
