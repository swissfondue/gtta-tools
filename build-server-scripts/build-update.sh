#!/bin/bash

set -e

if [ -z $1 || -z $2 ]
then
    echo "Missing required parameter"
    exit
fi

rm -rf ~/gtta/output/updates/$1

cd ~/gtta/gtta-web
git clean -f
git checkout master
git pull origin master && git checkout v$1
cd ../gtta-tools
git clean -f
git checkout master
git pull origin master && git checkout v$1

cd builder
export PYTHONPATH="/opt/build/gtta"
python build.py update $1 $2

cd ~/lucy/output
scp -r updates/$1 update.phishing-server.com:/opt/lust/repository/ps/
