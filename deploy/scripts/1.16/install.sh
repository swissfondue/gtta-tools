#!/bin/bash

set -e

# remove system packages directory
mv /opt/gtta/scripts/system/* /opt/gtta/scripts
rm -r /opt/gtta/scripts/system
