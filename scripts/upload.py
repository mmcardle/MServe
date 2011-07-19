# To change this template, choose Tools | Templates
# and open the template in the editor.

#!/usr/bin/env python

import sys, os, time
from optparse import OptionParser
import httplib, urlparse
import urllib2
import StringIO
import pycurl

class MServeUpload():
    """Upload to webdav server"""

    def __init__(self, serverURL, filename, login=None, password=None) :
        self.filename = filename
        self.login = login
        self.password = password
        self.serverURL = serverURL
        scheme, netplace, self.path, query, fragid = urlparse.urlsplit(serverURL)
        self.host = ''
        self.port = 80
        if ":" in netplace:
                self.host, port = netplace.split(':', 2)
                self.port = int(port)
        else :
                self.host = netplace

        self.upload_file()
        #self.poster_file()

    def upload_file(self):
        
        pf = [  ('file', (pycurl.FORM_FILE, self.filename)), ]
        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, self.serverURL)
        c.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        #c.setopt(c.HTTPHEADER, [ 'Expect:' ] )
        c.setopt(c.HTTPPOST, pf)
        #c.setopt(c.VERBOSE, 1)

        startT = time.time()
        c.perform()
        c.close()

        stopT = time.time()
        print "transferred",'bytes from', 'in' , stopT - startT, 'seconds'

    def poster_file(self):

        remoteservice = "http://ogio/services/sivLOmBVYcYyLvYBHJTwxaitbg5O5Tzj8wS4ED7oDo/mfiles/"
	remoteservice = "http://jester.it-innovation.soton.ac.uk/services/7Ql9EYAvyZFwh4HfrZyOgMPjy5z7mD8JOkT6UFtY/mfiles/"
        print remoteservice
        
        resp = StringIO.StringIO()

        pf = [  ('file', (pycurl.FORM_FILE, str(self.filename))), ]
        c = pycurl.Curl()
        c.setopt(c.POST, 1)
        c.setopt(c.URL, remoteservice)
        c.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        #c.setopt(c.HTTPHEADER, [ 'Expect:' ] )
        c.setopt(c.WRITEFUNCTION, resp.write)

        c.setopt(c.HTTPPOST, pf)
        #c.setopt(c.VERBOSE, 1)

        c.perform()
        c.close()

        print resp.getvalue()

        import json

        js = json.loads(resp.getvalue())

        id = js['id']

        remotejob = 'http://ogio/mfiles/%s/jobs/' % id

        jobresp = StringIO.StringIO()

        jobpf = [  ('jobtype', (pycurl.FORM_CONTENTS, "dataservice.tasks.posterimage") ),
                    ('width', (pycurl.FORM_CONTENTS, "420") ),
                    ('height', (pycurl.FORM_CONTENTS, "256") ),
                    ]
        c2 = pycurl.Curl()
        c2.setopt(c2.POST, 1)
        c2.setopt(c2.URL, str(remotejob))
        c2.setopt(c.HTTPHEADER, [ 'Expect:', 'Content-Type: multipart/form-data' ] )
        #c2.setopt(c.HTTPHEADER, [ 'Expect:' ] )
        c2.setopt(c2.WRITEFUNCTION, jobresp.write)

        c2.setopt(c2.HTTPPOST, jobpf)
        #c2.setopt(c.VERBOSE, 1)

        c2.perform()

        print "Job Resp - %s" % jobresp.getvalue()

        c2.close()

        jobjs = json.loads(jobresp.getvalue())

        jobid = jobjs['id']

        remotejob = 'http://ogio/jobs/%s/' % jobid

        import time

        jobstatusresp = StringIO.StringIO()
        c3 = pycurl.Curl()
        c3.setopt(c2.URL, str(remotejob))
        c3.setopt(c2.WRITEFUNCTION, jobstatusresp.write)

        status = False
        while True:
            time.sleep(3)

            c3.perform()

            print "Job Resp - %s" % jobstatusresp.getvalue()

            jobjs = json.loads(jobstatusresp.getvalue())

            status = jobjs['tasks']['successful']

            print status

            if status:
                break

        c3.close()

        import tempfile
        if status:

            outfile =  "./file.png"
            f = open(outfile,'w')
            remotemfile= "http://ogio/mfiles/%s/" % id

            print remotemfile
            mfileresp = StringIO.StringIO()
            c4 = pycurl.Curl()
            c4.setopt(c4.URL, str(remotemfile))
            c4.setopt(c4.WRITEFUNCTION, mfileresp.write)
            c4.perform()
            c4.close()

            print "Mfile Resp - %s" % mfileresp.getvalue()

            mfilejs = json.loads(mfileresp.getvalue())

            posterpath = mfilejs['posterurl']

            posterurl = "http://ogio/%s/" % posterpath

            c5 = pycurl.Curl()
            c5.setopt(c5.URL, str(posterurl))
            c5.setopt(c5.WRITEFUNCTION, f.write)
            c5.perform()
            c5.close()
            
            print outfile

            mfiledelresp = StringIO.StringIO()
            c6 = pycurl.Curl()
            c6.setopt(pycurl.CUSTOMREQUEST, 'DELETE')
            c6.setopt(c6.URL, str(remotemfile))
            c6.setopt(c6.WRITEFUNCTION, mfiledelresp.write)
            c6.perform()

            print mfiledelresp.getvalue()



class WebDAVUpload():
	"""Upload to webdav server"""

	def __init__(self, serverURL, filename, login=None, password=None) :
		self.filename = filename
		self.login = login
		self.password = password
		scheme, netplace, self.path, query, fragid = urlparse.urlsplit(serverURL)
		self.host = ''
		self.port = 80
		if ":" in netplace:
			self.host, port = netplace.split(':', 2)
			self.port = int(port)
		else :
			self.host = netplace

		#self.uploadFile_range()
		self.uploadFile()

	def uploadFile_range(self):
		auth = False
		f = open(self.filename, 'rb')
		filesize = os.path.getsize(self.filename)
		transferredBytes = 0
		#uploadFile = "".join(["/", os.path.basename(self.filename)])
		uploadFile = os.path.join(self.path, os.path.basename(self.filename))
		print "upload file", uploadFile, "host", self.host, "port", self.port
		startT = time.time()
		davConn = httplib.HTTPConnection(self.host, self.port)
		#davConn.set_debuglevel(10)
		davConn.putrequest('PUT', uploadFile)
		#davConn.putheader('Transfer-Encoding', 'chunked')
		davConn.putheader('Content-Length', filesize)
		if auth:
			davConn.putheader('Authorization', None)
		davConn.endheaders()

		while True:
			bytes = f.read(4096)
			if not bytes: break
			length = len(bytes)
			transferredBytes += length
			#davConn.send('%X\r\n' % length)
			#davConn.send(bytes + '\r\n')
			davConn.send(bytes)

		davConn.send('0\r\n\r\n')

		stopT = time.time()
		resps =  davConn.getresponse()

		okey = set([200, 201, 204])

		if resps.status not in okey:
			#print "response has status:", resps.status, "reason:", resps.reason
			data =  resps.read()
			if len(data):
				print data

		f.close()
		davConn.close()
		print "transferred", transferredBytes, 'bytes from', filesize, 'in' , stopT - startT, 'seconds'


	def uploadFile(self):
		auth = False
		f = open(self.filename, 'rb')
		fileSize = os.path.getsize(self.filename)
		transferredBytes = 0
		#uploadFile = "".join(["/", os.path.basename(self.filename)])
		uploadFile = os.path.join(self.path, os.path.basename(self.filename))
		print "upload file", uploadFile, "host", self.host, "port", self.port
		startT = time.time()
		davConn = httplib.HTTPConnection(self.host, self.port)
		#davConn.set_debuglevel(10)
		davConn.putrequest('PUT', uploadFile)
		davConn.putheader('Transfer-Encoding', 'chunked')
		if auth:
			davConn.putheader('Authorization', None)
		davConn.endheaders()

		while True:
			bytes = f.read(4096)
			if not bytes: break
			length = len(bytes)
			transferredBytes += length
			davConn.send('%X\r\n' % length)
			davConn.send(bytes + '\r\n')

		davConn.send('0\r\n\r\n')

		#stopT = time.time()
		resps =  davConn.getresponse()

		okey = set([200, 201, 204])

		if resps.status not in okey:
			#print "response has status:", resps.status, "reason:", resps.reason
			data =  resps.read()
			if len(data):
				print data

		davConn.close()
		f.close()
		stopT = time.time()
		print "transferred", transferredBytes, 'bytes from', fileSize, 'in' , stopT - startT, 'seconds'


def main():
	description = "WebDAV upload test"
	usage = """[-h] -s <WebDAV server URL> [-l <login name>] [-p <password>] file]
		-h, --help 	print this help message
		-s, --server	WebDAV server url, e.g. http://webdav.server:8000/
		-l, --login	login user
		-p, --passowrd	user password"""

	parser = OptionParser(usage=usage, description=description)
	parser.add_option("-s", dest="webdav_server_url", help="WebDAV server URL")
	parser.add_option("-l", dest="login_user", help="login name")
	parser.add_option("-p", dest="user_password", help="user password")

	(options, args) = parser.parse_args()

	if len(args) != 1:
		parser.error("incorrect number of arguments")

	#print "Run WebDAV upload test:", sys.argv

	# Default values
	webdavServerURL = ""
	loginUser = ""
	userPassword = ""
	filename =  args[-1]

	if not os.path.isfile(filename):
		print "filename", filename, "does not exist"
		sys.exit(1)

	if options.webdav_server_url:
		webdavServerURL = options.webdav_server_url
		if len(webdavServerURL) == 0:
			print "empty WebDAV server URL"
			sys.exit(1)
	if options.login_user:
		loginUser = options.login_user
	if options.user_password:
		userPassword = options.user_password

	WebDAVUpload(webdavServerURL, filename, loginUser, userPassword)

if __name__ == "__main__":
    main()
    #WebDAVUpload("http://ogio/webdav/sivLOmBVYcYyLvYBHJTwxaitbg5O5Tzj8wS4ED7oDo/", "/home/mm/Pictures/IMAG0369.jpg", "", "")
    #MServeUpload("http://ogio/services/sivLOmBVYcYyLvYBHJTwxaitbg5O5Tzj8wS4ED7oDo/mfiles/", "/home/mm/Pictures/IMAG0369.jpg", "", "")

