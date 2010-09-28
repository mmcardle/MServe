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
from dataservice.models import ManagementProperty
from dataservice.forms import HostingContainerForm
from dataservice.forms import DataServiceForm
from dataservice.forms import DataStagerForm
from dataservice.forms import DataStagerAuthForm
from dataservice.forms import SubAuthForm
from dataservice.forms import ManagementPropertyForm
from dataservice.forms import UploadFileForm
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.core import serializers

import pickle
import base64
import logging

base            = "/home/"
container_base  = "/container/"
service_base    = "/service/"
stager_base     = "/stager/"
auth_base       = "/auth/"

class HostingContainerHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')
    model = HostingContainer
    exclude = ()

    def read(self, request, containerid):
        container = HostingContainer.objects.get(id=containerid)
        if request.META["HTTP_ACCEPT"] == "application/json":
            return container
        return self.render(container)
    
    def render(self, container):
        auths = HostingContainerAuth.objects.filter(hostingcontainer=container.id)
        services = DataService.objects.filter(container=container.id)
        properties = ManagementProperty.objects.filter(container=container.id)
        form = DataServiceForm()
        managementpropertyform = ManagementPropertyForm()
        dict = {}
        dict["container"] = container
        dict["services"] = services
        dict["properties"] = properties
        dict["form"] = form
        dict["managementpropertyform"] = managementpropertyform
        dict["auths"] = auths
        return render_to_response('container.html', dict)

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

            return redirect('/container/'+str(hostingcontainer.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataService
    exclude = ()
    
    def read(self, request, serviceid):
        service = DataService.objects.get(id=serviceid)
        if request.META["HTTP_ACCEPT"] == "application/json":
            return service
        return self.render(service)

    def render(self, service, form=DataStagerForm()):
        stagers = DataStager.objects.filter(service=service)
        form2 = UploadFileForm()
        dict = {}
        dict["service"] = service
        dict["stagers"] = stagers
        dict["form"] = form
        dict["form2"] = form2
        return render_to_response('service.html', dict)

    def create(self, request):
        form = DataServiceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            container = form.cleaned_data['container']
            dataservice = DataService(name=name,container=container)
            dataservice.save()
            return redirect('/service/'+str(dataservice.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class DataStagerHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStager
    exclude = ()
    
    def read(self, request, stagerid):
        stager = DataStager.objects.get(id=stagerid)
        if request.META["HTTP_ACCEPT"] == "application/json":
            return stager
        return self.render(stager)

    def render(self, stager):
        auths = DataStagerAuth.objects.filter(stager=stager)
        form = DataStagerAuthForm()
        dict = {}
        dict["stager"] = stager
        dict["form"] = form
        dict["auths"] = auths
        return render_to_response('stager.html', dict)

    def render_partial(self, stager, auth, show=False):
        sub_auths = JoinAuth.objects.filter(parent=auth.id)
        subauths = []
        for sub in sub_auths:
            subauth = SubAuth.objects.get(id=sub.child)
            subauths.append(subauth)

        form = SubAuthForm()
        dict = {}
        dict["stager"] = stager
        if not show:
            stager.file = "/forbidden.png"
        dict["form"] = form
        dict["auths"] = subauths
        return render_to_response('auth.html', dict)

    def create(self, request):
        form = DataStagerForm(request.POST,request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            file = request.FILES['file']
            service = form.cleaned_data['service']
            #service = DataService.objects.get(id=serviceid)
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

            return redirect('/stager/'+str(datastager.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class ManagedResourcesContainerHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, containerid):

        container = HostingContainer.objects.get(id=containerid)
        services = DataService.objects.filter(container=container)

        response = HttpResponse(mimetype="application/json")

        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(services, ensure_ascii=False ,stream=response)

        return response

class ManagedResourcesServiceHandler(BaseHandler):
    allowed_methods = ('GET')

    def read(self, request, serviceid):
        
        service = DataService.objects.get(id=serviceid)
        stagers = DataStager.objects.filter(service=service)

        response = HttpResponse(mimetype="application/json")

        json_serializer = serializers.get_serializer("json")()
        json_serializer.serialize(stagers, ensure_ascii=False ,stream=response)

        return response


class ManagementPropertyHandler(BaseHandler):
    allowed_methods = ('GET', 'POST')

    def read(self,request, containerid):
        container = HostingContainer.objects.get(id=containerid)
        properties = ManagementProperty.objects.filter(container=container)
        properties_json = []
        for prop in properties:
            properties_json.append(prop)
        return properties_json

    def create(self, request, containerid):
        form = ManagementPropertyForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            property = form.cleaned_data['property']
            container = HostingContainer.objects.get(id=containerid)
            try:
                existingmanagementproperty = ManagementProperty.objects.get(property=property,container=container)
                print existingmanagementproperty
                if existingmanagementproperty is not None:
                    return HttpResponseError("That Property allready exists")
            except ObjectDoesNotExist:
                pass

            property = form.cleaned_data['property']
            value    = form.cleaned_data['value']
            managementproperty = ManagementProperty(property=property,value=value,container=container)
            managementproperty.save()
            return redirect('/container/'+containerid)
        else:
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
            print "DataStagerAuth  doesn't exist."

        try:
            container_auth = HostingContainerAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = container_auth

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            print "HostingContainer Auth doesn't exist."

        try:
            dataservice_auths = DataServiceAuth.objects.get(id=id)
            dict = {}
            dict["auth"] = dataservice_auths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            print "HostingContainer Auth doesn't exist."

        try:
            sub_auth = SubAuth.objects.get(id=id)
            form = SubAuthForm()
            dict = {}
            dict["auth"] = sub_auth
            dict["form"] = form
            dict["subauths"] = subauths

            return render_to_response('auth.html', dict)
        except ObjectDoesNotExist:
            print "Sub Auth doesn't exist."

        dict = {}
        dict["error"] = "That Authority does not exist"
        return render_to_response('error.html', dict)
    
    def create(self, request):
        form = DataStagerAuthForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            authname = form.cleaned_data['authname']
            methods_csv = form.cleaned_data['methods_csv']
            description= form.cleaned_data['description']
            stager = form.cleaned_data['stager']
            methodslist = methods_csv.split(',')

            methods_encoded = base64.b64encode(pickle.dumps(methodslist))

            datastagerauth = DataStagerAuth(stager=stager,authname=authname,methods_encoded=methods_encoded,description=description)
            datastagerauth.save()

            return redirect('/auth/'+str(datastagerauth.id))
        else:
            return HttpResponseRedirect(request.META["HTTP_REFERER"])

class AuthHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = SubAuth

    def create(self, request):
        form = SubAuthForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
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

            handler = DataStagerHandler()
            
            if 'get' in methods:
                return handler.render_partial(stagerauth.stager, stagerauth, show=True)
            else:
                return handler.render_partial(stagerauth.stager, stagerauth, show=False)
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

        handler = DataStagerHandler()

        if 'get' in methods:
            return handler.render_partial(dsAuth.stager, auth, show=True)
        else:
            return handler.render_partial(dsAuth.stager, auth, show=False)

        if "get" in methods_intersection:
            return HttpResponseRedirect("/files"+dsAuth.stager.file.url)
        else:
            return HttpResponseForbidden("<html>Forbidden</html>")

