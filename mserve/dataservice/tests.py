from django.test import TestCase
from dataservice.models import *

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
