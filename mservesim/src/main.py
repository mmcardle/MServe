#! /usr/bin/python

__author__="mm"
__date__ ="$17-Feb-2011 20:31:01$"

import random

class Base(object):

    def __init__(self):
        self.id = random.randint(1000,9999)
        self.methods = []
        self.usage = {}
        self.properties = {}
        self.auths = []
        self.urls = {
            "auth":[],
            "property":[],
            "usage":[]
            }
        
    def check(self, url , method):
        if url==None:
            return method in self.methods
        else:
            return method in self.urls[url]

    def do(self, method, url=None, args=None):
        if url==None:
            print "%s : on %s args=%s" % (method,self,args)
        else:
            print "%s : /%s/ on %s args=%s" % (method,url,self,args)
        
        if not self.check(url,method):
            print  "Exception: Cannot do %s: on /%s/ methods are %s, urls are %s"\
                % (method,url,self.methods,self.urls)
            return None

        if method=="GET" and url=="auth":
            return self.auths

        if method=="GET" and url=="usage":
            return self.usage

        if method=="GET" and url=="property":
            return self.properties

        if method=="PUT" and url=="property":
            for k in args.keys():
                self.properties[k] = args[k]
            return self.properties

        if method=="POST" and url=="auth":
            auth = Auth(self,args=args)
            self.auths += [auth]
            return auth

        if method=="GET":
            return self.get(url)
        if method=="POST":
            return self.post(url,args=args)
        if method=="PUT":
            return self.put(url,args=args)

        print "ERROR: 404 Pattern no matched for %s on %s" % (method,url)

class Auth(Base):

    def __init__(self,base,args=[]):
        super(Auth,self).__init__()
        self.base = base
        self.methods = args["methods"]
        self.urls = args["urls"]

    def check(self, url, method):
        if url==None:
            return method in self.methods and self.base.check(url,method)
        else:
            return self.urls.has_key(url)\
            and method in self.urls[url]\
            and self.base.check(url,method)
        
    def get(self,url):
        return self.base.get(url)

    def put(self,url,args={}):
        return self.base.put(url,args)

    def post(self,url,args={}):
        return self.base.post(url,args)
        
    def __str__(self):
        return "Auth#%s%s_of_%s" % (self.id,self.methods,self.base)
    
class Hosting(Base):

    def __init__(self):
        super(Hosting,self).__init__()
        self.methods = ["GET","POST","PUT"]
        self.urls = {
            "auth":["GET","PUT","POST","DELETE"],
            "property":["GET","PUT"],
            "usage":["GET"]
            }

    def get(self,url):
        return self

    def post(self,url,args={}):
        return Service()

    def put(self,url):
        return self

    def __str__(self):
        return "Hosting#%s " % self.id

class Service(Base):

    def __init__(self):
        super(Service,self).__init__()
        self.properties = {"speed":100}
        self.methods = ["GET","POST","PUT","DELETE"]
        self.urls = {
            "auth":["GET","PUT","POST","DELETE"],
            "property":["GET","PUT"],
            "usage":["GET"]
            }
        
    def get(self,url):
        return self

    def post(self,url,args={}):
        return MFile()

    def put(self,url,args={}):
        return self

    def __str__(self):
        return "Service#%s " % self.id

class MFile(Base):

    def __init__(self):
        super(MFile,self).__init__()
        self.file = "NoFile"
        self.usage = {"disc_access":100}
        self.methods = ["GET","POST","PUT","DELETE"]
        self.urls = {
            "auth":["GET","PUT","POST","DELETE"],
            "property":["GET","PUT"],
            "usage":["GET"]
            }

    def get(self,url):
        self.usage["disc_access"] = self.usage["disc_access"] + 100
        return self

    def post(self,url,args={}):
        if url=="":
            return Service()

    def put(self,url,args={}):
        self.file=args["file"]
        return self

    def __str__(self):
        return "MFile#%s/%s" % (self.id,self.file)

if __name__ == "__main__":
    print "### Create Hosting"
    hosting = Hosting()
    print "\t-> %s" % hosting

    service = hosting.do("POST")
    print "\t-> %s" % service

    mfile = service.do("POST")
    print "\t-> %s" % mfile

    mfile = mfile.do("PUT", args={"file":"image.jpg"})
    print "\t-> %s" % mfile

    print "\n### Do a PUT on Mfile readwrite"
    mfilereadwriteauth = mfile.do("POST", "auth", {"methods":["GET","PUT"],"urls":[]})
    print "\t-> %s " % mfilereadwriteauth
    mfilereadwriteauth = mfilereadwriteauth.do("PUT", args={"file":"newimage.jpg"})
    
    mfilereadauth = mfile.do("POST", "auth", {"methods":["GET"],"urls":[]})
    print "\t-> %s " % mfilereadauth

    print "\n### Do a GET on Mfile readonly"
    mfilereadauth.do("GET", args={"file":"newimage.jpg"})
    
    print "\n### Do a PUT on Mfile readonly"
    mfilereadauth.do("PUT", args={"file":"newimage.jpg"})
    print "-> %s " % mfile

    print "\n### Get Usage on Service"
    usage = service.do("GET","usage")
    print "\t-> %s " % usage

    print "\n### Get Usage on MFile"
    usage = mfile.do("GET","usage")
    print "\t-> %s " % usage

    print "\n### Change Property"
    properties = service.do("GET","property")
    print "\t-> %s " % properties
    
    properties = service.do("PUT","property",{"speed":1000})
    print "\t-> %s " % properties

    print "\n### Get Auths for a Service "
    auths = service.do("GET","auth")
    print "\t-> %s " % auths

    auth = service.do("POST","auth",{"methods":[],"urls":{}})
    print "\t-> %s " % auth

    auth.do("GET","auth")

    print "\n### Create sufficient auth"
    sufficient_auth = service.do("POST","auth",{"methods":["GET","POST"],"urls":{"auth":["GET","POST"]}})

    print "\n### Try post on sufficient auth"
    sufficient_auth.do("POST","auth",{"methods":["GET","POST"],"urls":{}})
    
    print "\n### Create insufficient auth"
    not_sufficient_auth = service.do("POST","auth",{"methods":["GET"],"urls":{}})
    
    print "\n### Try post on insufficient auth"
    not_sufficient_auth.do("POST","auth",{"methods":["GET","POST"],"urls":{}})

    print "\n### Create subauth"
    subauth = sufficient_auth.do("POST","auth",{"methods":["POST"],"urls":{}})
    sub_notsufficient_subauth = subauth.do("GET","auth")
    print "\t-> %s " % (sub_notsufficient_subauth)

    print "\n### Create auth for getting properties"
    propauth = mfile.do("POST","auth",{"methods":[],"urls":{"property":"GET"}})
    print propauth

    print propauth.do("GET","property")
    
    
