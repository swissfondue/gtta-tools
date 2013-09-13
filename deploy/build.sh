#!/bin/sh

set -e

SRC="/Users/anton/Projects/gtta/src"
DST="/tmp/gtta"
CLEANLIST=(".hg" ".hgtags" ".hgrc" ".hgignore" ".idea" ".DS_Store" '"*.swp"' '"*~"' '"*.svn"')
ZIP="/tmp/gtta.zip"
SIG="/tmp/gtta.sig"
KEY="/Users/anton/Projects/gtta/security/keys/update-server.priv"

if [ -e $DST ] 
then
    rm -rf $DST
fi

if [ -e $ZIP ] 
then
    rm -f $ZIP
fi

if [ -e $SIG ] 
then
    rm -f $SIG
fi

mkdir $DST
cp -r $SRC/web $DST/
cp -r $SRC/scripts $DST/
cp $SRC/tools/crontab.txt $DST/

# tools
mkdir $DST/tools
cp $SRC/tools/backup/backup.sh $DST/tools/
cp $SRC/tools/deploy/make_config.py $DST/tools/
cp -r $SRC/tools/setup $DST/tools/

# install scripts
if [ ! -z $1 ]
then
    if [ -e "$SRC/tools/deploy/scripts/$1" ]
    then
        mkdir $DST/install/
        cp $SRC/tools/deploy/scripts/$1/* $DST/install/
    fi
fi

# remove temporary files
for ITEM in ${CLEANLIST[@]}
do
    find $DST -iname $ITEM | xargs rm -rf
done

# encode PHP files
ioncube $DST/web -o $DST/web-encoded --copy migrations/template.php --copy config/main.example.php --copy config/console.example.php --without-loader-check
rm -r $DST/web
mv $DST/web-encoded $DST/web

# compress
pushd /tmp
zip -9 -r $ZIP gtta
popd
openssl dgst -sha1 -sign $KEY -out $SIG $ZIP

# clean
rm -rf $DST
