#!/bin/sh

### BEGIN INIT INFO
# Provides:             gtta-init
# Required-Start:       $local_fs $remote_fs $network $syslog postgresql
# Required-Stop:        $local_fs $remote_fs $network $syslog
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# X-Start-Before:       apache2
# X-Interactive:        true
# Short-Description:    GTTA init.d script
### END INIT INFO

case "$1" in
    start)
        /opt/gtta/tools/setup/system/gtta-setup.sh start
        ;;
    stop)
        ;;
    *)
        echo "Usage: /etc/init.d/gtta-init {start|stop}"
        exit 1
        ;;
esac

exit 0
