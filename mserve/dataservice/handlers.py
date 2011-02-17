from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import *
from dataservice.forms import *
from django.conf import settings
from django.http import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseNotFound
import settings as settings

import utils as utils
import api as api
import usage_store as usage_store
import time
import logging
import os
import os.path
import shutil

sleeptime = 10
DEFAULT_ACCESS_SPEED = settings.DEFAULT_ACCESS_SPEED

metric_corruption = "http://mserve/corruption"
metric_dataloss = "http://mserve/dataloss"

class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST','DELETE')
    model = HostingContainer
    fields = ('name', 'id','dataservice_set',"reportnum")
    exclude = ('pk')

    def read(self, request, id=None):
        if id == None and request.user.is_staff:
            return super(HostingContainerHandler, self).read(request)
        else:
            if id == None and not request.user.is_staff:
                r = rc.FORBIDDEN
                return r
            else:
                return HostingContainer.objects.get(id=str(id))

    def delete(self, request, id):
        logging.info("Deleting Container %s " % id)
        api.delete_container(request,id)
        r = rc.DELETED
        return r

    def create(self, request):
        form = HostingContainerForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            hostingcontainer = api.create_container(request,name)
            return hostingcontainer
        else:
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE')
    model = DataService
    #fields = ('name', 'id')
    fields = ('name', 'id','reportnum', 'mfile_set','job_set')
    exclude = ('pk')

    def delete(self, request, id):
        logging.info("Deleting Service %s " % id)
        api.delete_service(request,id)
        r = rc.DELETED
        return r

    def create(self, request):
        form = DataServiceForm(request.POST)

        if form.is_valid(): 
            containerid = form.cleaned_data['cid']
            name = form.cleaned_data['name']
            dataservice = api.create_data_service(request,containerid,name)
            return dataservice
        else:
            logging.info(form)
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r

class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):
        form = DataServiceURLForm(request.POST)
        if form.is_valid(): 
            name = form.cleaned_data['name']
            dataservice = api.create_data_service(request,containerid,name)
            return dataservice
        else:
            r = rc.BAD_REQUEST
            resp.write("Invalid Request!")
            return r


class ThumbHandler(BaseHandler):
    allowed_methods = ('GET','POST')

    def create(self, request):
        logging.info("Thumb Update")
        if request.FILES.has_key('file'):
            file = request.FILES['file']
            logging.info("file %s"%file)
            if request.POST.has_key('mfileid'):
                mfileid = request.POST['mfileid']
                logging.info("mfileid %s"%mfileid)
                mfile = MFile.objects.get(id=mfileid)
                if mfile == None:
                    logging.info("No such mfile %s"%mfileid)
                    r = rc.BAD_REQUEST
                    r.write("Invalid Request!")
                    return r

                try:
                    thumb = mfile.thumb
                    logging.info("Deleting existing thumb for mfile %s"%mfile)
                    mfile.thumb.delete()
                except ObjectDoesNotExist:
                    pass

                logging.info("Updating thumb for mfile %s"%mfile)

                thumb = Thumb(mfile=mfile,file=file)
                thumb.file = file
                thumb.save()
                logging.info("Updated %s"%thumb)

                return thumb
            else:
                r = rc.BAD_REQUEST
                r.write("Invalid Request!")
                return r
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class CorruptionHandler(BaseHandler):
    allowed_methods = ('PUT')

    def update(self, request, mfileid, backup=False):
        mfile = MFile.objects.get(pk=mfileid)
        if not backup:
            mfile = MFile.objects.get(pk=mfileid)
            logging.info("Attempting to corrupt file '%s' " % (mfile))
            f = open(mfile.file.path,'wb')
            f.writelines(["corruption"])
        else:
            logging.info("Attempting to corrupt backup file for file'%s'" % (mfile))
            backup = BackupFile.objects.get(mfile=mfile)
            f = open(backup.file.path,'wb')
            f.writelines(["corruption"])
        
        return mfile

class HeadHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')

    def read(self, request, id):
        try:
            auth = Auth.objects.get(id=id)
            parent = auth

            while parent.base == None:
                parent = parent.parent

            base = parent.base
            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=base.id)
                return utils.clean_mfile(mfile)
        except Auth.DoesNotExist:
            # TODO - fix
            logger.error("Auth does not exist")
            return []


class MFileHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = MFile
    fields = ('name', 'id' ,'file', 'checksum', 'size', 'mimetype', 'thumb', 'poster', 'created' , 'updated','thumburl','posterurl','reportnum')

    def delete(self, request, id):
        logging.info("Deleting mfile %s " % id)
        api.delete_mfile(request,id)
        r = rc.DELETED
        return r

    def update(self, request, mfileid=None):
        form = UpdateMFileForm(request.POST,request.FILES)
        if form.is_valid(): 
            
            file = request.FILES['file']
            mfileid = form.cleaned_data['sid']
            logging.info("Update %s" % mfileid)
            #service = DataService.objects.get(id=serviceid)
            mfile = MFile.objects.get(pk=mfileid)
            mfile.file = file
            mfile.name = file.name
            mfile.size = file.size
            
            mfile.save()

            backup = BackupFile(name="backup_%s"%file.name,mfile=mfile,mimetype=mfile.mimetype,checksum=mfile.checksum,file=file)
            backup.save()

            #usage_store.startrecording(mfileid,usage_store.metric_disc,mfile.size)
            #usage_store.startrecording(mfileid,usage_store.metric_archived,mfile.size)

            return mfile

        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

    def create(self, request, serviceid=None):
        logging.debug("Create MFile")
        logging.debug("Create MFile len(request.raw_post_data)=%s "% (len(request.raw_post_data)))

        form = MFileForm(request.POST,request.FILES)
        if form.is_valid():

            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None

            if serviceid == None:
                serviceid = form.cleaned_data['sid']

            mfile = api.create_mfile(request, serviceid, file)
            return mfile
        else:
            r = rc.BAD_REQUEST
            r.write("Invalid Request!")
            return r

class MFileVerifyHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        md5 = utils.md5_for_file(mfile.file)

        dict= {}
        dict["mfile"] = mfile
        dict["md5"] = md5
        
        return dict

class MFileContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, mfileid):
        mfile = MFile.objects.get(pk=mfileid)
        service = mfile.service
        container = service.container
        logging.info("Finding limit for %s " % (mfile.name))
        accessspeed = DEFAULT_ACCESS_SPEED
        try:
            prop = ManagementProperty.objects.get(base=service,property="accessspeed")
            accessspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (accessspeed,mfile.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="accessspeed")
                accessspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (accessspeed,mfile.name))
            except ObjectDoesNotExist:
                pass

        #dlfoldername = "dl%s"%accessspeed
        dlfoldername = "dl"

        check1 = mfile.checksum
        check2 = utils.md5_for_file(mfile.file)

        file=mfile.file

        if(check1==check2):
            logging.info("Verification of %s on read ok" % mfile)
        else:
            logging.info("Verification of %s on read FAILED" % mfile)
            usage_store.record(mfile.id,metric_corruption,1)
            backup = BackupFile.objects.get(mfile=mfile)
            check3 = mfile.checksum
            check4 = utils.md5_for_file(backup.file)
            if(check3==check4):
                shutil.copy(backup.file.path, mfile.file.path)
                file = backup.file
            else:
                logging.info("The file %s has been lost" % mfile)
                usage_store.record(mfile.id,metric_dataloss,mfile.size)
                return rc.NOT_HERE

        p = str(file)

        redirecturl = utils.gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        mfilefilepath = file.path

        logging.info("Redirect URL      = %s " % redirecturl)
        logging.info("fullfilepath      = %s " % fullfilepath)
        logging.info("fullfilefolder    = %s " % fullfilepathfolder)
        logging.info("mfilefp      = %s " % mfilefilepath)
        logging.info("mfilef       = %s " % file)

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            os.link(mfilefilepath,fullfilepath)

        import dataservice.models as models
        usage_store.record(mfile.id,models.metric_access,mfile.size)

        return redirect("/%s"%redirecturl)
    
class RoleHandler(BaseHandler):
    allowed_methods = ('GET','PUT')
    model = Role
    fields = ('id','rolename','description','methods')

    def update(self,request,roleid):
        import logging
        logging.info("updating role")

        role = Role.objects.get(id=roleid)
        newmethods = request.POST["methods"].split(',')

        logging.info("updating role with methods %s " % newmethods)
        logging.info("auth %s " % role.auth)
        logging.info("dir %s " % dir(role.auth))

        for a in role.auth.all():
            logging.info(a)
            logging.info(dir(a))

        allowed_methods = api.all_container_methods + api.all_service_methods + api.all_mfile_methods

        # TODO: Should we check each type of authority this role could be under?
        #if hasattr(role.auth,"hostingcontainerauth"):
        #    allowed_methods = all_container_methods

        #if hasattr(role.auth,"dataserviceauth"):
        #    allowed_methods = all_service_methods

        #if hasattr(role.auth,"MFileauth"):
        #    allowed_methods = all_mfile_methods

        if not set(newmethods).issubset(set(allowed_methods)):
            return HttpResponseBadRequest("The methods '%s' are not allowed. Allowed Methods '%s' " % (newmethods, allowed_methods))

        existingmethods = role.methods()

        if set(newmethods).issubset(set(existingmethods)):
            return HttpResponseBadRequest("The methods '%s' are already contained in this role . Existing Methods '%s' " % (newmethods, existingmethods))

        role.addmethods(newmethods)
        role.save()
        return role

class AccessControlHandler(BaseHandler):
    allowed_methods = ('GET','PUT','POST')
    #fields = ('id','authname',('roles', ('description') ), )
    #fields = ('id','authname' )
    #model = Auth

    def create(self, request, method, pk):
        

        if not method in generic_post_methods:
            return HttpResponseBadRequest("Cannot do 'PUT' %s on %s" % (method,pk))

        if method == "getorcreateauth" or method == "addauth":
            name = request.POST["name"]
            roles_string = request.POST["roles"]
            roleids = roles_string.split(",")
            base = NamedBase.objects.get(pk=pk)

            if utils.is_container(base):
                hc = HostingContainer.objects.get(pk=pk)
                hca,created = Auth.objects.get_or_create(hostingcontainer=hc,authname=name)
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return hca
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                hca.save()
                hca.roles = roles
                return hca

            if utils.is_service(base):
                ser = DataService.objects.get(pk=pk)
                dsa,created  = Auth.objects.get_or_create(dataservice=ser,authname=name)
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return dsa
                roles = []
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                dsa.save()
                dsa.roles = roles
                return dsa

            if utils.is_mfile(base):
                mfile = MFile.objects.get(pk=pk)
                dsa,created  = Auth.objects.get_or_create(base=mfile.id,authname=name)
                logging.info("%s %s " % (created,method))
                if not created and method == "addauth":
                    return rc.DUPLICATE_ENTRY
                if not created:
                    return dsa
                roles = []
                roles = []
                for roleid in roleids:
                    role = Role.objects.get(pk=roleid)
                    roles.append(role)

                dsa.save()
                dsa.roles = roles
                return dsa

        return HttpResponse("called %s on %s" % (method,pk))

    def update(self, request, method, pk):

        logging.info("update %s %s" % (method,pk))

        if not method in api.generic_put_methods:
            return HttpResponseBadRequest("Cannot do 'PUT' %s on %s" % (method,pk))

        if method == "setroles":
            roles_string = request.POST["roles"]
            roleids = roles_string.split(",")

            logging.info("auth pk = %s " % (pk))
            auth = Auth.objects.get(pk=pk)

            for roleid in roleids:
                role = Role.objects.get(id=roleid)
                auth.roles.add(role)

            auth.save()

            return HttpResponse("called %s on %s roles=%s" % (method,pk,",".join(roleids)))

            if utils.is_containerauth(auth):
                if roles in api.all_container_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_mfileauth(auth):
                if roles in api.all_service_methods:
                    role.setmethods(roles)
                    role.save()
            if utils.is_mfileauth(auth):
                if roles in api.all_mfile_methods:
                    role.setmethods(roles)
                    role.save()

            return HttpResponse("called %s on %s name=%s roles=%s" % (method,pk,name,",".join(roles)))

        return HttpResponse("called %s on %s" % (method,pk))

    def read(self,request, method, pk):

        if not method in api.generic_get_methods:
            return HttpResponseBadRequest("Cannot do 'GET' %s on %s" % (method,pk))
        
        if method == "getauths":
            try:
                base = NamedBase.objects.get(pk=pk)

                if utils.is_container(base):
                    return Auth.objects.filter(hostingcontainer=base)

                if utils.is_service(base):
                    return Auth.objects.filter(dataservice=base)

                if utils.is_mfile(base):
                    return Auth.objects.filter(base=base)
            except ObjectDoesNotExist:
                pass

            auth = Auth.objects.get(pk=pk)
            if utils.is_containerauth(auth) \
                or utils.is_serviceauth(auth) \
                    or utils.is_mfileauth(auth):
                        joins = JoinAuth.objects.filter(parent=auth.id)
                        return SubAuth.objects.filter(pk=joins)

            return HttpResponseBadRequest("Called %s on %s" % (method,pk))

        if method == "getroles":
            try:
                auth = Auth.objects.get(pk=pk)
                dict = {}
                roles = Role.objects.filter(auth=auth)
                for role in roles:
                    dict[role.rolename] = True

                return dict
            except ObjectDoesNotExist:
                return HttpResponseBadRequest("No Such Auth %s" % (pk))

        return HttpResponse("called %s on %s" % (method,pk))

class RoleInfoHandler(BaseHandler):
    def read(self,request, id):
        base = NamedBase.objects.get(pk=id)
        if utils.is_container(base):
            containerauths = Auth.objects.filter(base=base.id)
            roles = []
            for containerauth in containerauths:
                roledict = []
                for role in containerauth.roles.all():
                    roles.append(role)
                roledict.append(roles)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        if utils.is_service(base):
            serviceauths = Auth.objects.filter(base=base.id)
            roles = []
            for serviceauth in serviceauths:
                for role in serviceauth.roles.all():
                    roles.append(role)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        if utils.is_mfile(base):
            mfileauths = Auth.objects.filter(base=base.id)
            roles = []
            for mfileauth in mfileauths:
                for a in mfileauth.roles.all():
                    roles.append(a)

            dict = {}
            dict["roles"] = set(roles)
            return dict

        r = rc.BAD_REQUEST
        r.write("Invalid Request!")
        return r

class UsageHandler(BaseHandler):
    allowed_methods = ('GET')
    model = Usage
    fields = ('squares','total','nInProgress','metric','rate','reports','time,','rateCumulative','total','rateTime')

    def read(self,request, id):
        return usage_store.get_usage(id)

class UsageSummaryHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self,request, id, last_report=-1):
        last = int(last_report)
        try:
            base = NamedBase.objects.get(pk=id)
        except NamedBase.DoesNotExist:
            auth = Auth.objects.get(pk=id)
            base = auth.base

        if last is not -1:
            while last == base.reportnum:
                logging.debug("Waiting for new usage lastreport=%s" % last)
                time.sleep(sleeptime)
                base = NamedBase.objects.get(id=id)

        usages = usage_store.get_usage_summary(id)

        result = {}
        result["usages"] = usages
        result["reportnum"] = base.reportnum

        return result

class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'PUT', 'POST')
    fields = ("value","property","id")

    def read(self,request, id):
        base = NamedBase.objects.get(id=id)
        properties = ManagementProperty.objects.filter(base=base)
        properties_json = []
        for prop in properties:
            properties_json.append(prop)
        return properties_json

    def create(self, request, id):
        resp = rc.BAD_REQUEST
        #resp.write("Not Allowed")
        return resp

    def update(self, request, id):
        form = ManagementPropertyForm(request.POST) 
        if form.is_valid(): 

            property = form.cleaned_data['property']

            base = NamedBase.objects.get(id=id)

            try:
                existingmanagementproperty = ManagementProperty.objects.get(property=property,base=base)
                value    = form.cleaned_data['value']
                existingmanagementproperty.value = value
                existingmanagementproperty.save()
                logging.warn("### Management Property '%s' on '%s' set to '%s' ###"%(property,base,value))
                return existingmanagementproperty
            except ObjectDoesNotExist:
                resp = rc.BAD_REQUEST
                resp.write(" The Management Property '%s' doesn't exist " % (property))
                return resp

        else:
            logging.info("Bad Form %s " % form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        
class AuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = Auth
    fields = ('authname','id','auth_set',('roles' ,('id','rolename','description','methods') ) )


    def read(self, request, id):
        try:
            auth = Auth.objects.get(id=id)
            return auth
        except Auth.DoesNotExist:
            pass

        try:
            base = NamedBase.objects.get(id=id)
            return base.auth_set.all()
        except NamedBase.DoesNotExist:
            logging.debug("NamedBase does not exist")



        return HttpResponseNotFound("Auth not found")


    def create(self, request, id):

        methods_string = request.POST['methods']
        methods = methods_string.split(",")

        try:
            base = NamedBase.objects.get(id=id)

            

        except NamedBase.DoesNotExist:
            logging.debug("NamedBase does not exist")

        try:
            auth = Auth.objects.get(id=id)

            subauth = Auth(parent=auth,authname="New Auth")
            subauth.save()

            role = Role(rolename="newrole")
            role.setmethods(methods)
            role.description = "New Role"
            role.save()

            subauth.roles.add(role)

            logging.debug("create subauth %s for %s with methods %s " % (subauth,auth,methods) )

            return subauth
        except Auth.DoesNotExist:
            logging.debug("Auth does not exist")

        return []
        

class ResourcesHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, id, last_known=-1):

        last = int(last_known)
        try:
            base = NamedBase.objects.get(pk=id)

            if last is not -1:
                while last == base.reportnum:
                    logging.debug("Waiting for new services lastreport=%s" % (last))
                    time.sleep(sleeptime)
                    base = NamedBase.objects.get(id=id)

            if utils.is_container(base):
                container = HostingContainer.objects.get(id=id)
                return container

            if utils.is_service(base):
                service = DataService.objects.get(id=id)
                return service

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=id)
                return mfile
        except NamedBase.DoesNotExist:
            pass

        try:
            auth = Auth.objects.get(pk=id)
            base = auth.base

            if last is not -1:
                while last == base.reportnum:
                    logging.debug("Waiting for new services lastreport=%s" % (last))
                    time.sleep(sleeptime)
                    base = NamedBase.objects.get(id=base.id)

            if utils.is_container(base):
                container = HostingContainer.objects.get(id=base.id)
                return container

            if utils.is_service(base):
                service = DataService.objects.get(id=base.id)
                logging.info("Returning Mfile %s " % service)
                return service

            if utils.is_mfile(base):
                mfile = MFile.objects.get(id=base.id)

                return mfile

        except Auth.DoesNotExist:
            pass

        r = rc.BAD_REQUEST
        r.write("Unknown Resource")
        return r