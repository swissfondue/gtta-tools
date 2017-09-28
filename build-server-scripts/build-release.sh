#!/bin/bash

set -e

if [ -z $1 ]
then
	echo "Missing required parameter"
	exit
fi

rm -rf ~/gtta/output/gtta-$1
rm -f ~/gtta/output/vmware.zip

cd ~/gtta/gtta-web
git clean -f
git pull && git checkout v$1
cd ../gtta-tools
git clean -f
git pull && git checkout v$1
cd builder

export PYTHONPATH="/opt/build/gtta"
python build.py vmware $1

cd ~/gtta/output
zip -r vmware.zip gtta-$1
ssh download.phishing-server.com "mkdir /var/www/html/dl/gtta-$1" || true
scp -r vmware.zip download.phishing-server.com:/var/www/html/dl/gtta-$1/vmware.zip
