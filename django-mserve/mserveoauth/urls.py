########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Mark McArdle
#	Created Date :			2011-03-25
#	Created for Project :		PrestoPrime
#
########################################################################
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