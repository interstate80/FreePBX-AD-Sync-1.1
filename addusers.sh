#!/bin/bash

SPATH="/home/asterisk"
LOG_FILE="/var/log/asterisk/adduser.log"
DT=$(date +"%d-%m-%y %H:%M:%S")

cd $SPATH
# echo $DT >> $LOG_FILE 2>&1
$SPATH/users_adv.py >> $LOG_FILE 2>&1
chown -R tftpd:tftpd /var/lib/tftpboot >> $LOG_FILE 2>&1
/usr/sbin/fwconsole reload > /dev/null # $LOG_FILE 2>&1
