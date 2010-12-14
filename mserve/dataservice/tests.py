from django.test import TestCase

class SimpleTest(TestCase):
    def test_objects(self):
        from dataservice.models import *
        container = HostingContainer(name="HostingContainer1")
        container.save()
        container2 = HostingContainer.objects.get(id=container.id)
        self.failUnlessEqual(container, container2)
        
        service = DataService(name="DataService",container=container)
        service.save()
        service2 = DataService.objects.get(id=service.id)
        self.failUnlessEqual(service, service2)
        
        mfile = MFile(name="MFile",service=service)
        mfile.save()
        mfile2 = MFile.objects.get(id=mfile.id)
        self.failUnlessEqual(mfile, mfile2)

        MFileauth = MFileAuth(authname="MFileAuth",mfile=mfile)
        MFileauth.save()
        MFileauth2 = MFileAuth.objects.get(id=MFileauth.id)
        self.failUnlessEqual(MFileauth, MFileauth2)

        subauth = SubAuth(authname="SubAuth")
        subauth.save()
        subauth2 = SubAuth.objects.get(id=subauth.id)
        self.failUnlessEqual(subauth, subauth2)

        subauth.delete()
        MFileauth.delete()
        mfile.delete()
        service.delete()
        container.delete()
