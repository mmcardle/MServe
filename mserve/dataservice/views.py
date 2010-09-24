from mserve.dataservice.models import HostingContainer
from mserve.dataservice.models import HostingContainerAuth
from mserve.dataservice.models import DataService
from mserve.dataservice.models import DataServiceAuth
from mserve.dataservice.models import DataStager
from mserve.dataservice.models import DataStagerAuth
from mserve.dataservice.models import JoinAuth
from mserve.dataservice.models import SubAuth
from mserve.dataservice.forms import HostingContainerForm
from mserve.dataservice.forms import DataServiceForm
from mserve.dataservice.forms import DataStagerForm
from mserve.dataservice.forms import DataStagerAuthForm
from mserve.dataservice.forms import SubAuthForm
from mserve.dataservice.forms import UploadFileForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response

def home(request):
    form = HostingContainerForm()
    hostings = HostingContainer.objects.all()
    dict = {}
    dict["hostingcontainers"] = hostings
    dict["form"] = form
    return render_to_response('home.html', dict)

def container(request,id):
    container = HostingContainer.objects.get(id=id)
    auths = HostingContainerAuth.objects.filter(hostingcontainer=container)
    services = DataService.objects.filter(container=container)
    form = DataServiceForm()
    dict = {}
    dict["container"] = container
    dict["services"] = services
    dict["form"] = form
    dict["auths"] = auths
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
    auths = DataStagerAuth.objects.filter(stager=stager)
    form = DataStagerAuthForm()
    dict = {}
    dict["stager"] = stager
    dict["form"] = form
    dict["auths"] = auths
    return render_to_response('stager.html', dict)

class Row:
    value = ""
    name = ""
    parent = ""
    tip = ""
    def __init__(self,name,parent,value,tip):
        self.name = name
        self.value = value
        self.tip = tip
        self.parent = parent

def map(request):
    dict = {}
    
    #rows = [['Hosting','Hosting','Hosting']]
    rows = []
    rows.append(Row(name='Hosting',value='Hosting',parent='',tip='Hosting'))

    containers = HostingContainer.objects.all()

    for container in containers:
        row = Row(name=container.name,value=container.id, parent='Hosting', tip=container.name)
        rows.append(row)
        services = DataService.objects.filter(container=container)
        for service in services:
            id  = str(service.id)
            name  = str(service.name)
            row = Row(value=id, name=name, parent=container.id, tip=service.name)
            rows.append(row)
            stagers = DataStager.objects.filter(service=service)
            for stager in stagers:
                id  = str(stager.id)
                name  = str(stager.name)
                row = Row( value=id, name=name, parent=service.id, tip=stager.name)
                rows.append(row)
                stagerauths = DataStagerAuth.objects.filter(stager=stager)
                for stagerauth in stagerauths:
                    row = Row(name=stagerauth.authname, value=stagerauth.id, parent=stager.id, tip=stagerauth.authname)
                    rows.append(row)


    joins = JoinAuth.objects.all()
    for join in joins:
        c = join.child
        p = join.parent

        subs = SubAuth.objects.get(id=c)
        try:
            dsauth = DataStagerAuth.objects.get(id=p)
            id = p
            name  = str(subs.authname)
            value = str(subs.id)
            row = Row(name=name, value=value, parent=p, tip=subs.authname)
            rows.append(row)
        except ObjectDoesNotExist:
            pass

        try:
            sub = SubAuth.objects.get(id=p)
            row = Row(name=subs.authname, value=subs.id, parent=sub.id, tip=subs.authname)
            rows.append(row)
        except ObjectDoesNotExist:
            pass


    '''rows = [
        ['Hosting', 'Hosting', 'The President'],
        ['Container1', 'Hosting', 'The President'],
        ['Container2', 'Hosting', 'VP'],
        ['Service1', 'Container1', ''],
        ['Service2', 'Container1', ''],
        ['Service3', 'Container2', '']
    ]'''

    dict["rows"] = rows
    return render_to_response('map.html', dict)


def auth(request,id):

    sub_auths = JoinAuth.objects.filter(parent=id)
    subauths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        subauths.append(subauth)
        
    try:
        datastager_auth = DataStagerAuth.objects.get(id=id)

        form = SubAuthForm()
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
        print "HostginContainer Auth doesn't exist."

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


    