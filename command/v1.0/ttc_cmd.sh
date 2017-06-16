#!/bin/sh

### BEGIN INIT INFO
# Provides:          Rocksat GNU Radio Transmitter
# Required-Start:    
# Required-Stop:     
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Starts GNU Radio Transmitter
# Description:       Executes the python program that launches a serial 
#                    to ethernet thread and the GNU Radio Flowgraph
# Reference: http://blog.scphillips.com/posts/2013/07/getting-a-python-script-to-run-in-the-background-as-a-service-on-boot/
### END INIT INFO

PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin
#PATH=/sbin:/bin:/usr/sbin:/usr/bin
LD_LIBRARY_PATH="/usr/local/lib:/usr/lib"
export PATH LD_LIBRARY_PATH

# Change the next 3 lines to suit where you install your script and what you want to call it
DIR=/home/root/scripts/v1.0
DAEMON=$DIR/ttc_cmd.py
DAEMON_NAME=ttc_cmd

# Add any command line options for your daemon here
#DAEMON_OPTS="--tx-gain=75 --bb-gain=0.4 --rx-gain=10 --sd 10 -g \'/home/root/waveforms/v3\'"
DAEMON_OPTS=" --tx-gain=75 --bb-gain=0.4 --rx-gain=10 --sd 10"
DATETIME=$(date -u +%Y%m%d_%H%M%S.%N_UTC)
LOG=/mnt/log/ttc_cmd.log

# This next line determines what user the script runs as.
# Root generally not recommended but necessary if you are using the Raspberry Pi GPIO from Python.
DAEMON_USER=root

# The process ID of the script when it runs is stored here:
PIDFILE=/var/run/$DAEMON_NAME.pid

#. /lib/lsb/init-functions

do_start () {
    #log_daemon_msg "Starting system $DAEMON_NAME daemon"
    start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS
    #start-stop-daemon --start --background --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON #-- $DAEMON_OPTS <<<---This works!
    #start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON > $LOG #-- $DAEMON_OPTS <<<---This works!
    #start-stop-daemon --start --quiet --pidfile $PIDFILE --make-pidfile --user $DAEMON_USER --chuid $DAEMON_USER --startas $DAEMON -- $DAEMON_OPTS > $OUT_LOG 2> $ERR_LOG
    #start-stop-daemon --start --quiet --pidfile $PIDFILE --exec $DAEMON -- $DAEMON_OPTS  > /dev/null
    #log_end_msg $?
    echo $DATETIME": TTC Service Started" >> $LOG
}
do_stop () {
    #log_daemon_msg "Stopping system $DAEMON_NAME daemon"
    start-stop-daemon --stop --pidfile $PIDFILE --retry 10
    echo $DATETIME": TTC Service Stopped" >> $LOG
    #log_end_msg $?
}

case "$1" in

    start|stop)
        do_${1}
        ;;

    restart|reload|force-reload)
     	echo "Restarting $DAEMON_NAME Service"
	echo $DATETIME": TTC Service Restarted" > $LOG
        do_stop
        do_start
        ;;

    status)
        status_of_proc "$DAEMON_NAME" "$DAEMON" && exit 0 || exit $?
        ;;

    *)
        echo "Usage: /etc/init.d/$DAEMON_NAME {start|stop|restart|status}"
        exit 1
        ;;

esac
exit 0
