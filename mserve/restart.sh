#!/bin/bash

# Replace these three settings.
PROJDIR="/opt/mserve/pp-dataservice/mserve"
PIDFILE="/tmp/pp-dataservice.pid"
SOCKET="/tmp/pp-dataservice-fcgi.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo -u www-data kill `cat -- $PIDFILE`
    sudo -u www-data rm -f -- $PIDFILE
fi
echo "Killed Previous Process"
sudo -u www-data ./manage.py runfcgi --pythonpath="/opt/mserve/pp-dataservice/mserve" socket=$SOCKET pidfile=$PIDFILE && sudo chmod 777 $SOCKET
sudo -u www-data chmod 777 $SOCKET
sudo chown www-data:www-data $SOCKET
if [ -f "/var/mserve/mservedb" ]; then
	sudo chown www-data:www-data /var/mserve/mservedb 
fi
cat $PIDFILE
echo "Perms"
echo "Running"
