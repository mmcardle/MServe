#!/bin/bash
echo "Celery Daemon... $1"
COMMAND=$1
if [ -z "${COMMAND}" ] ; then
	COMMAND="restart"
fi
MSERVE_HOME=/opt/mserve
MSERVE_DATA=/var/opt/mserve-data
MSERVE_LOG=/var/log/mserve
hn=$HOSTNAME
sudo -u www-data ${MSERVE_HOME}/manage.py celeryd_multi ${COMMAND} --logfile=${MSERVE_LOG}/celeryd%n.log -l DEBUG 2 -n:1 local.$hn -n:2 remote.$hn -Q:1 local_tasks -Q:2 remote_tasks -c 5 --pidfile=${MSERVE_DATA}/celeryd%n.pid
