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
from dataservice.models import HostingContainer
from django.test import TestCase
from dataservice.models import *
from dataservice.tasks import *
from jobservice.models import *
from django.http import HttpResponseForbidden
from django.http import HttpResponseBadRequest
from django.core.files.base import ContentFile
from django.core.files import File
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from django.http import HttpRequest

import simplejson as json
import magic
import settings

def make_request(get=None,post=None):
    request = HttpRequest()
    if get:
        request.GET = get
    if post:
        request.POST = post
    return request


class TaskTest(TestCase):

    def setUp(self):

        self.container_name = "testingcontainer"
        self.service_name = "testingservice"
        self.mfile_name = "testmfile"
        self.job_name = "testjob"
        self.joboutput_name = "testjoboutput"
        self.testfolder = os.path.join(settings.TESTDATA_ROOT)
        self.assertTrue(os.path.exists(self.testfolder))

        self.image_name = "IMAG0361.jpg"
        self.video_name = "sintel_trailer-480p.mp4"
        self.image_md5 = "d9bf0bdc061b74c4b731cb68d5f5cb61"
        self.image_mimetype = "image/jpeg"
        self.thumb_mimetype = "image/png"
        self.video_mimetype = "video/mp4"

        self.test_image_path = os.path.join(self.testfolder, self.image_name)
        self.test_video_path  = os.path.join(self.testfolder, self.video_name)

        self.test_image = File(open( self.test_image_path ,'r'))
        self.test_video = File(open( self.test_video_path ,'r'))

        self.hc = HostingContainer.create_container(self.container_name)
        self.service = self.hc.create_data_service(self.service_name)

        self.magicmime = magic.open(magic.MAGIC_MIME)
        self.magicmime.load()

    def test_register_task(self):
        from jobservice import register_task_description
        from rassc import task_descriptions
        register_task_description("rassc.tasks.swirl",task_descriptions["rassc.tasks.swirl"])

    def test_mimefile(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        mimefile([mfile.id],[])
        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertEqual(updatedmfile.mimetype, self.image_mimetype)

    def test_md5file(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        md5file([mfile.id],[])
        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(updatedmfile.checksum==self.image_md5)

    def test_md5fileverify(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        self.assertRaises(Exception,  md5fileverify , ([mfile.id],[]) )
        md5file([mfile.id],[])
        result = md5fileverify([mfile.id],[])
        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(updatedmfile.checksum==result["md5"])

    def test_thumbimage(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        thumbimage([mfile.id],[], options={"width":"210","height":"120"})

        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(os.path.exists(updatedmfile.thumb.path))
        self.assertTrue(updatedmfile.thumb.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedmfile.thumb.path).split(';')[0], self.thumb_mimetype )

    def test_posterimage(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        job = mfile.create_job(self.job_name)
        posterimage([mfile.id],[], options={"width":"210","height":"120"})

        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(os.path.exists(updatedmfile.poster.path))
        self.assertTrue(updatedmfile.poster.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedmfile.poster.path).split(';')[0], self.thumb_mimetype )

    def test_thumbvideo(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_video )
        thumbvideo([mfile.id],[], options={"width":"210","height":"120"})

        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(os.path.exists(updatedmfile.thumb.path))
        self.assertTrue(updatedmfile.thumb.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedmfile.thumb.path).split(';')[0], self.thumb_mimetype )

    def test_postervideo(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_video )
        job = mfile.create_job(self.job_name)
        output = JobOutput(name=self.joboutput_name, job=job, mimetype="image/png")
        output.save()
        postervideo([mfile.id],[output.id], options={"width":"210","height":"120"})

        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(os.path.exists(updatedmfile.poster.path))
        self.assertTrue(updatedmfile.poster.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedmfile.poster.path).split(';')[0], self.thumb_mimetype )

    def test_proxyvideo(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_video )
        proxyvideo([mfile.id],[], options={"width":"210","height":"120"})

        updatedmfile = MFile.objects.get(id=mfile.id)
        self.assertTrue(os.path.exists(updatedmfile.proxy.path))
        self.assertTrue(updatedmfile.proxy.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedmfile.proxy.path).split(';')[0], self.video_mimetype )

    def test_transcodevideo(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_video )
        job = mfile.create_job(self.job_name)
        output = JobOutput(name=self.joboutput_name, job=job, mimetype="video/mp4")
        output.save()
        transcodevideo([mfile.id],[output.id], options={"width":"210","height":"120"})

        updatedjoboutput = JobOutput.objects.get(id=output.id)
        self.assertTrue(os.path.exists(updatedjoboutput.file.path))
        self.assertTrue(updatedjoboutput.file.size>0)
        self.failUnlessEqual(self.magicmime.file(updatedjoboutput.file.path).split(';')[0], self.video_mimetype )

    def test_mfilefetch(self):
        mfile = self.service.create_mfile(self.image_name, file=self.test_image )
        job = mfile.create_job(self.job_name)
        output = JobOutput(name=self.joboutput_name, job=job, mimetype="video/mp4")
        output.save()
        mfilefetch([mfile.id],[output.id])
        updatedjoboutput = JobOutput.objects.get(id=output.id)
        self.assertTrue(os.path.exists(updatedjoboutput.file.path))
        self.assertTrue(updatedjoboutput.file.size==mfile.size)
        self.failUnlessEqual(self.magicmime.file(updatedjoboutput.file.path).split(';')[0], self.image_mimetype )

class ClientTest(TestCase):

    def test_service_workflows(self):
        service = self.hc.create_data_service(self.service_name)
        service.save()
        self.service = service
        service_url_profiles = reverse('dataservice_profiles', args=[service.id])
        response = self.c.get(service_url_profiles)
        self.failUnlessEqual(response.status_code,200)

    def setUp(self):
        self.password = 'mypassword'
        self.username = 'myuser'
        self.container_name = "testingcontainer"
        self.service_name = "testingservice"
        self.mfile_name = "testmfile"
        self.mfile_name_2 = "testmfile2"
        self.unauthclient = Client()
        self.c = Client()
        User.objects.create_superuser(self.username, 'myemail@tempuri.com', self.password)
        self.c.login(username=self.username, password=self.password)
        hc = HostingContainer.create_container(self.container_name)
        hc.save()
        self.hc = hc
        self.hc_post_url = reverse('hostingcontainers')
        self.service_post_url = reverse('dataservices')
        

        self.testfolder = os.path.join(settings.TESTDATA_ROOT)
        self.assertTrue(os.path.exists(self.testfolder))

        self.image_name = "IMAG0361.jpg"
        self.video_name = "sintel_trailer-480p.mp4"
        self.image_md5 = "d9bf0bdc061b74c4b731cb68d5f5cb61"
        self.image_mimetype = "image/jpeg"
        self.thumb_mimetype = "image/png"
        self.video_mimetype = "video/mp4"
        self.thumb_image_url = settings.MEDIA_URL+'images/image-x-generic.png'
        self.thumb_generic_url = settings.MEDIA_URL+'images/text-x-generic.png'

        self.test_image_path = os.path.join(self.testfolder, self.image_name)
        self.test_video_path  = os.path.join(self.testfolder, self.video_name)

        self.test_image = File(open( self.test_image_path ,'r'))
        self.test_video = File(open( self.test_video_path ,'r'))

        self.hc = HostingContainer.create_container(self.container_name)
        self.service = self.hc.create_data_service(self.service_name)

        self.mfile_post_url = reverse('dataservice_mfiles', args=[self.service.id])

        self.magicmime = magic.open(magic.MAGIC_MIME)
        self.magicmime.load()

    def test_unauth_html(self):
        self.failUnlessEqual(self.unauthclient.get(reverse('home'), follow=True).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('usage')).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('traffic')).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('stats')).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('tasks')).status_code,200)

        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        mfileid = js["id"]
        self.failUnlessEqual(self.unauthclient.get(reverse('videoplayer',args=[mfileid])).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('stats',args=[mfileid])).status_code,200)

        authid = self.service.auth_set.all()[0].id
        self.failUnlessEqual(self.unauthclient.get(reverse('browse',args=[authid])).status_code,200)
        self.failUnlessEqual(self.unauthclient.get(reverse('stats',args=[authid])).status_code,200)

    def test_admin_html(self):
        self.failUnlessEqual(self.c.get(reverse('home')).status_code,200)
        self.failUnlessEqual(self.c.get(reverse('usage')).status_code,200)
        self.failUnlessEqual(self.c.get(reverse('traffic')).status_code,200)
        self.failUnlessEqual(self.c.get(reverse('stats')).status_code,200)
        self.failUnlessEqual(self.c.get(reverse('stats')).status_code,200)

    def test_create_service(self):

        response = self.c.post(self.service_post_url, {"name": self.service_name, "container": self.hc.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        serviceid = js["id"]
        self.failUnlessEqual(js["name"], self.service_name)
        self.failUnlessEqual(len(js["mfile_set"]), 0)
        self.failUnlessEqual(len(js["mfolder_set"]), 0)
        self.failUnlessEqual(js["subservices_url"], reverse("dataservice_subservices", args=[serviceid] ))
        self.failUnlessEqual(type(js["folder_structure"]), dict )
        self.failUnlessEqual(type(js["thumbs"]), list )
        self.failUnlessEqual(js["priority"], False )
        self.failUnlessEqual(js["starttime"], None )
        self.failUnlessEqual(js["endtime"], None )
        self.failUnlessEqual(js["reportnum"], 1 )
        
        now = datetime.datetime.now()

        response = self.c.post(self.service_post_url, {
            "name": self.service_name,
            "container": self.hc.id,
            "starttime" : datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S"),
            "endtime" : datetime.datetime.strftime(now, "%Y-%m-%d %H:%M:%S")
            })

        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        serviceid = js["id"]
        self.failUnlessEqual(js["name"], self.service_name)
        self.failUnlessEqual(len(js["mfile_set"]), 0)
        self.failUnlessEqual(len(js["mfolder_set"]), 0)
        self.failUnlessEqual(js["subservices_url"], reverse("dataservice_subservices", args=[serviceid] ))
        self.failUnlessEqual(type(js["folder_structure"]), dict )
        self.failUnlessEqual(type(js["thumbs"]), list )
        self.failUnlessEqual(js["priority"], False )
        self.assertTrue((now - datetime.datetime.strptime(js["starttime"],"%Y-%m-%d %H:%M:%S")).total_seconds() < 1 )
        self.assertTrue((now - datetime.datetime.strptime(js["endtime"],"%Y-%m-%d %H:%M:%S")).total_seconds() < 1 )
        self.failUnlessEqual(js["reportnum"], 1 )

    def test_create_mfile(self):
        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)

    def test_update_mfile(self):
        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        mfileid = js["id"]
        self.mfile_url = reverse('mfile', args=[mfileid])
        response = self.c.put(self.mfile_url, {"name": self.mfile_name})
        self.failUnlessEqual(response.status_code,200)
        response2 = self.c.post(self.mfile_post_url, {"name":self.mfile_name_2, "serviceid" : self.service.id})
        self.failUnlessEqual(response2.status_code,200)
        js2 = json.loads(response2.content)
        mfileid2 = js2["id"]
        self.mfile_url_2 = reverse('mfile', args=[mfileid2])

        # Check we cant update the name of an mfile to an existing
        response3 = self.c.put(self.mfile_url_2, {"name": self.mfile_name})
        self.failUnlessEqual(response3.status_code,400)

    def test_create_job(self):
        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        mfileid = js["id"]
        self.mfile_post_job_url = reverse('mfile_jobs', args=[mfileid])
        response = self.c.post(self.mfile_post_job_url, {"name": "New Job", "jobtype": "dataservice.tasks.md5file"})
        self.failUnlessEqual(response.status_code,200)

    def test_create_mfile_from_joboutput(self):
        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        mfileid = js["id"]
        self.mfile_post_job_url = reverse('mfile_jobs', args=[mfileid])
        response = self.c.post(self.mfile_post_job_url, {"name": "New Job", "jobtype": "dataservice.tasks.thumbimage"})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        joboutputid = js["joboutput_set"][0]["id"]
        self.joboutput_mfile_url = reverse('joboutput_mfile', args=[joboutputid])
        response = self.c.post(self.joboutput_mfile_url, {"name": "New Mfile"})
        self.failUnlessEqual(response.status_code,200)

    def test_create_mfile_relationship(self):
        response = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        mfileid1 = js["id"]
        response2 = self.c.post(self.mfile_post_url, {"name":self.mfile_name, "serviceid" : self.service.id})
        self.failUnlessEqual(response2.status_code,200)
        js = json.loads(response2.content)
        mfileid2 = js["id"]
        mfile_relationship_url = reverse('mfile_relationships', args=[mfileid1])
        response3 = self.c.post(mfile_relationship_url, {"name":"is related to", "mfileid" : mfileid2})
        self.failUnlessEqual(response3.status_code,200)

    def test_get_mfile(self):
        service = self.hc.create_data_service(self.service_name)
        service.save()
        self.service = service
        self.service_url = reverse('dataservice',args=[service.id])
        self.mfile = service.create_mfile( self.mfile_name , file=self.test_image)

        self.mfile_url = reverse('mfile', args=[self.mfile.id] )
        self.mfile_url_usagesummary = reverse('mfile_usagesummary', args=[self.mfile.id] )

        response = self.c.get(self.mfile_url_usagesummary)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["min"]),float)
        self.failUnlessEqual(type(js["usages"][0]["max"]),float)
        self.failUnlessEqual(type(js["usages"][0]["stddev"]),float)
        self.failUnlessEqual(type(js["usages"][0]["variance"]),float)
        self.failUnlessEqual(type(js["usages"][0]["n"]),int)
        self.failUnlessEqual(type(js["usages"][0]["sum"]),float)
        self.failUnlessEqual(type(js["usages"][0]["avg"]),float)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)

        # Test GET Methods
        response = self.c.get(self.mfile_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],self.mfile_name)

        self.assertTrue( (datetime.datetime.now() - datetime.datetime.strptime(js["updated"],"%Y-%m-%d %H:%M:%S")).total_seconds() < 10 )
        self.assertTrue( (datetime.datetime.now() - datetime.datetime.strptime(js["created"],"%Y-%m-%d %H:%M:%S")).total_seconds() < 10 )
        self.failUnlessEqual(js["thumburl"], self.thumb_image_url)
        self.failUnlessEqual(js["posterurl"], self.thumb_image_url)
        self.failUnlessEqual(js["proxyurl"], '')
        self.failUnlessEqual(js["proxy"], '')
        self.failUnlessEqual(js["file"], self.mfile.file )
        self.failUnlessEqual(js["thumb"], '')
        self.failUnlessEqual(js["poster"], '')
        self.failUnlessEqual(js["reportnum"], 1)
        self.failUnlessEqual(js["id"], self.mfile.id)
        self.failUnlessEqual(js["size"], self.mfile.size )

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
        self.failUnlessEqual(len(js),2)

        hc_url =  reverse('hostingcontainer', args=[self.hc.id])
        response = self.c.get(hc_url)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnlessEqual(js["name"],self.container_name)
        self.failUnlessEqual(len(js["dataservice_set"]),1)

    def test_get_container_urls(self):
        containerid = self.hc.id
        hc_url =  reverse('hostingcontainer', args=[containerid])
        hc_url_usage =  reverse('hostingcontainer_usages', args=[containerid])
        hc_url_usagesummary =  reverse('hostingcontainer_usagesummary', args=[containerid])
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

        response = self.c.get(hc_url_usagesummary)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["min"]),float)
        self.failUnlessEqual(type(js["usages"][0]["max"]),float)
        self.failUnlessEqual(type(js["usages"][0]["stddev"]),float)
        self.failUnlessEqual(type(js["usages"][0]["variance"]),float)
        self.failUnlessEqual(type(js["usages"][0]["n"]),int)
        self.failUnlessEqual(type(js["usages"][0]["sum"]),float)
        self.failUnlessEqual(type(js["usages"][0]["avg"]),float)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)

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
        self.failUnlessEqual(len(js),1)

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
        service_url_usagesummary =  reverse('dataservice_usagesummary', args=[serviceid])
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

        response = self.c.get(service_url_usagesummary)
        self.failUnlessEqual(response.status_code,200)
        js = json.loads(response.content)
        self.failUnless(js["reportnum"]>0)
        self.failUnlessEqual(type(js["reportnum"]),int)
        self.failUnlessEqual(type(js["usages"][0]["min"]),float)
        self.failUnlessEqual(type(js["usages"][0]["max"]),float)
        self.failUnlessEqual(type(js["usages"][0]["stddev"]),float)
        self.failUnlessEqual(type(js["usages"][0]["variance"]),float)
        self.failUnlessEqual(type(js["usages"][0]["n"]),int)
        self.failUnlessEqual(type(js["usages"][0]["sum"]),float)
        self.failUnlessEqual(type(js["usages"][0]["avg"]),float)
        self.failUnlessEqual(type(js["usages"][0]["metric"]),str)

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
        # TODO Fix Test
        #for profile in js:
        #    for workflow in profile["workflows"]:
        #        service_url_profiles_tasks = reverse('dataservice_profiles_tasks', args=[serviceid,profile["id"]])
        #        response = self.c.post(service_url_profiles_tasks,{"workflow":workflow["id"],"condition":"","task_name":"thumbimage","args":""})
        #        self.failUnlessEqual(response.status_code,200)
        #        js = json.loads(response.content)

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
            roles = auth.roles()
            self.assertTrue( "containeradmin" in roles )

        service = container.create_data_service("Service1")
        for auth in service.auth_set.all():
            roles = auth.roles()
            self.assertTrue( "serviceadmin" in roles or "servicecustomer" in roles )

        mfile = service.do("POST","mfiles",name="FullFile",file=ContentFile('new content'))
        for auth in mfile.auth_set.all():
            roles = auth.roles()
            self.assertTrue( "mfileowner" in roles )
            
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
        self.failUnlessEqual(len(auths[0].urls()),4)

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
        props = service.do("GET", "properties")
        for prop in props:
            self.assertTrue(prop.property != None)
            self.assertTrue(prop.value != None)

        usagesresult = service.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = service.do("GET","auths")
        self.failUnlessEqual(len(auths), 2)

        # PUT container
        props = service.do("PUT","properties",{"accesspeed":100})
        for prop in props:
            if prop.property == "accesspeed":
                self.assertTrue(prop.value != 100)

        shouldbe403_1 = service.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        newroles= {"roles":"serviceadmin"}
        kwargs = {"full":newroles}
        request = make_request(post=kwargs)
        auths = service.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),2)
        self.failUnlessEqual(len(auths[0].urls()),8)

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

        # File 1 starts off with 'new content'
        # File 2 starts off with 'new content2'
        # Write 'XXX' over 'new content2' giving 'XXX content2'
        # Access file through subservice and shold return new content

        file1.file.open()
        filecontents1 = file1.file.read()
        self.failUnlessEqual(filecontents1, 'new content')
        file1.file.close()

        try:
            wfile = open(file2.file.path,'r+')
            try:
                wfile.seek(0)
                wfile.write('XXX')
            finally:
                wfile.close()
        except IOError:
            logging.error("Error writing partial content to MFile '%s'" % file2)

        file2.file.open()
        filecontents2 = file2.file.read()
        self.failUnlessEqual(filecontents2, 'XXX content2')
        file2.file.close()

        readfiles = subservice.do("GET","mfiles")
        for readfile in readfiles:
            if readfile.file.path == file2.file.path:
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
        for prop in props:
            self.assertTrue(prop.property != None)
            self.assertTrue(prop.value != None)

        usagesresult = service_auth.do("GET","usages")
        self.failUnlessEqual(len(usagesresult["usages"]), 1)

        auths = service_auth.do("GET","auths")
        self.failUnlessEqual(len(auths), 0)

        # PUT
        props = service_auth.do("PUT","properties",{"accesspeed":100})
        for prop in props:
            if prop.property == "accesspeed":
                self.assertTrue(prop.value != 100)

        shouldbe403_1 = service_auth.do("PUT","usages")
        self.failUnlessEqual(type(shouldbe403_1), HttpResponseForbidden)

        request = make_request(post={"roles":"serviceadmin","name":"newsubauth"})

        service_auth.do("POST","auths",request=request)

        newroles= {"roles":"serviceadmin"}
        request = make_request(post={"newsubauth":newroles})
        auths = service_auth.do("PUT","auths",request=request)
        self.failUnlessEqual(type(auths[0]), Auth)
        self.failUnlessEqual(len(auths),1)
        self.failUnlessEqual(len(auths[0].urls()),8)

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
        for prop in props:
            self.assertTrue(prop.property != None)
            self.assertTrue(prop.value != None)

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
        self.failUnlessEqual(len(auths[0].urls()),8)

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
        self.failUnlessEqual(len(auths[0].urls()),5)

        badrequest = make_request(post={"505authname":[]})
        shouldbe503_3 = mfile.do("PUT","auths",request=badrequest)
        self.failUnlessEqual(type(shouldbe503_3), HttpResponseBadRequest)

        # POST MFile
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

        # DELETE mfile
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

