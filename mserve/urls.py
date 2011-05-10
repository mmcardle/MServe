from django.conf.urls.defaults import *

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    (r'^', include('mserve.dataservice.urls')),
    (r'^', include('mserve.jobservice.urls')),
    (r'^', include('mserve.webdav.urls')),
    (r'^', include('mserve.mserveoauth.urls')),
    (r'^', include('mserve.prestoprime.urls')),

    (r'^openid/', include('django_openid_auth.urls')),

    (r'^mservemedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/opt/mserve/pp-dataservice/media/'}),
    (r'^mservethumbs/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/var/mserve/www-root/mservethumbs'}),

    (r'^admin/', include(admin.site.urls)),
)
