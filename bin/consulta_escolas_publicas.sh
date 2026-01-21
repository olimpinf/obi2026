#!/bin/sh

for i in `seq 2005 2019`;
do echo $i;
   psql -d obi$i -U obi -c "\copy (select count(*),school_name,school_state from compet,school where school_type in (1,3) and school_id = compet_school_id group by school_name,school_state order by count desc) to '/tmp/obi$i.csv' CSV ";
done


   


