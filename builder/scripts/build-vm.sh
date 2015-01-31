#!/bin/bash

set -e

# locale setup
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen
locale-gen
update-locale LANG=en_US.UTF-8 LC_CTYPE=en_US.UTF-8
export LANG="en_US.UTF-8"
export LANGUAGE="en_US.UTF-8"
export LC_ALL="en_US.UTF-8"

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive

# install packages
apt-get -y update
apt-get -y upgrade
apt-get -y purge exim4 exim4-daemon-light exim4-base exim4-config
apt-get -y install linux-image-openvz-`uname -r | cut -d "-" -f 3` vzctl vzquota
apt-get -y install apache2 postgresql make libyaml-dev ntp redis-server supervisor
apt-get -y install libapache2-mod-php5 php5-pgsql php5-curl php5-gd php5-suhosin php-pear php5-dev
apt-get -y install python python-psycopg2 python-dev python-pip

# php extensions
printf "\n" | pecl install yaml
echo "extension=yaml.so" > /etc/php5/apache2/conf.d/yaml.ini

# kernel settings for OpenVZ
echo "net.ipv4.ip_forward = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.forwarding = 1" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.proxy_arp = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.rp_filter = 1" >> /etc/sysctl.conf
echo "kernel.sysrq = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.send_redirects = 1" >> /etc/sysctl.conf
echo "net.ipv4.conf.all.send_redirects = 0" >> /etc/sysctl.conf

# iptables setup for OpenVZ container
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables-save > /etc/iptables.rules
echo -e "#!/bin/sh\niptables-restore < /etc/iptables.rules" >> /etc/network/if-pre-up.d/iptables
chmod 0755 /etc/network/if-pre-up.d/iptables

# debian image
wget -q -O /var/lib/vz/template/cache/debian-7.0-i386-minimal.tar.gz http://download.openvz.org/template/precreated/debian-7.0-x86-minimal.tar.gz

