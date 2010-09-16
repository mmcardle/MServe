from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from django.contrib import admin

admin.site.register(HostingContainer)
admin.site.register(DataService)
admin.site.register(DataStager)
admin.site.register(DataStagerAuth)
admin.site.register(SubAuth)
admin.site.register(JoinAuth)