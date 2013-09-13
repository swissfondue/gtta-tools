#!/bin/sh

set -e

# init script
rm /etc/init.d/gtta-init
ln -s /opt/gtta/tools/setup/system/gtta-init.sh /etc/init.d/gtta-init

# SSH config
sed -i 's/gtta\/current\/tools/gtta\/tools/g' /home/gtta/.ssh/authorized_keys

# restore tools directory
mv /tmp/gtta-tools.bak /opt/gtta/tools

if [ -e "/opt/gtta/.setup-completed" ];
then
    touch /opt/gtta/tools/setup/.setup-completed
    rm /opt/gtta/.setup-completed
fi

# sudoers
sed -i 's/gtta\/current\/tools/gtta\/tools/g' /etc/sudoers
