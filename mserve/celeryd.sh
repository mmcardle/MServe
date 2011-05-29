#!/bin/bash
echo "Running Celery Daemon..."
sudo -u www-data ./manage.py celeryd --concurrency=10 --verbosity=2 --logfile=/var/mserve/mserve.log --loglevel=DEBUG -E
