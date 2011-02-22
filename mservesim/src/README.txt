
The simulator is meant to model the capabilities auth system using just "GET","PUT","POST" and "DELETE"


In the base class you have the list of allowed methods for the object itself

self.methods = ["GET","PUT","POST","DELETE"]

And you have a mapping of urls to a method list

self.access = {
            "auth" : ["GET","PUT","POST","DELETE"],
            "property" : ["GET","PUT"],
            "usage" : ["GET"]
            }


All requests comes through the base.do(method, url) method and must pass the check(method,url) which uses method name and url to make a decision

For Base Objects:
If the request comes through without a url then we check self.methods
If the request comes through with a url "auth", "property" or "usage" then we check self.access

For Auth Objects:
If the request comes through without a url then we check self.methods  and recursively call base.check(url,method)
If the request comes through with a url "auth", "property" or "usage" then we check self.access and recursively check base.check(url,method)

If the checks pass then the get(), put(), post() or delete() of the base object is called, which can be recursive if called on a Auth
