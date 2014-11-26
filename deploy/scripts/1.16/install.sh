#!/bin/bash

set -e

# remove system packages directory
cp -r /opt/gtta/versions/1.16/scripts/* /opt/gtta/scripts || true
rm -rf /opt/gtta/scripts/system || true
sudo -upostgres psql -c "alter user gtta with password 'cqxLvzTW96BbiYoPjiyMbiQpG'"

# sudoers setup
sed -i 's/Cmnd_Alias GTTA =.*/Cmnd_Alias GTTA = \/usr\/bin\/python \/opt\/gtta\/current\/tools\/setup\/setup.py/' /etc/sudoers

# getty setup
sed -i 's/^\([2-6].*\)$/#\1/g' /etc/inittab
sed -i 's/^1.*$/1:2345:respawn:\/usr\/bin\/python \/opt\/gtta\/current\/tools\/setup\/setup.py/g' /etc/inittab

# increase PHP memory limit
sed -i 's/memory_limit = .*/memory_limit = 1024M/' /etc/php5/apache2/php.ini

# remove init scripts
update-rc.d -f gtta-init remove || true
rm /etc/init.d/gtta-init || true
