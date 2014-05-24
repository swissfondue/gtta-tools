#!/bin/bash

set -e

# config update
echo -e '\n[community]\nurl = http://community.gtta.net\n' >> /opt/gtta/config/gtta.ini

NAME=$0
INDEX=$((`expr index "$NAME" .sh`-1))
VERSION=`expr substr "$NAME" 1 $INDEX`
VERSION_DIR=/opt/gtta/versions/$VERSION

/usr/bin/python $VERSION_DIR/tools/make_config.py /opt/gtta/config/gtta.ini $VERSION_DIR/web/protected/config/
