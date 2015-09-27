#!/bin/bash

set -e

# create rating images directory
DIR=/opt/gtta/files/rating-images

mkdir $DIR || true
chmod -R 0770 $DIR true
chown -R gtta:gtta $DIR || true

mkdir /opt/gtta/files/system
chmod -R 0770 /opt/gtta/files/system
chown -R gtta:gtta /opt/gtta/files/system
