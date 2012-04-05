MServe README.txt
=================

MServe is licensed under the LGPL v2.1 license (see LICENSE).
Information about the licenses for third-party code distributed with and used by MServe can be found in the file IPR.txt.
Individual files have their own copyright headers but in general the source code is copyright University of Southampton IT Innovation Centre.

Contents
--------

=============   ===========
File/Folder     Description
=============   ===========
django-mserve	django code for MServe
docs			documentation for MServe
examples		example code (java)
licenses		licenses for third-party code distributed with MServe
scripts			utility scripts
static			static content
IPR.txt			licenses for third-party code
LICENSE			LGPL v2.1 license
README.txt		this file
=============   ===========

To set up MServe
================

./scripts/setup-mserve.sh 

 usage: ./setup-mserve.sh [-m mserve home] [-d mserve data] [-s http server] [-a mserve tarball]
	OPTIONS:
	-c <install|update|uninstall|dependencies>  # script operation, default: install
	-m <MSERVE home directory>                  # default: /var/opt/mserve
	-d <MSERVE data directory>                  # default: /var/opt/mserve-data
	-l <MSERVE log directory>                   # defautl: /var/log/mserve
	-t <MSERVE HTTP server>                     # [apache|lighttpd] default: apache
	-u <MSERVE admin user name>                 # administrator user name, default: admin
	-p <MSERVE admin password>                  # admin password
	-e <MSERVE admin email>                     # administrator email, default: admin@my.email.com
	-U <Database admin user>                    # Database admin user, default root
	-P <Database admin password>                # Database admin password
	-a <mserve tarball>                         # MServe distribution archive
	-s <schema>                                 # Schema (http/https)
	-v verbose mode

* install - will install a fresh MServe deployment
* update - will update the current MServe deployment to the latest version
* uninstall - will uninstall the current deployment
* dependencies - will install all libraries MServe depends on
