#!/bin/sh

COMMAND="/usr/bin/python3 /home/hmd82/parking/Call.py"
LOGFILE=restartCalling.txt

writelog() {
  now=`date`
  echo "$now $*" >> $LOGFILE
}

writelog "Starting"
while true ; do
  $COMMAND
  writelog "Exited with status $?"
  writelog "Restarting"
done

