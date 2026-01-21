#!/bin/bash

# script for crontab, to execute the commands to sync the cms user db
# with the django user db. 

CONTEST=provaf1

tmpfile=$(mktemp /tmp/cms.XXXXXXXXX)
ps aux > ${tmpfile}
ex=`grep "manage.py cms_sync_submissions" ${tmpfile}`
rm ${tmpfile}

if [ "$ex" = "" ]; then
    # activate virtual env
    source /home/olimpinf/django3.2/bin/activate
    # run command
    echo "start"
    /home/olimpinf/django3.2/obi2023/manage.py cms_sync_submissions ${CONTEST} >> /home/olimpinf/django3.2/obi2023/crontab/LOG_CMS_SYNC 2>&1
else
    echo "already running"
fi
