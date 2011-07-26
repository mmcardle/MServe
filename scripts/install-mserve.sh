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


MSERVE_HOME=/var/opt/mserve
MSERVE_DATA=/var/opt/mserve-data
MSERVE_ADMIN_USER="admin"
MSERVE_ADMIN_EMAIL="admin@my.email.com"
MSERVE_ADMIN_PASSWD=
MSERVE_DATABASE_USER=mserve
MSERVE_DATABASE_PASSWORD=
HTTP_SERVER=apache
VERBOSE=
MSERVE_ARCHIVE=
DATABASE_ADMIN_USER=root
DATABASE_ADMIN_PASSWORD=


###############
# print usage
usage_f() {
	echo "usage: $0 [-m mserve home] [-d mserve data] [-s http server] [mserve tarball]
	OPTIONS:
	-m <MSERVE home directory>	# default: /var/opt/mserve
	-d <MSERVE data directory>	# default: /var/opt/mserve-data
	-s <MSERVE HTTP server>     	# [apache|lighttpd] default: apache
	-u <MSERVE admin user name> 	# administrtor user name, default: admin
	-p <MSERVE admin password>	# admin password
	-e <MSERVE admin email>		# administrator email, default: admin@my.email.com
	-U <Database admin user>	# Database admin user, default root
	-P <Database admin password>	# Database admin password
	-v verbose mode

	example: $0 -s apache
"
}


###################################
# report a fault and exit function
f_ () {
	echo $1
	exit 2
}


gen_password () {
	openssl rand -base64 8 | sed 's/0/2/;s/=//;s/O/P/;s/l/s/;s/1/2/;s/\//j/'
}


###################################
# parse input options arguments
while getopts 'm:d:s:u:e:p:U:P:hv' OPTION
do
	case $OPTION in
		m) MSERVE_HOME=$OPTARG
			;;
		d) MSERVE_DATA=$OPTARG
			;;
		s) HTTP_SERVER=$OPTARG
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


##############################################
# check for mserve archive argument provided
if [ $# -ge 1 ]; then
	MSERVE_ARCHIVE=$1
	
	# check if archive exists
	if [ ! -f $MSERVE_ARCHIVE ]; then
		f_ "specified MSERVE archive is not found"
	fi
	echo "MSERVE archive $MSERVE_ARCHIVE found"
	MSERVE_ARCHIVE=$(pwd)/$MSERVE_ARCHIVE
	if [ ! -f $MSERVE_ARCHIVE ]; then
		f_ "failed to find absolute path of $MSERVE_ARCHIVE"
	fi
fi


#######################
# check for passwords
if [ -n $MSERVE_ADMIN_PASSWD ]; then
	echo "MSERVE admin password is not set, generating a new one"
	MSERVE_ADMIN_PASSWD=$(gen_password)
fi


echo "Generating password for MSERVE database user"
MSERVE_DATABASE_PASSWORD=$(gen_password)

if [ -n $DATABASE_ADMIN_PASSWORD ]; then
	echo "Database admin password is not set, generating a new one"
	DATABASE_ADMIN_PASSWORD=$(gen_password)
fi
	

#############################################
# print installation configuration summary
print_summary() {
	date_stamp=$(date)
	echo "
	MSERVE installation summary $date_stamp
        	
	Configuration:
	
	MSERVE_HOME=$MSERVE_HOME
	MSERVE_DATA=$MSERVE_DATA

	HTTP_SERVER=$HTTP_SERVER

	MSERVE_ADMIN_USER=$MSERVE_ADMIN_USER
	MSERVE_ADMIN_PASSWD=$MSERVE_ADMIN_PASSWD
	MSERVE_ADMIN_EMAIL=$MSERVE_ADMIN_EMAIL

	DATABASE_ADMIN_USER=$DATABASE_ADMIN_USER
	DATABASE_ADMIN_PASSWORD=$DATABASE_ADMIN_PASSWORD

	MSERVE_DATABASE_USER=$MSERVE_DATABASE_USER
	MSERVE_DATABASE_PASSWORD=$MSERVE_DATABASE_PASSWORD

	NB: the above information is stored under $MSERVE_HOME/installation_summary.txt
	"
}

echo "##############################
# Do not edit or remove this file

" > /root/installation_summary.txt
print_summary >> /root/installation_summary.txt


######################################
# check root is executing this script
check_root_f() {
	# need to run tests as root ;-(
	#Make sure only root can run this script
	if [[ $EUID -ne 0 ]]; then
		echo "This script must be run as root"
		exit 1
	fi
}


#####################################################
# check if root is running the script and OS release
check_root_f

release=$(lsb_release -r | awk '{print $2}')
if [ "$release" != "10.04" ]; then
	echo "this system is not Ubuntu 10.04 TLS"
	exit 1
fi



##################################################
echo "PART-I installing MServe prerequisites"

#################################################
# upgrade system
#sudo apt-get update
#sudo apt-get -y upgrade

#sudo reboot

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
}


#######################
# install http server
case $HTTP_SERVER in 
	apache) apt-get -y install apache2 libapache2-mod-fastcgi libapache2-mod-xsendfile
	        install_mod_auth_token	
		;;
        lighttpd) apt-get -y install lighttpd
                ;;
esac


##################
# install erlang
apt-get -y install erlang-inets erlang-asn1 erlang-corba erlang-docbuilder \
	erlang-edoc erlang-eunit erlang-ic erlang-inviso erlang-odbc erlang-parsetools \
	erlang-percept erlang-ssh erlang-tools erlang-webtool erlang-xmerl erlang-nox \
	python-django python-setuptools python-flup python-magic \
	python-imaging python-pycurl python-openid python-crypto python-lxml || \
	f_ "failed to install erlang packages"


####################################################################
# MySQL installation
# during installation set MySQL root password, we assume it is pass 
# 
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
# install django 1.2.3
#echo "Installing django_1.2.3-3"
#wget  http://security.debian.org/debian-security/pool/updates/main/p/python-django/python-django_1.2.3-3+squeeze1_all.deb || \
#	f_ "failed to fetch python-django_1.2.3-3"
#
#dpkg -i python-django_1.2.3-3+squeeze1_all.deb || f_ "failed to install python-django"
#rm python-django_1.2.3-3+squeeze1_all.deb
apt-get -y remove python-django || f_ "failed to uninstall python-django"
wget https://www.djangoproject.com/download/1.3/tarball/ || f_ "failed to fetch Django-1.3.tar.gz"
mv index.html Django-1.3.tar.gz 
tar xzf Django-1.3.tar.gz || f_ "failed to untar Django-1.3.tar.gz"
cd Django-1.3
python setup.py install || f_ "failed to install Django-1.3.tar.gz"



##############################################################
# update rabbitmq to a newer version, i.e. 2.5.1
echo "Updating rabbitmq to 2.5"
wget http://www.rabbitmq.com/releases/rabbitmq-server/v2.5.1/rabbitmq-server_2.5.1-1_all.deb ||\
	f_ "failed to fetch rabbitmq-server_2.3.1-1"

dpkg -i rabbitmq-server_2.5.1-1_all.deb || f_ "failed to install rabbitmq-server_2.5.1-1"
rm rabbitmq-server_2.5.1-1_all.deb





##########################################
# PART II 
# MSERVE configuration
echo "PART-II MServe configuration"


#############################################
# Create mserve users and mservedb database
echo "Create mserve users and mservedb database"
echo "CREATE DATABASE mservedb;" | mysql -u root -p$MYSQL_ROOT_PWD || f_ "failed to create mservedb database"
echo "CREATE USER '$MSERVE_DATABASE_USER'@'localhost' IDENTIFIED BY '$MSERVE_DATABASE_PASSWORD'; \
	GRANT ALL ON mservedb.* TO '$MSERVE_DATABASE_USER';" | \
	mysql -u root -p$MYSQL_ROOT_PWD || f_ "failed to create mserve database user"



############################################################
# create a temp directory and install mserve components here
cd 
mkdir mserve$$
cd mserve$$


######################
#Install django-oauth
echo "Installing django-oauth"
django_oauth_url="http://bitbucket.org/david/django-oauth"
hg clone $django_oauth_url || f_ "failed to checkout django-auth from $django_oauth_url"
cd django-oauth
python setup.py install || f_ "failed to install django-oauth"
cd ..


################
# install oauth2
echo "Installing oauth2"
python_oauth2_url="https://github.com/simplegeo/python-oauth2.git"
git clone $python_oauth2_url || f_ "failed to fetch $python_oauth2_url"
cd python-oauth2/
make || f_ "failed to make python-oauth2"
easy_install dist/oauth2-1.5.170-py2.6.egg || f_ "failed to install python-oauth2" 
cd ..


#######################
# Install django-piston
echo "installing django-piston"
django_piston_url="http://bitbucket.org/jespern/django-piston"
hg clone $django_piston_url || f_ "failed to fetch django-piston from $django_piston_url"
cd django-piston
python setup.py install || f_ "failed to install django-piston"
cd ..


#######################
# Install django-celery
echo "installing django-celery"
django_celery_url="https://github.com/ask/django-celery.git"
git clone $django_celery_url || f_ "failed to fetch django-celery from $django_celery_url"
cd  django-celery
python setup.py install || f_ "failed to install django-celery"
cd ..


#########################
# Install django-request
echo "installing django-request"
django_request_url="https://github.com/kylef/django-request.git"
git clone $django_request_url || f_ "failed to fetch django-request from $django_request_url"
#cp -r ../django-request .
cd django-request
python setup.py install || f_ "failed to install django-request"
cd ..


############################
# Install django-openid-auth
echo "installing django-openid-auth"
django_openid_auth_url="https://bitbucket.org/sramana/django-openid-auth"
hg clone $django_openid_auth_url || f_ "failed to fetch django-openid-auth from $django_openid_auth_url"
cd django-openid-auth
python setup.py install || f_ "failed to install django-openid-auth"
cd ..


#########################
# Install pp-dataservice
echo -n "installing mserve pp-dataservice from"
if [ -z "$MSERVE_ARCHIVE" ]; then
	mserve_url="git://soave.it-innovation.soton.ac.uk/git/pp-dataservice"
	echo " $mserve_rul"
	git clone $mserve_url || f_ "failed to fetch mserve from $mserve_url"
	cd pp-dataservice

	# checkout mm version
	git checkout mm-pp-dataservice

	git submodule init || f_ "failed to init submodule"
	git submodule update || f_ "failed to update submodule"
else
	# use the provided mserve archive, we assume tgz file
	echo " $MSERVE_ARCHIVE"
	tar xvfz $MSERVE_ARCHIVE || f_ "failed to untar MSERVE archive"
	cd pp-dataservice
fi


#########################################
# Configuring MSERVE in standalone mode
echo "Configuring MServe in standalone mode"
mkdir -p ${MSERVE_DATA}/www-root
chown -R www-data:www-data ${MSERVE_DATA}


#####################################
#Configuration of mserve settings.py
mv mserve/settings.py mserve/settings_dist.py
sed -e "s#/opt/mserve#${MSERVE_HOME}#g; s#/var/mserve#${MSERVE_DATA}#g; \
	s#\('USER'.*:.*'\).*\('.*\)\$#\1$MSERVE_DATABASE_USER\2#; \
	s#\('PASSWORD'.*:.*'\).*\('.*\)\$#\1$MSERVE_DATABASE_PASSWORD\2#" \
	mserve/settings_dist.py > mserve/settings.py


###########################
# modify mserve/restart.sh
# other user, e.g. /var/opt/mserve
mv mserve/restart.sh mserve/restart_dist.sh
sed -e "s#/opt/mserve#${MSERVE_HOME}#g; s#/var/mserve#${MSERVE_DATA}#g" \
	mserve/restart_dist.sh > mserve/restart.sh
chmod +x mserve/restart.sh


####################
# modify celaryd.sh
mv mserve/celeryd.sh mserve/celeryd_dist.sh
sed -e "s#\./manage.py#${MSERVE_HOME}/pp-dataservice/mserve/manage.py#g; s#/var/mserve#${MSERVE_DATA}#g" \
	mserve/celeryd_dist.sh > mserve/celeryd.sh
chmod +x mserve/celeryd.sh
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

	cat scripts/10-mserve-EXAMPLE.conf | sed -e "s#/var/mserve/dl#$MSERVE_DATA/dl#" > \
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
	local _target=/etc/apache2/sites-available/mserve
	# create a new site, e.g. copy the default one
	cat $_source | sed -e "s@/var/www@${MSERVE_DATA}/www-root@ ; \
		s@DocumentRoot.*\$@DocumentRoot ${MSERVE_DATA}/www-root\n\n\
	FastCGIExternalServer ${MSERVE_DATA}/www-root/mysite.fcgi -socket /tmp/pp-dataservice-fcgi.sock\n\n\
        XSendFile On\nXSendFileAllowAbove On\n\
	Alias /media ${MSERVE_DATA}/www-root/media\n\n\
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
	    AuthTokenSecret \'ugeaptuk6\'\n\
	    AuthTokenPrefix /dl/\n\
	    AuthTokenTimeout 60\n\
	</Location>\n\n\
	@" > $_target || f_ "failed to create mserve site correctly"	

	if [ ! -s $_target ]; then
		f_ "failed to create successfully $_target (zero size mserve site detected)"
	fi

	###############################################################
	# create a link to dl, it does not exist at the moment but will
	# become alive when mserve starts
	sudo -u www-data ln -s ../dl  ${MSERVE_DATA}/www-root/dl

	###################################################
	# disable old site enable fast cgi, enable new site
	a2dissite default || f_ "failed to disable apache default site"
	a2enmod fastcgi rewrite || f_ "failed to enable fastcgi rewrite modules"
	a2ensite mserve	|| f_ "failed to enable mserve site"
}


#######################
# configure http server
echo "configuring $HTTP_SERVER as HTTP server"
echo $HTTP_SERVER > .HTTP_SERVER
case $HTTP_SERVER in
	apache) configure_apache
		;;
	lighttpd) configure_lighttpd
		;;
esac




####################################
# PART III deploy mserve in /var/opt
####################################

########################################################################
# changing permissions and running the rest from /opt/mserve as www-data
echo "copying mserve directory"
cd
mkdir ${MSERVE_HOME} || f_ "failed to create $MSERVE_HOME directory"
cp -r mserve$$/* ${MSERVE_HOME}
chown -R www-data:www-data ${MSERVE_HOME}
rm -rf mserve$$


#######################
# create media links
echo "creating media links"
cd ${MSERVE_DATA}/www-root
ln -s /usr/share/pyshared/django/contrib/admin/media
ln -s ${MSERVE_HOME}/pp-dataservice/static mservemedia


######################
# Rabbit MQ Setup
echo "RabbitMQ setup"
rabbitmqctl add_user myuser mypassword
rabbitmqctl add_vhost myvhost
rabbitmqctl set_permissions -p myvhost myuser ".*" ".*" ".*"


######################
# restart http server 
echo "Restarting http server $HTTP_SERVER"
case $HTTP_SERVER in
	apache) /etc/init.d/apache2 force-reload || \
		f_ "failed to reload correctly apache configuration"
		;;
	lighttpd) /etc/init.d/lighttpd force-reload || \
		f_ "failed to reload lighttpd configuration" 
		;;
esac


###############################################################################
# update mserve db, you need to provide information creating user and password
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

sudo -u www-data ${MSERVE_HOME}/pp-dataservice/mserve/manage.py syncdb --noinput || \
	f_ "failed to configure mserve database"
rm initial_data.json

# fix db
mysql -u $MSERVE_DATABASE_USER -p$MSERVE_DATABASE_PASSWORD < ${MSERVE_HOME}/pp-dataservice/scripts/request_fix.sql || \
	f_ "failed to fix mservedb"


echo "##############################
# Do not edit or remove this file

" > ${MSERVE_HOME}/.installation_summary.txt
print_summary >> ${MSERVE_HOME}/.installation_summary.txt



###############################
#PART IV  Starting up service
###############################

# start up mserver
${MSERVE_HOME}/pp-dataservice/mserve/restart.sh || f_ "failed to restart mserve"

# Celery Startup in debugging mode
#sudo -u www-data ${MSERVE_HOME}/pp-dataservice/mserve/manage.py celeryd --verbosity=2 --loglevel=DEBUG

${MSERVE_HOME}/pp-dataservice/mserve/celeryd.sh || f_ "failed to restart celeryd"

# sometimes apache needs restarting
if [ $HTTP_SERVER == "apache" ]; then
	if [ ! /etc/init.d/apache2 ]; then
		echo "restarting apache"
		/etc/init.d/apache2 restart || f_ "failed to restart apache"
	fi
fi

#print_summary | tee ${MSERVE_HOME}/installation_summary.txt
mv /root/installation_summary.txt ${MSERVE_HOME}/.installation_summary.txt || \
	f_ "failed to copy installation summary from /root to ${MSERVE_HOME}"
print_summary

exit

