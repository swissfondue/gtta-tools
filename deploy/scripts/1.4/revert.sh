#!/bin/sh

# apt-get variables
export PATH=/usr/bin:/bin:/usr/sbin:/sbin
export DEBIAN_FRONTEND=noninteractive

# remove ruby
apt-get -y purge ruby
apt-get -y autoremove
apt-get clean
