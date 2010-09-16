from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from piston.handler import BaseHandler
from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.forms import HostingContainerForm
from dataservice.forms import DataServiceForm
from dataservice.forms import DataStagerForm
from dataservice.forms import DataStagerAuthForm
from dataservice.forms import SubAuthForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

import pickle
import base64
import logging

base           = "/m/home/"
container_base = "/m/container/"
service_base   = "/m/service/"
stager_base   = "/m/stager/"
auth_base   = "/m/auth/"

class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    model = HostingContainer

    def create(self, request):
        form = HostingContainerForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            hostingcontainer = HostingContainer(name=name)
            hostingcontainer.save()
            hostingcontainerauth = HostingContainerAuth(hostingcontainer=hostingcontainer,authname="owner")
            methods = ["makeServiceInstance","getServiceMetadata","getDependencies","getProvides","setResourceLookup","getUsageSummary"]
            hostingcontainerauth.description = "Full access to the container"
            hostingcontainerauth.setmethods(methods)
            hostingcontainerauth.save()
            return HttpResponseRedirect(base)
        else:
            return HttpResponse("<html>"+str(form)+"</html>")

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataService

    def create(self, request, containerid):
        form = DataServiceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            #containerid = form.cleaned_data['container'].id
            container = HostingContainer.objects.get(id=containerid)
            dataservice = DataService(name=name,container=container)
            dataservice.save()
            return HttpResponseRedirect(container_base+containerid+"/")
        else:
            return HttpResponse(form)

class DataStagerHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStager

    def create(self, request, serviceid):
        form = DataStagerForm(request.POST,request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            file = request.FILES['file']
            service = DataService.objects.get(id=serviceid)
            datastager = DataStager(name=file.name,service=service,file=file)
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

            return HttpResponseRedirect(service_base+serviceid+"/")
        else:
            return HttpResponse("<html>"+str(form)+"</html>")

class DataStagerAuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStagerAuth
    
    def create(self, request, id):
        form = DataStagerAuthForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            stagerid = id
            authname = form.cleaned_data['authname']
            methods_csv = form.cleaned_data['methods_csv']
            description= form.cleaned_data['description']
            methodslist = methods_csv.split(',')

            methods_encoded = base64.b64encode(pickle.dumps(methodslist))

            stager = DataStager.objects.get(id=stagerid)
            datastagerauth = DataStagerAuth(stager=stager,authname=authname,methods_encoded=methods_encoded,description=description)
            datastagerauth.save()
            return HttpResponseRedirect(stager_base+id+"/")
        else:
            return HttpResponse("<html>"+str(form)+"</html>")

class SubAuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = SubAuth

    def create(self, request, auth):
        form = SubAuthForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            authname = form.cleaned_data['authname']
            methods_csv = form.cleaned_data['methods_csv']
            description= form.cleaned_data['description']
            methodslist = methods_csv.split(',')

            subauth = SubAuth(authname=authname,description=description)
            subauth.setmethods(methodslist)
            subauth.save()

            parent = str(auth)
            child = str(subauth.id)

            join = JoinAuth(parent=parent,child=child)
            join.save()

            return HttpResponseRedirect(auth_base+str(auth)+"/")
        else:
            return HttpResponse("<html>"+str(form)+"</html>")


class AuthHandler(BaseHandler):
    allowed_methods = ('GET')
    model = SubAuth

    def read(self, request, id):

        try:
            stagerauth = DataStagerAuth.objects.get(id=id)
            logging.info("%s a DataStagerAuth" % (id))
            methods = stagerauth.methods()
            if 'get' in methods:
                return HttpResponseRedirect("/m/"+stagerauth.stager.file.url)
            else:
                return HttpResponseForbidden("<html>Forbidden</html>")
        except ObjectDoesNotExist:
            pass

        dsAuth = None
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
            return HttpResponseBadRequest("Bad Request")

        if "get" in methods_intersection:
            return HttpResponseRedirect("/m/"+dsAuth.stager.file.url)
        else:
            return HttpResponseForbidden("<html>Forbidden</html>")

