#!/bin/bash

set -e

# config update
echo -e '[community]\nurl = http://community.gtta.net\n' >> /opt/gtta/config/gtta.ini

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION=$(cat $DIR/version)
VERSION_DIR=/opt/gtta/versions/$VERSION

/usr/bin/python $VERSION_DIR/tools/make_config.py /opt/gtta/config/gtta.ini $VERSION_DIR/web/protected/config/
