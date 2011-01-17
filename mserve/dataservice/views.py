from mserve.dataservice.models import MFileAuth
from mserve.dataservice.models import Auth
import os.path
from mserve.dataservice.models import *
from mserve.dataservice.forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template import RequestContext
from piston.utils import rc
import usage_store as usage_store
import utils as utils
import api as api
import handlers as handlers
import logging

from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

#from dataservice.tasks import ProcessVideoTask
from dataservice.tasks import thumbvideo
from dataservice.tasks import render_blender
from django.http import HttpResponse
from django.shortcuts import redirect

#@staff_member_required
def home(request,form=HostingContainerForm()):
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
    return render_to_response('home.html', dict, context_instance=RequestContext(request))

def thumb(request,mfileid):
    mfile = MFile.objects.get(pk=mfileid)
    dict = {}
    dict["mfile"] = mfile
    r = render_to_response('mfilethumb.html', dict, context_instance=RequestContext(request))
    return r

@login_required
def profile(request):
    dict ={}
    return render_to_response('user.html', dict, context_instance=RequestContext(request))

def create_container(request):
    form = HostingContainerForm(request.POST)
    if form.is_valid():

        name = form.cleaned_data['name']
        hostingcontainer = api.create_container(request,name)

        return redirect('/browse/container/'+str(hostingcontainer.id))
    else:
        return home(request,form=form)

#@staff_member_required
def render_container(request,id,form=DataServiceForm()):
    container = HostingContainer.objects.get(pk=id)
    auths = HostingContainerAuth.objects.filter(hostingcontainer=container.id)
    roles = Role.objects.filter(auth=auths)
    methods = []
    for role in roles:
        methods  = methods + role.methods()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    form.fields['cid'].initial = id
    usagerates = UsageRate.objects.filter(base=container)
    usage = Usage.objects.filter(base=container)
    usagesummary = usage_store.container_usagesummary(container)

    managementpropertyform = ManagementPropertyForm()
    dict = {}
    dict["container"] = container
    dict["services"] = services
    dict["properties"] = properties
    dict["form"] = form
    dict["managementpropertyform"] = managementpropertyform
    dict["auths"] = auths
    dict["usage"] = usage
    dict["usagerate"] = usagerates
    dict["usagesummary"] = usagesummary
    dict["roles"] = roles
    dict["methods"] = methods

    return render_to_response('container.html', dict, context_instance=RequestContext(request))

def render_containerauth(request,authid,form=DataServiceForm()):
    #container = HostingContainer.objects.get(pk=id)
    hca = HostingContainerAuth.objects.get(pk=authid)
    container=hca.hostingcontainer
    sub_auths = JoinAuth.objects.filter(parent=authid)
    auths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        auths.append(subauth)
    roles = Role.objects.filter(auth=auths)
    #roles = hca.roles.all()
    methods = []
    for role in  hca.roles.all():
        methods  = methods + role.methods()
    services = DataService.objects.filter(container=container.id)
    properties = ManagementProperty.objects.filter(base=container.id)
    form.fields['cid'].initial = container.id
    usagerates = UsageRate.objects.filter(base=container)
    usage = Usage.objects.filter(base=container)
    usagesummary = usage_store.container_usagesummary(container)

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
    dict["usagerate"] = usagerates
    dict["usagesummary"] = usagesummary
    dict["roles"] = roles
    dict["methods"] = methods
    
    return render_to_response('container.html', dict, context_instance=RequestContext(request))

def create_service(request):
    form = DataServiceForm(request.POST)
    if form.is_valid():

        containerid = form.cleaned_data['cid']
        name = form.cleaned_data['name']
        dataservice = api.create_data_service(request,containerid,name)

        return redirect('/browse/service/'+str(dataservice.id))
    else:
        containerid = form.data['cid']
        return render_container(request,containerid,form=form)

#@staff_member_required
def render_service(request,id,form=MFileForm(),newmfile=None):
    service = DataService.objects.get(pk=id)
    mfiles = MFile.objects.filter(service=service).order_by('created').reverse()
    properties = ManagementProperty.objects.filter(base=service)
    auths = DataServiceAuth.objects.filter(dataservice=id)
    roles = Role.objects.filter(auth=auths)
    methods = []
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
    dict["usage"] = Usage.objects.filter(base=service)
    dict["usagerate"] = UsageRate.objects.filter(base=service)
    dict["usagesummary"] = usage_store.service_usagesummary(service.id)
    dict["methods"] = methods
    if newmfile is not None:
        dict["newmfile"] = newmfile
    return render_to_response('service.html', dict, context_instance=RequestContext(request))

def render_serviceauth(request,authid,form=MFileForm()):
    dsa = DataServiceAuth.objects.get(pk=authid)
    service = dsa.dataservice
    mfiles = MFile.objects.filter(service=service)
    properties = ManagementProperty.objects.filter(base=service)
    #auths = DataServiceAuth.objects.filter(dataservice=id)
    sub_auths = JoinAuth.objects.filter(parent=authid)
    auths = []
    for sub in sub_auths:
        subauth = SubAuth.objects.get(id=sub.child)
        auths.append(subauth)
    methods = []
    for role in  dsa.roles.all():
        methods  = methods + role.methods()
    roles = Role.objects.filter(auth=auths)
    managementpropertyform = ManagementPropertyForm()
    form.fields['sid'].initial = service.id
    dict = {}
    dict["properties"] = properties
    dict["managementpropertyform"] = managementpropertyform
    dict["service"] = service
    dict["mfiles"] = mfiles
    dict["auths"] = auths
    dict["roles"] = roles
    dict["jobs"] = service.job_set
    dict["form"] = form
    dict["usage"] = Usage.objects.filter(base=service)
    dict["usagerate"] = UsageRate.objects.filter(base=service)
    dict["usagesummary"] = usage_store.service_usagesummary(service.id)
    dict["methods"] = methods
    return render_to_response('service.html', dict, context_instance=RequestContext(request))

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

        return redirect('/browse/auth/%s/' % str(subauth.id))

    else:
        return render_error(request,form)

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

        return redirect('/browse/mfile/'+str(mfile.id)+"/")
    else:
        serviceid = form.data['sid']
        return render_service(request,serviceid,form=form)

def render_mfile(request,id, form=MFileAuthForm(), show=False):
    mfile = MFile.objects.get(pk=id)

    auths = MFileAuth.objects.filter(mfile=id)
    roles = Role.objects.filter(auth=auths)
    methods = []
    for role in roles:
        methods  = methods + role.methods()
    form.fields['dsid'].initial = mfile.id
    dict = {}

    dict["thumburl"] = "/mservemedia/images/empty.png"

    if mfile.thumb == "":
        dict["thumburl"] = "/mservemedia/images/busy.gif"
    else:
        dict["thumburl"] = "%s%s" % ("/mservethumbs/",mfile.thumb)

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
    dict["form"] = form
    dict["auths"] = auths
    dict["formtarget"] = "/mfileauth/"
    dict["usage"] = Usage.objects.filter(base=mfile)
    dict["usagerate"] = UsageRate.objects.filter(base=mfile)
    dict["usagesummary"] = usage_store.mfile_usagesummary(mfile.id)
    dict["roles"] = roles
    dict["methods"] = methods
    
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

def render_mfileauth(request, mfile, auth, show=False, dict={}):
    sub_auths = JoinAuth.objects.filter(parent=auth.id)
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
    dict["thumburl"] = "%s%s%s" % ("/mservethumbs/",mfile.file,".thumb.jpg")

    dict["thumburl"] = "/mservemedia/images/empty.png"

    if mfile.thumb == "":
        dict["thumburl"] = "/mservemedia/images/busy.gif"
    else:
        dict["thumburl"] = "%s%s" % ("/mservethumbs/",mfile.thumb)

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
    return render_to_response('mfile.html', dict, context_instance=RequestContext(request))

#@staff_member_required
def usage(request):
    usagesummary = usage_store.usagesummary()
    usagerate = UsageRate.objects.all()
    usage = Usage.objects.all()
    dict = {}
    dict["usage"] = usage
    dict["usagesummary"] = usagesummary
    dict["usagerate"] = usagerate
    return render_to_response('allusage.html', dict, context_instance=RequestContext(request))

#@staff_member_required
def viz(request):
    dict={}

    hostings = HostingContainer.objects.all()

    rows = []
    for hosting in hostings:
        services = DataService.objects.filter(container=hosting)
        totalservices = len(services)
        totalmfiles = 0
        totaldisc = 0.0
        for service in services:
            mfiles = MFile.objects.filter(service=service)
            totalmfiles += len(mfiles)
            for mfile in mfiles:
                if mfile.file != None and mfile.file != "":
                    totaldisc    += mfile.file.size

        n = {"c":[{"v": str(hosting.name)}, {"v": totalservices}, {"v": totalmfiles}, {"v": totaldisc}]}
        rows.append(n)


    viz_data = {
        "cols":
                [   {"id": 'container', "label": 'Container', "type": 'string'},
                    {"id": 'services', "label": 'Services', "type": 'number'},
                    {"id": 'mfiles', "label": 'Files', "type": 'number'},
                    {"id": 'mfiles', "disc": 'Disc', "type": 'number'}
                ],
        "rows": [
                    {"c":[{"v": 'Work'},     {"v": 11}]},
                    {"c":[{"v": 'Eat'},     {"v": 2 }]},
                    {"c":[{"v": 'Commute'}, {"v": 2 }]}
                ]
            }

    viz_data = {
        "cols":
                [   {"id": 'container', "label": 'Container', "type": 'string'},
                    {"id": 'services', "label": 'Services', "type": 'number'},
                    {"id": 'mfiles', "label": 'Files', "type": 'number'},
                    {"id": 'disc', "label": 'Disc', "type": 'number'}
                ],
        "rows": rows
            }

    dict["viz_data"] = viz_data
    return render_to_response('viz.html', dict, context_instance=RequestContext(request))

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


#@staff_member_required
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
            mfiles = MFile.objects.filter(service=service)
            for mfile in mfiles:
                id  = str(mfile.id)
                name  = str(mfile.name)
                row = Row( value=id, name=name, parent=service.id, tip=mfile.name)
                rows.append(row)
                mfileauths = MFileAuth.objects.filter(mfile=mfile)
                for mfileauth in mfileauths:
                    row = Row(name=mfileauth.authname, value=mfileauth.id, parent=mfile.id, tip=mfileauth.authname)
                    rows.append(row)


    joins = JoinAuth.objects.all()
    for join in joins:
        c = join.child
        p = join.parent

        subs = SubAuth.objects.get(id=c)
        try:
            dsauth = MFileAuth.objects.get(id=p)
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
    return render_to_response('map.html', dict, context_instance=RequestContext(request))

def render_error(request,error):
    dict = {}
    dict["error"] = error
    return render_to_response('error.html', dict, context_instance=RequestContext(request))

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


    