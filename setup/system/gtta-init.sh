#!/bin/sh

### BEGIN INIT INFO
# Provides:             gtta-init
# Required-Start:       $all
# Required-Stop:
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    GTTA init.d script
### END INIT INFO

case "$1" in
    start)
        /opt/gtta/tools/setup/system/gtta-setup.sh
        ;;
    stop)
        ;;
    *)
        echo "Usage: /etc/init.d/gtta-init {start|stop}"
        exit 1
        ;;
esac

exit 0
