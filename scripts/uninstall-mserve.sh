#!/bin/bash
########################################################################
#
# University of Southampton IT Innovation Centre, 2011
#
# Copyright in this library belongs to the University of Southampton
# University Road, Highfield, Southampton, UK, SO17 1BJ
#
# This software may not be used, sold, licensed, transferred, copied
# or reproduced in whole or in part in any manner or form or in or
# on any media by any person other than in accordance with the terms
# of the Licence Agreement supplied with the software, or otherwise
# without the prior written consent of the copyright owners.
#
# This software is distributed WITHOUT ANY WARRANTY, without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE, except where stated in the Licence Agreement supplied with
# the software.
#
#	Created By :			Panos Melas
#	Created Date :			2011-07-11
#	Created for Project :		POSTMARK
#
########################################################################


MSERVE_HOME=/var/opt/mserve
MSERVE_DATA=/var/opt/mserve-data

check_root_f() {
	# need to run tests as root ;-(
	#Make sure only root can run this script
	if [[ $EUID -ne 0 ]]; then
		echo "This script must be run as root"
		exit 1
	fi
}

check_root_f

# stop mserve processes
echo "Stopping MSERVE processes"
PIDFILE="/tmp/pp-dataservice.pid"
if [ -f $PIDFILE ]; then
    sudo -u www-data kill `cat -- $PIDFILE`
    sudo -u www-data rm -f -- $PIDFILE
fi
echo "Killed Previous Process"

# killing celery processes
echo -e "\n\nStopping celeryd processes"
sudo -u www-data ${MSERVE_HOME}/pp-dataservice/mserve/manage.py celeryd_multi stop \
	--logfile=${MSERVE_DATA}/celeryd%n.log -l DEBUG 2 -n:1 local.$hn \
	-n:2 remote.$hn -Q:1 local_tasks -Q:2 remote_tasks -c 5 \
	--pidfile=${MSERVE_DATA}/celeryd%n.pid

# find configured http server
echo -e "\n\nReconfiguring http server"
if [ -f "${MSERVE_HOME}/.HTTP_SERVER" ]; then
	http_server=$(cat "${MSERVE_HOME}/.HTTP_SERVER")
else
	http_server=
fi

if [ http_server="apache" ]; then
	a2dissite mserve
	a2dismod fastcgi rewrite
	a2ensite default
	/etc/init.d/apache2 force-reload
fi


# remove mserve data
echo "removing installed files from /var/opt"
rm -rf "$MSERVE_DATA"
rm -rf "$MSERVE_HOME"

# clear mserve database
echo -e "\n\nCleaning DB"
cat > .drop_mserve_db <<DROPDB
DROP DATABASE IF EXISTS mservedb;
DROPDB
mysql -u root -ppass < .drop_mserve_db
rm .drop_mserve_db

# remove other configuration files
echo -e "\n\nCleaning rabbitmq"
rabbitmqctl clear_permissions -p myvhost myuser
rabbitmqctl delete_vhost myvhost
rabbitmqctl delete_user myuser

# removed added packages

# remove system packages

exit

