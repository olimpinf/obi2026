#!/bin/bash

for f in /home/olimpinf/django3.2/obi2022/media/escolas/semana/semana/pagam_taxa/* ; do
    if [ -d "$f" ]; then
        for t in $f/taxa* ; do
            if [[ $t != *.pdf && $t != *.png && $t != *.png ]]; then
                school_id=$(echo `basename $f` | sed 's/^0*//')
                echo "$school_id $t"
                ./manage.py generate_hash_file $school_id $t
            fi
        done
    fi
done
