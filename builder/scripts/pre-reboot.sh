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
echo "deb http://download.openvz.org/debian wheezy main" >> /etc/apt/sources.list

# get OpenVZ key
wget http://ftp.openvz.org/debian/archive.key
apt-key add archive.key
rm archive.key

# install packages
apt-get -y update
apt-get -y upgrade
apt-get -y purge exim4 exim4-daemon-light exim4-base exim4-config
apt-get -y --force-yes install linux-image-openvz-amd64 linux-headers-2.6.32-openvz-amd64 vzctl vzquota ploop vzstats
apt-get -y install apache2 postgresql make libyaml-dev ntp redis-server supervisor
apt-get -y install libapache2-mod-php5 php5-pgsql php5-curl php5-gd php-pear php5-dev php5-mcrypt
apt-get -y install python python-psycopg2 python-dev python-pip git

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
wget -q -O /var/lib/vz/template/cache/debian-8.0-x86_64-minimal.tar.gz http://download.openvz.org/template/precreated/debian-8.0-x86_64-minimal.tar.gz

# grub setup
sed -i 's/GRUB_TIMEOUT=5/GRUB_TIMEOUT=0/g' /etc/default/grub
sed -i 's/GRUB_DEFAULT=0/GRUB_DEFAULT=2/g' /etc/default/grub
update-grub

reboot
sleep 60
