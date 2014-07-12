#!/bin/bash

set -e

# create docx reports directory
REPORTS_DIR=/opt/gtta/files/report-templates

if [ ! -d $REPORTS_DIR ]; then
    mkdir $REPORTS_DIR
    chown gtta:gtta $REPORTS_DIR
    chmod 0770 $REPORTS_DIR
fi
