#!/bin/sh

set -e

# init script
rm /etc/init.d/gtta-init
ln -s /opt/gtta/current/tools/setup/system/gtta-init.sh /etc/init.d/gtta-init

# SSH config
sed -i 's/gtta\/tools/gtta\/current\/tools/g' /home/gtta/.ssh/authorized_keys

# remove old tools directory
if [ -e "/opt/gtta/tools/setup/.setup-completed" ]
then
    touch /opt/gtta/.setup-completed
fi

# will be removed on reboot
mv /opt/gtta/tools /tmp/gtta-tools.bak

# sudoers
sed -i 's/gtta\/tools/gtta\/current\/tools/g' /etc/sudoers
