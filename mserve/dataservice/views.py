from mserve.dataservice.models import HostingContainer
from mserve.dataservice.models import HostingContainerAuth
from mserve.dataservice.models import DataService
from mserve.dataservice.models import DataServiceAuth
from mserve.dataservice.models import DataStager
from mserve.dataservice.models import DataStagerAuth
from mserve.dataservice.models import Usage
from mserve.dataservice.models import UsageRate
from mserve.dataservice.models import ManagementProperty
from mserve.dataservice.models import JoinAuth
from mserve.dataservice.models import SubAuth
from mserve.dataservice.forms import HostingContainerForm
from mserve.dataservice.forms import DataServiceForm
from mserve.dataservice.forms import DataStagerForm
from mserve.dataservice.forms import DataStagerAuthForm
from mserve.dataservice.forms import SubAuthForm
from mserve.dataservice.forms import ManagementPropertyForm
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response

from django.http import HttpResponse

import usage_store as usage_store

class Sleeper(object):

    def main(self, request, length):
        import time
        sleeptime = int(length)
        time.sleep(sleeptime)
        return HttpResponse("Sleep for %s"%sleeptime)

sleeper = Sleeper()
sleep = sleeper.main

def viz(request):
    dict={}

    hostings = HostingContainer.objects.all()

    rows = []
    for hosting in hostings:
        services = DataService.objects.filter(container=hosting)
        totalservices = len(services)
        totalstagers = 0
        totaldisc = 0.0
        for service in services:
            stagers = DataStager.objects.filter(service=service)
            totalstagers += len(stagers)
            for stager in stagers:
                totaldisc    += stager.file.size

        n = {"c":[{"v": str(hosting.name)}, {"v": totalservices}, {"v": totalstagers}, {"v": totaldisc}]}
        rows.append(n)


    viz_data = {
        "cols":
                [   {"id": 'container', "label": 'Container', "type": 'string'},
                    {"id": 'services', "label": 'Services', "type": 'number'},
                    {"id": 'stagers', "label": 'Stagers', "type": 'number'},
                    {"id": 'stagers', "disc": 'Disc', "type": 'number'}
                ],
        "rows": [
                    {"c":[{"v": 'Work'},     {"v": 11}]},
                    {"c":[{"v": 'Eat'},     {"v": 2 }]},
                    {"c":[{"v": 'Commute'}, {"v": 2 }]}
                ]
            }
    import logging
    logging.info(viz_data)
    
    viz_data = {
        "cols":
                [   {"id": 'container', "label": 'Container', "type": 'string'},
                    {"id": 'services', "label": 'Services', "type": 'number'},
                    {"id": 'stagers', "label": 'Stagers', "type": 'number'},
                    {"id": 'disc', "label": 'Disc', "type": 'number'}
                ],
        "rows": rows
            }

    
    logging.info(viz_data)
    dict["viz_data"] = viz_data
    return render_to_response('viz.html', dict)

def usage(request):
    usagesummary = usage_store.usagesummary()
    usagerate = UsageRate.objects.all()
    usage = Usage.objects.all()
    dict = {}
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    dict["usagerate"] = usagerate
    return render_to_response('allusage.html', dict)

def home(request):
    form = HostingContainerForm()
    hostings = HostingContainer.objects.all()
    usagesummary = usage_store.usagesummary()
    usagerate = UsageRate.objects.all()
    usage = Usage.objects.all()
    dict = {}
    dict["hostingcontainers"] = hostings
    dict["form"] = form
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    dict["usagerate"] = usagerate
    return render_to_response('home.html', dict)

def container(request,id):
    container = HostingContainer.objects.get(id=id)
    auths = HostingContainerAuth.objects.filter(hostingcontainer=container)
    services = DataService.objects.filter(container=container)
    properties = ManagementProperty.objects.filter(container=container)
    form = DataServiceForm()
    managementpropertyform = ManagementPropertyForm()
    dict = {}
    dict["container"] = container
    dict["services"] = services
    dict["properties"] = properties
    dict["form"] = form
    dict["managementpropertyform"] = managementpropertyform
    dict["auths"] = auths
    dict["error"] = request.GET["error"]
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


    