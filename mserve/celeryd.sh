#!/bin/bash
echo "Running Celery Daemon..."
sudo -u www-data ./manage.py celeryd --verbosity=2 --loglevel=DEBUG
