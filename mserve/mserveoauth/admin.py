from mserveoauth.models import *
from django.contrib import admin

admin.site.register(ClientConsumer)
admin.site.register(RemoteService)
admin.site.register(MFileOAuthToken)

from piston.models import Token
from piston.models import Consumer

admin.site.register(Token)
admin.site.register(Consumer)