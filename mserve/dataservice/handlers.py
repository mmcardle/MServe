import os.path
from piston.handler import BaseHandler
from piston.utils import rc
from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataServiceAuth
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import Usage
from dataservice.models import AggregateUsageRate
from dataservice.models import NamedBase
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import ManagementProperty
from dataservice.models import UsageReport
from dataservice.models import ContainerResourcesReport
from dataservice.models import ServiceResourcesReport
from dataservice.forms import HostingContainerForm
from dataservice.forms import DataServiceForm
from dataservice.forms import DataServiceURLForm
from dataservice.forms import DataStagerForm
from dataservice.forms import UpdateDataStagerForm
from dataservice.forms import UpdateDataStagerFormURL
from dataservice.forms import DataStagerURLForm
from dataservice.forms import DataStagerAuthForm
from dataservice.forms import SubAuthForm
from dataservice.forms import ManagementPropertyForm
from dataservice import views
from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404

import utils as utils
import usage_store as usage_store

import time
import pickle
import base64
import logging
import magic
import hashlib
import os

base            = "/home/"
container_base  = "/container/"
service_base    = "/service/"
stager_base     = "/stager/"
auth_base       = "/auth/"

sleeptime = 10

def gen_sec_link_orig(rel_path,prefix):
      import time, hashlib
      if not rel_path.startswith("/"):
        rel_path = "%s%s" % ("/", rel_path)
      secret = 'ugeaptuk6'
      uri_prefix = '/%s/' % prefix
      hextime = "%08x" % time.time()
      token = hashlib.md5(secret + rel_path + hextime).hexdigest()
      return '%s%s/%s%s' % (uri_prefix, token, hextime, rel_path)

def create_container(request,name):
    hostingcontainer = HostingContainer(name=name)
    hostingcontainer.save()
    hostingcontainerauth = HostingContainerAuth(hostingcontainer=hostingcontainer,authname="owner")
    methods = ["makeServiceInstance","getServiceMetadata","getDependencies","getProvides","setResourceLookup","getUsageSummary"]
    hostingcontainerauth.description = "Full access to the container"
    hostingcontainerauth.setmethods(methods)
    hostingcontainerauth.save()

    usage_store.startrecording(hostingcontainer.id,usage_store.metric_container,1)

    reportusage(hostingcontainer)

    return hostingcontainer

def delete_container(request,containerid):
    usage_store.stoprecording(containerid,usage_store.metric_container)
    container = HostingContainer.objects.get(id=containerid)
    logging.info("Deleteing service %s %s" % (container.name,containerid))

    usages = Usage.objects.filter(base=container)
    for usage in usages:
        usage.base = None
        usage.save()

    reportusage(container)

    container.delete()
    logging.info("Container Deleted %s " % containerid)

def create_data_service(request,containerid,name):
    container = HostingContainer.objects.get(id=containerid)
    dataservice = DataService(name=name,container=container)
    dataservice.save()

    usage_store.startrecording(dataservice.id,usage_store.metric_service,1)

    reportusage(dataservice)
    
    return dataservice

def delete_service(request,serviceid):
    usage_store.stoprecording(serviceid,usage_store.metric_service)
    service = DataService.objects.get(id=serviceid)
    logging.info("Deleteing service %s %s" % (service.name,serviceid))

    usages = Usage.objects.filter(base=service)
    for usage in usages:
        usage.base = service.container
        usage.save()

    reportusage(service)

    service.delete()
    logging.info("Service Deleted %s " % serviceid)

def create_data_stager(request,serviceid,file):
    service = DataService.objects.get(id=serviceid)
    if file==None:
        datastager = DataStager(name="Empty File",service=service)
    else:
        datastager = DataStager(name=file.name,service=service,file=file)
    datastager.save()

    if datastager.file:
        # MIME type
        m = magic.open(magic.MAGIC_MIME)
        m.load()
        mimetype = m.file(datastager.file.path)
        datastager.mimetype = mimetype
        # checksum
        datastager.checksum = utils.md5_for_file(datastager.file)
        # save it
        datastager.save()

    datastagerauth_owner = DataStagerAuth(stager=datastager,authname="owner")
    methods_owner = ["get", "put", "post", "delete"]
    datastagerauth_owner.setmethods(methods_owner)
    datastagerauth_owner.description = "Owner of the data"
    datastagerauth_owner.save()

    datastagerauth_monitor = DataStagerAuth(stager=datastager,authname="monitor")
    methods_monitor = ["getUsageSummary"]
    datastagerauth_monitor.setmethods(methods_monitor)
    datastagerauth_monitor.description = "Collect usage reports"
    datastagerauth_monitor.save()

    usage_store.startrecording(datastager.id,usage_store.metric_stager,1)
    
    reportusage(datastager)

    if file is not None:
        usage_store.startrecording(datastager.id,usage_store.metric_disc,file.size)

    return datastager

def delete_stager(request,stagerid):
    usage_store.stoprecording(stagerid,usage_store.metric_stager)
    usage_store.stoprecording(stagerid,usage_store.metric_disc)
    stager = DataStager.objects.get(id=stagerid)
    logging.info("Deleteing stager %s %s" % (stager.name,stagerid))

    usages = Usage.objects.filter(base=stager)
    logging.info("Deleteing stager usage")
    for usage in usages:
        logging.info("Saving Usage %s " % usage)
        usage.base = stager.service
        usage.save()

    reportusage(stager)

    stager.delete()
    logging.info("Stager Deleted %s " % stagerid)

def is_container(base):
    return hasattr(base,"hostingcontainer")

def is_service(base):
    return hasattr(base,"dataservice")

def is_stager(base):
    return hasattr(base,"datastager")

def reportusage(base):
    logging.info("Report usage %s" % base)
    toreport = []

    if is_container(base):

        toreport =  [base]

    if is_service(base):
        container = HostingContainer.objects.get(dataservice=base)
        container_report,created = ContainerResourcesReport.objects.get_or_create(base=container)
        container_report.reportnum = container_report.reportnum+1
        container_report.save()

        toreport =  [container,base]

    if is_stager(base):
        service   = DataService.objects.get(datastager=base)
        container = HostingContainer.objects.get(dataservice=service)

        service_report,created = ServiceResourcesReport.objects.get_or_create(base=service)
        service_report.reportnum = service_report.reportnum+1
        service_report.save()

        toreport =  [container,service,base]

    for ob in toreport:
        logging.info("Reporting usage for %s "%ob)
        reports = UsageReport.objects.filter(base=ob)
        for r in reports:
            logging.info("\tReport %s "%r)
            r.reportnum = r.reportnum + 1
            r.save()


class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST','DELETE')
    model = HostingContainer
    fields = ('name', 'id' )
    exclude = ('pk')

    def delete(self, request, containerid):
        logging.info("Deleting Container %s " % containerid)
        delete_container(request,containerid)

    def read(self, request, containerid):
        container = HostingContainer.objects.get(id=containerid)
        if request.META["HTTP_ACCEPT"] == "application/json":
            return container
        return views.render_container(request,containerid)

    def create(self, request):
        reqjson = (request.META["HTTP_ACCEPT"] == "application/json")
        form = HostingContainerForm(request.POST)
        if form.is_valid():

            name = form.cleaned_data['name']
            hostingcontainer = create_container(request,name)

            if reqjson:
                return hostingcontainer

            return redirect('/container/'+str(hostingcontainer.id))
        else:
            return views.home(request,form=form)
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            if request.META.has_key("HTTP_REFERER"):
                return HttpResponseRedirect(request.META["HTTP_REFERER"])
            else:
                r = rc.BAD_REQUEST
                logging.info(form)
                return r

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST','DELETE')
    model = DataService
    fields = ('name', 'id' )
    exclude = ('pk')

    def delete(self, request, serviceid):
        logging.info("Deleting Service %s " % serviceid)
        delete_service(request,serviceid)
    
    def read(self, request, serviceid):
        service = DataService.objects.get(id=serviceid)
        if request.META["HTTP_ACCEPT"] == "application/json":
           return service
        return views.render_service(request,service.id)

    def create(self, request):
        reqjson = (request.META["HTTP_ACCEPT"] == "application/json")
        form = DataServiceForm(request.POST) 
        if form.is_valid(): 
            
            containerid = form.cleaned_data['cid']
            name = form.cleaned_data['name']
            dataservice = create_data_service(request,containerid,name)

            if reqjson:
                return dataservice

            return redirect('/service/'+str(dataservice.id))
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            containerid = form.data['cid']
            return views.render_container(request,containerid,form=form)

class DataServiceURLHandler(BaseHandler):

    def create(self, request, containerid):

        form = DataServiceURLForm(request.POST)
        logging.info("Request data = %s" % form)
        if form.is_valid(): 
            logging.info("Form valid = %s" % form)
            name = form.cleaned_data['name']
            dataservice = create_data_service(request,containerid,name)

            if request.META["HTTP_ACCEPT"] == "application/json":
                logging.info("Returning JSON = " % dataservice)
                return dataservice

            logging.info("Returning Redirect = %s" % dataservice)
            return redirect('/service/'+str(dataservice.id))
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            return HttpResponseRedirect(request.META["HTTP_REFERER"])


class DataStagerHandler(BaseHandler):
    allowed_methods = ('GET','POST','PUT','DELETE')
    model = DataStager
    fields = ('name', 'id', 'file')
    exclude = ('pk')

    def delete(self, request, stagerid):
        logging.info("Deleting Stager %s " % stagerid)
        delete_stager(request,stagerid)

    def read(self, request, stagerid):
        stager = DataStager.objects.get(pk=stagerid)
        base = NamedBase.objects.get(pk=stagerid)

        if request.META["HTTP_ACCEPT"] == "application/json":
            return stager
        return views.render_stager(request,stager.id,show=True)

    def update(self, request):
        form = UpdateDataStagerForm(request.POST,request.FILES) 
        if form.is_valid(): 
            
            file = request.FILES['file']
            stagerid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            datastager = DataStager.objects.get(pk=stagerid)
            datastager.file = file
            usage_store.startrecording(stagerid,usage_store.metric_disc,file.size)

            datastager.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])
        
    def render_subauth(self, stager, auth, show=False):
        sub_auths = JoinAuth.objects.filter(parent=auth.id)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        form = SubAuthForm()
        form.fields['id_parent'].initial = auth.id
        dict = {}
        dict["stager"] = stager
        if stager.file == '' or stager.file == None:
            dict["altfile"] = "/mservemedia/images/empty.png"
        if not show:
            stager.file = None
            dict["altfile"] = "/mservemedia/images/forbidden.png"
    
        dict["form"] = form
        dict["auths"] = subauths
        dict["formtarget"] = "/auth/"
        return render_to_response('stager.html', dict)

    def create(self, request):
        reqjson=(request.META["HTTP_ACCEPT"] == "application/json")
        form = DataStagerForm(request.POST,request.FILES) 
        if form.is_valid(): 
            
            if request.FILES.has_key('file'):
                file = request.FILES['file']
            else:
                file = None
            serviceid = form.cleaned_data['sid']
            #service = DataService.objects.get(id=serviceid)
            datastager = create_data_stager(request, serviceid, file)

            if reqjson:
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
        else:
            if reqjson:
                r = rc.BAD_REQUEST
                resp.write("Invalid Request!")
                return r
            return views.render_stager(request,stager.id)

class DataStagerContentsHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, stagerid):
        datastager = DataStager.objects.get(pk=stagerid)
        service = datastager.service
        container = service.container
        logging.info("Finding limit for %s " % (datastager.name))
        downloadspeed = 50
        try:
            prop = ManagementProperty.objects.get(base=service,property="speed")
            downloadspeed = prop.value
            logging.info("Limit set from service property to %s for %s " % (downloadspeed,datastager.name))
        except ObjectDoesNotExist:
            try:
                prop = ManagementProperty.objects.get(base=container,property="speed")
                downloadspeed = prop.value
                logging.info("Limit set from container property to %s for %s " % (downloadspeed,datastager.name))
            except ObjectDoesNotExist:
                pass

        dlfoldername = "dl%s"%downloadspeed

        p = str(datastager.file)

        redirecturl = gen_sec_link_orig(p,dlfoldername)
        redirecturl = redirecturl[1:]

        SECDOWNLOAD_ROOT = settings.SECDOWNLOAD_ROOT

        fullfilepath = os.path.join(SECDOWNLOAD_ROOT,dlfoldername,p)
        fullfilepathfolder = os.path.dirname(fullfilepath)
        datastagerfilepath = datastager.file.path

        logging.info("Redirect URL      = %s " % redirecturl)
        logging.info("fullfilepath      = %s " % fullfilepath)
        logging.info("fullfilefolder    = %s " % fullfilepathfolder)
        logging.info("datastagerfp      = %s " % datastagerfilepath)
        logging.info("datastagerf       = %s " % datastager.file)

        if not os.path.exists(fullfilepathfolder):
            os.makedirs(fullfilepathfolder)

        if not os.path.exists(fullfilepath):
            os.link(datastagerfilepath,fullfilepath)

        return redirect("/%s"%redirecturl)


class DataStagerURLHandler(BaseHandler):
    
    def update(self, request, stagerid):
        form = UpdateDataStagerFormURL(request.POST,request.FILES) 
        if form.is_valid(): 
            
            file = request.FILES['file']
            datastager = DataStager.objects.get(pk=stagerid)
            datastager.file = file
            datastager.name = file.name
            datastager.save()

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id)+"/")
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def create(self, request, serviceid):
        form = DataStagerURLForm(request.POST,request.FILES) 
        if form.is_valid(): 
            
            file = request.FILES['file']
            #service = DataService.objects.get(id=serviceid)
            datastager = create_data_stager(request, serviceid, file)

            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastager

            return redirect('/stager/'+str(datastager.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class ManagedResourcesContainerHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ContainerResourcesReport
    fields = ('services','base','reportnum')
    exclude = ('pk')
    
    def read(self, request, containerid, last_known):

        last = int(last_known)
        container = HostingContainer.objects.get(id=containerid)

        report,created = ContainerResourcesReport.objects.get_or_create(base=container)

        if last is not -1:
            while last == report.reportnum:
                logging.info("Waiting for new services lastreport=%s" % (last))
                time.sleep(sleeptime)
                report = ContainerResourcesReport.objects.get(base=container)

        services = DataService.objects.filter(container=container)
        report.services = services
        report.save()
        return report

class ManagedResourcesServiceHandler(BaseHandler):
    allowed_methods = ('GET')
    model = ServiceResourcesReport
    fields = ('stagers','meta','base','reportnum')


    def read(self, request, serviceid, last_known):

        last = int(last_known)
        service = DataService.objects.get(id=serviceid)

        report,created = ServiceResourcesReport.objects.get_or_create(base=service)

        if last is not -1:
            while last == report.reportnum:
                logging.info("Waiting for new stagers lastreport=%s" % (last))
                time.sleep(sleeptime)
                report = ServiceResourcesReport.objects.get(base=service)
        
        stagers = DataStager.objects.filter(service=service)
        report.stagers = stagers
        report.save()
        return report

class AggregateUsageRateHandler(BaseHandler):
    model =  AggregateUsageRate
    exclude =('pk','base','id')

class RoleInfoHandler(BaseHandler):
    allowed_methods = ('GET')
    model =  HostingContainerAuth
    #fields = ('methods')
    #exclude =('methods_encoded','description')

    def read(self,request, baseid):
        base = NamedBase.objects.get(pk=baseid)
        if is_container(base):
            containerauths = HostingContainerAuth.objects.filter(hostingcontainer=base)
            dict = {}
            arr = []
            for containerauth in containerauths:
                ad = {}
                ad["methods"]= containerauth.methods()
                ad["description"] = containerauth.description
                ad["name"] = containerauth.authname
                arr.append(ad)
            dict["roleinfo"] = arr
            return dict
        if is_service(base):
            serviceauths = DataServiceAuth.objects.filter(dataservice=base)
            dict = {}
            arr = []
            for serviceauth in serviceauths:
                ad = {}
                ad["methods"]= serviceauth.methods()
                ad["description"] = serviceauth.description
                ad["name"] = serviceauth.authname
                arr.append(ad)
            dict["roleinfo"] = arr
            return dict
        if is_stager(base):
            stagerauths = DataStagerAuth.objects.filter(stager=base)
            dict = {}
            arr = []
            for stagerauth in stagerauths:
                ad = {}
                ad["methods"]= stagerauth.methods()
                ad["description"] = stagerauth.description
                ad["name"] = stagerauth.authname
                arr.append(ad)
            dict["roleinfo"] = arr
            return dict
        r = rc.BAD_REQUEST
        resp.write("Invalid Request!")
        return r

class UsageSummaryHandler(BaseHandler):
    allowed_methods = ('GET')
    model = UsageReport
    fields = ('summarys','inprogress','reportnum')

    def read(self,request, baseid, last_report):

        lr = int(last_report)

        base = NamedBase.objects.get(pk=baseid)

        usagereport, created = UsageReport.objects.get_or_create(base=base)

        logging.info("Report = %s" % usagereport)

        if lr != -1:
            while lr == usagereport.reportnum:
                logging.info("Waiting for report=%s lastreport=%s" % (usagereport.reportnum,lr))
                time.sleep(sleeptime)
                usagereport = UsageReport.objects.get(pk=usagereport.pk)

        inprogress= []
        summarys= []
        if is_container(base):
            inprogress = usage_store.container_inprogresssummary(baseid)
            summarys = usage_store.container_usagesummary(baseid)

        if is_service(base):
            inprogress = usage_store.service_inprogresssummary(baseid)
            summarys = usage_store.service_usagesummary(baseid)

        if is_stager(base):
            inprogress = usage_store.stager_inprogresssummary(baseid)
            summarys = usage_store.stager_usagesummary(baseid)

        usagereport.summarys = summarys

        for summary in summarys:
            summary.save()

        for ip in inprogress:
            ip.save()

        usagereport.inprogress = inprogress
        usagereport.save()

        return usagereport


class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self,request, baseid):
        container = HostingContainer.objects.get(id=baseid)
        properties = ManagementProperty.objects.filter(base=container)
        properties_json = []
        for prop in properties:
            properties_json.append(prop)
        return properties_json

    def create(self, request, baseid):
        form = ManagementPropertyForm(request.POST) 
        if form.is_valid(): 
            
            property = form.cleaned_data['property']

            base = NamedBase.objects.get(pk=baseid)

            try:
                existingmanagementproperty = ManagementProperty.objects.get(property=property,base=base)
                if existingmanagementproperty is not None:
                    return HttpResponseBadRequest("That Property allready exists")
            except ObjectDoesNotExist:
                pass

            property = form.cleaned_data['property']
            value    = form.cleaned_data['value']
            managementproperty = ManagementProperty(property=property,value=value,base=base)
            managementproperty.save()
            
            redirecturl = ""
            if is_container(base):
                redirecturl = "container"
            if is_service(base):
                redirecturl = "service"
            if is_stager(base):
                redirecturl = "stager"
            return redirect('/%s/%s' % (redirecturl,baseid) )
        else:
            logging.info("Bad Form %s " % form)
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class DataStagerAuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStagerAuth

    def read(self, request, stagerauthid):

        sub_auths = JoinAuth.objects.filter(parent=stagerauthid)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        try:
            datastager_auth = DataStagerAuth.objects.get(id=stagerauthid)

            form = SubAuthForm()
            form.fields['parent'].initial = stagerauthid
            dict = {}
            dict["auth"] = datastager_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("DataStagerAuth  doesn't exist.")

        try:
            container_auth = HostingContainerAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = container_auth

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("HostingContainer Auth doesn't exist.")

        try:
            dataservice_auths = DataServiceAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = dataservice_auths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("HostingContainer Auth doesn't exist.")

        try:
            sub_auth = SubAuth.objects.get(id=id)
            form = SubAuthForm()
            dict = {}
            dict["auth"] = sub_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            logging.info("Sub Auth doesn't exist.")

        dict = {}
        dict["error"] = "That Authority does not exist"
        return render_to_response('error.html', dict)
    
    def create(self, request):
        form = DataStagerAuthForm(request.POST) 
        if form.is_valid(): 
            authname = form.cleaned_data['authname']
            methods_csv = form.cleaned_data['methods_csv']
            description= form.cleaned_data['description']
            stagerid = form.cleaned_data['dsid']
            stager = DataStager.objects.get(pk=stagerid)
            methodslist = methods_csv.split(',')

            methods_encoded = base64.b64encode(pickle.dumps(methodslist))

            datastagerauth = DataStagerAuth(stager=stager,authname=authname,methods_encoded=methods_encoded,description=description)
            datastagerauth.save()
            
            if request.META["HTTP_ACCEPT"] == "application/json":
                return datastagerauth

            return redirect('/auth/'+str(datastagerauth.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class AuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = SubAuth

    def create(self, request):
        form = SubAuthForm(request.POST) 
        if form.is_valid(): 
            
            authname = form.cleaned_data['authname']
            methods_csv = form.cleaned_data['methods_csv']
            description= form.cleaned_data['description']
            parent = form.cleaned_data['id_parent']
            methodslist = methods_csv.split(',')

            subauth = SubAuth(authname=authname,description=description)
            subauth.setmethods(methodslist)
            subauth.save()
            child = str(subauth.id)
            join = JoinAuth(parent=parent,child=child)
            join.save()

            return redirect('/auth/'+str(subauth.id))
            
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

    def read(self, request, id):

        '''
        Have to add the case where this could be a hosting container or data
        service auth.
        '''
        
        try:
            stagerauth = DataStagerAuth.objects.get(id=id)
            methods = stagerauth.methods()
            
            if 'get' in methods:
                return views.render_subauth(request,stagerauth.stager, stagerauth, show=True)
            else:
                return views.render_subauth(request,stagerauth.stager, stagerauth, show=False)
        except ObjectDoesNotExist:
            pass

        dsAuth = None
        datastagerauth = None
        subauth = None
        parent = id
        done = False
        methods_intersection = None
        all_methods = set()

        logging.info("Trying %s" % (parent))

        while not done:
            try:
                joins = JoinAuth.objects.get(child=parent)
                parent = joins.parent

                try:
                    subauth = SubAuth.objects.get(id=parent)
                    logging.info("%s a SubAuth" % (parent))
                    logging.info("%s has Methods %s" % (parent,subauth.methods()))
                    if methods_intersection is None:
                        methods_intersection = set(subauth.methods())
                    methods_intersection = methods_intersection & set(subauth.methods())
                    all_methods = all_methods | set(subauth.methods())
                except ObjectDoesNotExist:
                    pass
                try:
                    datastagerauth = DataStagerAuth.objects.get(id=parent)
                    logging.info("%s a DataStagerAuth" % (parent))
                    logging.info("%s has Methods %s" % (parent,datastagerauth.methods()))
                    dsAuth = datastagerauth
                    if methods_intersection is None:
                        methods_intersection = set(datastagerauth.methods())
                    methods_intersection = methods_intersection & set(datastagerauth.methods())
                    all_methods = all_methods | set(datastagerauth.methods())
                    done = True
                    pass
                except ObjectDoesNotExist:
                    pass

            except ObjectDoesNotExist:
                parent = None
                done = True
                
        if dsAuth is None:
            return HttpResponseBadRequest("Bad Request %s " % (id))

        auth = SubAuth.objects.get(id=id)
        methods = auth.methods()

        if 'get' in methods:
            return views.render_subauth(dsAuth.stager, auth, show=True)
        else:
            return views.render_subauth(dsAuth.stager, auth, show=False)

        if "get" in methods_intersection:
            return HttpResponseRedirect("/files"+dsAuth.stager.file.url)
        else:
            return HttpResponseForbidden("<html>Forbidden</html>")

