from dataservice.models import *
from django.contrib import admin

admin.site.register(HostingContainer)
admin.site.register(DataService)
admin.site.register(MFile)
admin.site.register(MFolder)
admin.site.register(Usage)
admin.site.register(Auth)
admin.site.register(Role)
admin.site.register(BackupFile)
admin.site.register(ClientConsumer)
admin.site.register(RemoteService)
admin.site.register(MServeProfile)
admin.site.register(MFileOAuthToken)

from piston.models import Token
from piston.models import Consumer

admin.site.register(Token)
admin.site.register(Consumer)