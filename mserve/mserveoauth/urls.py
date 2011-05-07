from django.conf.urls.defaults import *

from piston.resource import Resource
from piston.authentication import OAuthAuthentication
from mserveoauth.handlers import *

auth = OAuthAuthentication(realm="MServe Realm")

protected_resource_handler = Resource(handler=ProtectedResourceHandler, authentication=auth)
consumer_handler = Resource(ConsumerHandler)
receive_handler = Resource(ReceiveHandler)
remote_service_handler = Resource(RemoteServiceHandler)

urlpatterns = patterns('',
    url(r'^api/protected/', protected_resource_handler, name='protected'),
    url(r'^api/consumers/$', consumer_handler , name='consumer'),
    url(r'^api/consumers/(?P<id>[^/]+)/(?P<oauth_token>[^/]+)', consumer_handler),
    url(r'^api/receive/', receive_handler, name='receive'),
    url(r'^api/remoteservices/', remote_service_handler, name='remoteservice'),
    url(r'^api/oauth/access_token/$','mserveoauth.handlers.oauth_access_token', name='oauth_access_token'),
)

urlpatterns += patterns(
    'piston.authentication',
    url(r'^api/oauth/request_token/$','oauth_request_token' , name='oauth_request_token'),
    url(r'^api/oauth/authorize/$','oauth_user_auth', name='oauth_user_auth'),
    #url(r'^api/oauth/access_token/$','oauth_access_token' , name='oauth_access_token'),
)