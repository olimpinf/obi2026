#!/bin/bash

# script for crontab, to execute the commands to close exams for ini compets (verify if time is up)

tmpfile=$(mktemp /tmp/cms.XXXXXXXXX)
ps aux > ${tmpfile}
ex=`grep "manage.py close_exams_ini" ${tmpfile}`
rm ${tmpfile}

if [ "$ex" = "" ]; then
    # activate virtual env
    source /home/olimpinf/django3.2/bin/activate
    # run command
    echo "start"
    date >> /home/olimpinf/django3.2/obi2021/crontab/LOG_CLOSE_EXAMS 2>&1
    /home/olimpinf/django3.2/obi2021/manage.py close_exams_ini provaf2 0 >> /home/olimpinf/django3.2/obi2021/crontab/LOG_CLOSE_EXAMS 2>&1
    #/home/olimpinf/django3.2/obi2021/manage.py close_exams_ini testef1 0 >> /home/olimpinf/django3.2/obi2021/crontab/LOG_CLOSE_EXAMS 2>&1
else
    echo "already running"
fi
