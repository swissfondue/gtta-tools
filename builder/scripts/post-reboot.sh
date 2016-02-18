#!/bin/bash

set -e

if [ -z $1 ] || [ -z $2 ]
then
    echo "Usage: post-reboot.sh <type> <version>"
    exit 1
fi

# constants and variables
TYPE=$1
VERSION=$2

SRC_DIR=/tmp/files
ROOT_DIR=/opt/gtta
FILES_DIR=$ROOT_DIR/files
SECURITY_DIR=$ROOT_DIR/security
SSL_DIR=$SECURITY_DIR/ssl
CA_DIR=$SECURITY_DIR/ca
VERSION_DIR=$ROOT_DIR/versions/$VERSION
SSH_DIR=/home/gtta/.ssh

DIRECTORIES=(
    "$ROOT_DIR/config"
    "$ROOT_DIR/runtime"
    "$ROOT_DIR/runtime/bg"
    "$FILES_DIR/attachments"
    "$FILES_DIR/backups"
    "$FILES_DIR/header-images"
    "$FILES_DIR/logos"
    "$FILES_DIR/rating-images"
    "$FILES_DIR/reports"
    "$FILES_DIR/report-templates"
    "$FILES_DIR/system"
    "$SECURITY_DIR/ca"
    "$SECURITY_DIR/keys"
    "$SECURITY_DIR/ssl"
    "$VERSION_DIR/web"
    "$VERSION_DIR/scripts"
    "$VERSION_DIR/tools"
)

# apache configuration
cp $SRC_DIR/virtualhost.txt /etc/apache2/sites-available/gtta.conf
cp $SRC_DIR/virtualhost_ssl.txt /etc/apache2/sites-available/gtta-ssl.conf
a2ensite gtta*
a2dissite 000-default
a2enmod ssl rewrite

# increase PHP limits
sed -i 's/memory_limit = .*/memory_limit = 1024M/' /etc/php5/apache2/php.ini
sed -i 's/upload_max_filesize = .*/upload_max_filesize = 1024M/' /etc/php5/apache2/php.ini
sed -i 's/post_max_size = .*/post_max_size = 1024M/' /etc/php5/apache2/php.ini

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

# install tools and config
tar xf $SRC_DIR/tools.tgz -C $VERSION_DIR/tools --strip-components=3
cp $SRC_DIR/gtta.ini $ROOT_DIR/config
cp $SRC_DIR/update-server.pub $SECURITY_DIR/keys
chown -R gtta:gtta $ROOT_DIR

# create a link
ln -s $VERSION_DIR $ROOT_DIR/current

# database setup
sudo -upostgres psql -c "create database gtta encoding 'utf-8'"
sudo -upostgres psql -c "create user gtta with password 'cqxLvzTW96BbiYoPjiyMbiQpG'"
sudo -upostgres psql -c "grant all on database gtta to gtta"
sudo -upostgres psql gtta < $VERSION_DIR/web/protected/data/schema.sql
sed -i 's/^local\s\+all\s\+all\s\+peer/local all all password/g' /etc/postgresql/9.1/main/pg_hba.conf
service postgresql restart
cd $VERSION_DIR/web/protected
python $VERSION_DIR/tools/make_config.py $ROOT_DIR/config/gtta.ini $VERSION_DIR/web/protected/config
chmod 0755 yiic
./yiic migrate --interactive=0

# database initialization
sudo -upostgres psql gtta -c "INSERT INTO languages(name,code,\"default\") values('English','en','t'),('Deutsch','de','f');"
sudo -upostgres psql gtta -c "INSERT INTO system(timezone, version, version_description) VALUES('Europe/Zurich', '$VERSION', 'Initial version.');"
sudo -upostgres psql gtta -c "UPDATE languages SET user_default = 't' WHERE id = 1;"

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

# passwords
ROOT_PW=`openssl rand -base64 32 | sha256sum | head -c 25`
USER_PW=`openssl rand -base64 32 | sha256sum | head -c 25`

echo "root:$ROOT_PW" | chpasswd
echo "gtta:$USER_PW" | chpasswd

# supervisor setup
cp $SRC_DIR/resque-*.conf /etc/supervisor/conf.d
service supervisor stop
service supervisor start

# save build type
echo "$TYPE" > $ROOT_DIR/config/type
