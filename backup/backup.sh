#!/bin/bash

DATE=`date '+%Y-%m-%d_%H%M'`
STATIC_SOURCE="/opt/gtta/"
BACKUPS_LOCATION="/var/backups/gtta"
DATABASE_BACKUP="$BACKUPS_LOCATION/db"
STATIC_BACKUP="$BACKUPS_LOCATION/static"

# database
DB_PASSWORD=$(sed -n '{N;s/.*\[database\]\npassword *= *\( *\)/\1/p}' < /opt/gtta/config/gtta.ini)
PGPASSWORD="$DB_PASSWORD" pg_dump -U gtta gtta | gzip -9 > $DATABASE_BACKUP/$DATE.sql.gz

# check if file exists
if [ ! -e $STATIC_BACKUP/current ]
then
    ln -s $STATIC_SOURCE $STATIC_BACKUP/current
fi

rsync -az --partial --link-dest=$STATIC_BACKUP/current $STATIC_SOURCE $STATIC_BACKUP/$DATE
rm -f $STATIC_BACKUP/current
ln -s $STATIC_BACKUP/$DATE $STATIC_BACKUP/current
