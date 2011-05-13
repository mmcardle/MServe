#!/bin/bash
echo "Running Celery Daemon..."
sudo -u www-data ./manage.py celeryd --verbosity=2 --logfile=/var/mserve/mserve.log --loglevel=DEBUG -E
