#!/bin/sh

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive

# remove ruby
apt-get -y purge php-pear php5-dev libyaml-dev linux-image-openvz-`uname -r | cut -d "-" -f 3` vzctl vzquota
apt-get -y autoremove
apt-get clean

# yaml extension
rm /etc/php5/apache2/conf.d/yaml.ini
/etc/init.d/apache2 restart

# scripts location
rm -r /opt/gtta/scripts

# iptables
rm /etc/iptables.rules
rm /etc/network/if-pre-up.d/iptables

# restore a deleted folder
mkdir /opt/gtta/files/automation
