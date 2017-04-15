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
hg pull && hg up version-$1
cd ../gtta-tools
hg pull && hg up version-$1
cd builder
python build.py vmware $1

cd ~/gtta/output
zip -r vmware.zip gtta-$1
ssh download.phishing-server.com "mkdir /var/www/html/dl/gtta-$1" || true
scp -r vmware.zip download.phishing-server.com:/var/www/html/dl/gtta-$1/vmware.zip

