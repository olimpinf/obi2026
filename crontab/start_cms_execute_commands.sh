#!/bin/bash

# script for crontab, to execute the commands to sync the cms user db
# with the django user db. Commands are stored in the django db table CMScommand.

tmpfile=$(mktemp /tmp/cms.XXXXXXXXX)
ps aux > ${tmpfile}
ex=`grep "manage.py cms_execute_commands" ${tmpfile}`
rm ${tmpfile}

if [ "$ex" = "" ]; then
    # activate virtual env
    source /home/olimpinf/django4.2/bin/activate
    # run command
    echo "start"
    /home/olimpinf/django4.2/obi2024/manage.py cms_execute_commands >> /home/olimpinf/django4.2/obi2024/crontab/LOG_CMS_EXECUTE 2>&1
    #/home/olimpinf/django3.2/obi2021//manage.py cms_execute_commands > /dev/null 2>&1
else
    echo "already running"
fi
