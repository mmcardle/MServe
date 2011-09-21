"""The Mserve dataservice module """
########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-03-25
#	Created for Project :		PrestoPrime
#
########################################################################

# pylint: disable-msg=W0613

import utils
import logging
from models import NamedBase
from models import HostingContainer
from models import DataService
from models import MFile
from models import Auth
from models import Usage
from models import ManagementProperty
from forms import ServiceRequestForm
from forms import HostingContainerForm
from forms import DataServiceForm
from forms import ManagementPropertyForm
from forms import SubServiceForm
from forms import MFileForm
from forms import AuthForm
from forms import DataServiceTaskForm
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import simplejson
from request.models import Request
from request.traffic import modules
from datetime import timedelta
from datetime import date

MOBILE_UAS = [
	'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
	'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
	'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
	'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
	'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
	'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
	'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
	'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
	'wapr','webc','winw','winw','xda','xda-'
	]
 
MOBILE_UAS_HINTS = [ 'SymbianOS', 'Opera Mini', 'iPhone', 'iPad' ]

def append_dict(_dict, request):
    """Detect and append mobile user agents to a dict """
    mobile_browser = False
    uagent = request.META['HTTP_USER_AGENT'].lower()[0:4]
    logging.debug("User Agent is %s " , uagent )
    if (uagent in MOBILE_UAS):
        mobile_browser = True
    else:
        for hint in MOBILE_UAS_HINTS:
            if request.META['HTTP_USER_AGENT'].find(hint) > 0:
                mobile_browser = True

    _dict['mobile_browser'] = mobile_browser
    return _dict

def home(request, form=HostingContainerForm()):
    """Render the home page """
    hostings = HostingContainer.objects.all()
    usagesummary = Usage.usages_to_summary(Usage.objects.all())
    servicerequestform = ServiceRequestForm()
    _dict = {}
    _dict["servicerequestform"] = servicerequestform
    if request.user.is_authenticated() and request.user.is_staff:
        _dict["hostingcontainers"] = hostings
        _dict["form"] = form
        _dict["usagesummary"] = usagesummary
    return render_to_response('home.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

@staff_member_required
def stats(request):  
    """Render the json stats for graphing """
    days = [date.today() - timedelta(day) for day in range(10)]
    days_qs = [(day, Request.objects.day(date=day)) for day in days]
    _json = simplejson.dumps(modules.graph(days_qs))
    return HttpResponse(_json, mimetype="application/json")

def render_base(request, baseid):
    """Render a specified base """
    try:
        base = NamedBase.objects.get(id=baseid)

        if utils.is_container(base):
            return render_container(request, baseid)

        if utils.is_service(base):
            return render_service(request, baseid)

        if utils.is_mfile(base):
            return render_mfile(request, baseid, show=True)

    except NamedBase.DoesNotExist:
        logging.info("Request to browse %s ,\
            ID does not relate to a service/container/mfile object." , baseid )

    try:
        auth = Auth.objects.get(id=baseid)

        logging.debug("Displaying auth %s" , (auth))

        parent = auth

        while parent.base == None:
            parent = parent.parent
            logging.debug("Recurse auth %s" , (parent.id))

        logging.debug("final auth %s" , (auth.id))
        base = parent.base
        if utils.is_container(base):
            return render_container_auth(request, baseid)

        if utils.is_service(base):
            return render_service_auth(request, auth)

        if utils.is_mfile(base):
            return render_mfile_auth(request, auth)

        _dict = {}
        _dict["error"] = "Error displaying the auth with id='%s' " % baseid
        return render_to_response('error.html', append_dict(_dict, request), \
                context_instance=RequestContext(request))

    except Auth.DoesNotExist:
        logging.info("Request to browse '%s' , \
            ID does not relate to a auth object." , baseid)

    return Http404()

@login_required
def profile(request):
    """Render the user page"""
    _dict = {}
    return render_to_response('user.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

def render_container(request, containerid, form=DataServiceForm()):
    """Render the container page"""
    container = HostingContainer.objects.get(pk=containerid)
    auths = Auth.objects.filter(base=container.id)
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    usage = container.get_usage()
    usagesummary = container.get_usage_summary()

    managementpropertyform = ManagementPropertyForm()
    hcform = HostingContainerForm(instance=container)

    subserviceform = SubServiceForm()
    serviceform = DataServiceForm()

    _dict = {}
    _dict["container"] = container
    _dict["hcform"] = hcform
    _dict["services"] = services
    _dict["properties"] = properties
    _dict["form"] = form
    _dict["managementpropertyform"] = managementpropertyform
    _dict["subserviceform"] = subserviceform
    _dict["serviceform"] = serviceform
    _dict["auths"] = auths
    _dict["usage"] = usage
    _dict["usagesummary"] = usagesummary

    return render_to_response('container.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

@staff_member_required
def render_container_auth(request, authid):
    """Render the container auth page"""
    #container = HostingContainer.objects.get(pk=id)
    hca = Auth.objects.get(pk=authid)
    container = hca.base
    auths = hca.auth_set.all()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    usage = hca.get_usage()
    usagesummary = hca.get_usage_summary()
    managementpropertyform = ManagementPropertyForm()
    _dict = {}
    _dict["container"] = container
    _dict["services"] = services
    _dict["properties"] = properties
    _dict["managementpropertyform"] = managementpropertyform
    _dict["auths"] = auths
    _dict["usage"] = usage
    _dict["usagesummary"] = usagesummary
    
    return render_to_response('container.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

def render_service(request, serviceid, form=MFileForm()):
    """Render the service page"""
    service = DataService.objects.get(pk=serviceid)
    mfiles = MFile.objects.filter(service=service).order_by('created').reverse()
    properties = ManagementProperty.objects.filter(base=service)
    auths = Auth.objects.filter(base=serviceid)
    managementpropertyform = ManagementPropertyForm()
    dataservicetaskform = DataServiceTaskForm()
    subserviceform = SubServiceForm()
    form.fields['sid'].initial = service.id
    _dict = {}
    _dict["properties"] = properties
    _dict["managementpropertyform"] = managementpropertyform
    _dict["dataservicetaskform"] = dataservicetaskform
    _dict["subserviceform"] = subserviceform
    _dict["service"] = service
    _dict["mfiles"] = mfiles
    _dict["auths"] = auths
    _dict["form"] = form
    _dict["usage"] = service.get_usage()
    _dict["usagesummary"] = service.get_usage_summary()
    return render_to_response('service.html', append_dict(_dict, request), \
        context_instance=RequestContext(request))

def render_service_auth(request, auth):
    """Render the service auth page"""
    base = utils.get_base_for_auth(auth)
    form = MFileForm()
    form.fields['sid'].initial = base.id
    
    _dict = {}
    _dict["auth"] = auth
    _dict["usagesummary"] = auth.get_usage_summary()
    _dict["service"] = DataService.objects.get(id=base.id)
    _dict["form"] = form
    
    return render_to_response('auths/service_auth.html', \
        append_dict(_dict, request),\
        context_instance=RequestContext(request))

def render_mfile(request, mfileid, form=AuthForm(), show=False):
    """Render the mfile page"""
    mfile = MFile.objects.get(pk=mfileid)

    auths = Auth.objects.filter(base=mfileid)

    form.fields['dsid'].initial = mfile.id
    _dict = {}

    _dict["thumburl"] = "/mservemedia/images/empty.png"

    if mfile.thumb == "":
        _dict["thumburl"] = "/mservemedia/images/busy.gif"
    else:
        _dict["thumburl"] = "%s" % (mfile.thumburl())

    if not show or mfile.file == '' or mfile.file == None:
        _dict["altfile"] = "/mservemedia/images/empty.png"
        _dict["thumburl"] = "/mservemedia/images/empty.png"
        mfile.file = None

    _dict['verify'] = False
    if request.GET.has_key('verify') and request.GET['verify'] is not None:
        check = utils.md5_for_file(mfile.file)
        _dict['verifychecksum'] = check
        _dict['verifystate'] = (check == mfile.checksum)
        _dict['verify'] = True

    _dict["mfile"] = mfile
    _dict["fullaccess"] = True
    _dict["auths"] = auths
    _dict["formtarget"] = "/mfileauth/"
    _dict["usage"] = mfile.get_usage()
    _dict["usagesummary"] = mfile.get_usage_summary()
    
    return render_to_response('mfile.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

def render_mfile_auth(request, auth):
    """Render the mfile auth page"""
    _dict = {}
    _dict["auth"] = auth
    return render_to_response('auths/mfile_auth.html', \
            append_dict(_dict, request), \
            context_instance=RequestContext(request))

@staff_member_required
def render_usage(request):
    """Render the usage page"""
    usages = Usage.objects.all()
    usagesummary = Usage.get_full_usagesummary()
    _dict = {}
    _dict["usage"] = usages
    _dict["usagesummary"] = usagesummary
    return render_to_response('allusage.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

def render_error(request, error):
    """Render the error page"""
    _dict = {}
    _dict["error"] = error
    return render_to_response('error.html', append_dict(_dict, request), \
        context_instance=RequestContext(request))


    