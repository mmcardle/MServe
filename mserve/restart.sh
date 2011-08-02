#!/bin/bash

# Replace these three settings.
MSERVE_HOME=/opt/mserve
MSERVE_DATA=/var/opt/mserve-data
PROJDIR="${MSERVE_HOME}"
PIDFILE="/tmp/mserve.pid"
SOCKET="/tmp/mserve-fcgi.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo -u www-data kill `cat -- $PIDFILE`
    sudo -u www-data rm -f -- $PIDFILE
fi
echo "Killed Previous Process"
sudo -u www-data ./manage.py runfcgi --pythonpath="${MSERVE_HOME}" socket=$SOCKET pidfile=$PIDFILE && sudo chmod 777 $SOCKET
sudo -u www-data chmod 777 $SOCKET
sudo chown www-data:www-data $SOCKET
if [ -f "${MSERVE_DATA}/mservedb" ]; then
	sudo chown www-data:www-data ${MSERVE_DATA}/mservedb 
fi
cat $PIDFILE
echo "Running"
