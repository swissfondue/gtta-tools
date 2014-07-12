#!/bin/bash

set -e

# remove docx report directory
REPORTS_DIR=/opt/gtta/files/report-templates

if [ -d $REPORTS_DIR ]; then
    rm -rf $REPORTS_DIR
fi
