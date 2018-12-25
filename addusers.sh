#!/bin/bash

SPATH="/home/asterisk"
LOG_FILE="/var/log/asterisk/adduser.log"
DT=$(date +"%d-%m-%y %H:%M:%S")

cd $SPATH
$SPATH/users_adv.py >> $LOG_FILE 2>&1
chown -R tftpd:tftpd /var/lib/tftpboot > /dev/null
/usr/sbin/fwconsole reload > /dev/null
