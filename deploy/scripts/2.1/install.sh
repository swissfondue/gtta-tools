#!/bin/bash

pushd /opt/gtta/current/web/protected
./yiic hostresolve
popd

echo '0 * * * *     root    cd /opt/gtta/current/web/protected && ./yiic hostresolve' >> /etc/crontab
/etc/init.d/cron restart