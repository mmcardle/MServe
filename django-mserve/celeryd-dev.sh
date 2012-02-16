#!/bin/bash
echo "Celery Daemon... $1"
COMMAND=$1
if [ -z "${COMMAND}" ] ; then
        COMMAND="restart"
fi
MSERVE_HOME=/home/mm/dev/mserve/django-mserve/
MSERVE_DATA=/home/mm/mserve-test-data/
MSERVE_LOG=/home/mm/dev/mserve/django-mserve/
hn=`hostname`
${MSERVE_HOME}manage.py celeryd_multi ${COMMAND} -E --logfile=${MSERVE_LOG}celeryd%n.log -l DEBUG 2 -n:1 normal.$hn -n:2 priority.$hn -Q:1 normal_tasks -Q:2 priority_tasks -c 5 --pidfile=${MSERVE_DATA}celeryd%n.pid

if [ "${COMMAND}" == "restart" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}celerycam.pid ] ; then
        kill `cat ${MSERVE_DATA}celerycam.pid`
        rm ${MSERVE_DATA}celerycam.pid
    fi
    ${MSERVE_HOME}manage.py celerycam --detach -f ${MSERVE_LOG}celerycam.log --pidfile=${MSERVE_DATA}celerycam.pid
    echo "Celery Beat... $1"
    if [ -f ${MSERVE_DATA}celerybeat.pid ] ; then
        kill `cat ${MSERVE_DATA}celerybeat.pid`
        rm ${MSERVE_DATA}celerybeat.pid
    fi
    ${MSERVE_HOME}manage.py celerybeat --detach -f ${MSERVE_LOG}celerybeat.log --pidfile=${MSERVE_DATA}celerybeat.pid
fi

if [ "${COMMAND}" == "stop" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}celerycam.pid ] ; then
        kill `cat ${MSERVE_DATA}celerycam.pid`
        rm ${MSERVE_DATA}celerycam.pid
    fi
    echo "Celery Beat... $1"
    if [ -f ${MSERVE_DATA}celerybeat.pid ] ; then
        kill `cat ${MSERVE_DATA}celerybeat.pid`
        rm ${MSERVE_DATA}celerybeat.pid
    fi
fi

if [ "${COMMAND}" == "start" ] ; then
    echo "Celery Monitor... $1"
    ${MSERVE_HOME}manage.py celerycam --detach -f ${MSERVE_LOG}celerycam.log --pidfile=${MSERVE_DATA}celerycam.pid
    echo "Celery Beat... $1"
    ${MSERVE_HOME}manage.py celerybeat --detach -f ${MSERVE_LOG}celerybeat.log --pidfile=${MSERVE_DATA}celerybeat.pid
fi
