#!/bin/bash
echo "Celery Daemon... $1"
COMMAND=$1
if [ -z "${COMMAND}" ] ; then
	COMMAND="restart"
fi
MSERVE_HOME=/opt/mserve/
MSERVE_DATA=/var/opt/mserve-data/
MSERVE_LOG=/var/log/mserve/
hn=$HOSTNAME
sudo -u www-data ${MSERVE_HOME}/django-mserve/manage.py celeryd_multi ${COMMAND} -E --logfile=${MSERVE_LOG}celeryd%n.log -l DEBUG 2 -n:1 normal.$hn -n:2 priority.$hn -Q:1 normal_tasks -Q:2 priority_tasks -c 5 --pidfile=${MSERVE_DATA}celeryd%n.pid

if [ "${COMMAND}" == "restart" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}celerycam.pid ] ; then
        su www-data -c "kill `cat ${MSERVE_DATA}celerycam.pid`"
        su www-data -c "rm ${MSERVE_DATA}celerycam.pid"
    fi
    su www-data -c "${MSERVE_HOME}django-mserve/manage.py celerycam --detach -f ${MSERVE_LOG}celerycam.log --pidfile=${MSERVE_DATA}celerycam.pid"
    echo "Celery Beat... $1"
    if [ -f ${MSERVE_DATA}celerybeat.pid ] ; then
        su www-data -c "ls -la ${MSERVE_DATA}"
        su www-data -c "kill `cat ${MSERVE_DATA}celerybeat.pid`"
    #   su www-data -c "rm ${MSERVE_DATA}celerybeat.pid"
    fi
    su www-data -c "${MSERVE_HOME}django-mserve/manage.py celerybeat --detach -f ${MSERVE_LOG}celerybeat.log --pidfile=${MSERVE_DATA}celerybeat.pid"
fi


if [ "${COMMAND}" == "stop" ] ; then
    echo "Celery Monitor... $1"
    if [ -f ${MSERVE_DATA}celerycam.pid ] ; then
        su www-data -c "kill `cat ${MSERVE_DATA}celerycam.pid`"
        su www-data -c "rm ${MSERVE_DATA}celerycam.pid"
    fi
    echo "Celery Beat... $1"
    if [ -f ${MSERVE_DATA}celerybeat.pid ] ; then
        su www-data -c "kill `cat ${MSERVE_DATA}celerybeat.pid`"
        su www-data -c "rm ${MSERVE_DATA}celerybeat.pid"
    fi
fi

if [ "${COMMAND}" == "start" ] ; then
    echo "Celery Monitor... ${COMMAND}"
    su www-data -c "${MSERVE_HOME}django-mserve/manage.py celerycam --detach -f ${MSERVE_LOG}celerycam.log --pidfile=${MSERVE_DATA}celerycam.pid"
    echo "Celery Beat... $1"
    su www-data -c "${MSERVE_HOME}django-mserve/manage.py celerybeat --detach -f ${MSERVE_LOG}celerybeat.log --pidfile=${MSERVE_DATA}celerybeat.pid"
fi