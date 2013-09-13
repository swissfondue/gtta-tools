#!/bin/sh

# set up directory paths
SETUP_DIR="/opt/gtta/current/tools/setup"
CWD=$(pwd)

cd $SETUP_DIR
python setup.py $1
cd $CWD

# unset variables
unset $SETUP_DIR
unset $CWD
