MServe README.txt
=================

Contents
--------

=============   ===========
File/Folder     Description
=============   ===========
django-mserve   django code for MServe
docs            documentation for MServe
examples        example code (java)
script          utility scripts
static          static content
API.txt         external dependencies list
README.txt      this file
=============   ===========

Setup MServe
============

./scripts/setup-mserve.sh 

 usage: ./setup-mserve.sh [-m mserve home] [-d mserve data] [-s http server] [-t mserve tarball]
	OPTIONS:
	-c <install|update|uninstall|dependencies>  # script operation, default: install
	-m <MSERVE home directory>                  # default: /var/opt/mserve
	-d <MSERVE data directory>                  # default: /var/opt/mserve-data
	-l <MSERVE log directory>                   # defautl: /var/log/mserve
	-t <MSERVE HTTP server>                     # [apache|lighttpd] default: apache
	-u <MSERVE admin user name>                 # administrtor user name, default: admin
	-p <MSERVE admin password>                  # admin password
	-e <MSERVE admin email>                     # administrator email, default: admin@my.email.com
	-U <Database admin user>                    # Database admin user, default root
	-P <Database admin password>                # Database admin password
	-a <mserve tarball>                         # MSERVE distribution archive
	-s <schema>                                 # Schema (http/https)
	-v verbose mode

* install - will install a fresh MServe deployment
* update - will update the current MServe deployment to the latest version
* uninstall - will uninstall the current deployment
* dependencies - will install all librarys MServe depends on

