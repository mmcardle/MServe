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
