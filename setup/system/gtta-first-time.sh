#!/bin/sh

### BEGIN INIT INFO
# Provides:             gtta-first-time
# Required-Start:       $all
# Required-Stop:
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    First time GTTA setup.
### END INIT INFO

SETUP_COMPLETED_FLAG="/opt/gtta/tools/setup/.setup-completed"

case "$1" in
    start)
        if [ ! -f $SETUP_COMPLETED_FLAG ];
        then
            /usr/bin/gtta-setup
        fi
        ;;
    stop)
        ;;
    *)
        echo "Usage: /etc/init.d/gtta-first-time {start|stop}"
        exit 1
        ;;
esac

exit 0
