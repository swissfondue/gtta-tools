#!/bin/bash

set -e

# create rating images directory
DIR=/opt/gtta/files/rating-images

mkdir $DIR || true
chmod -R 0770 $DIR true
chown -R gtta:gtta $DIR || true

mkdir /opt/gtta/files/system
chmod -R 0770 /opt/gtta/files/system
chown -R gtta:gtta /opt/gtta/files/system

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive
echo "deb http://backports.debian.org/debian-backports squeeze-backports main" >> /etc/apt.sources.list

# refresh packages
apt-get -y update

apt-get purge git
apt-get install git=1:1.7.10.4-1~bpo60+1
