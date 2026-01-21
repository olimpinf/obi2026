#!/bin/sh

for year in `seq 2005 2019`; do
    echo '------------'
    echo ${year}
    echo '------------'
    ../../manage.py set_medals ${year} all
done


