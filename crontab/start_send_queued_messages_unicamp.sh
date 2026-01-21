#!/bin/bash

# script for crontab, to execute the commands to sync the cms user db
# with the django user db. Commands are stored in the django db table CMScommand.

tmpfile=$(mktemp /tmp/cms.XXXXXXXXX)
ps aux > ${tmpfile}
ex=`grep "manage.py send_queued_messages_hotmail" ${tmpfile}`
rm ${tmpfile}

if [ "$ex" = "" ]; then
    # to set the openAI api key
    /usr/bin/bash
    # activate virtual env
    source /home/olimpinf/django5.1/bin/activate
    cd /home/olimpinf/django5.1/obi2025
    # run command
    echo "start"
    /home/olimpinf/django5.1/obi2025/manage.py send_queued_messages_unicamp --settings=obi.settings_unicamp >> /home/olimpinf/django5.1/obi2025/crontab/LOG_MSG_UNICAMP 2>&1
else
    echo "already running"
fi
