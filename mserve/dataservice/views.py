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
    roles = Role.objects.filter(auth=auths)
    methods = []
    for auth in auths:
        roles = Role.objects.filter(auth=auth)
        for role in roles:
            methods  = methods + role.methods()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    form.fields['cid'].initial = id
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
    dict["roles"] = roles
    dict["methods"] = set(methods)

    return render_to_response('container.html', dict, context_instance=RequestContext(request))

'''
def render_containerauth(request,authid,form=DataServiceForm()):
    #container = HostingContainer.objects.get(pk=id)
    hca = Auth.objects.get(pk=authid)
    container=hca.hostingcontainer
    sub_auths = JoinAuth.objects.filter(parent=authid)
    auths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        auths.append(subauth)
    roles = Role.objects.filter(auth=auths)
    #roles = hca.roles.all()
    methods = []
    #for role in  hca.roles.all():
    #    methods  = methods + role.methods()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    form.fields['cid'].initial = container.id
    usage = usage_store.get_usage(id)
    usagesummary = usage_store.get_usage_summary(container.id)

    managementpropertyform = ManagementPropertyForm()
    dict = {}
    dict["container"] = container
    dict["auth"] = hca
    dict["services"] = services
    dict["properties"] = properties
    dict["form"] = form
    dict["managementpropertyform"] = managementpropertyform
    dict["auths"] = auths
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    dict["roles"] = roles
    dict["methods"] = set(methods)
    
    return render_to_response('container.html', dict, context_instance=RequestContext(request))
'''

#@staff_member_required
def render_service(request,id,form=MFileForm()):
    service = DataService.objects.get(pk=id)
    mfiles = MFile.objects.filter(service=service).order_by('created').reverse()
    properties = ManagementProperty.objects.filter(base=service)
    methods = []
    auths = Auth.objects.filter(base=id)
    for auth in auths:
        roles = Role.objects.filter(auth=auth)
        for role in roles:
            methods  = methods + role.methods()
    managementpropertyform = ManagementPropertyForm()
    form.fields['sid'].initial = service.id
    dict = {}
    dict["properties"] = properties
    dict["managementpropertyform"] = managementpropertyform
    dict["service"] = service
    dict["mfiles"] = mfiles
    dict["auths"] = auths
    dict["roles"] = roles
    dict["form"] = form
    dict["usage"] = usage_store.get_usage(id)
    dict["usagesummary"] = usage_store.get_usage_summary(service.id)
    dict["methods"] = set(methods)
    return render_to_response('service.html', dict, context_instance=RequestContext(request))

def render_service_auth(request,auth):

    roles = auth.roles

    methodslist = [ pickle.loads(base64.b64decode(method_enc)) for method_enc in roles.all().values_list('methods_encoded',flat=True) ]
    methods = [item for sublist in methodslist for item in sublist]

    methods = utils.get_methods_for_auth(auth)
    logging.info("methods %s" % methods )

    dict = {}
    dict["methods"] = methods
    dict["auth"] = auth

    return render_to_response('auths/service_auth.html', dict, context_instance=RequestContext(request))

def create_auth(request):
    form = SubAuthForm(request.POST)
    if form.is_valid():

        authname = form.cleaned_data['authname']
        roles_csv = form.cleaned_data['roles_csv']
        parent = form.cleaned_data['id_parent']

        subauth = SubAuth(authname=authname)
        subauth.save()
        
        rolenames = roles_csv.split(',')
        rolestoadd = rolenames
        allowedroles = []

        r = None
        try:
            parent_auth = MFileAuth.objects.get(id=parent)
            roles = Role.objects.filter(auth=parent_auth)
            for role in roles:
                allowedroles.append(role.rolename)
                if role.rolename in rolenames:
                    rolestoadd.remove(role.rolename)
                    subauth.roles.add(role)
        except ObjectDoesNotExist:
            pass

        if len(rolestoadd) != 0:
            subauth.delete()
            return render_error(request,"Could not add methods '%s'. Allowed = %s" % (','.join(rolestoadd),','.join(set(allowedroles))))


        child = str(subauth.id)

        join = JoinAuth(parent=parent,child=child)
        join.save()

        return redirect('/browse/%s/' % str(subauth.id))

    else:
        return render_error(request,form)
'''
def create_mfileauth(request):
    form = MFileAuthForm(request.POST)
    if form.is_valid():
        authname = form.cleaned_data['authname']
        roles_csv = form.cleaned_data['roles']
        mfileid = form.cleaned_data['dsid']
        mfile = MFile.objects.get(pk=mfileid)

        mfileauth = MFileAuth(mfile=mfile,authname=authname)
        mfileauth.save()

        auths = MFileAuth.objects.filter(mfile=mfile)

        rolenames = roles_csv.split(',')
        rolestoadd = rolenames
        allowedroles = []

        for auth in auths:
            roles  = Role.objects.filter(auth=auth)
            for role in roles:
                allowedroles.append(role.rolename)
                if role.rolename in rolenames:
                    rolestoadd.remove(role.rolename)
                    mfileauth.roles.add(role)

        if len(rolestoadd) != 0:
            mfileauth.delete()
            return render_error(request,"Could not add methods '%s'. Allowed = %s" % (','.join(rolestoadd),','.join(set(allowedroles))))

        return render_mfileauth(request, mfileauth.mfile, mfileauth)

    else:
        return render_error(request,form)
'''
def create_mfile(request):
    form = MFileForm(request.POST,request.FILES)
    if form.is_valid():

        if request.FILES.has_key('file'):
            file = request.FILES['file']
        else:
            file = None
        serviceid = form.cleaned_data['sid']
        #service = DataService.objects.get(id=serviceid)
        mfile = api.create_mfile(request, serviceid, file)

        return redirect('/browse/'+str(mfile.id)+"/")
    else:
        serviceid = form.data['sid']
        return render_service(request,serviceid,form=form)

def render_mfile(request, id, form=AuthForm(), show=False):
    mfile = MFile.objects.get(pk=id)

    methods = []
    auths = Auth.objects.filter(base=id)
    roles = []
    for auth in auths:
        roles = Role.objects.filter(auth=auth)
        for role in roles:
            methods  = methods + role.methods()
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
    dict["roles"] = roles
    dict["methods"] = set(methods)
    
    return render_to_response('mfile.html', dict, context_instance=RequestContext(request))

def render_auth(request, id):
    '''
    Have to add the case where this could be a hosting container or data
    service auth.
    '''
    auth = Auth.objects.get(id=id)
    if utils.is_mfileauth(auth):
        mfileauth = MFileAuth.objects.get(id=id)
        methods = get_auth_methods(mfileauth)
        if 'get' in methods:
            return render_mfileauth(request, mfileauth.mfile, mfileauth, show=True)
        else:
            return render_mfileauth(request, mfileauth.mfile, mfileauth, show=False)

    if utils.is_serviceauth(auth):
        dsa = DataServiceAuth.objects.get(pk=auth.id)
        return render_serviceauth(request,dsa.id)

    if utils.is_containerauth(auth):
        hca = HostingContainerAuth.objects.get(pk=auth.id)
        return views.render_containerauth(request,hca.id)

    dsAuth, methods_intersection = find_mfile_auth(id)

    if dsAuth is None:
        return HttpResponseBadRequest("No Interface for %s " % (id))

    auth = SubAuth.objects.get(id=id)
    methods = get_auth_methods(auth)

    dict = {}
    dict['actions'] = methods
    dict['actionprefix'] = "mfileapi"
    dict['authapi'] = id
    if 'get' in methods:
        return render_mfileauth(request, dsAuth.mfile, auth, show=True, dict=dict)
    else:
        return render_mfileauth(request, dsAuth.mfile, auth, show=False, dict=dict)

def get_auth_methods(auth):
    methods = []
    for role in auth.roles.all():
        methods = methods + role.methods()
    return list(set(methods))

def find_mfile_auth(parent):
    dsAuth = None
    methods_intersection = None
    all_methods = set()
    done = False
    while not done:
        try:
            joins = JoinAuth.objects.get(child=parent)
            parent = joins.parent

            try:
                subauth = SubAuth.objects.get(id=parent)
                if methods_intersection is None:
                    methods_intersection = set(get_auth_methods(subauth))
                methods_intersection = methods_intersection & set(get_auth_methods(subauth))
                all_methods = all_methods | set(get_auth_methods(subauth))
            except ObjectDoesNotExist:
                pass
            try:
                MFileauth = MFileAuth.objects.get(id=parent)
                dsAuth = MFileauth
                if methods_intersection is None:
                    methods_intersection = set(get_auth_methods(MFileauth))
                methods_intersection = methods_intersection & set(get_auth_methods(MFileauth))
                all_methods = all_methods | set(get_auth_methods(MFileauth))
                done = True
                pass
            except ObjectDoesNotExist:
                pass

        except ObjectDoesNotExist:
            parent = None
            done = True
    return dsAuth, methods_intersection

def render_mfile_auth(request, auth):

    roles = auth.roles

    methodslist = [ pickle.loads(base64.b64decode(method_enc)) for method_enc in roles.all().values_list('methods_encoded',flat=True) ]
    methods = [item for sublist in methodslist for item in sublist]

    methods = utils.get_methods_for_auth(auth)
    logging.info("methods %s" % methods )

    dict = {}
    dict["methods"] = methods
    dict["auth"] = auth

    return render_to_response('auths/mfile_auth.html', dict, context_instance=RequestContext(request))

    subauths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        subauths.append(subauth)
    methods = []
    for role in  auth.roles.all():
        methods  = methods + role.methods()
    form = SubAuthForm()
    form.fields['id_parent'].initial = auth.id
    dict["mfile"] = mfile
    dict["thumburl"] = "%s" % (mfile.thumburl())

    dict["thumburl"] = "/mservemedia/images/empty.png"

    if mfile.thumb == "":
        dict["thumburl"] = "/mservemedia/images/busy.gif"
    else:
        dict["thumburl"] = "%s" % (mfile.thumburl())

    if mfile.file == '' or mfile.file == None:
        dict["altfile"] = "/mservemedia/images/empty.png"
        dict["thumburl"] = "/mservemedia/images/empty.png"
    if not show:
        mfile.file = None
        dict["altfile"] = "/mservemedia/images/forbidden.png"
        dict["thumburl"] = "/mservemedia/images/forbidden.png"

    dict["form"] = form
    dict["auths"] = subauths
    dict["fullaccess"] = False
    dict["methods"] = methods
    dict["formtarget"] = "/form/auth/"
    return render_to_response('auths/mfile_auth.html', dict, context_instance=RequestContext(request))


def auth(request,id):

    sub_auths = JoinAuth.objects.filter(parent=id)
    subauths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        subauths.append(subauth)

    try:
        MFile_auth = MFileAuth.objects.get(id=id)

        form = SubAuthForm()
        dict = {}
        dict["auth"] = MFile_auth
        dict["form"] = form
        dict["subauths"] = subauths

        return render_to_response('auth.html', dict, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
        print "MFileAuth  doesn't exist."

    try:
        container_auth = HostingContainerAuth.objects.get(id=id)
        dict = {}
        dict["auth"] = container_auth
        dict["subauths"] = subauths

        return render_to_response('auth.html', dict, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
        print "HostingContainer Auth doesn't exist."

    try:
        dataservice_auths = DataServiceAuth.objects.get(id=id)
        dict = {}
        dict["auth"] = dataservice_auths

        return render_to_response('auth.html', dict, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
        print "HostingContainer Auth doesn't exist."

    try:
        sub_auth = SubAuth.objects.get(id=id)
        form = SubAuthForm()
        dict = {}
        dict["auth"] = sub_auth
        dict["form"] = form
        dict["subauths"] = subauths

        return render_to_response('auth.html', dict, context_instance=RequestContext(request))
    except ObjectDoesNotExist:
        print "Sub Auth doesn't exist."

    dict = {}
    dict["error"] = "That Authority does not exist"
    return render_to_response('error.html', dict, context_instance=RequestContext(request))


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


    