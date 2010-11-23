Prerequisites for Ubuntu 10.10 desktop
======================================

sudo apt-get install lighttpd
sudo apt-get install python-django
sudo-apt-get install python-setuptools
sudo apt-get install python-flup
sudo apt-get install mercurial

hg clone http://bitbucket.org/david/django-oauth
cd django-oauth
python setup.py install

hg clone http://bitbucket.org/jespern/django-piston
cd django-piston
python setup.py install

sudo apt-get install git
git clone git://soave.it-innovation.soton.ac.uk/git/pp-dataservice


MServe
======

To run the server in standalone mode
Create the folder /var/mserve (linux) or somewhere else (windows)
Edit settings.py and change template directory "TEMPLATE_DIRS" to install location   
Edit settings.py and change database location "DATABASE_NAME" to an appropriate directory
Create the database
./manage.py syncdb
./manage.py runserver
Follow the link given

WARNING: Since this is singlethreaded usage reporting (long polling) will not work, for this lighttp is needed (See Below)

Lighttpd Configuration
=====================
Edit /etc/lighttpd/lighttpd.conf
Enable the following 
mod_rewrite
set the root directory to /var/mserve/www-root/

create the links in /var/mserve/www-root/
media -> /usr/share/pyshared/django/contrib/admin/media/
mservemedia -> /home/mm/dev/pp-dataservice/mserve/media/

run lighttpd-enable-mod
choose fastcgi
edit /etc/lighttpd/conf-enabled/10-fastcgi.conf


=======================================
10-fastcgi.conf
=======================================

server.modules   += ( "mod_fastcgi" )
fastcgi.debug = 1
fastcgi.server = (
    "/project.fcgi" =>
    (
        "django-fcgi" =>
        (
         "socket" => "/tmp/pp-dataservice-fcgi.sock",
         "check-local" => "disable",
        )
    )
)
$HTTP["url"] =~ "^/dl50" {
        connection.kbytes-per-second=50
        secdownload.secret          = "ugeaptuk6"
        secdownload.document-root   = "/var/mserve/www-root/dl50"
        secdownload.uri-prefix      = "/dl50/"
        secdownload.timeout         = 60
}
$HTTP["url"] =~ "^/dl100" {
        connection.kbytes-per-second=100
        secdownload.secret          = "ugeaptuk6"
        secdownload.document-root   = "/var/mserve/www-root/dl100"
        secdownload.uri-prefix      = "/dl100/"
        secdownload.timeout         = 60
}


url.rewrite-once = (
    "^(/dl100.*)$" => "$1",
    "^(/dl50.*)$" => "$1",
    "^(/media.*)$" => "$1",
    "^(/mservemedia.*)$" => "$1",
    "^(/mservedata.*)$" => "$1",
    "^/favicon\.ico$" => "/media/favicon.ico",
    "^(/.*)$" => "/project.fcgi$1",
)

=======================================
=======================================

Modify mserve/restart.sh
The SOCKET param must match the one in the lighttpd configuration

=======================================
restart.sh
=======================================

#!/bin/bash

# Replace these three settings.
PROJDIR="/home/mm/dev/pp-dataservice/mserve"
PIDFILE="/tmp/pp-dataservice.pid"
SOCKET="/tmp/pp-dataservice-fcgi.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo kill `cat -- $PIDFILE`
    sudo rm -f -- $PIDFILE
fi
echo "Killed Previous Process"
sudo ./manage.py runfcgi --pythonpath="/home/mm/dev/pp-dataservice/mserve" socket=$SOCKET pidfile=$PIDFILE && sudo chmod 777 $SOCKET
sudo chmod 777 $SOCKET
cat $PIDFILE
echo "Perms"
echo "Running"

=======================================
=======================================

Run this file to stop/start django

Rabbit MQ Setup
===============

Follow this guide
http://celeryq.org/docs/getting-started/broker-installation.html

Or Quick start, paste:
rabbitmqctl add_user myuser mypassword
rabbitmqctl add_vhost myvhost
rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

Celery Startup
=============
sudo -u www-data ./manage.py celeryd --verbosity=2 --loglevel=DEBUG
