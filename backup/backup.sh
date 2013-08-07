#!/bin/bash

DATE=`date '+%Y-%m-%d_%H%M'`

# DB
PGPASSWORD="123" pg_dump -U gtta gtta | gzip -9 > /var/backups/gtta/db/$DATE.sql.gz

# FILES
STATIC_SRC="/opt/gtta/web/"
STATIC_DST="/var/backups/gtta/static"

# check if file exists
if [ ! -e $STATIC_DST/current ]
then
    ln -s $STATIC_SRC $STATIC_DST/current
fi

rsync -az --partial --link-dest=$STATIC_DST/current $STATIC_SRC $STATIC_DST/$DATE
rm -f $STATIC_DST/current
ln -s $STATIC_DST/$DATE $STATIC_DST/current

