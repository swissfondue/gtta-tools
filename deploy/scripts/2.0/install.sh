#!/bin/bash

set -e

# create rating images directory
DIR=/opt/gtta/files/rating-images

mkdir $DIR || true
chmod -R 0770 $DIR true
chown -R gtta:gtta $DIR || true
