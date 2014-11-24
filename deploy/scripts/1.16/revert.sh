#!/bin/bash

set -e

# restore system packages directory
mkdir /opt/gtta/scripts/system
chown gtta:gtta /opt/gtta/scripts/system
sudo -upostgres psql -c "alter user gtta with password '123'"
