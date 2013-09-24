#!/bin/sh

set -e

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive

# refresh packages
apt-get -y update

# install ruby
apt-get -y install ruby
