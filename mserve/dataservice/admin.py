from dataservice.models import HostingContainer
from dataservice.models import DataService
from dataservice.models import DataStager
from dataservice.models import Auth
from django.contrib import admin

admin.site.register(HostingContainer)
admin.site.register(DataService)
admin.site.register(DataStager)
admin.site.register(Auth)