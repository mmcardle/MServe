from django.test import TestCase

class SimpleTest(TestCase):
    def test_objects(self):
        from dataservice.models import HostingContainer
        from dataservice.models import DataService
        from dataservice.models import DataStager
        from dataservice.models import DataStagerAuth
        from dataservice.models import SubAuth

        container = HostingContainer(name="HostingContainer1")
        container.save()
        container2 = HostingContainer.objects.get(id=container.id)
        self.failUnlessEqual(container, container2)
        
        service = DataService(name="DataService",container=container)
        service.save()
        service2 = DataService.objects.get(id=service.id)
        self.failUnlessEqual(service, service2)
        
        stager = DataStager(name="DataStager",service=service)
        stager.save()
        stager2 = DataStager.objects.get(id=stager.id)
        self.failUnlessEqual(stager, stager2)

        datastagerauth = DataStagerAuth(authname="DataStagerAuth",stager=stager)
        datastagerauth.save()
        datastagerauth2 = DataStagerAuth.objects.get(id=datastagerauth.id)
        self.failUnlessEqual(datastagerauth, datastagerauth2)

        subauth = SubAuth(authname="SubAuth")
        subauth.save()
        subauth2 = SubAuth.objects.get(id=subauth.id)
        self.failUnlessEqual(subauth, subauth2)

        subauth.delete()
        datastagerauth.delete()
        stager.delete()
        service.delete()
        container.delete()
