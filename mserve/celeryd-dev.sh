#!/bin/bash
echo "Celery Daemon... $1"
COMMAND=$1
if [ -z "${COMMAND}" ] ; then
        COMMAND="restart"
fi
MSERVE_HOME=/home/mm/dev/pp-dataservice/mserve/
MSERVE_DATA=/home/mm/mserve-test-data
MSERVE_LOG=/home/mm/dev/pp-dataservice/mserve/
hn=$HOSTNAME
${MSERVE_HOME}/manage.py celeryd_multi ${COMMAND} -E --logfile=${MSERVE_LOG}/celeryd%n.log -l DEBUG 2 -n:1 normal.$hn -n:2 priority.$hn -Q:1 normal_tasks -Q:2 priority_tasks -c 5 --pidfile=${MSERVE_DATA}/celeryd%n.pid

if [ "${COMMAND}" == "restart" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}/celerycam.pid ] ; then
        kill `cat ${MSERVE_DATA}/celerycam.pid`
        rm ${MSERVE_DATA}/celerycam.pid
    fi
    ${MSERVE_HOME}/manage.py celerycam --detach -f celerycam.log --pidfile=${MSERVE_DATA}/celerycam.pid
fi

if [ "${COMMAND}" == "stop" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}/celerycam.pid ] ; then
        kill `cat ${MSERVE_DATA}/celerycam.pid`
        rm ${MSERVE_DATA}/celerycam.pid
    fi
fi

if [ "${COMMAND}" == "start" ] ; then
    echo "Celery Monitor... $1"
    ${MSERVE_HOME}/manage.py celerycam --detach -f celerycam.log --pidfile=${MSERVE_DATA}/celerycam.pid
fi