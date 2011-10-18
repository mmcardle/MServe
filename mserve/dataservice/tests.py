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
from mserve.dataservice.models import HostingContainer
import simplejson as json
from django.test import TestCase
from dataservice.models import *
from jobservice.models import *
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from django.http import HttpRequest

def make_request(get=None,post=None):
    request = HttpRequest()
    if get:
        request.GET = get
    if post:
        request.POST = post
    return request

class ClientTest(TestCase):

    def setUp(self):
        self.password = 'mypassword'
        self.username = 'myuser'
        self.container_name = "testingcontainer"
        self.service_name = "testingservice"
        self.c = Client()
        User.objects.create_superuser(self.username, 'myemail@tempuri.com', self.password)
        self.c.login(username=self.username, password=self.password)
        hc = HostingContainer.create_container(self.container_name)
        hc.save()
        self.hc = hc
        self.hc_post_url = reverse('hostingcontainers')
        self.service_post_url = reverse('dataservices')


    def test_create_container(self):

        unauthclient = Client()
        response = unauthclient.post(self.hc_post_url)
        self.failUnlessEqual(response.status_code,403)

        self.c.login(username='mm', password=self.password)
        response = self.c.post(self.hc_post_url, {"name":self.container_name})
        self.failUnlessEqual(response.status_code,200)

    def test_get_container(self):

        # Test GET Methods
        response = self.c.get(self.hc_post_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(len(js),1)

        hc_url =  reverse('hostingcontainer', args=[self.hc.id])
        response = self.c.get(hc_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],self.container_name)
        self.failUnlessEqual(len(js["dataservice_set"]),0)

    def test_get_container_urls(self):
        containerid = self.hc.id
        hc_url =  reverse('hostingcontainer', args=[containerid])
        hc_url_usage =  reverse('hostingcontainer_usages', args=[containerid])
        hc_url_properties = reverse('hostingcontainer_props', args=[containerid])
        hc_url_auths = reverse('hostingcontainer_auths', args=[containerid])
        hc_url_services = reverse('hostingcontainer_services', args=[containerid])
        hc_url_subservices = reverse('hostingcontainer_subservices', args=[containerid])

        response = self.c.get(hc_url_usage)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        response = self.c.get(hc_url_usage, {"full":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        response = self.c.get(hc_url_usage, {"aggregate":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)
        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(hc_url_usage, {"full":"True","aggregate":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)
        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(hc_url_usage, {"full":"True","aggregate":"True","last":"-1"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(hc_url_auths)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js[0]["roles"]),list)
        self.failUnlessEqual(type(js[0]["thumburl"]),str)
        self.failUnlessEqual(type(js[0]["basename"]),str)
        self.failUnlessEqual(type(js[0]["auth_set"]),list)
        self.failUnlessEqual(type(js[0]["urls"]),dict)
        self.failUnlessEqual(type(js[0]["id"]),str)
        self.failUnlessEqual(type(js[0]["authname"]),str)
        self.failUnlessEqual(js[0]["authname"],"full")

        response = self.c.get(hc_url_services)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js),list)
        self.failUnlessEqual(len(js),0)

        response = self.c.get(hc_url_subservices)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js),list)
        self.failUnlessEqual(len(js),0)

        response = self.c.get(hc_url_properties)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js[0]["property"]),str)
        self.failUnlessEqual(type(js[0]["value"]),str)

        # Test POST Methods
        response = self.c.post(hc_url)
        self.failUnlessEqual(response.status_code,400)

        response = self.c.post(hc_url_usage)
        self.failUnlessEqual(response.status_code,405)

        # Test POST Methods
        response = self.c.post(hc_url_auths,{"name":"newcontainerauthname","roles":"containeradmin"})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["authname"],"newcontainerauthname")
        self.failUnlessEqual(js["roles"],["containeradmin"])

        response = self.c.post(hc_url_services, {"name": "testservice"})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],"testservice")
        self.failUnlessEqual(len(js["mfile_set"]),0)
        serviceid = js["id"]

        response = self.c.post(hc_url_subservices, {"name": "testsubservice", "serviceid": serviceid})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],"testsubservice")
        self.failUnlessEqual(len(js["mfile_set"]),0)

        # Test PUT Methods
        newname = "newcontainername"
        response = self.c.put(hc_url, {"name": newname})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        jsname = js["name"]
        self.failUnlessEqual(jsname, newname)

        newprofile = "newprofile"
        response = self.c.put(hc_url, {"name": "newcontainername","default_profile": newprofile})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        jsprofile = js["default_profile"]
        self.failUnlessEqual(jsprofile, newprofile)

        # Test DELETE Methods
        response = self.c.delete(hc_url)
        self.failUnlessEqual(response.status_code,204)

        response = self.c.get(hc_url)
        self.failUnlessEqual(response.status_code,404)

    def test_get_service(self):
        service = self.hc.create_data_service(self.service_name)
        service.save()
        self.service = service
        self.service_url = reverse('dataservice',args=[service.id])

        # Test GET Methods
        response = self.c.get(self.service_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)

        response = self.c.get(self.service_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],self.service_name)
        self.failUnlessEqual(len(js["mfile_set"]),0)
        self.failUnlessEqual(len(js["mfolder_set"]),0)
        self.failUnlessEqual(js["starttime"],None)
        self.failUnlessEqual(js["endtime"],None)
        self.failUnlessEqual(js["priority"],False)
        self.failUnlessEqual(js["reportnum"],1)

    def test_get_service_urls(self):
        service = self.hc.create_data_service(self.service_name)
        service.save()
        self.service = service
        self.service_url = reverse('dataservice',args=[service.id])
        serviceid = self.service.id
        service_url =  reverse('dataservice', args=[serviceid])
        service_url_usage =  reverse('dataservice_usages', args=[serviceid])
        service_url_properties = reverse('dataservice_props', args=[serviceid])
        service_url_auths = reverse('dataservice_auths', args=[serviceid])
        service_url_mfiles = reverse('dataservice_mfiles', args=[serviceid])
        service_url_mfolders = reverse('dataservice_mfolders', args=[serviceid])
        service_url_subservices = reverse('dataservice_subservices', args=[serviceid])
        service_url_profiles = reverse('dataservice_profiles', args=[serviceid])

        response = self.c.get(service_url_usage)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        response = self.c.get(service_url_usage, {"full":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        response = self.c.get(service_url_usage, {"aggregate":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)
        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(service_url_usage, {"full":"True","aggregate":"True"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)
        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(service_url_usage, {"full":"True","aggregate":"True","last":"-1"} )
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["squares"]),float)
        self.failUnlessEqual(type(js["usages"][0]["nInProgress"]),int)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)
        self.failUnlessEqual(type(js["usages"][0]["reports"]),int)
        self.failUnlessEqual(type(js["usages"][0]["rate"]),float)
        self.failUnlessEqual(type(js["usages"][0]["rateCumulative"]),float)
        self.failUnlessEqual(type(js["usages"][0]["total"]),float)

        metrics = [m["metric"] for m in js["usages"] ]
        self.failUnlessEqual(set(metrics),set(metrics).union(metrics))

        response = self.c.get(service_url_auths)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js[0]["roles"]),list)
        self.failUnlessEqual(type(js[0]["thumburl"]),str)
        self.failUnlessEqual(type(js[0]["basename"]),str)
        self.failUnlessEqual(type(js[0]["auth_set"]),list)
        self.failUnlessEqual(type(js[0]["urls"]),dict)
        self.failUnlessEqual(type(js[0]["id"]),str)
        self.failUnlessEqual(type(js[0]["authname"]),str)
        self.failUnlessEqual(js[0]["authname"],"full")

        response = self.c.get(service_url_mfiles)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js),list)
        self.failUnlessEqual(len(js),0)

        response = self.c.get(service_url_mfolders)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js),list)
        self.failUnlessEqual(len(js),0)

        response = self.c.get(service_url_subservices)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js),list)
        self.failUnlessEqual(len(js),0)

        response = self.c.get(service_url_properties)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(type(js[0]["property"]),str)
        self.failUnlessEqual(type(js[0]["value"]),str)

        response = self.c.get(service_url_profiles)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js[0]["name"], "default")

        # Test POST Methods
        for profile in js:
            for workflow in profile["workflows"]:
                service_url_profiles_tasks = reverse('dataservice_profiles_tasks', args=[serviceid,profile["id"]])
                response = self.c.post(service_url_profiles_tasks,{"workflow":workflow["id"],"condition":"","task_name":"thumbimage","args":""})
                self.failUnlessEqual(response.status_code,200)
                js = json.loads(response.content)

        response = self.c.post(self.service_post_url)
        self.failUnlessEqual(response.status_code,400)

        response = self.c.post(service_url_usage)
        self.failUnlessEqual(response.status_code,405)

        # Test POST Methods
        response = self.c.post(service_url_auths,{"name":"newserviceauthname","roles":"servicecustomer"})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["authname"],"newserviceauthname")
        self.failUnlessEqual(js["roles"],["servicecustomer"])

        response = self.c.post(service_url_auths,{"name":"newserviceauthname2","roles":"serviceadmin"})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["authname"],"newserviceauthname2")
        self.failUnlessEqual(js["roles"],["serviceadmin"])

        response = self.c.post(self.service_post_url, {"name": "testservice", "container": self.hc.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],"testservice")
        self.failUnlessEqual(len(js["mfile_set"]),0)
        serviceid = js["id"]

        response = self.c.post(service_url_subservices, {"name": "testsubservice", "serviceid": serviceid})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],"testsubservice")
        self.failUnlessEqual(len(js["mfile_set"]),0)
        
        # Test PUT Methods
        newname = "newservicename"
        response = self.c.put(service_url, {"name": newname})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        jsname = js["name"]
        self.failUnlessEqual(jsname, newname)

        # Test DELETE Methods
        response = self.c.delete(service_url)
        self.failUnlessEqual(response.status_code,204)
        
        response = self.c.get(service_url)
        self.failUnlessEqual(response.status_code,404)

class APITest(TestCase):

    def test_roles(self):
        container = HostingContainer.create_container("HostingContainer")
        for auth in container.auth_set.all():
            roles = auth.getroles()

        service = container.create_data_service("Service1")
        for auth in service.auth_set.all():
            roles = auth.getroles()

        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        for auth in mfile.auth_set.all():
            roles = auth.getroles()
            
    def test_container(self):
        container = HostingContainer.create_container("HostingContainer1")

        # GET container
        props = container.do("GET","properties")
        self.failUnlessEqual(len(props), 1)

        usagesresult = container.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        # PUT container
        props = container.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 1)

        shouldbe403_1 = container.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":"containeradmin"}
        kwargs = {"full":newroles}
        request = make_request(post=kwargs)

        auths = container.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(auths[0].authname,"full")
        self.failUnlessEqual(len(auths[0].geturls()),4)

        kwargs_2 = {"505authname": {"roles" : ""} }
        request = make_request(post=kwargs_2)
        shouldbe503_3 = container.do("PUT","auths",request=request)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = container.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = container.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = container.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        newroles= "containeradmin"
        kwargs = {"roles":newroles,"name":"newauth"}
        request = make_request(post=kwargs)
        newauth = container.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        badkwargs = {"badkey":"","name":"newauth"}
        request = make_request(post=badkwargs)
        shouldbe503_5 = container.do("POST","auths",request=request)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = container.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = container.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        request = make_request(post={"name":"newauth"})
        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        delauth = container.do("DELETE","auths",request=request)
        self.failUnlessEqual(delauth.status_code,204)
        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

    def test_service(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")

        # GET container
        props = service.do("GET","properties")
        self.failUnlessEqual(len(props), 2)

        usagesresult = service.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        # PUT container
        props = service.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 2)

        shouldbe403_1 = service.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":"serviceadmin"}
        kwargs = {"full":newroles}
        request = make_request(post=kwargs)
        auths = service.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),2)
        self.failUnlessEqual(len(auths[0].geturls()),8)

        kwargs_2 = {"505authname":[]}
        request = make_request(post=kwargs_2)
        shouldbe503_3 = service.do("PUT","auths",request=request)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        badrequest = make_request(post={"urls":[],"name":"newauth"})

        newauthname = "newauthname"
        request = make_request(post={"roles":"serviceadmin","name":newauthname})
        newauth = service.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        shouldbe503_5 = service.do("POST","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        request = make_request(post={"name":newauthname})
        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 3)
        delauth = service.do("DELETE","auths",request=request)
        self.failUnlessEqual(delauth.status_code,204)
        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        emptymfile = service.do("POST","mfiles",name="EmptyFile",file=None)

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        fullfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        ffresp = fullfile.do("GET","file")
        # Status code will depend on time it take to backup
        self.failUnless(ffresp.status_code==302 or ffresp.status_code==410 )

        folder1 = service.do("POST","mfolders",name="folder1")
        shouldbe_409 = service.do("POST","mfolders",name="folder1")
        self.failUnlessEqual(shouldbe_409.status_code,409)
        folders = service.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 1)

        folder2 = service.do("POST","mfolders",name="folder2",parent=folder1)
        shouldbe_409_2 = service.do("POST","mfolders",name="folder2",parent=folder1)
        self.failUnlessEqual(shouldbe_409_2.status_code,409)

        folders = service.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 2)

    def test_subservice(self):
        container = HostingContainer.create_container("HostingContainer1")

        service = container.create_data_service("Service1")
        subservice =  service.create_subservice("SubService")

        file1 = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        self.failUnlessEqual(len(service.do("GET","mfiles")), 1)
        self.failUnlessEqual(len(service.do("GET","mfiles")), len(subservice.do("GET","mfiles")))

        file2 = subservice.do("POST","mfiles",name="FullFile2",file=ContentFile('new content2'))

        self.failUnlessEqual(len(service.do("GET","mfiles")), 2)
        self.failUnlessEqual(len(service.do("GET","mfiles")), len(subservice.do("GET","mfiles")))

        file1.file.open()
        filecontents1 = file1.file.read()
        self.failUnlessEqual(filecontents1, 'new content')
        file1.file.close()

        try:
            wfile = open(file2.file.path,'r+b')
            try:
                wfile.write('XXX')
            finally:
                wfile.close()
        except IOError:
            logging.error("Error writing partial content to MFile '%s'" % file2)

        file2.file.open()
        filecontents2 = file2.file.read()
        self.failUnlessEqual(filecontents2, 'XXX content2')
        file2.file.close()

        readfile = subservice.do("GET","mfiles")[0]
        readfile.file.open()
        filecontents3 = readfile.file.read()
        self.failUnlessEqual(filecontents3, 'XXX content2')
        readfile.file.close()

        file1.do("DELETE")
        self.failUnlessEqual(len(service.do("GET","mfiles")), 1)
        self.failUnlessEqual(len(subservice.do("GET","mfiles")), 1)

        file2.do("DELETE")
        self.failUnlessEqual(len(service.do("GET","mfiles")), 0)
        self.failUnlessEqual(len(subservice.do("GET","mfiles")), 0)

    def test_serviceauth(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")
        request = make_request(post={"roles":"serviceadmin","name":"newauth"})

        service_auth = service.do("POST","auths",request=request)

        # GET service auth
        props = service_auth.do("GET","properties")
        self.failUnlessEqual(len(props), 2)

        usagesresult = service_auth.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT
        props = service_auth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 2)

        shouldbe403_1 = service_auth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        request = make_request(post={"roles":"serviceadmin","name":"newsubauth"})

        service_auth.do("POST","auths",request=request)

        newroles= {"roles":"serviceadmin"}
        request = make_request(post={"newsubauth":newroles})
        auths = service_auth.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),8)

        badrequest = make_request(post={"505authname":""})
        shouldbe503_3 = service_auth.do("PUT","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service_auth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service_auth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service_auth.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        badrequest = make_request(post={"badkey":"","name":"newauth"})

        request = make_request(post={"roles":"serviceadmin","name":"newauth"})
        newauth = service_auth.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        shouldbe503_5 = service_auth.do("POST","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service_auth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service_auth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        request = make_request(post={"name":"newauth"})
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = service_auth.do("DELETE","auths",request=request)
        self.failUnlessEqual(delauth.status_code,204)
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        emptymfile = service_auth.do("POST","mfiles",name="EmptyFile",file=None)

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        fullfile = service_auth.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        ffile = fullfile.do("GET","file")
        # Status code will depend on time it take to backup
        self.failUnless(ffile.status_code==302 or ffile.status_code==410 )

        folder1 = service_auth.do("POST","mfolders",name="folder1")
        shouldbe_409 = service_auth.do("POST","mfolders",name="folder1")
        self.failUnlessEqual(shouldbe_409.status_code,409)
        folders = service_auth.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 1)

        folder2 = service_auth.do("POST","mfolders",name="folder2",parent=folder1)
        shouldbe_409_2 = service_auth.do("POST","mfolders",name="folder2",parent=folder1)
        self.failUnlessEqual(shouldbe_409_2.status_code,409)

        folders = service_auth.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 2)

        jobs = service_auth.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 2)

    def test_serviceauth_customer(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")
        
        # Start testing service auth customer
        request = make_request(post={"roles":"servicecustomer","name":"newauth"})
        service_auth = service.do("POST","auths",request=request)

        # Create 1 files on the service
        service_auth.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        
        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        mfile = service.do("GET","mfiles")[0]

        request = {"file":ContentFile('four')}
        updatedmfile = mfile.do("PUT",**request)
        self.failUnlessEqual(updatedmfile.size, 4)

        service_auth_2 = service_auth.do("GET")
        self.failUnlessEqual(type(service_auth_2), Auth)

        shouldbe_mfile = service_auth.do("DELETE")
        self.failUnlessEqual(type(shouldbe_mfile), HttpResponseForbidden)

        # GET service auth
        props = service_auth.do("GET","properties")
        self.failUnlessEqual(len(props), 2)

        usagesresult = service_auth.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT 
        shouldbe403_0= service_auth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe403_0),HttpResponseForbidden)

        shouldbe403_1 = service_auth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        request = make_request(post={"roles":"serviceadmin","name":"newsubauth"})
        service_auth.do("POST","auths",request=request)

        newroles= {"roles":"serviceadmin"}
        request = make_request(post={"newsubauth":newroles})
        auths = service_auth.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),8)

        badrequest = make_request(post={"505authname":[]})
        shouldbe503_3 = service_auth.do("PUT","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service_auth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service_auth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service_auth.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        
        request = make_request(post={"roles":"serviceadmin","name":"newauth"})
        newauth = service_auth.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        badrequest = make_request(post={"badkey":[],"name":"newauth"})
        shouldbe503_5 = service_auth.do("POST","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service_auth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service_auth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        request = make_request(post={"name":"newauth"})
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = service_auth.do("DELETE","auths",request=request)
        self.failUnlessEqual(delauth.status_code,204)
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        shouldbe_mfile = service_auth.do("POST","mfiles",name="EmptyFile",file=None)
        self.failUnlessEqual(type(shouldbe_mfile), MFile)

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        shouldbe_mfile = service_auth.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        self.failUnlessEqual(type(shouldbe_mfile), MFile)

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 3)

        shouldbe_mfolder = service_auth.do("POST","mfolders",name="folder1")
        self.failUnlessEqual(type(shouldbe_mfolder), MFolder)
        folders = service_auth.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 1)

        jobs = service_auth.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 4)

    def test_mfile(self):
        service = HostingContainer.create_container("HostingContainer1").create_data_service("Service1")
        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        # GET container
        shouldbe_403 = mfile.do("GET","properties")
        self.failUnlessEqual(type(shouldbe_403), HttpResponseForbidden)

        usageresult = mfile.do("GET","usages")
        self.failUnlessEqual(type(usageresult["usages"][0]), type(Usage()))

        auths = mfile.do("GET","auths")
        self.failUnlessEqual(type(auths[0]), type(Auth()))

        # PUT container
        shouldbe_403_2 = mfile.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe_403_2), HttpResponseForbidden)

        shouldbe403_1 = mfile.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":"mfileowner"}
        request = make_request(post={"owner":newroles})
        auths = mfile.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),5)

        badrequest = make_request(post={"505authname":[]})
        shouldbe503_3 = mfile.do("PUT","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = mfile.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = mfile.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = mfile.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        request = make_request(post={"roles":"mfileowner","name":"newauth"})
        newauth = mfile.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        badrequest =  make_request(post={"badkey":"","name":"newauth"})
        shouldbe503_5 = mfile.do("POST","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = mfile.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = mfile.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        request = make_request(post={"name":"newauth"})
        auths = mfile.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = mfile.do("DELETE","auths",request=request)
        self.failUnlessEqual(delauth.status_code,204)
        auths = mfile.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        request = {"file":ContentFile('four')}
        updatedmfile = mfile.do("PUT",**request)
        self.failUnlessEqual(updatedmfile.size, 4)

        job = mfile.do("POST","jobs",name="job1")
        self.failUnlessEqual(type(job), Job)

        jobs = mfile.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 3)
        
    def test_mfile_readonly(self):
        service = HostingContainer.create_container("HostingContainer1").create_data_service("Service1")
        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        request = make_request(post={"name":"newreadonlyauth","roles":"mfilereadonly"})
        mfileauth = mfile.do("POST","auths",request=request)

        # GET 
        shouldbe_403 = mfileauth.do("GET","properties")
        self.failUnlessEqual(type(shouldbe_403), HttpResponseForbidden)

        usagesresult = mfileauth.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 4)

        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT 
        shouldbe_403_2 = mfileauth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe_403_2), HttpResponseForbidden)

        shouldbe403_1 = mfileauth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        badrequest = make_request(post={"505authname":[]})
        shouldbe503_3 = mfileauth.do("PUT","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST
        shouldbe403_2 = mfileauth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = mfileauth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        request = make_request(post={"name":"newerreadonlyauth","roles":"mfilereadonly"})
        mfileauthsubauth = mfileauth.do("POST","auths", request=request)
        
        self.failUnlessEqual(type(mfileauthsubauth), Auth)
        #self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        request = make_request(post={"roles":"mfileowner","name":"newauth"})
        newauth = mfileauth.do("POST","auths",request=request)
        self.failUnlessEqual(type(newauth), Auth)

        badrequest = make_request(post={"badkey":[],"name":"newauth"})
        shouldbe503_5 = mfileauth.do("POST","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE
        shouldbe403_4 = mfileauth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = mfileauth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)
        
        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        request = make_request(post={"name":"newerreadonlyauth"})
        delauth = mfileauth.do("DELETE","auths",request=request)

        self.failUnlessEqual(delauth.status_code,204)
        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        request = {"file":ContentFile('four')}
        updatedmfile_403 = mfileauth.do("PUT",**{"request":request})
        self.failUnlessEqual(type(updatedmfile_403), HttpResponseForbidden)

