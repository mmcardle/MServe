from dataservice.models import HostingContainer
from dataservice.models import HostingContainerAuth
from dataservice.models import DataService
from dataservice.models import DataServiceAuth
from dataservice.models import DataStager
from dataservice.models import DataStagerAuth
from dataservice.models import BackupFile
from dataservice.models import Usage
from dataservice.models import UsageRate
from dataservice.models import UsageReport
from dataservice.models import UsageSummary
from dataservice.models import SubAuth
from dataservice.models import JoinAuth
from dataservice.models import Role
from django.contrib import admin

admin.site.register(HostingContainer)
admin.site.register(HostingContainerAuth)
admin.site.register(DataService)
admin.site.register(DataServiceAuth)
admin.site.register(DataStager)
admin.site.register(DataStagerAuth)
admin.site.register(Usage)
admin.site.register(UsageRate)
admin.site.register(UsageReport)
admin.site.register(UsageSummary)
admin.site.register(SubAuth)
admin.site.register(JoinAuth)
admin.site.register(Role)
admin.site.register(BackupFile)