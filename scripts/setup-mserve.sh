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
#	Created Date :			2011-03-22
#	Created for Project :		POSTMARK
#
########################################################################



#################################################
#PART I
#Installing prerequisites for Ubuntu 10.04 server
# 
#################################################
#
# At this point we assume the following default 
# values:
# mserve username: www-data password: rand() 
# mysql root password: rand()
# installation directory /var/opt/mserve
# mserve data directory: /var/opt/mserve-data
#
#################################################


MSERVE_HOME=/opt/mserve
MSERVE_DATA=/var/opt/mserve-data
MSERVE_LOG=/var/log/mserve
MSERVE_ADMIN_USER="admin"
MSERVE_ADMIN_EMAIL="admin@my.email.com"
MSERVE_ADMIN_PASSWD=
MSERVE_DATABASE_USER=mserve
MSERVE_DATABASE_PASSWORD=
HTTP_SERVER=apache
HTTP_SCHEMA=http
VERBOSE=
MSERVE_ARCHIVE=NOTSET
DATABASE_ADMIN_USER=root
DATABASE_ADMIN_PASSWORD=

CONFIGURATION=

COMMAND=install

date_stamp=$(date +%F)

#check for embedded binary
if [ "$MSERVE_ARCHIVE" != "NOTSET" ]; then
	SELF_EXTRACT=1
else
	SELF_EXTRACT=0
fi

##############
# print usage
usage_f() {
	echo "usage: $0 [-m mserve home] [-d mserve data] [-s http server] [-t mserve tarball]
	OPTIONS:
	-c <install|update|uninstall|dependencies>  # script operation, default: install
	-m <MSERVE home directory>                  # default: /var/opt/mserve
	-d <MSERVE data directory>                  # default: /var/opt/mserve-data
	-l <MSERVE log directory>                   # defautl: /var/log/mserve
	-t <MSERVE HTTP server>                     # [apache|lighttpd] default: apache
	-u <MSERVE admin user name>                 # administrtor user name, default: admin
	-p <MSERVE admin password>                  # admin password
	-e <MSERVE admin email>                     # administrator email, default: admin@my.email.com
	-U <Database admin user>                    # Database admin user, default root
	-P <Database admin password>                # Database admin password
	-a <mserve tarball>                         # MSERVE distribution archive
	-s <schema>                                 # Schema (http/https)
	-v verbose mode

	example: $0 -s apache
"
}

extract_payload () {
	match=$(grep --text --line-number '^PAYLOAD:$' $0 | cut -d ':' -f 1)
	payload_start=$((match + 1))
	tail -n +$payload_start $0 > $MSERVE_ARCHIVE #| tar -tzvf -
}

###################################
# report fault and exit function
f_ () {
	printf "\033[01;31m\nMSERVE setup %s\n\n" "$1"
	tput sgr0
        print_summary
	exit 2
}


gen_password () {
	openssl rand -base64 8 | sed 's/0/2/;s/=//;s/O/P/;s/l/s/;s/1/2/;s/\//j/'
}


##############################################
# check for mserve archive argument provided
check_mserve_archive () {
	if [ $SELF_EXTRACT -eq 1 ]; then
		echo "Self-extract binary file to $MSERVE_ARCHIVE"
		extract_payload
		sleep 1
	fi

	if [ $MSERVE_ARCHIVE != "NOTSET" ]; then

		# check if archive exists
		if [ ! -f $MSERVE_ARCHIVE ]; then
			f_ "specified MSERVE archive is not found"
		fi
		echo "MSERVE archive $MSERVE_ARCHIVE found"
		MSERVE_ARCHIVE=$(pwd)/$MSERVE_ARCHIVE
		if [ ! -f $MSERVE_ARCHIVE ]; then
			f_ "failed to find absolute path of $MSERVE_ARCHIVE"
		fi
	else
		echo "MSERVE archive file is not provided"
	fi

}

#######################
# check for passwords
check_mserve_admin_passwd () {
	if [ -z $MSERVE_ADMIN_PASSWD ]; then
		echo "MSERVE admin password is not set, generating a new one"
		MSERVE_ADMIN_PASSWD=$(gen_password)
	fi
}

check_mysql_password () {
        echo "$DATABASE_ADMIN_PASSWORD"
	if [ -z "$DATABASE_ADMIN_PASSWORD" ]; then
		echo "no password provided for mysql, try connect with no password"
		verify_pass=$(mysql -u root -Bse 'show databases')
		if [ $? -ne 0 ]; then
			f_ "failed to connect to mysql, setup requires db root password, run installer with -P argument"
		fi
	else
		echo "verify mysql connection with provided password"
		verify_pass=$(mysql -u root -p$DATABASE_ADMIN_PASSWORD -Bse 'show databases')
		if [ $? -ne 0 ]; then
			f_ "failed to verify mysql provided password"
		fi
		echo "mysql password verification passed ok"
	fi
}


#####################################
#check if mysql is already installed
check_mysql_status() {
	status=$(service mysql status)
	ret=$?
	if [ $ret -eq 0 ]; then
		echo "mysql is installed and its status is: $status"
		state=$(echo $status | sed -e 's/^mysql \([^ ,]*\).*$/\1/')
		case $state in
			stop/waiting) echo "MySQL service is not running, trying to restart service"
				#f_ "restart mysql service and restart the installer"
				service mysql start
				check_mysql_password
				;;
			start/running) echo "MySQL service is up and running"
				check_mysql_password
				;;
			*) echo "cannot recognise the state of MySQL server"
				f_ "start mysql service and restart the installer"
				;;
		esac	
	else
		echo "mysql is not installed"
		if [ -z $DATABASE_ADMIN_PASSWORD ]; then
			echo "Database admin password is not set, creating one now"
			DATABASE_ADMIN_PASSWORD=$(gen_password)
		fi
	fi
}

#############################################
# print installation configuration summary
print_summary() {
	local date_stamp=$(date)
	echo "
# MSERVE installation summary $date_stamp
        	
# Configuration:
	
_MSERVE_HOME=$MSERVE_HOME
_MSERVE_DATA=$MSERVE_DATA
_MSERVE_LOG=$MSERVE_LOG

_HTTP_SERVER=$HTTP_SERVER
_HTTP_SCHEMA=$HTTP_SCHEMA

_MSERVE_ADMIN_USER=$MSERVE_ADMIN_USER
_MSERVE_ADMIN_PASSWD=$MSERVE_ADMIN_PASSWD
_MSERVE_ADMIN_EMAIL=$MSERVE_ADMIN_EMAIL

_DATABASE_ADMIN_USER=$DATABASE_ADMIN_USER
_DATABASE_ADMIN_PASSWORD=$DATABASE_ADMIN_PASSWORD

_MSERVE_DATABASE_USER=$MSERVE_DATABASE_USER
_MSERVE_DATABASE_PASSWORD=$MSERVE_DATABASE_PASSWORD

	"
}


######################################
# check root is executing this script
check_root_f() {
	#Make sure only root can run this script
	if [[ $EUID -ne 0 ]]; then
		echo "This script must be run as root"
		exit 1
	fi
}

check_os_release () {
	release=$(lsb_release -r | awk '{print $2}')
	#if [ "$release" != "10.04" ]; then
	#	echo "this system is not Ubuntu 10.04 TLS"
	#	exit 1
	#fi
	case $release in
		10.04) echo "Release 10.04 is supported"
			;;
		11.04) echo "Release 11.04 is supported"
			;;
		11.10) echo "Release 11.10 is supported"
			;;
		*) echo "MSERVE installer does not support this ($release)"
			exit 1
			;;
	esac
}


#########################################

####################################
# parse input options arguments
while getopts 'm:d:s:l:u:e:p:U:P:a:c:hv:x:' OPTION
do
	case $OPTION in
		m) MSERVE_HOME=$OPTARG
			;;
		d) MSERVE_DATA=$OPTARG
			;;
		l) MSERVE_LOG=$OPTARG
			;;
		t) HTTP_SERVER=$OPTARG
			case $OPTARG in
				apache) HTTP_SERVER=$OPTARG
					;;
				lightttpd) HTTP_SERVER=$OPTARG
					;;
				*) echo "HTTP server $OPTARG is not supported"
					usage_f >&2
					;;
			esac
			;;
		s) HTTP_SCHEMA=$OPTARG
			case $OPTARG in
				http) HTTP_SCHEMA=$OPTARG
					;;
				https) HTTP_SCHEMA=$OPTARG
					;;
				*) echo "HTTP schema $OPTARG is not supported"
					usage_f >&2
					;;
			esac
			;;
		u) MSERVE_ADMIN_USER=$OPTARG
			;;
		e) MSERVE_ADMIN_EMAIL=$OPTARG
			;;
		p) MSERVE_ADMIN_PASSWD=$OPTARG
			;;
		U) DATABASE_ADMIN_USER=$OPTARG
			;;
		P) DATABASE_ADMIN_PASSWORD=$OPTARG
			;;
		a) MSERVE_ARCHIVE=$OPTARG
			# override embedded
			SELF_EXTRACT=0
			;;
		c) COMMAND=$OPTARG
			;;	
		v) VERBOSE="ON"
			;;
		h|\?) usage_f
			exit 2
			;;
		*) echo "Invalid option: -$OPTION" >&2
			usage_f
			exit 2
			;;
	esac
done

check_existing_installation () {
	local ret=0
	echo "check for existing MSERVE installation: $MSERVE_HOME"
	if [ ! -d $MSERVE_HOME ]; then
		echo "cannot find mserve home directory, please use the -m option"
		usage_f
		exit 3
	fi

	echo "reading existing configuration"
	if [ -f $MSERVE_HOME/.installation_summary.txt ]; then
		. $MSERVE_HOME/.installation_summary.txt
		ret=1
	fi
	return $ret
}

stop_mserve_processes () {
	echo "stopping MSERVE processes"
	PIDFILE="/tmp/mserve.pid"
	if [ -f $PIDFILE ]; then
		sudo -u www-data kill `cat -- $PIDFILE`
		sudo -u www-data rm -f -- $PIDFILE
	fi
	echo "Killed Previous Process"

	echo -e "\n\nStopping celeryd processes"
	sudo -u www-data ${MSERVE_HOME}/manage.py celeryd_multi stop \
		--logfile=${MSERVE_DATA}/celeryd%n.log -l DEBUG 2 -n:1 normal.$hn \
		-n:2 priority.$hn -Q:1 normal_tasks -Q:2 priority_tasks -c 5 \
		--pidfile=${MSERVE_DATA}/celeryd%n.pid
}


uninstall_mserve () {
	# check existing istallation and read old configuration
	check_existing_installation

	# stop mserve running processes
	stop_mserve_processes

	# remove service init scripts
	update-rc.d -f mserve-service remove || f_ "update-rc.d failed to remove mserve-service"
	rm -f /etc/init.d/mserve-service
	update-rc.d -f celeryd-service remove || f_ "update-rc.d failed to remove celeryd-service"
	rm -f /etc/init.d/celeryd-service 

	echo -e "\n\nReconfiguring http server $_HTTP_SERVER"
	if [ _HTTP_SERVER == "apache" ]; then
		a2dissite mserve
		a2dismod fastcgi rewrite bw
                if [ "${HTTP_SCHEMA}" == "https" ]; then
                    a2dissite mserve-redir
                    a2dismod ssl
                fi
		a2ensite default
		/etc/init.d/apache2 force-reload
		/etc/init.d/apache2 restart
	fi

	# remove mserve data
	echo "removing installed files from /var/opt"
	#rm -rf "$MSERVE_DATA"
	#rm -rf "$MSERVE_HOME"
	mv "${MSERVE_DATA}" "${MSERVE_DATA}${date_stamp}-$$"
	mv "${MSERVE_HOME}" "${MSERVE_HOME}${date_stamp}-$$"

	# clear mserve database
	echo -e "\n\nCleaning DB"
	cat > .drop_mserve_db <<DROPDB
	DROP DATABASE IF EXISTS mservedb;
	DROP USER 'mserve'@'%';
DROPDB
	mysql -u root -p${_DATABASE_ADMIN_PASSWORD} < .drop_mserve_db
	rm .drop_mserve_db

	# remove other configuration files
	echo -e "\n\nCleaning rabbitmq"
	rabbitmqctl clear_permissions -p myvhost myuser
	rabbitmqctl delete_vhost myvhost
	rabbitmqctl delete_user myuser

	# removed added packages

	# remove system packages

	printf "\033[01;32m\nMSERVE uninstall completed successfully.\n"
	tput sgr0
}

update_mserve () {
	# check existing istallation and read old configuration
	check_existing_installation

	# stop mserve running processes
	stop_mserve_processes

	#update variables
	MSERVE_HOME=$_MSERVE_HOME
	MSERVE_DATA=$_MSERVE_DATA
	MSERVE_LOG=$_MSERVE_LOG

	HTTP_SERVER=$_HTTP_SERVER
	HTTP_SCHEMA=$_HTTP_SCHEMA

	MSERVE_ADMIN_USER=$_MSERVE_ADMIN_USER
	MSERVE_ADMIN_PASSWD=$_MSERVE_ADMIN_PASSWD
	MSERVE_ADMIN_EMAIL=$_MSERVE_ADMIN_EMAIL

	DATABASE_ADMIN_USER=$_DATABASE_ADMIN_USER
	DATABASE_ADMIN_PASSWORD=$_DATABASE_ADMIN_PASSWORD


	MSERVE_DATABASE_USER=$_MSERVE_DATABASE_USER
	MSERVE_DATABASE_PASSWORD=$_MSERVE_DATABASE_PASSWORD

}

install_dependencies () {
    #############################
    # update system repositories
    apt-get update || f_ "fail, could not update system repositories"

    apt-get -y install debconf-utils wget || f_ "failed to install debconf-utils wget"
    apt-get -y install git-core mercurial ffmpegthumbnailer || \
            f_ "failed to install git-core mercurial ffmpegthumbnailer"


    ##########################################
    # skip rabbitmq-server confirmation screen
    echo "rabbitmq-server	rabbitmq-server/upgrade_previous	note" > rabbitmq.preseed
    cat rabbitmq.preseed | sudo debconf-set-selections

    apt-get -y install rabbitmq-server || f_ "failed to install rabbitmq-server" || \
            f_ "failed to install rabbitmq-server"
    rm rabbitmq.preseed

    echo "RabbitMQ setup"
    rabbitmqctl add_user myuser mypassword
    rabbitmqctl add_vhost myvhost
    rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"

    ##########################################
    # Setup Memcached
    apt-get -y install memcached python-memcache || f_ "failed to install memcached"

    ###################################
    # install other basic prerequisites

    install_mod_auth_token() {
            apt-get -y install autoconf libtool apache2-threaded-dev || \
                    f_ "failed to install autoconf libtool apache2-threaded-dev"
            wget http://mod-auth-token.googlecode.com/files/mod_auth_token-1.0.5.tar.gz || \
                    f_ "failed to fetch mod_auth_token"
            tar xvfz mod_auth_token-1.0.5.tar.gz
            cd mod_auth_token-1.0.5
            rm -f configure
            autoreconf -fi || f_ "failed to autoreconf mod_auth_token"
            automake -f || f_ "failed to automake mod_auth_token"
            ./configure || f_ "failed to configure mod_auth_token"
            make || f_ "failed to compile successfully mod_auth_token"
            make install || f_ "failed to install mod_auth_token"
            cd ..
            rm mod_auth_token-1.0.5.tar.gz
            rm -rf mod_auth_token-1.0.5
    }

    #######################
    # install http server
    case $HTTP_SERVER in
            apache) apt-get -y install apache2 libapache2-mod-fastcgi libapache2-mod-bw libapache2-mod-xsendfile
                    a2enmod headers
                    a2enmod auth_token
                    if [ $? -ne 0 ]; then
                            echo "mod_auth_token is not found, trying to install it"
                            install_mod_auth_token
                    fi
                    if [ "${HTTP_SCHEMA}" == "https" ]; then
                        a2enmod ssl
                    fi
                    ;;
            lighttpd) apt-get -y install lighttpd
                    ;;
    esac

    ##################
    # install erlang and python
    echo "installing system packages for erlang and python libraries"
    apt-get -y install erlang-inets erlang-asn1 erlang-corba erlang-docbuilder \
            erlang-edoc erlang-eunit erlang-ic erlang-inviso erlang-odbc erlang-parsetools \
            erlang-percept erlang-ssh erlang-tools erlang-webtool erlang-xmerl erlang-nox \
            python-setuptools python-flup python-magic python-dev python-pythonmagick \
            python-fuse sendmail python-imaging python-pycurl python-openid \
            python-lxml python-pip || \
            f_ "failed to install erlang packages and python libraries"


    ######################
    #Install python-crypto
    #Remove any installed ubuntu version
    apt-get -y remove python-crypto
    # import crypto
    echo "import sys
try:
   import Crypto
   from Crypto.Random import atfork
   sys.exit(0)
except ImportError:
   sys.exit(1)
    " | python
    if [ $? -ne 0 ]; then
            echo "installing python-crypto"
            python_crypto_url="http://ftp.dlitz.net/pub/dlitz/crypto/pycrypto/pycrypto-2.3.tar.gz"
            wget $python_crypto_url || f_ "failed to get python-crypto from $python_crypto_url"
            tar xzf pycrypto-2.3.tar.gz || f_ "failed to untar pycrypto-2.3.tar.gz"
            cd pycrypto-2.3
            python setup.py install || f_ "failed to install python-crypto"
            cd ..
            rm -rf pycrypto-2.3
    else
            echo "python-crypto found"
    fi

    ######################
    #Install paramiko
    # import paramiko
    echo "import sys
try:
   import paramiko
   sys.exit(0)
except ImportError:
   sys.exit(1)
" | python
    if [ $? -ne 0 ]; then
            echo "installing paramiko"
            paramiko_url="http://www.lag.net/paramiko/download/paramiko-1.7.7.1.tar.gz"
            wget $paramiko_url || f_ "failed to get paramiko from $paramiko_url"
            tar xzf paramiko-1.7.7.1.tar.gz || f_ "failed to untar paramiko-1.7.7.1.tar.gz"
            cd paramiko-1.7.7.1
            python setup.py install || f_ "failed to install paramiko"
            cd ..
            rm -rf paramiko-1.7.7.1
    else
            echo "paramiko found"
    fi


    ####################################################################
    # MySQL installation
    # in order to avoid mysql prompts it can be installed as:
    echo "Installing MySQL"
    MYSQL_ROOT_PWD=$DATABASE_ADMIN_PASSWORD
    echo "mysql-server-5.1 mysql-server/root_password password $MYSQL_ROOT_PWD" > mysql.preseed
    echo "mysql-server-5.1 mysql-server/root_password_again password $MYSQL_ROOT_PWD" >> mysql.preseed
    echo "mysql-server-5.1 mysql-server/start_on_boot boolean true" >> mysql.preseed
    cat mysql.preseed | sudo debconf-set-selections

    apt-get -y install mysql-server python-mysqldb || f_ "failed to install MySQL"
    rm mysql.preseed

    ######################
    # install django 1.3
    install_django () {
            wget https://www.djangoproject.com/download/1.3/tarball/ || f_ "failed to fetch Django-1.3.tar.gz"
            mv index.html Django-1.3.tar.gz
            tar xzf Django-1.3.tar.gz || f_ "failed to untar Django-1.3.tar.gz"
            cd Django-1.3
            python setup.py install || f_ "failed to install Django-1.3.tar.gz"
    }

    #from django import get_version as django_version
    #django_version()

    django_min_version=1.3
    django_version=$(django-admin.py --version)
    if [ $? -eq 0 ]; then
            echo "Django version: $django_version found"
            if [[ $django_version < $django_min_version ]]; then
                    echo "remove existing Django version and install 1.3"
                    apt-get -y remove python-django || f_ "failed to uninstall python-django"
                    install_django
            else
                    echo "django version $django_version is ok"
            fi
    else
            echo "django is not found, installing django 1.3"
            install_django
    fi



    update_rabbitmq () {
            wget http://www.rabbitmq.com/releases/rabbitmq-server/v2.5.1/rabbitmq-server_2.5.1-1_all.deb ||\
                    f_ "failed to fetch rabbitmq-server_2.3.1-1"

            dpkg -i rabbitmq-server_2.5.1-1_all.deb || f_ "failed to install rabbitmq-server_2.5.1-1"
            rm rabbitmq-server_2.5.1-1_all.deb
    }

    ##############################################################
    # update rabbitmq to a newer version, i.e. 2.5.1
    if [[ $(dpkg -l rabbitmq-server) ]]; then
            rabbit_version=$(dpkg -s rabbitmq-server | grep ^Version: | awk '{print $2}')
            if [[ $rabbit_version < "2.5.1" ]]; then
                    echo "Updating rabbitmq to 2.5"
                    update_rabbitmq
            else
                    echo "rabbitmq-server is updated"
            fi
    else
            echo "Updating rabbitmq"
            update_rabbitmq
    fi

    ######################
    #Install django-south
    pip install South

    ######################
    #Install django-oauth
    pip install django-oauth

    ################
    # install oauth2
    pip install oauth2

    ################
    # install django_extensions
    pip install django-extensions

    #######################
    # Install django-piston
    # import piston
echo "import sys
try:
   import piston
   sys.exit(0)
except ImportError:
   sys.exit(1)
    " | python
    if [ $? -ne 0 ]; then
            echo "installing django-piston"
            django_piston_url="http://bitbucket.org/jespern/django-piston"
            hg clone $django_piston_url || f_ "failed to fetch django-piston from $django_piston_url"
            cd django-piston
            python setup.py install || f_ "failed to install django-piston"
            cd ..
            rm -rf django-piston
    else
            echo "django-piston found"
    fi

    #######################
    # install celery
    pip install Celery==2.3.3

    #######################
    # Install django-celery
    pip install django-celery==2.3.3

    #########################
    # Install django-request
    pip install django-request

    ############################
    # Install django-openid-auth
    # import django_openid_auth
    echo "import sys
try:
   import django_openid_auth
   sys.exit(0)
except ImportError:
   sys.exit(1)
    " | python
    if [ $? -ne 0 ]; then
            echo "installing django-openid-auth"
            django_openid_auth_url="https://bitbucket.org/sramana/django-openid-auth"
            hg clone $django_openid_auth_url || f_ "failed to fetch django-openid-auth from $django_openid_auth_url"
            cd django-openid-auth
            python setup.py install || f_ "failed to install django-openid-auth"
            cd ..
            rm -rf django-openid-auth
    else
            echo "django-openid-auth found"
    fi

}

echo -en "\n\n\tStarting MSERVE "
case $COMMAND in
	install) echo -e "installation\n\n"
		COMMAND="installation"
		if [ -d $MSERVE_HOME ]; then
			echo "An existing installation of MSERVE found in $MSERVE_HOME. 
Please use the -c argument to either update (-c update) the existing one,
or uninstall it first (-c uninstall)."
			exit 3
		fi	
		;;
	update) echo -e "update\n\n"
		update_mserve
		;;
	uninstall) echo -e "uninstall\n\n"
		uninstall_mserve
		exit
		;;
	dependencies) echo -e "uninstall\n\n"
		install_dependencies
		exit
		;;
	*) echo -e "unknown command $COMMAND\n\n"
		usage_f
		exit 3
		;;
esac



check_mserve_archive

check_mserve_admin_passwd

if [ -z $MSERVE_DATABASE_PASSWORD ]; then
	echo "Generating password for MSERVE database user"
	MSERVE_DATABASE_PASSWORD=$(gen_password)
fi

check_mysql_status

print_summary

echo "##############################
# Do not edit or remove this file
" > /root/installation_summary.tmp
print_summary >> /root/installation_summary.tmp

# check if root is running the script and OS release
check_root_f

check_os_release


#########################################################################################

##################################################
echo "PART-I installing MServe prerequisites"
##################################################

#################################################
# upgrade system
#sudo apt-get update
#sudo apt-get -y upgrade
#sudo reboot

install_dependencies || f_ "failed to install MServe dependencies"

##########################################
# PART II 
# MSERVE configuration
echo "PART-II MServe configuration"


#############################################
# Create mserve users and mservedb database
# need to check if db exists and user too
if [ $COMMAND == "installation" ]; then
	echo "Create mserve users and mservedb database"
	echo "CREATE DATABASE mservedb; FLUSH PRIVILEGES;" | mysql -u root -p$MYSQL_ROOT_PWD || \
		f_ "failed to create mservedb database, check manually your database and drop existing mservedb."
	echo "CREATE USER '$MSERVE_DATABASE_USER'@'%' IDENTIFIED BY '$MSERVE_DATABASE_PASSWORD'; \
		GRANT ALL ON mservedb.* TO '$MSERVE_DATABASE_USER';" | \
		mysql -u root -p$MYSQL_ROOT_PWD || f_ "failed to create mserve database user, check database manually and drop existing $MSERVE_DATABASE_USER user."

	# echo "select user from mysql.user where user='mserve'" | mysql -u root -pwtnq6dWTgnM | grep -q mserve
	# echo "use mservedb;" | mysql -u root -pwtnq6dWTgnM
fi

############################################################
# create a temp directory and install mserve components here

MSERVE_CHECKOUT=`mktemp -d`
MSERVE_TEMP=`mktemp -d`

#########################
# Install mserve 
echo -n "installing mserve from"
if [ "$MSERVE_ARCHIVE" == "NOTSET" ]; then
	mserve_url="git://github.com/itinnov-mserve/MServe.git"
	echo " $mserve_url"
	git clone $mserve_url $MSERVE_CHECKOUT || f_ "failed to fetch mserve from $mserve_url"
else
	# use the provided mserve archive, we assume tgz file
	echo " $MSERVE_ARCHIVE"
        tar -C $MSERVE_CHECKOUT --extract --file=$MSERVE_ARCHIVE || f_ "failed to untar MSERVE archive"
        MSERVE_CHECKOUT="$MSERVE_CHECKOUT/mserve"
fi

cp -a $MSERVE_CHECKOUT/* $MSERVE_TEMP || f_ "failed to copy mserve files in temp dir"

cd $MSERVE_TEMP

#########################################
# Configuring MSERVE in standalone mode
if [ $COMMAND == "installation" ]; then
	echo "Configuring MServe in standalone mode"
	mkdir -p ${MSERVE_DATA}/www-root
	chown -R www-data:www-data ${MSERVE_DATA}
	echo "Configuring mserve log"
	mkdir -p "${MSERVE_LOG}"
	chown -R www-data:www-data "${MSERVE_LOG}"
fi


#####################################
#Configuration of mserve settings.py
mv $MSERVE_TEMP/django-mserve/settings.py $MSERVE_TEMP/django-mserve/settings_dist.py
sed -e "s#MSERVE_HOME='/opt/mserve'#MSERVE_HOME='${MSERVE_HOME}/django-mserve'#; \
	s#MSERVE_DATA='/var/opt/mserve-data'#MSERVE_DATA='${MSERVE_DATA}'#; \
	s#MSERVE_LOG='/var/log/mserve'#MSERVE_LOG='${MSERVE_LOG}'#; \
	s#\('USER'.*:.*'\).*\('.*\)\$#\1$MSERVE_DATABASE_USER\2#; \
	s#\('PASSWORD'.*:.*'\).*\('.*\)\$#\1$MSERVE_DATABASE_PASSWORD\2#" \
	$MSERVE_TEMP/django-mserve/settings_dist.py > $MSERVE_TEMP/django-mserve/settings.py


###########################
# modify restart.sh
mv $MSERVE_TEMP/django-mserve/restart.sh $MSERVE_TEMP/django-mserve/restart_dist.sh
sed -e "s#^MSERVE_HOME=/opt/mserve#MSERVE_HOME=${MSERVE_HOME}/django-mserve#; \
	s#^MSERVE_DATA=/var/opt/mserve-data#MSERVE_DATA=${MSERVE_DATA}#" \
	$MSERVE_TEMP/django-mserve/restart_dist.sh > $MSERVE_TEMP/django-mserve/restart.sh
chmod +x $MSERVE_TEMP/django-mserve/restart.sh


####################
# modify celaryd.sh
mv $MSERVE_TEMP/django-mserve/celeryd.sh $MSERVE_TEMP/django-mserve/celeryd_dist.sh
sed -e "s#^MSERVE_HOME='/opt/mserve'#MSERVE_HOME='${MSERVE_HOME}/django-mserve'#; \
	s#^MSERVE_DATA='/var/opt/mserve-data'#MSERVE_DATA='${MSERVE_DATA}'#; \
	s#^MSERVE_LOG='/var/log/mserve'#MSERVE_LOG='${MSERVE_LOG}'#" \
	$MSERVE_TEMP/django-mserve/celeryd_dist.sh > $MSERVE_TEMP/django-mserve/celeryd.sh

chmod +x $MSERVE_TEMP/django-mserve/celeryd.sh

############################
# configure init scripts
if [ -f $MSERVE_TEMP/scripts/mserve-service ]; then
	mv $MSERVE_TEMP/scripts/mserve-service $MSERVE_TEMP/scripts/mserve-service_dist
	sed -e "s#^MSERVE_HOME='/opt/mserve'#MSERVE_HOME='${MSERVE_HOME}/django-mserve'#; \
		s#^MSERVE_DATA='/var/opt/mserve-data'#MSERVE_DATA='${MSERVE_DATA}'#; \
		s#^MSERVE_LOG='/var/log/mserve'#MSERVE_LOG='${MSERVE_LOG}'#" \
		$MSERVE_TEMP/scripts/mserve-service_dist > $MSERVE_TEMP/scripts/mserve-service
	chmod +x $MSERVE_TEMP/scripts/mserve-service
else
	echo "No $MSERVE_TEMP/scripts/mserve-service found"
fi

if [ -f $MSERVE_TEMP/scripts/celeryd-service ]; then
	mv $MSERVE_TEMP/scripts/celeryd-service $MSERVE_TEMP/scripts/celeryd-service_dist
	sed -e "s#^MSERVE_HOME='/opt/mserve'#MSERVE_HOME='${MSERVE_HOME}/django-mserve'#; \
		s#^MSERVE_DATA='/var/opt/mserve-data'#MSERVE_DATA='${MSERVE_DATA}'#; \
		s#^MSERVE_LOG='/var/log/mserve'#MSERVE_LOG='${MSERVE_LOG}'#" \
		$MSERVE_TEMP/scripts/celeryd-service_dist > $MSERVE_TEMP/scripts/celeryd-service
	chmod +x $MSERVE_TEMP/scripts/celeryd-service
else
	echo "No scripts/celeryd-service found"
fi

cd ..


##################################
# configure lighttpd
configure_lighttpd () {
	#################################
	# lighttpd configuration 
	# edit /etc/lighttpd/lighttpd.conf
	# enable mod_rewrite
	# set root directory to /var/opt/mserve-data/www-root/
	if [ -f /etc/lighttpd/lighttpd.conf-dist ]; then
		cp /etc/lighttpd/lighttpd.conf-dist /etc/lighttpd/lighttpd.conf
	else
		cp  /etc/lighttpd/lighttpd.conf /etc/lighttpd/lighttpd.conf-dist
	fi

	cat /etc/lighttpd/lighttpd.conf | sed -e "s@^# *\"mod_rewrite\"@            \"mod_rewrite\"@ ; \
		s@^server.document-root *= \"/var/www/\" *\$@server.document-root = \"${MSERVE_DATA}/www-root\"@" > /tmp/lighttpd.conf

	cp /tmp/lighttpd.conf /etc/lighttpd/lighttpd.conf


	if [ -f /etc/lighttpd/conf-available/10-fastcgi.conf-dist ]; then
		cp /etc/lighttpd/conf-available/10-fastcgi.conf-dist /etc/lighttpd/conf-available/10-fastcgi.conf
	else
		cp /etc/lighttpd/conf-available/10-fastcgi.conf /etc/lighttpd/conf-available/10-fastcgi.conf-dist
	fi

	cat $MSERVE_TEMP/scripts/10-mserve-EXAMPLE.conf | sed -e "s#/var/mserve/dl#$MSERVE_DATA/dl#" > \
		/etc/lighttpd/conf-available/10-fastcgi.conf


	#######################
	# enable fastcgi module
	echo "enable fastcgi module"
	lighttpd-enable-mod fastcgi || f_ "failed to enable fastcgi module"

}


################################
# configure apache
configure_apache () {
	local _source=/etc/apache2/sites-available/default
        if [ "${HTTP_SCHEMA}" == "https" ]; then
            echo "SCHEMA IS $HTTP_SCHEMA"
            local _source=/etc/apache2/sites-available/default-ssl
            local _redirect=/etc/apache2/sites-available/mserve-redir
            echo "<VirtualHost *:80>
            ServerAdmin webmaster@localhost
            RewriteEngine On
            RewriteCond %{HTTPS} !=on
            RewriteRule ^(.*) https://%{SERVER_NAME}/\$1 [R,L]
            </VirtualHost>" > $_redirect || f_ "failed to create mserve http to https redirect correctly"
        fi
	local _target=/etc/apache2/sites-available/mserve
	# create a new site, e.g. copy the default one
	cat $_source | sed -e "s@/var/www@${MSERVE_DATA}/www-root@ ; \
		s@DocumentRoot.*\$@DocumentRoot ${MSERVE_DATA}/www-root\n\n\
	FastCGIExternalServer ${MSERVE_DATA}/www-root/mysite.fcgi -socket /tmp/mserve-fcgi.sock -idle-timeout 30\n\n\
        XSendFile On\n\
        XSendFileAllowAbove On\n\
	Alias /media ${MSERVE_DATA}/www-root/media\n\
        Alias /dl /var/opt/mserve-data/dl\n\n\
	RewriteEngine On\n\
	RewriteRule ^/(dl.*)$ /\$1 [QSA,L,PT]\n\
	RewriteRule ^/(media.*)$ /\$1 [QSA,L,PT]\n\
	RewriteRule ^/(mservemedia.*)$ /\$1 [QSA,L,PT]\n\
	RewriteRule ^/(mservethumbs.*)$ /\$1 [QSA,L,PT]\n\
	RewriteRule ^/favicon\.ico$ /media/favicon.ico [QSA,L,PT]\n\
	RewriteRule ^/(\\/.*)$ /\$1 [QSA,L,PT]\n\
	RewriteCond %{REQUEST_FILENAME} !-f\n\
	RewriteRule ^/(.*)$ /mysite.fcgi/\$1 [QSA,L]\n\n\
        <Location /dl/>\n\
            SetEnvIf Request_URI '^.*/([^/]*)$' FILENAME=\$1\n\
            Header set 'Content-disposition' 'attachment; filename=%{FILENAME}e'\n\
            UnsetEnv FILENAME\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenPrefix /dl/\n\
            AuthTokenTimeout 60\n\
        </Location>\n\n\
        <Location /dl/100/>\n\
            AuthTokenPrefix /dl/100/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 100\n\
        </Location>\n\n\
        <Location /dl/1000/>\n\
            AuthTokenPrefix /dl/1000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 1000\n\
        </Location>\n\n\
        <Location /dl/10000/>\n\
            AuthTokenPrefix /dl/10000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 10000\n\
        </Location>\n\n\
        <Location /dl/100000/>\n\
            AuthTokenPrefix /dl/100000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 100000\n\
        </Location>\n\n\
        <Location /dl/1000000/>\n\
            AuthTokenPrefix /dl/1000000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 1000000\n\
        </Location>\n\n\
        <Location /dl/10000000/>\n\
            AuthTokenPrefix /dl/10000000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 10000000\n\
        </Location>\n\n\
        <Location /dl/100000000/>\n\
            AuthTokenPrefix /dl/100000000/\n\
            AuthTokenSecret 'ugeaptuk6'\n\
            AuthTokenTimeout 60\n\
            BandWidthModule On\n\
            ForceBandWidthModule On\n\
            BandWidth all 100000000\n\
        </Location>\n\n\
	@" > $_target || f_ "failed to create mserve site correctly"	

	if [ ! -s $_target ]; then
		f_ "failed to create successfully $_target (zero size mserve site detected)"
	fi

	###################################################
	# disable old site enable fast cgi, enable new site
	a2dissite default || f_ "failed to disable apache default site"
	a2enmod fastcgi rewrite bw || f_ "failed to enable fastcgi rewrite bw modules"
        if [ "${HTTP_SCHEMA}" == "https" ]; then
            a2enmod ssl || f_ "failed to enable ssl mod"
            a2ensite mserve-redir || f_ "failed to enable redirect to https site"
        fi
	a2ensite mserve	|| f_ "failed to enable mserve site"
}


#######################
# configure http server
echo "configuring $HTTP_SERVER as HTTP server"
case $HTTP_SERVER in
	apache) configure_apache
		;;
	lighttpd) configure_lighttpd
		;;
esac


####################################
# PART III deploy mserve in /var/opt
####################################
echo -e "\n\nPART III deploying mserve in $MSERVE_HOME"


########################################################################
# changing permissions and running the rest from /opt/mserve as www-data
old_installation=${MSERVE_HOME}-${date_stamp}-$$
if [ $COMMAND == "update" ]; then
	echo "moving old installation in $old_installation"
	mv $MSERVE_HOME $old_installation
fi

echo "copying mserve directory"
cd
mv $MSERVE_TEMP ${MSERVE_HOME} || f_ "failed to copy mserve files in MSERVE_HOME location $MSERVE_HOME"
chown -R www-data:www-data ${MSERVE_HOME} || f_ "failed to change ${MSERVE_HOME} permissions to www-data"
chmod 755 ${MSERVE_HOME} || f_ "failed to chmod MSERVE_HOME $MSERVE_HOME to 755"

#######################
# create media links
echo "creating media links"
cd ${MSERVE_DATA}/www-root

DJANGO_HOME=`python -c "
import django
import os
print os.path.dirname(django.__file__)
"`

ln -s ${DJANGO_HOME}/contrib/admin/media
ln -s ${MSERVE_HOME}/static mservemedia


######################
# Rabbit MQ Setup
if [ $COMMAND == "installation" ]; then
	echo "RabbitMQ setup"
	rabbitmqctl add_user myuser mypassword
	rabbitmqctl add_vhost myvhost
	rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"
fi

######################
# restart http server 
echo "Restarting http server $HTTP_SERVER"
case $HTTP_SERVER in
	apache) /etc/init.d/apache2 restart || \
		f_ "failed to reload correctly apache configuration"
		;;
	lighttpd) /etc/init.d/lighttpd force-reload || \
		f_ "failed to reload lighttpd configuration" 
		;;
esac

if [ $COMMAND == "installation" ]; then

	###############################################################################
	# update mserve db, you need to provide information creating user and password
	cd
	now=$(date +"%F %T")
	cat > .python_script<<EOFPY
from django.utils.hashcompat import sha_constructor
from django.utils.encoding import smart_str
import random
ran = smart_str(str(random.random()))
salt = sha_constructor(ran).hexdigest()[:5]
hash = sha_constructor(salt + smart_str("$MSERVE_ADMIN_PASSWD")).hexdigest()
print "sha1\$%s\$%s" % (salt, hash)
EOFPY

	hash=$(python .python_script)
	rm .python_script

	cat > initial_data.json <<JSON
[
  {
    "pk": 1,
    "model": "auth.user",
    "fields": {
      "username": "$MSERVE_ADMIN_USER",
      "first_name": "",
      "last_name": "",
      "is_active": true,
      "is_superuser": true,
      "is_staff": true,
      "last_login": "$now",
      "groups": [],
      "user_permissions": [],
      "password": "$hash",
      "email": "$MSERVE_ADMIN_EMAIL",
      "date_joined": "$now"
    }
  }
]
JSON

fi

sudo -u www-data ${MSERVE_HOME}/django-mserve/manage.py syncdb --noinput || f_ "failed to configure mserve database"
sudo -u www-data ${MSERVE_HOME}/django-mserve/manage.py schemamigration jobservice dataservice --auto
sudo -u www-data ${MSERVE_HOME}/django-mserve/manage.py migrate --noinput
sudo -u www-data ${MSERVE_HOME}/django-mserve/manage.py register_tasks dataservice

if [ -f initial_data.json ]; then
	rm initial_data.json
fi

# fix db
if [ $COMMAND == "installation" ]; then
	mysql -u $MSERVE_DATABASE_USER -p$MSERVE_DATABASE_PASSWORD < \
		${MSERVE_HOME}/scripts/request_fix.sql || \
		f_ "failed to fix mservedb"
fi


###############################
#PART IV  Starting up service
###############################

# start up mserver
if [ -x ${MSERVE_HOME}/scripts/mserve-service ]; then
	echo "trying to start mserve using mserve using init script"
	${MSERVE_HOME}/scripts/mserve-service start || f_ "mserve-service failed to start mserve"
	# try to deploy service script
	sleep 4
	echo "trying to stop mserve using mserve init script"
	${MSERVE_HOME}/scripts/mserve-service stop || f_ "mserve-service failed to stop mserve"
	echo "deploying mserve init script"
	cp $MSERVE_HOME/scripts/mserve-service /etc/init.d/ || f_ "failed to copy mserve-service script to /etc/init.d"
	update-rc.d mserve-service defaults || f_ "failed to register mserve-service with system update-rc.d util"
	# starting service
	echo "starting mserve service"
	sleep 4
	service mserve-service start || f_ "service mserve-service start failed to start mserve"
else
	echo "no mserve init script found, starting mserve service manually"
	${MSERVE_HOME}/django-mserve/restart.sh || f_ "failed to restart/etc mserve"
fi

# start celeryd
if [ -x ${MSERVE_HOME}/scripts/celeryd-service ]; then
	echo "trying to start celeryd using celeryd init script"
	${MSERVE_HOME}/scripts/celeryd-service start || f_ "celeryd-service failed to start celeryd"
	# try to deploy service script
	sleep 4
	echo "trying to stop celeryd service using init script"
	${MSERVE_HOME}/scripts/celeryd-service stop || f_ "celeryd-service failed to stop mserve"
	cp $MSERVE_HOME/scripts/celeryd-service /etc/init.d/ || f_ "failed to copy celeryd-service script to /etc/init.d"
	update-rc.d celeryd-service defaults || f_ "failed to register celeryd-service with system update-rc.d util"
	# starting service
	echo "starting celeryd service"
	sleep 4
	service celeryd-service start || f_ "service mserve-service start failed to start mserve"

else
	echo "no celeryd init script found, starting celeryd service manually"
	${MSERVE_HOME}/django-mserve/celeryd.sh || f_ "failed to restart celeryd"
fi

# sometimes apache needs restarting
if [ $HTTP_SERVER == "apache" ]; then
	if [ ! /etc/init.d/apache2 ]; then
		echo "restarting apache"
		/etc/init.d/apache2 restart || f_ "failed to restart apache"
	fi
fi

#print_summary | tee ${MSERVE_HOME}/installation_summary.txt
mv /root/installation_summary.tmp ${MSERVE_HOME}/.installation_summary.txt || \
	f_ "failed to copy installation summary from /root to ${MSERVE_HOME}"

echo -e "\nNB: a copy of MSERVE installation summary is stored under ${MSERVE_HOME}/.installation_summary.txt"

if [ ! -f /etc/init.d/mserve-service ]; then
	echo -e "\nNB: mserve-service should be copied into /etc/init.d directory."
        echo -e "\nNB: update-rc.d mserve-service defaults"
fi

if [ ! -f /etc/init.d/celeryd-service ]; then
	echo -e "\nNB: celeryd-service should be copied into /etc/init.d directory."
	echo -e "\nNB: update-rc.d celeryd-service defaults"
fi

if [ -d $old_installation ]; then
	echo -e "\nThe old MSERVE installation, moved in $old_installation, can now be deleted."
fi

printf "\033[01;32m\nMSERVE $COMMAND completed successfully.\n"
tput sgr0

exit 0




