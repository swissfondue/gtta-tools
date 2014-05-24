#!/bin/bash

set -e

# revert config (remove 3 last lines)
head -n -3 /opt/gtta/config/gtta.ini > /opt/gtta/config/gtta.ini

NAME=$0
INDEX=$((`expr index "$NAME" .sh`-1))
VERSION=`expr substr "$NAME" 1 $INDEX`
VERSION_DIR=/opt/gtta/versions/$VERSION

/usr/bin/python $VERSION_DIR/tools/make_config.py /opt/gtta/config/gtta.ini $VERSION_DIR/web/protected/config/
