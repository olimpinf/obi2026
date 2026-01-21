#!/bin/sh

for school_id in `seq 1 1072`; do
    echo ${school_id}
    psql -d obi2020 -U obi -c "SELECT compet_name FROM compet WHERE compet_school_id = ${school_id} GROUP BY compet_name HAVING COUNT(*) > 1" > /tmp/school_${school_id}
done
