from mserve.dataservice.models import HostingContainer
from mserve.dataservice.models import DataService
from mserve.dataservice.models import DataStager
from mserve.dataservice.models import Auth
from django.shortcuts import render_to_response
from mserve.dataservice.forms import HostingContainerForm
from mserve.dataservice.forms import DataServiceForm
from mserve.dataservice.forms import DataStagerForm
from mserve.dataservice.forms import UploadFileForm
from mserve.dataservice.forms import AuthForm

def home(request):
    form = HostingContainerForm()
    hostings = HostingContainer.objects.all()
    dict = {}
    dict["hostingcontainers"] = hostings
    dict["form"] = form
    return render_to_response('home.html', dict)

def container(request,id):
    container = HostingContainer.objects.get(id=id)
    services = DataService.objects.filter(container=container)
    form = DataServiceForm()
    dict = {}
    dict["container"] = container
    dict["services"] = services
    dict["form"] = form
    return render_to_response('container.html', dict)

def service(request,id):
    service = DataService.objects.get(id=id)
    stagers = DataStager.objects.filter(service=service)
    form = DataStagerForm()
    form2 = UploadFileForm()
    dict = {}
    dict["service"] = service
    dict["stagers"] = stagers
    dict["form"] = form
    dict["form2"] = form2
    return render_to_response('service.html', dict)

def stager(request,id):
    stager = DataStager.objects.get(id=id)
    dict = {}
    dict["stager"] = stager
    return render_to_response('stager.html', dict)