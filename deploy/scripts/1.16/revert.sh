#!/bin/bash

set -e

# restore system packages directory
mkdir /opt/gtta/scripts/system || true
chown gtta:gtta /opt/gtta/scripts/system || true
sudo -upostgres psql -c "alter user gtta with password '3yNeMw4sMaj6TC8gJ2Ecvh2GF'"
