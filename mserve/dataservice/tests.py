from django.http import HttpResponseRedirect
from django.test import TestCase
from dataservice.models import *
from jobservice.models import *
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotFound
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
import simplejson

class APITest(TestCase):
    
    def test_container(self):
        container = HostingContainer.create_container("HostingContainer1")

        # GET container
        props = container.do("GET","properties")
        self.failUnlessEqual(len(props), 1)

        usages = container.do("GET","usages")
        self.failUnlessEqual(len(usages), 1)

        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        # PUT container
        props = container.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 1)

        shouldbe403_1 = container.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":["containeradmin"]}
        kwargs = {"full":newroles}
        auths = container.do("PUT","auths",**kwargs)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(auths[0].authname,"full")
        self.failUnlessEqual(len(auths[0].geturls()),4)

        kwargs_2 = {"505authname": {"roles" : []} }
        shouldbe503_3 = container.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = container.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = container.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = container.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        newroles= ["containeradmin"]
        kwargs = {"roles":newroles,"name":"newauth"}
        newauth = container.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        badkwargs = {"badkey":[],"name":"newauth"}
        shouldbe503_5 = container.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = container.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = container.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        kwargs = {"name":"newauth"}
        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = container.do("DELETE","auths",**kwargs)
        self.failUnlessEqual(delauth.status_code,204)
        auths = container.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)


    def test_service(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")

        # GET container
        props = service.do("GET","properties")
        self.failUnlessEqual(len(props), 1)

        usages = service.do("GET","usages")
        self.failUnlessEqual(len(usages), 1)

        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        # PUT container
        props = service.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 1)

        shouldbe403_1 = service.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":["serviceadmin"]}
        kwargs = {"full":newroles}
        auths = service.do("PUT","auths",**kwargs)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),2)
        self.failUnlessEqual(len(auths[0].geturls()),6)

        kwargs_2 = {"505authname":[]}
        shouldbe503_3 = service.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        badkwargs = {"urls":[],"name":"newauth"}

        newauthname = "newauthname"
        kwargs = {"roles":["serviceadmin"],"name":newauthname}
        newauth = service.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        shouldbe503_5 = service.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        kwargs = {"name":newauthname}
        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 3)
        delauth = service.do("DELETE","auths",**kwargs)
        self.failUnlessEqual(delauth.status_code,204)
        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        emptymfile = service.do("POST","mfiles",name="EmptyFile",file=None)

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        fullfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        efile = emptymfile.do("GET","file")
        self.failUnlessEqual(type(efile), HttpResponseNotFound)

        ffile = fullfile.do("GET","file")
        self.failUnlessEqual(type(ffile), HttpResponseRedirect)

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

        job = service.do("POST","jobs",name="folder1")
        self.failUnlessEqual(type(job), Job)

        jobs = service.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 1)

    def test_serviceauth(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")
        kwargs = {"roles":["serviceadmin"],"name":"newauth"}

        service_auth = service.do("POST","auths",**kwargs)

        # GET service auth
        props = service_auth.do("GET","properties")
        self.failUnlessEqual(len(props), 1)

        usages = service_auth.do("GET","usages")
        self.failUnlessEqual(len(usages), 0)

        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT
        props = service_auth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(len(props), 1)

        shouldbe403_1 = service_auth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        kwargs = {"roles":["serviceadmin"],"name":"newsubauth"}

        service_auth.do("POST","auths",**kwargs)

        newroles= {"roles":["serviceadmin"]}
        kwargs = {"newsubauth":newroles}
        auths = service_auth.do("PUT","auths",**kwargs)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),6)

        kwargs_2 = {"505authname":[]}
        shouldbe503_3 = service_auth.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service_auth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service_auth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service_auth.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        badkwargs = {"badkey":[],"name":"newauth"}

        kwargs = {"roles":["serviceadmin"],"name":"newauth"}
        newauth = service_auth.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        shouldbe503_5 = service_auth.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service_auth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service_auth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        kwargs = {"name":"newauth"}
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = service_auth.do("DELETE","auths",**kwargs)
        self.failUnlessEqual(delauth.status_code,204)
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        emptymfile = service_auth.do("POST","mfiles",name="EmptyFile",file=None)

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        fullfile = service_auth.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        files = service_auth.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        efile = emptymfile.do("GET","file")
        self.failUnlessEqual(type(efile), HttpResponseNotFound)

        ffile = fullfile.do("GET","file")
        self.failUnlessEqual(type(ffile), HttpResponseRedirect)

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

        job = service_auth.do("POST","jobs",name="folder1")
        self.failUnlessEqual(type(job), Job)

        jobs = service_auth.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 1)

    def test_serviceauth_customer(self):
        container = HostingContainer.create_container("HostingContainer1")
        service = container.create_data_service("Service1")
        
        # Start testing service auth customer
        kwargs = {"roles":["servicecustomer"],"name":"newauth"}
        service_auth = service.do("POST","auths",**kwargs)

        # Create 1 files on the service
        service_auth.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        
        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        mfile = service.do("GET","mfiles")[0]

        kwargs = {"file":ContentFile('four')}
        updatedmfile = mfile.do("PUT",**kwargs)
        self.failUnlessEqual(updatedmfile.size, 4)

        service_auth_2 = service_auth.do("GET")
        self.failUnlessEqual(type(service_auth_2), Auth)

        shouldbe_mfile = service_auth.do("DELETE")
        self.failUnlessEqual(type(shouldbe_mfile), HttpResponseForbidden)

        # GET service auth
        props = service_auth.do("GET","properties")
        self.failUnlessEqual(len(props), 1)

        usages = service_auth.do("GET","usages")
        self.failUnlessEqual(len(usages), 0)

        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT 
        shouldbe403_0= service_auth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe403_0),HttpResponseForbidden)

        shouldbe403_1 = service_auth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        kwargs = {"roles":["serviceadmin"],"name":"newsubauth"}

        service_auth.do("POST","auths",**kwargs)

        newroles= {"roles":["serviceadmin"]}
        kwargs = {"newsubauth":newroles}
        auths = service_auth.do("PUT","auths",**kwargs)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),6)

        kwargs_2 = {"505authname":[]}
        shouldbe503_3 = service_auth.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = service_auth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = service_auth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = service_auth.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        badkwargs = {"badkey":[],"name":"newauth"}

        kwargs = {"roles":["serviceadmin"],"name":"newauth"}
        newauth = service_auth.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        shouldbe503_5 = service_auth.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = service_auth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = service_auth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        kwargs = {"name":"newauth"}
        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = service_auth.do("DELETE","auths",**kwargs)
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

        shouldbe_job = service_auth.do("POST","jobs",name="folder1")
        self.failUnlessEqual(type(shouldbe_job), Job)

        jobs = service_auth.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 1)

    def test_mfile(self):
        service = HostingContainer.create_container("HostingContainer1").create_data_service("Service1")
        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        # GET container
        shouldbe_403 = mfile.do("GET","properties")
        self.failUnlessEqual(type(shouldbe_403), HttpResponseForbidden)

        usages = mfile.do("GET","usages")
        self.failUnlessEqual(len(usages), 3)

        auths = mfile.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        # PUT container
        shouldbe_403_2 = mfile.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe_403_2), HttpResponseForbidden)

        shouldbe403_1 = mfile.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":["mfileowner"]}
        kwargs = {"owner":newroles}
        auths = mfile.do("PUT","auths",**kwargs)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].geturls()),5)

        kwargs_2 = {"505authname":[]}
        shouldbe503_3 = mfile.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST container
        shouldbe403_2 = mfile.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = mfile.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe503_4 = mfile.do("POST","auths")
        self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        kwargs = {"roles":["mfileowner"],"name":"newauth"}
        newauth = mfile.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        badkwargs = {"badkey":[],"name":"newauth"}
        shouldbe503_5 = mfile.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE container
        shouldbe403_4 = mfile.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = mfile.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        kwargs = {"name":"newauth"}
        auths = mfile.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)
        delauth = mfile.do("DELETE","auths",**kwargs)
        self.failUnlessEqual(delauth.status_code,204)
        auths = mfile.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        kwargs = {"file":ContentFile('four')}
        updatedmfile = mfile.do("PUT",**kwargs)
        self.failUnlessEqual(updatedmfile.size, 4)
        
    def test_mfile_readonly(self):
        service = HostingContainer.create_container("HostingContainer1").create_data_service("Service1")
        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))

        kwargs = {"name":"newreadonlyauth","roles":["mfilereadonly"]}
        mfileauth = mfile.do("POST","auths",**kwargs)

        # GET 
        shouldbe_403 = mfileauth.do("GET","properties")
        self.failUnlessEqual(type(shouldbe_403), HttpResponseForbidden)

        usages = mfileauth.do("GET","usages")
        self.failUnlessEqual(len(usages), 0)

        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT 
        shouldbe_403_2 = mfileauth.do("PUT","properties",{"accesspeed":100})
        self.failUnlessEqual(type(shouldbe_403_2), HttpResponseForbidden)

        shouldbe403_1 = mfileauth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        kwargs_2 = {"505authname":[]}
        shouldbe503_3 = mfileauth.do("PUT","auths",**kwargs_2)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST
        shouldbe403_2 = mfileauth.do("POST","properties")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = mfileauth.do("POST","usages")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        kwargs = {"name":"newerreadonlyauth","roles":["mfilereadonly"]}
        mfileauthsubauth = mfileauth.do("POST","auths", **kwargs)
        
        self.failUnlessEqual(type(mfileauthsubauth), Auth)
        #self.failUnlessEqual(type(shouldbe503_4), HttpResponseBadRequest)

        kwargs = {"roles":["mfileowner"],"name":"newauth"}
        newauth = mfileauth.do("POST","auths",**kwargs)
        self.failUnlessEqual(type(newauth), Auth)

        badkwargs = {"badkey":[],"name":"newauth"}
        shouldbe503_5 = mfileauth.do("POST","auths",**badkwargs)
        self.failUnlessEqual(type(shouldbe503_5), HttpResponseBadRequest)

        # DELETE
        shouldbe403_4 = mfileauth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = mfileauth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        
        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        kwargs = {"name":"newerreadonlyauth"}
        delauth = mfileauth.do("DELETE","auths",**kwargs)

        self.failUnlessEqual(delauth.status_code,204)
        auths = mfileauth.do("GET","auths")
        self.failUnlessEqual(len(auths), 1)

        kwargs = {"file":ContentFile('four')}
        updatedmfile_403 = mfileauth.do("PUT",**kwargs)
        self.failUnlessEqual(type(updatedmfile_403), HttpResponseForbidden)


'''def test_objects(self):

        container = HostingContainer.create_container("HostingContainer1")

        kwargs = {"accessspeed":50}
        container.do("PUT","properties",**kwargs)

        services = container.do("GET","services")
        self.failUnlessEqual(len(services), 0)

        badkwargs = {"badproperty":50}
        shouldbe404_1 = container.do("PUT","properties",**badkwargs)
        self.failUnlessEqual(type(shouldbe404_1), HttpResponseNotFound)

        service = container.do("POST","services",name="Service1")

        services = container.do("GET","services")
        self.failUnlessEqual(len(services), 1)

        folders = service.do("GET","mfolders")
        files = service.do("GET","mfiles")
        jobs = service.do("GET","jobs")

        self.failUnlessEqual(len(folders), 0)
        self.failUnlessEqual(len(files), 0)
        self.failUnlessEqual(len(jobs), 0)

        emptyfile = service.do("POST","mfiles",name="EmptyFile",file=None)

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 1)

        fullfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        fullfile.do("GET","auths")
        fullfile.do("GET","properties")
        fullfile.do("GET","usages")

        files = service.do("GET","mfiles")
        self.failUnlessEqual(len(files), 2)

        folder = service.do("POST","mfolders",name="folder1")
        folder.do("GET","auths")
        folder.do("GET","properties")
        folder.do("GET","usages")

        folders = service.do("GET","mfolders")
        self.failUnlessEqual(len(folders), 1)

        job = service.do("POST","jobs",name="folder1")
        job.do("GET","auths")
        job.do("GET","properties")
        job.do("GET","usages")

        jobs = service.do("GET","jobs")
        self.failUnlessEqual(len(jobs), 1)

        file = fullfile.do("GET","file")

        print "#### "
        print file
        print "#### "

        container.do("GET","auths")
        container.do("GET","properties")
        container.do("GET","usages")

        service.do("GET","auths")
        service.do("GET","properties")
        service.do("GET","usages")


        print "#### FOLDERS ####"
        print folders
        print "#### "

        emptyfile.do("GET","auths")
        emptyfile.do("GET","properties")
        emptyfile.do("GET","usages")

        shouldbe410_1 = emptyfile.do("GET","file")
        self.failUnlessEqual(type(shouldbe410_1.status_code), type(rc.NOT_HERE.status_code))


        print "#### "
        print container
        print service
        print emptyfile
        print "#### "
        print ""

        container.do("GET")
        service.do("GET")
        emptyfile.do("GET")

        shouldbe404_1 = container.do("GET","a404")
        self.failUnlessEqual(type(shouldbe404_1), HttpResponseNotFound)
        shouldbe404_2 = service.do("GET","a404")
        self.failUnlessEqual(type(shouldbe404_2), HttpResponseNotFound)
        shouldbe404_3 = emptyfile.do("GET","a404")
        self.failUnlessEqual(type(shouldbe404_3), HttpResponseNotFound)

        cauth = container.do("POST","auths",name="newauth",methods="GET,POST,PUT,DELETE")
        sauth = service.do("POST","auths",name="newauth",methods="GET,POST,PUT,DELETE")
        mauth = emptyfile.do("POST","auths",name="newauth",methods="GET,POST,PUT,DELETE")

        cauth.do("GET")
        sauth.do("GET")
        mauth.do("GET")

        print "#### "
        print cauth
        print sauth
        print mauth
        print "#### "
        print ""

        submauth = mauth.do("POST","auths",name="newsubauth")

        print "#### "
        print submauth
        print "#### "
        print ""

        submauth.setmethods([])
        submauth.seturls({
                "auths":[],\
                "properties":[],\
                "usages":[]\
                })
        submauth.save()

        shouldbe403_1 = submauth.do("POST","auths",name="newsubsubauth",methods="GET,POST,PUT,DELETE")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        shouldbe403_2 = submauth.do("POST","properties",name="newsubsubauth",methods="GET,POST,PUT,DELETE")
        self.failUnlessEqual(type(shouldbe403_2), HttpResponseForbidden)

        shouldbe403_3 = submauth.do("POST","usages",name="newsubsubauth",methods="GET,POST,PUT,DELETE")
        self.failUnlessEqual(type(shouldbe403_3), HttpResponseForbidden)

        shouldbe403_4 = submauth.do("GET","auths")
        self.failUnlessEqual(type(shouldbe403_4), HttpResponseForbidden)

        shouldbe403_5 = submauth.do("GET","properties")
        self.failUnlessEqual(type(shouldbe403_5), HttpResponseForbidden)

        shouldbe403_6 = submauth.do("GET","usages")
        self.failUnlessEqual(type(shouldbe403_6), HttpResponseForbidden)

        shouldbe403_7 = submauth.do("PUT","auths")
        self.failUnlessEqual(type(shouldbe403_7), HttpResponseForbidden)

        shouldbe403_8 = submauth.do("PUT","properties")
        self.failUnlessEqual(type(shouldbe403_8), HttpResponseForbidden)

        shouldbe403_9 = submauth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_9), HttpResponseForbidden)

        shouldbe403_10 = submauth.do("DELETE","auths")
        self.failUnlessEqual(type(shouldbe403_10), HttpResponseForbidden)

        shouldbe403_11 = submauth.do("DELETE","properties")
        self.failUnlessEqual(type(shouldbe403_11), HttpResponseForbidden)

        shouldbe403_12 = submauth.do("DELETE","usages")
        self.failUnlessEqual(type(shouldbe403_12), HttpResponseForbidden)

        mfileid = emptyfile.id
        emptyfile.do("DELETE")
        mfile_deleted = False
        try:
            MFile.objects.get(id=mfileid)
        except MFile.DoesNotExist:
            mfile_deleted = True
        self.failUnlessEqual(mfile_deleted, True)

        fullfile.do("DELETE")

        serviceid = service.id
        service.do("DELETE")
        service_deleted = False
        try:
            DataService.objects.get(id=serviceid)
        except DataService.DoesNotExist:
            service_deleted = True
        self.failUnlessEqual(service_deleted, True)

        containerid = container.id
        container.do("DELETE")
        container_deleted = False
        try:
            HostingContainer.objects.get(id=containerid)
        except HostingContainer.DoesNotExist:
            container_deleted = True
        self.failUnlessEqual(container_deleted, True)'''


'''
class SimpleTest(TestCase):
    def test_objects(self):        
        container = HostingContainer(name="HostingContainer1")
        container.save()
        container2 = HostingContainer.objects.get(id=container.id)
        self.failUnlessEqual(container, container2)
        
        service = DataService(name="DataService",container=container)
        service.save()
        service2 = DataService.objects.get(id=service.id)
        self.failUnlessEqual(service, service2)
        
        mfile = MFile(name="MFile",service=service,empty=True)
        mfile.save()
        mfile2 = MFile.objects.get(id=mfile.id)
        self.failUnlessEqual(mfile, mfile2)

        mfileauth = Auth(authname="MFileAuth",base=mfile)
        mfileauth.save()
        MFileauth2 = Auth.objects.get(id=mfileauth.id)
        self.failUnlessEqual(mfileauth, MFileauth2)

        subauth = Auth(authname="SubAuth",parent=mfileauth)
        subauth.save()
        subauth2 = Auth.objects.get(id=subauth.id)
        self.failUnlessEqual(subauth, subauth2)
        self.failUnlessEqual(subauth.parent, mfileauth)

        subauth.delete()
        mfileauth.delete()
        mfile.delete()
        service.delete()
        container.delete()
'''