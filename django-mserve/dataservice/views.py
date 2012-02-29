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
"""The Mserve views module """
# pylint: disable-msg=W0613

import utils
import logging
import datetime
from django.conf import settings
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
from django.shortcuts import redirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from django.utils import simplejson
from request.models import Request
from request.traffic import modules
from datetime import timedelta
from datetime import date
from django_openid_auth.forms import OpenIDLoginForm
from django_openid_auth.views import make_consumer
from django_openid_auth.views import ax
from django_openid_auth.views import render_openid_request
from django_openid_auth.views import default_render_failure
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.forms import AuthenticationForm
from django_openid_auth import teams
from openid.consumer.discover import DiscoveryFailure
from openid.extensions import sreg, ax


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
    """Detect and append mobile user agents to a dict"""
    mobile_browser = False
    uagent = request.META.get('HTTP_USER_AGENT', None)
    if uagent:
        uagent = uagent.lower()[0:4]
        if (uagent in MOBILE_UAS):
            mobile_browser = True
        else:
            for hint in MOBILE_UAS_HINTS:
                if request.META.get('HTTP_USER_AGENT').find(hint) > 0:
                    mobile_browser = True

    _dict['mobile_browser'] = mobile_browser
    if request.user.is_authenticated() and request.user.is_staff:
        _dict['STORAGE_ROOT'] = settings.STORAGE_ROOT
        _dict['managementpropertyform'] = ManagementPropertyForm()

    return _dict

def home(request):
    """Render the home page """
    hostings = HostingContainer.objects.all()
    usagesummary = Usage.usages_to_summary(Usage.objects.all())
    servicerequestform = ServiceRequestForm()
    _dict = {}
    _dict["servicerequestform"] = servicerequestform
    if request.user.is_authenticated() and request.user.is_staff:
        _dict["hostingcontainers"] = hostings
        _dict["hostingcontainerform"] = HostingContainerForm(initial={
            'name': "Container",
            })
        _dict["serviceform"] = DataServiceForm(initial={
            'name': "Service",
            "starttime":datetime.datetime.today(),
            "endtime":datetime.datetime.today() + datetime.timedelta(hours=1)
            })
        _dict["usagesummary"] = usagesummary
        return render_to_response('home.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))
    elif request.user.is_authenticated():
        return render_to_response('home.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))
    else:
        return redirect(reverse('login'))
        from django.contrib.auth.forms import AuthenticationForm
        from django_openid_auth.forms import OpenIDLoginForm
        _dict["authform"] = AuthenticationForm()
        _dict["form"] = OpenIDLoginForm()
        return render_to_response('login.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

@csrf_protect
@never_cache
def login(request, template_name='login.html',
                login_complete_view='openid-complete',
                form_class=OpenIDLoginForm,
                render_failure=default_render_failure,
                redirect_field_name=REDIRECT_FIELD_NAME):
    """Begin an OpenID login request, possibly asking for an identity URL."""
      
    redirect_to = request.REQUEST.get(redirect_field_name, '')

    # Get the OpenID URL to try.  First see if we've been configured
    # to use a fixed server URL.
    openid_url = getattr(settings, 'OPENID_SSO_SERVER_URL', None)

    if openid_url is None:
        if request.POST:
            login_form = form_class(data=request.POST)
            if login_form.is_valid():
                openid_url = login_form.cleaned_data['openid_identifier']
        else:
            login_form = form_class()

        # Invalid or no form data:
        if openid_url is None:
            return render_to_response(template_name, {
                    'oidform': login_form,
                    'form': AuthenticationForm(),
                    redirect_field_name: redirect_to
                    }, context_instance=RequestContext(request))

    error = None
    consumer = make_consumer(request)
    try:
        openid_request = consumer.begin(openid_url)
    except DiscoveryFailure, exc:
        return render_failure(
            request, "OpenID discovery error: %s" % (str(exc),), status=500)

    # Request some user details.  If the provider advertises support
    # for attribute exchange, use that.
    if openid_request.endpoint.supportsType(ax.AXMessage.ns_uri):
        fetch_request = ax.FetchRequest()
        # We mark all the attributes as required, since Google ignores
        # optional attributes.  We request both the full name and
        # first/last components since some providers offer one but not
        # the other.
        for (attr, alias) in [
            ('http://axschema.org/contact/email', 'email'),
            ('http://axschema.org/namePerson', 'fullname'),
            ('http://axschema.org/namePerson/first', 'firstname'),
            ('http://axschema.org/namePerson/last', 'lastname'),
            ('http://axschema.org/namePerson/friendly', 'nickname'),
            # The myOpenID provider advertises AX support, but uses
            # attribute names from an obsolete draft of the
            # specification.  We request them for compatibility.
            ('http://schema.openid.net/contact/email', 'old_email'),
            ('http://schema.openid.net/namePerson', 'old_fullname'),
            ('http://schema.openid.net/namePerson/friendly', 'old_nickname')]:
            fetch_request.add(ax.AttrInfo(attr, alias=alias, required=True))
        openid_request.addExtension(fetch_request)
    else:
        openid_request.addExtension(
            sreg.SRegRequest(optional=['email', 'fullname', 'nickname']))

    # Request team info
    teams_mapping_auto = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO', False)
    teams_mapping_auto_blacklist = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING_AUTO_BLACKLIST', [])
    launchpad_teams = getattr(settings, 'OPENID_LAUNCHPAD_TEAMS_MAPPING', {})
    if teams_mapping_auto:
        #ignore launchpad teams. use all django-groups
        launchpad_teams = dict()
        all_groups = Group.objects.exclude(name__in=teams_mapping_auto_blacklist)
        for group in all_groups:
            launchpad_teams[group.name] = group.name

    if launchpad_teams:
        openid_request.addExtension(teams.TeamsRequest(launchpad_teams.keys()))

    # Construct the request completion URL, including the page we
    # should redirect to.
    return_to = request.build_absolute_uri(reverse(login_complete_view))
    if redirect_to:
        if '?' in return_to:
            return_to += '&'
        else:
            return_to += '?'
        return_to += urllib.urlencode({redirect_field_name: redirect_to})

    return render_openid_request(request, openid_request, return_to)


@staff_member_required
def traffic(request ):
    """Render the json stats for graphing """
    days = [date.today() - timedelta(day) for day in range(10)]
    days_qs = [(day, Request.objects.day(date=day)) for day in days]
    _json = simplejson.dumps(modules.graph(days_qs))
    return HttpResponse(_json, mimetype="application/json")

def stats(request, baseid=None):
    from jobservice.models import Job
    job_json = Job.get_job_plots(request, baseid=baseid)
    mfile_json = MFile.get_mfile_plots(request, baseid=baseid)
    usage_json = Usage.get_usage_plots(request, baseid=baseid)
    json = job_json + mfile_json + usage_json
    if json == None:
        return HttpResponseNotFound()
    _json = simplejson.dumps(json)
    return HttpResponse(_json, mimetype="application/json")

def render_base(request, baseid):
    try:
        auth = Auth.objects.get(id=baseid)

        logging.debug("Displaying auth %s" , (auth))

        parent = auth

        while parent.base == None:
            parent = parent.parent
            logging.debug("Recurse auth %s" , (parent.id))

        logging.debug("final auth %s" , (auth.id))
        base = parent.base

        if utils.is_service(base):
            return render_service_auth(request, auth)

    except Auth.DoesNotExist:
        logging.info("Request to browse '%s' , \
            ID does not relate to a auth object." , baseid)

    _dict = {}
    _dict["error"] = "Error displaying the auth with id='%s' " % baseid
    resp = render_to_response('error.html', append_dict(_dict, request), \
                context_instance=RequestContext(request))
    resp.status_code = 404
    return resp


@csrf_exempt
def test_transformrequest(request):
    """Render the test_transformrequest page"""
    resp = {
       "transformAck" : {
          "operationInfo" : {
             "jobID" : {
                "jobGUID" : "CDDA518D-4A42-45d0-A866-9C340AA98C11",
                "serviceProviderJobID" : "121e23e9-2168-46f1-a891-7f6bb8bdbddb"
             },
             "operationName" : "transformrequest",
             "profileID" : "",
             "status" : {
                "code" : "queued",
                "description" : "Pending"
             }
          }
       }
    }
    return HttpResponse(simplejson.dumps(resp), mimetype="application/json")


@csrf_exempt
def test_queryjobrequest(request, jobid):
    """Render the test_transformrequest page"""
    if jobid:
        resp = {
            "queryJobRequest" : {
                "queryJobInfo" : {
                    "jobInfo" : {
                        "jobID" : {
                            "jobGUID" : "CDDA518D-4A42-45d0-A866-9C340AA98C11",
                            "serviceProviderJobID" : "121e23e9-2168-46f1-a891-7f6bb8bdbddb"
                        },
                        "operationName" : "transformrequest",
                        "priority" : "immediate",
                        "status" : {
                            "code" : "running",
                            "description" : "In Progress"
                        }
                    }
                }
            }
        }
        return HttpResponse( simplejson.dumps(resp), mimetype="application/json")
    else:
        resp = {
            "active transfers" : 1,
            "transfer_id_1" : "CDDA518D-4A42-45d0-A866-9C340AA98C11"
        }
        return HttpResponse( simplejson.dumps(resp), mimetype="application/json")


def test(request):
    _dict = {}
    return render_to_response('test.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

@login_required
def profile(request):
    """Render the user page"""
    _dict = {}
    return render_to_response('user.html', append_dict(_dict, request), \
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

def videoplayer(request, mfileid):
    mfile = get_object_or_404(MFile,id=mfileid)
    _dict = {}
    _dict["mfile"] = mfile
    return render_to_response('videoplayer.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

@staff_member_required
def render_usage(request):
    """Render the usage page"""
    usagesummary = Usage.get_full_usagesummary()
    _dict = {}
    _dict["usagesummary"] = usagesummary
    return render_to_response('allusage.html', append_dict(_dict, request), \
            context_instance=RequestContext(request))

def render_error(request, error):
    """Render the error page"""
    _dict = {}
    _dict["error"] = error
    return render_to_response('error.html', append_dict(_dict, request), \
        context_instance=RequestContext(request))


def redirect_to(request):
    if 'to' in request.GET:
        return redirect(request.GET['to'])
    else:
        _dict = {}
        _dict["error"] = "Error redirecting"
        return render_to_response('error.html', append_dict(_dict, request), \
                context_instance=RequestContext(request))