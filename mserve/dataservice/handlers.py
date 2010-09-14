from piston.handler import BaseHandler
from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.forms import HostingContainerForm
from dataservice.forms import DataServiceForm
from dataservice.forms import DataStagerForm
from dataservice.forms import UploadFileForm
from mserve.dataservice import utils
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect

base         = "/m/home/"
container_base = "/m/container/"
service_base  = "/m/service/"

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
            return HttpResponseRedirect(base)
        else:
            return HttpResponse("<html>"+str(form)+"</html>")

class DataServiceHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataService

    def create(self, request):
        form = DataServiceForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            name = form.cleaned_data['name']
            containerid = form.cleaned_data['container'].id
            container = HostingContainer.objects.get(id=containerid)
            dataservice = DataService(name=name,container=container)
            dataservice.save()
            return HttpResponseRedirect(container_base+containerid+"/")
        else:
            return HttpResponse(form)

class DataStagerHandler(BaseHandler):
    allowed_methods = ('GET','POST')
    model = DataStager

    def create(self, request):
        form = DataStagerForm(request.POST,request.FILES) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            serviceid = form.cleaned_data['service'].id
            file = request.FILES['file']
            service = DataService.objects.get(id=serviceid)
            datastager = DataStager(name=file.name,service=service,file=file)
            datastager.save()
            return HttpResponseRedirect(service_base+serviceid+"/")
        else:
            return HttpResponse("<html>"+str(form)+"</html>")

