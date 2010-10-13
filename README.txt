MServe
======

Lighttpd Configuration
=====================
Edit /etc/lighttpd/lighttpd.conf
Enable the following 
mod_rewrite

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

url.rewrite-once = (
    "^(/media.*)$" => "$1",
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


