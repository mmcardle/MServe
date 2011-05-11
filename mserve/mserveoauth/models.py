from django.db import models
from piston.models import Token
from dataservice.models import Auth
from django.core.urlresolvers import reverse
import urllib2

class RemoteService(models.Model):
    url             = models.URLField(verify_exists=False)
    consumer_key    = models.CharField(max_length=200)
    consumer_secret = models.CharField(max_length=200)

    def get_access_token_url(self):
        return "%s%s" % (self._get_url(),reverse('oauth_access_token'))

    def get_protected_resource_url(self):
        return "%s%s" % (self._get_url(),reverse('protected'))

    def get_request_token_url(self):
        return "%s%s" % (self._get_url(),reverse('oauth_request_token'))

    def get_authorize_token_url(self):
        return "%s%s" % (self._get_url(),reverse('oauth_user_auth'))

    #def get_callback_url(self,request):
        #return "" % (self._get_url(),reverse('receive'))
        #return "%s" % (request.build_absolute_uri(reverse('receive')))

    def get_auth_url(self,authid):
        return "%s%s" % (self._get_url(),"/auth/%s/getcontents/" % authid)

    def get_full_authcallback_url(self,oauth_token,callback):
        callback = urllib2.quote(callback)
        return  "%s?oauth_token=%s&oauth_callback=%s"% (self.get_authorize_token_url(), oauth_token,callback)

    def _get_url(self):
        url = self.url
        if url[-1:] == "/":
            url = url[0:-1]
        return url

    def __unicode__(self):
        return "Remote Service '%s' " % (self.url)

class ClientConsumer(models.Model):
    remote_service      = models.ForeignKey(RemoteService)
    service_auth        = models.ForeignKey(Auth)
    oauth_token         = models.CharField(max_length=200)
    oauth_token_secret  = models.CharField(max_length=200)

class MFileOAuthToken(models.Model):
    auths = models.ManyToManyField(Auth,null=True,blank=True,related_name="auths")
    request_token = models.ForeignKey(Token,related_name='request_token')
    access_token = models.ForeignKey(Token,null=True,blank=True,related_name='access_token')