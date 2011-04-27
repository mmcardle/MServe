from dataservice.models import *
from dataservice.forms import *
from django.http import *
from django.conf import settings
import settings as settings
from dataservice.tasks import thumbvideo
from dataservice.tasks import proxyvideo
from dataservice.tasks import thumbimage
from dataservice.tasks import mimefile
from dataservice.tasks import md5file
import api as api
import logging
import os
import os.path
from piston.utils import rc
import utils as utils

generic_get_methods = ["getauths","getroles"]

generic_post_methods = ["getorcreateauth","addauth"]

generic_put_methods = ["setroles"]

generic_delete_methods = ["revokeauth"]

generic_methods = ["usage","getusagesummary","getroleinfo","getmanagedresources"] + generic_get_methods + generic_post_methods + generic_put_methods + generic_delete_methods

all_container_methods = ["makeserviceinstance","getservicemetadata","getdependencies",
    "getprovides","setresourcelookup", "getstatus","setmanagementproperty","getmanagementproperties"] + generic_methods

service_customer_methods =  ["createmfile"] + generic_methods
service_admin_methods =  service_customer_methods + ["setmanagementproperty","getmanagementproperties"]

all_service_methods = [] + service_admin_methods

mfile_monitor_methods = ["getusagesummary"]
mfile_owner_methods = ["info", "get", "put", "post", "delete", "verify"] + generic_methods

all_mfile_methods = mfile_owner_methods + mfile_monitor_methods

use_celery = settings.USE_CELERY

if use_celery:
    thumbvideo = thumbvideo.delay
    thumbimage = thumbimage.delay
    proxyvideo = proxyvideo.delay

def create_data_service(dataservice):

    serviceauth = Auth(base=dataservice,authname="full")

    serviceauth.save()

    owner_role = Role(rolename="serviceadmin")
    owner_role.setmethods(api.service_admin_methods)
    owner_role.description = "Full control of the service"
    owner_role.save()

    customer_role = Role(rolename="customer")
    customer_role.setmethods(api.service_customer_methods)
    customer_role.description = "Customer Access to the service"
    customer_role.save()

    serviceauth.roles.add(owner_role)
    serviceauth.roles.add(customer_role)

    customerauth = Auth(base=dataservice,authname="customer")
    customerauth.save()

    customerauth.roles.add(customer_role)

    managementproperty = ManagementProperty(property="accessspeed",base=dataservice,value=settings.DEFAULT_ACCESS_SPEED)
    managementproperty.save()

    return dataservice

def create_mfile(request,serviceid,file):
    service = None
    try:
        service = DataService.objects.get(id=serviceid)
    except DataService.DoesNotExist:
        try:
            auth = Auth.objects.get(id=serviceid)
            base = utils.get_base_for_auth(auth)
            service = DataService.objects.get(id=base.id)
        except Auth.DoesNotExist:
            logging.error("Failed to create mfile")
            raise Exception()

    if file==None:
        mfile = MFile(name="Empty File",service=service,empty=True)
    else:
        mfile = MFile(name=file.name,service=service,file=file,empty=False)
    mfile.save()

    logging.debug("MFile creation started '%s' "%mfile)
    logging.debug("Creating roles for '%s' "%mfile)

    mfileauth_owner = Auth(base=mfile,authname="owner")
    mfileauth_owner.save()

    owner_role = Role(rolename="owner")
    methods = api.mfile_owner_methods
    owner_role.setmethods(methods)
    owner_role.description = "Owner of the data"
    owner_role.save()

    mfileauth_owner.roles.add(owner_role)

    monitor_role = Role(rolename="monitor")
    methods = api.mfile_monitor_methods
    monitor_role.setmethods(methods)
    monitor_role.description = "Collect usage reports"
    monitor_role.save()

    mfileauth_owner.roles.add(monitor_role)

    mfileauth_monitor = Auth(base=mfile,authname="monitor")
    mfileauth_monitor.save()

    mfileauth_monitor.roles.add(monitor_role)

    mfile.save()
    mfile_post_process(mfile)
    
    logging.debug("Backing up '%s' "%mfile)

    if file is not None:
        backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
        backup.save()

    return mfile

def mfile_post_process(mfile):
    if mfile.file:
        # MIME type
        mfile.mimetype = mimetype = mimefile(mfile.file.path)
        # checksum
        mfile.checksum = md5file(mfile.file.path)
        # record size
        mfile.size = mfile.file.size

        thumbpath = os.path.join( str(mfile.file) + ".thumb.jpg")
        posterpath = os.path.join( str(mfile.file) + ".poster.jpg")
        proxypath = os.path.join( str(mfile.file) + ".proxy.ogg")
        fullthumbpath = os.path.join(settings.THUMB_ROOT , thumbpath)
        fullposterpath = os.path.join(settings.THUMB_ROOT , posterpath)
        fullproxypath = os.path.join(settings.THUMB_ROOT , proxypath)
        (thumbhead,tail) = os.path.split(fullthumbpath)
        (posterhead,tail) = os.path.split(fullposterpath)
        (proxyhead,tail) = os.path.split(fullproxypath)

        if not os.path.isdir(thumbhead):
            os.makedirs(thumbhead)

        if not os.path.isdir(posterhead):
            os.makedirs(posterhead)

        if use_celery:
            logging.info("Using CELERY for processing ")
        else:
            logging.info("Processing synchronously (change settings.USE_CELERY to 'True' to use celery)" )

        if mimetype.startswith('video') or mfile.file.name.endswith('mxf'):
            thumbtask = thumbvideo(mfile.file.path,fullthumbpath,settings.thumbsize[0],settings.thumbsize[1])
            mfile.thumb = thumbpath
            postertask = thumbvideo(mfile.file.path,fullposterpath,settings.postersize[0],settings.postersize[1])
            mfile.poster = posterpath
            proxytask = proxyvideo(mfile.file.path,fullproxypath,width=settings.postersize[0],height=settings.postersize[1])
            mfile.proxy = proxypath

        elif mimetype.startswith('image'):
            logging.info("Creating thumb inprocess for Image '%s' %s " % (mfile,mimetype))
            thumbtask = thumbimage(mfile.file.path,fullthumbpath,options={"width":settings.thumbsize[0],"height":settings.thumbsize[1]})
            mfile.thumb = thumbpath
            postertask = thumbimage(mfile.file.path,fullposterpath,options={"width":settings.postersize[0],"height":settings.postersize[1]})
            mfile.poster = posterpath

        elif mfile.file.name.endswith('blend'):
            logging.info("Creating Blender thumb '%s' %s " % (mfile,mimetype))
            # TODO : Change to a Preview of a frame of the blend file
            thumbtask = thumbimage("/var/mserve/www-root/mservemedia/images/blender.png",fullthumbpath,options={"width":settings.thumbsize[0],"height":settings.thumbsize[1]})
            mfile.thumb = thumbpath
        else:
            logging.info("Not creating thumb for '%s' %s " % (mfile,mimetype))

        mfile.save()
        

def create_container(request,name):
    hostingcontainer = HostingContainer(name=name)
    hostingcontainer.save()

    hostingcontainerauth = Auth(base=hostingcontainer,authname="full")

    hostingcontainerauth.save()

    owner_role = Role(rolename="admin")
    owner_role.setmethods(all_container_methods)
    owner_role.description = "Full access to the container"
    owner_role.save()

    hostingcontainerauth.roles.add(owner_role)

    managementproperty = ManagementProperty(property="accessspeed",base=hostingcontainer,value=settings.DEFAULT_ACCESS_SPEED)
    managementproperty.save()

    return hostingcontainer


def delete_container(request,containerid):
    container = HostingContainer.objects.get(id=containerid)
    logging.info("Deleteing service %s %s" % (container.name,containerid))

    #usages = Usage.objects.filter(base=container)
    #for usage in usages:
    #    usage.base = None
    #    usage.save()

    container.delete()
    logging.info("Container Deleted %s " % containerid)

def delete_service(request,serviceid):
    service = DataService.objects.get(id=serviceid)
    logging.info("Deleteing service %s %s" % (service.name,serviceid))

    #usages = Usage.objects.filter(base=service)
    #for usage in usages:
      #  usage.base = service.container
       # usage.save()

    service.delete()
    logging.info("Service Deleted %s " % serviceid)

def delete_mfile(request,mfileid):
    mfile = MFile.objects.get(id=mfileid)

   # usages = Usage.objects.filter(base=mfile)
    #for usage in usages:
     #   usage.base = mfile.service
      #  usage.save()

    mfile.delete()
    logging.info("MFile Deleted %s " % mfileid)