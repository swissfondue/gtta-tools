#!/bin/sh

set -e

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive

# refresh packages
apt-get -y update

# install required packages
apt-get -y install php-pear php5-dev libyaml-dev

# yaml extension
printf "\n" | pecl install yaml
echo "extension=yaml.so" > /etc/php5/apache2/conf.d/yaml.ini

# apache SSL options
sed -i "s/SSLOptions +StdEnvVars/SSLOptions +StdEnvVars\n\t\tSSLRenegBufferSize 100486000/" /etc/apache2/sites-available/gtta-ssl
/etc/init.d/apache2 restart

# new scripts location
mkdir -p /opt/gtta/scripts/lib
chown -R gtta:gtta /opt/gtta/scripts
chmod -R 0750 /opt/gtta/scripts
ln -s /opt/gtta/current/scripts /opt/gtta/scripts/system

# install OpenVZ kernel
apt-get install -y linux-image-openvz-`uname -r | cut -d "-" -f 3` vzctl vzquota

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
echo "#!/bin/sh\niptables-restore < /etc/iptables.rules" >> /etc/network/if-pre-up.d/iptables
chmod 0755 /etc/network/if-pre-up.d/iptables

# don't need this anymore
rm -r /opt/gtta/files/automation

# debian image
wget -q -O /var/lib/vz/template/cache/debian-7.0-i386-minimal.tar.gz http://gta-update.does-it.net:8080/data/debian-7.0-i386-minimal.tar.gz
