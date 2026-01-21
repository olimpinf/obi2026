#!/bin/sh

ps aux > /tmp/axxx
ex=`grep "corretor_www.py -f obi_config_www" /tmp/axxx`
echo "$ex"
rm /tmp/axxx

if [ "$ex" = "" ]; then
    cd /home/exec_corretor/www
    echo "starting corretor_www"
    ./start_obi_www.sh
fi

