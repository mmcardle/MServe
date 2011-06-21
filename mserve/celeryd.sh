#!/bin/bash
echo "Restarting Celery Daemon..."
hn=$HOSTNAME
sudo -u www-data ./manage.py celeryd_multi restart --logfile=/var/mserve/celeryd%n.log -l DEBUG 2 -n:1 local.$hn -n:2 remote.$hn -Q:1 local_tasks -Q:2 remote_tasks -c 5 --pidfile=/var/mserve/celeryd%n.pid
