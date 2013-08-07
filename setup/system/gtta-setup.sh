#!/bin/sh

# set up directory paths
SETUP_DIR="/opt/gtta/setup"
CWD=$(pwd)

cd $SETUP_DIR
python setup.py
cd $CWD

# unset variables
unset $SETUP_DIR
unset $CWD
