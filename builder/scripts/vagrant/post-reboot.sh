#!/bin/bash

set -e

# constants and variables
SRC_DIR="/vagrant/builder/files"
ROOT_DIR="/opt/gtta"
FILES_DIR="$ROOT_DIR/files"
SECURITY_DIR="$ROOT_DIR/security"
SSL_DIR="$SECURITY_DIR/ssl"
CA_DIR="$SECURITY_DIR/ca"
SCRIPTS_DIR="$ROOT_DIR/scripts"
VERSION_DIR="$ROOT_DIR/versions/dev"
WEB_DIR="$VERSION_DIR/web"
TOOLS_DIR="$VERSION_DIR/tools"
SSH_DIR="/home/gtta/.ssh"

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
    "$VERSION_DIR"
)

# apache configuration
cp $SRC_DIR/virtualhost.txt /etc/apache2/sites-available/gtta
cp $SRC_DIR/virtualhost_ssl.txt /etc/apache2/sites-available/gtta-ssl
a2ensite gtta*
a2dissite default
a2enmod ssl rewrite

# increase PHP memory limit
sed -i 's/memory_limit = .*/memory_limit = 1024M/' /etc/php5/apache2/php.ini

# enable this for composer to normally work
echo "suhosin.executor.include.whitelist = phar" >> /etc/php5/cli/conf.d/suhosin.ini

# make directories
for ITEM in ${DIRECTORIES[@]}
do
    mkdir -p $ITEM
done

chmod -R 0777 $FILES_DIR
chmod -R 0775 $SECURITY_DIR
chmod 0777 $ROOT_DIR/runtime

# install web part
ln -s /gtta_web $WEB_DIR

# install scripts
ln -s /gtta_scripts $SCRIPTS_DIR

# install tools and config
cp $SRC_DIR/gtta.ini $ROOT_DIR/config
cp $SRC_DIR/update-server.pub $SECURITY_DIR/keys
ln -s /vagrant $TOOLS_DIR

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
chmod 0755 yiic
./yiic migrate --interactive=0

# database initialization
sudo -upostgres psql gtta -c "INSERT INTO languages(name,code,\"default\") values('English','en','t'),('Deutsch','de','f');"
sudo -upostgres psql gtta -c "INSERT INTO system(timezone, version, version_description, demo_check_limit) VALUES('Europe/Zurich', 'dev', 'Initial version.', 40);"
sudo -upostgres psql gtta -c "INSERT INTO gt_dependency_processors(name) VALUES('nmap-port');"
sudo -upostgres psql gtta -c "INSERT INTO users(email, password, role) VALUES('test@test.com', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'admin');"

# generate temporary SSL certificate
openssl genrsa -out $SSL_DIR/server.key 2048
openssl req -new -key $SSL_DIR/server.key -out $SSL_DIR/server.csr -subj "/C=CH/ST=Zurich/L=Zurich/O=Infoguard AG/OU=Infoguard AG/CN=gtta/emailAddress=info@infoguard.ch"
openssl x509 -req -days 3650 -in $SSL_DIR/server.csr -signkey $SSL_DIR/server.key -out $SSL_DIR/server.crt

# generate CA certificate for certificate-based login
openssl genrsa -out $CA_DIR/ca.key 2048
openssl req -new -key $CA_DIR/ca.key -out $CA_DIR/ca.csr -subj "/C=CH/ST=Zurich/L=Zurich/O=Infoguard AG/OU=Infoguard AG/CN=gtta/emailAddress=info@infoguard.ch"
openssl x509 -req -days 3650 -in $CA_DIR/ca.csr -signkey $CA_DIR/ca.key -out $CA_DIR/ca.crt

# restart apache to apply all settings
service apache2 restart

# generate OpenVZ container
cd $VERSION_DIR/web/protected
./yiic regenerate 1

# install packages
./yiic installpackage

# crontab setup
cp $SRC_DIR/crontab.txt /etc/cron.d/gtta

# supervisor setup
cp $SRC_DIR/resque-*.conf /etc/supervisor/conf.d
service supervisor stop
service supervisor start

# network settings
ifconfig eth1 up
IP_ADDRESS=`ifconfig eth1 | grep "inet addr" | cut -d ":" -f 2 | cut -d " " -f 1`
echo -e "\n\n\nDomain: gtta.local\nIP address: $IP_ADDRESS\n"
echo "Please point your domain to the system's IP address. You can do that by changing"
echo "the corresponding records on your nameserver or by modifying the local 'hosts'"
echo "file on your workstaiton (C:\WINDOWS\system32\drivers\etc\hosts in Windows,"
echo -e "/etc/hosts in Mac OS X and Linux).\n"
echo "https://gtta.local - enter this URL in your browser to access the system."
echo -e "Use the following credentials to enter the system:\n* Login: test@test.com\n* Password: 123."
