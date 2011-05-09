from mserve.dataservice.models import *
from mserve.dataservice.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template import RequestContext
import usage_store as usage_store
import utils as utils
import api as api
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from anyjson import serialize as JSON_dump
from django.db.models import Avg, Max, Min, Count
from django.utils import simplejson
from request.models import Request
from request.traffic import modules
from datetime import datetime
from datetime import timedelta
from datetime import date

def home(request,form=HostingContainerForm()):    
    hostings = HostingContainer.objects.all()
    usagesummary = usage_store.get_usage_summary(None)
    usage = usage_store.get_usage(None)
    dict = {}
    if request.user.is_authenticated() and request.user.is_staff:
        dict["hostingcontainers"] = hostings
        dict["form"] = form
        dict["usage"] = usage
        dict["usagesummary"] = usagesummary
    return render_to_response('home.html', dict, context_instance=RequestContext(request))

@staff_member_required
def stats(request):
    days = [date.today() - timedelta(day) for day in range(10)]
    days_qs = [(day, Request.objects.day(date=day)) for day in days]
    js = simplejson.dumps(modules.graph(days_qs))
    return HttpResponse(js,mimetype="application/json")

def render_base(request,id):
    try:
        base = NamedBase.objects.get(id=id)

        if utils.is_container(base):
            return render_container(request,id)

        if utils.is_service(base):
            return render_service(request,id)

        if utils.is_mfile(base):
            return render_mfile(request,id,show=True)
    except NamedBase.DoesNotExist:
        logging.info("Request to browse %s , ID does not relate to a service/container/mfile object." % (id) )

    try:
        auth = Auth.objects.get(id=id)

        logging.debug("Displaying auth %s" % (auth))

        parent = auth

        while parent.base == None:
            parent = parent.parent
            logging.debug("Recurse auth %s" % (parent.id))

        logging.debug("final auth %s" % (auth.id))
        base = parent.base
        if utils.is_container(base):
            return render_container_auth(request,id)

        if utils.is_service(base):
            return render_service_auth(request,auth)

        if utils.is_mfile(base):
            return render_mfile_auth(request,auth)



        dict = {}
        dict["error"] = "Error displaying the auth with id='%s' " % id
        return render_to_response('error.html', dict, context_instance=RequestContext(request))

    except Auth.DoesNotExist:
        logging.info("Request to browse '%s' , ID does not relate to a auth object." % (id))


    return

@login_required
def profile(request):
    dict ={}
    return render_to_response('user.html', dict, context_instance=RequestContext(request))

def render_container(request,id,form=DataServiceForm()):
    container = HostingContainer.objects.get(pk=id)
    auths = Auth.objects.filter(base=container.id)
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    #form.fields['cid'].initial = id
    usage = usage_store.get_usage(id)
    usagesummary = usage_store.get_usage_summary(container.id)

    managementpropertyform = ManagementPropertyForm()
    dict = {}
    dict["container"] = container
    dict["services"] = services
    dict["properties"] = properties
    dict["form"] = form
    dict["managementpropertyform"] = managementpropertyform
    dict["auths"] = auths
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary

    return render_to_response('container.html', dict, context_instance=RequestContext(request))

@staff_member_required
def render_container_auth(request,authid):
    #container = HostingContainer.objects.get(pk=id)
    hca = Auth.objects.get(pk=authid)
    container=hca.base
    auths = hca.auth_set.all()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    usage = usage_store.get_usage(container.id)
    usagesummary = usage_store.get_usage_summary(container.id)

    managementpropertyform = ManagementPropertyForm()
    dict = {}
    dict["container"] = container
    #dict["auth"] = hca
    dict["services"] = services
    dict["properties"] = properties
    dict["managementpropertyform"] = managementpropertyform
    dict["auths"] = auths
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    
    return render_to_response('container.html', dict, context_instance=RequestContext(request))

def render_service(request,id,form=MFileForm()):
    service = DataService.objects.get(pk=id)
    mfiles = MFile.objects.filter(service=service).order_by('created').reverse()
    properties = ManagementProperty.objects.filter(base=service)
    auths = Auth.objects.filter(base=id)
    managementpropertyform = ManagementPropertyForm()
    form.fields['sid'].initial = service.id
    dict = {}
    dict["properties"] = properties
    dict["managementpropertyform"] = managementpropertyform
    dict["service"] = service
    dict["mfiles"] = mfiles
    dict["auths"] = auths
    dict["form"] = form
    dict["usage"] = usage_store.get_usage(id)
    dict["usagesummary"] = usage_store.get_usage_summary(service.id)
    return render_to_response('service.html', dict, context_instance=RequestContext(request))

def render_service_auth(request,auth):

    base = utils.get_base_for_auth(auth)
    form=MFileForm()
    form.fields['sid'].initial = base.id
    
    dict = {}
    dict["auth"] = auth
    dict["usagesummary"] = usage_store.get_usage_summary(base.id)
    dict["service"] = DataService.objects.get(id=base.id)
    dict["form"] = form
    
    return render_to_response('auths/service_auth.html', dict, context_instance=RequestContext(request))

def render_mfile(request, id, form=AuthForm(), show=False):
    mfile = MFile.objects.get(pk=id)

    auths = Auth.objects.filter(base=id)

    form.fields['dsid'].initial = mfile.id
    dict = {}

    dict["thumburl"] = "/mservemedia/images/empty.png"

    if mfile.thumb == "":
        dict["thumburl"] = "/mservemedia/images/busy.gif"
    else:
        dict["thumburl"] = "%s" % (mfile.thumburl())

    if not show or mfile.file == '' or mfile.file == None:
        dict["altfile"] = "/mservemedia/images/empty.png"
        dict["thumburl"] = "/mservemedia/images/empty.png"
        mfile.file = None

    dict['verify'] = False
    if request.GET.has_key('verify') and request.GET['verify'] is not None:
        check = utils.md5_for_file(mfile.file)
        dict['verifychecksum'] = check
        dict['verifystate'] = (check == mfile.checksum)
        dict['verify'] = True

    dict["mfile"] = mfile
    dict["fullaccess"] = True
    dict["auths"] = auths
    dict["formtarget"] = "/mfileauth/"
    dict["usage"] = usage_store.get_usage(id)
    dict["usagesummary"] = usage_store.get_usage_summary(mfile.id)
    
    return render_to_response('mfile.html', dict, context_instance=RequestContext(request))

def render_mfile_auth(request, auth):
    dict = {}
    dict["auth"] = auth
    return render_to_response('auths/mfile_auth.html', dict, context_instance=RequestContext(request))

@staff_member_required
def usage(request):
    usagesummary = usage_store.get_usage_summary(None)
    usage = Usage.objects.all()
    dict = {}
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    return render_to_response('allusage.html', dict, context_instance=RequestContext(request))


def render_error(request,error):
    dict = {}
    dict["error"] = error
    return render_to_response('error.html', dict, context_instance=RequestContext(request))


    