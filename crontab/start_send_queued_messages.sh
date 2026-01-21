#!/bin/bash

# script for crontab, to execute the commands to sync the cms user db
# with the django user db. Commands are stored in the django db table CMScommand.

tmpfile=$(mktemp /tmp/cms.XXXXXXXXX)
ps aux > ${tmpfile}
ex=`grep "manage.py send_queued_messages" ${tmpfile}`
rm ${tmpfile}

if [ "$ex" = "" ]; then
    # activate virtual env
    /usr/bin/bash
    source /home/olimpinf/django5.1/bin/activate
    # run command
    echo "start"
    /home/olimpinf/django5.1/obi2025/manage.py send_queued_messages >> /home/olimpinf/django5.1/obi2025/crontab/LOG_MSG 2>&1
else
    echo "already running"
fi
