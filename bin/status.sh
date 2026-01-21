#!/bin/bash

echo "started"

psql -d obi2021 -U obi -c "select c.compet_type, count(*) from exam_fase1 as e, compet as c where c.compet_id=e.compet_id and compet_type in (1,2,7)and time_start is not null group by compet_type order by compet_type"

echo "running"

psql -d obi2021 -U obi -c "select c.compet_type, count(*) from exam_fase1 as e, compet as c where c.compet_id=e.compet_id and compet_type in (1,2,7)and time_start is not null and time_finish is  null group by compet_type order by compet_type"

echo "finished"
psql -d obi2021 -U obi -c "select c.compet_type, count(*) from exam_fase1 as e, compet as c where c.compet_id=e.compet_id and compet_type in (1,2,7)and time_start is not null and time_finish is not null group by compet_type order by compet_type"

echo "total started"
psql -d obi2021 -U obi -c "select count(*) from exam_fase1 as e, compet as c where c.compet_id=e.compet_id and compet_type in (1,2,7)and time_start is not null;"

date
echo
