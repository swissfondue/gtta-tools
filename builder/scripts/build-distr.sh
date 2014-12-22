#!/bin/bash

set -e

if [ -z $1 ] || [ -z $2 ] || [ -z $3 ]
then
    echo "Usage: build-distr.sh <version> <root password> <user password>"
    exit 1
fi

# constants and variables
VERSION=$1
ROOT_PW=$2
USER_PW=$3
SRC_DIR=/tmp/files
ROOT_DIR=/opt/gtta
FILES_DIR=$ROOT_DIR/files
SECURITY_DIR=$ROOT_DIR/security
SSL_DIR=$SECURITY_DIR/ssl
CA_DIR=$SECURITY_DIR/ca
SCRIPTS_DIR=$ROOT_DIR/scripts
VERSION_DIR=$ROOT_DIR/versions/$VERSION
SSH_DIR=/home/gtta/.ssh

DIRECTORIES=(
    "$ROOT_DIR/config"
    "$ROOT_DIR/runtime"
    "$FILES_DIR/attachments"
    "$FILES_DIR/header-images"
    "$FILES_DIR/logos"
    "$FILES_DIR/rating-images"
    "$FILES_DIR/reports"
    "$FILES_DIR/report-templates"
    "$SECURITY_DIR/ca"
    "$SECURITY_DIR/keys"
    "$SECURITY_DIR/ssl"
    "$SCRIPTS_DIR/lib"
    "$VERSION_DIR/web"
    "$VERSION_DIR/scripts"
    "$VERSION_DIR/tools"
)

# grub timeout
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=0/g' /etc/default/grub
update-grub

# apache configuration
cp $SRC_DIR/virtualhost.txt /etc/apache2/sites-available/gtta
cp $SRC_DIR/virtualhost_ssl.txt /etc/apache2/sites-available/gtta-ssl
a2ensite gtta*
a2dissite default
a2enmod ssl rewrite

# php configuration
EXT_DIR=`php -r 'echo ini_get("extension_dir");'`
mv $SRC_DIR/ioncube.so $EXT_DIR/
echo "zend_extension = $EXT_DIR/ioncube.so" >> /etc/php5/conf.d/ioncube.ini

# increase PHP memory limit
sed -i 's/memory_limit = .*/memory_limit = 1024M/' /etc/php5/apache2/php.ini

# make directories
for ITEM in ${DIRECTORIES[@]}
do
    mkdir -p $ITEM
done

chmod -R 0770 $FILES_DIR
chmod -R 0770 $SECURITY_DIR
chmod 0777 $ROOT_DIR/runtime

# install web part
tar xf $SRC_DIR/web.tgz -C $VERSION_DIR/web --strip-components=3

# install scripts
tar xf $SRC_DIR/scripts.tgz -C $VERSION_DIR/scripts --strip-components=3

# install tools and config
tar xf $SRC_DIR/tools.tgz -C $VERSION_DIR/tools --strip-components=3
cp $SRC_DIR/gtta.ini $ROOT_DIR/config
cp $SRC_DIR/update-server.pub $SECURITY_DIR/keys
chown -R gtta:gtta $ROOT_DIR

# create a link
ln -s $VERSION_DIR $ROOT_DIR/current

# database setup
sudo -upostgres psql -c "create database gtta"
sudo -upostgres psql -c "create user gtta with password 'cqxLvzTW96BbiYoPjiyMbiQpG'"
sudo -upostgres psql -c "grant all on database gtta to gtta"
sudo -upostgres psql gtta < $VERSION_DIR/web/protected/data/schema.sql
sed -i 's/^local\s\+all\s\+all\s\+ident/local all all password/g' /etc/postgresql/8.4/main/pg_hba.conf
service postgresql restart
cd $VERSION_DIR/web/protected
python $VERSION_DIR/tools/make_config.py $ROOT_DIR/config/gtta.ini $VERSION_DIR/web/protected/config
./yiic migrate --interactive=0

# database initialization
sudo -upostgres psql gtta -c "INSERT INTO languages(name,code,\"default\") values('English','en','t'),('Deutsch','de','f');"
sudo -upostgres psql gtta -c "INSERT INTO system(timezone, version, version_description, demo_check_limit) VALUES('Europe/Zurich', '$VERSION', 'Initial version.', 40);"
sudo -upostgres psql gtta -c "INSERT INTO gt_dependency_processors(name) VALUES('nmap-port');"

# generate temporary SSL certificate
openssl genrsa -out $SSL_DIR/server.key 2048
openssl req -new -key $SSL_DIR/server.key -out $SSL_DIR/server.csr -subj "/C=CH/ST=Zurich/L=Zurich/O=Infoguard AG/OU=Infoguard AG/CN=gtta/emailAddress=info@infoguard.ch"
openssl x509 -req -days 3650 -in $SSL_DIR/server.csr -signkey $SSL_DIR/server.key -out $SSL_DIR/server.crt
chown -R gtta:gtta $SSL_DIR

# generate CA certificate for certificate-based login
openssl genrsa -out $CA_DIR/ca.key 2048
openssl req -new -key $CA_DIR/ca.key -out $CA_DIR/ca.csr -subj "/C=CH/ST=Zurich/L=Zurich/O=Infoguard AG/OU=Infoguard AG/CN=gtta/emailAddress=info@infoguard.ch"
openssl x509 -req -days 3650 -in $CA_DIR/ca.csr -signkey $CA_DIR/ca.key -out $CA_DIR/ca.crt
chown -R gtta:gtta $CA_DIR

# restart apache to apply all settings
service apache2 restart

# user passwords setup
echo "root:$ROOT_PW" | chpasswd
echo "gtta:$USER_PW" | chpasswd

# add www-data user to gtta group
usermod -a -G gtta www-data

# SSH login setup
mkdir $SSH_DIR
cp $SRC_DIR/authorized_keys.txt $SSH_DIR/authorized_keys
chown -R gtta:gtta $SSH_DIR
chmod 0644 $SSH_DIR/authorized_keys
echo -e "\nMatch user gtta\nPasswordAuthentication no\n" >> /etc/ssh/sshd_config

# sudoers setup
echo "Cmnd_Alias GTTA = /usr/bin/python /opt/gtta/current/tools/setup/setup.py" >> /etc/sudoers
echo "gtta    ALL=GTTA, NOPASSWD:GTTA" >> /etc/sudoers

# getty setup
sed -i 's/^\([2-6].*\)$/#\1/g' /etc/inittab
sed -i 's/^1.*$/1:2345:respawn:\/usr\/bin\/python \/opt\/gtta\/current\/tools\/setup\/setup.py/g' /etc/inittab

# generate OpenVZ container
cd $VERSION_DIR/web/protected
./yiic regenerate 1

# crontab setup
cp $SRC_DIR/crontab.txt /etc/cron.d/gtta

# supervisor setup
cp $SRC_DIR/resque-*.conf /etc/supervisor/conf.d
service supervisor stop
service supervisor start
