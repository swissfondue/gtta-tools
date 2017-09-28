#!/bin/bash

set -e

if [ -z $1 ]
then
    echo "Missing required parameter"
    exit
fi

rm -rf ~/gtta/output/updates/$1

cd ~/gtta/gtta-web
git clean -f
git pull && git checkout v$1
cd ../gtta-tools
git clean -f
git pull && git checkout v$1

cd builder
python build.py update --version $1

cd ~/lucy/output
scp -r updates/$1 update.phishing-server.com:/opt/lust/repository/ps/
