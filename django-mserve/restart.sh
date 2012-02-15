#!/bin/bash

MSERVE_HOME="/opt/mserve/"
MSERVE_DATA="/var/opt/mserve-data"
PROJDIR="${MSERVE_HOME}/django-mserve/"
PIDFILE="/tmp/mserve.pid"
SOCKET="/tmp/mserve-fcgi.sock"

cd $PROJDIR
if [ -f $PIDFILE ]; then
    sudo -u www-data kill `cat -- $PIDFILE`
    sudo -u www-data rm -f -- $PIDFILE
    printf "\033[01;31mShutdown Previous Process\n"
    tput sgr0
fi

sudo -u www-data ./manage.py runfcgi --pythonpath="${PROJDIR}django-mserve/" socket=$SOCKET pidfile=$PIDFILE && sudo chmod 777 $SOCKET
printf "\033[01;32mMServe Running (`cat $PIDFILE`)\n"
tput sgr0

exit 0
