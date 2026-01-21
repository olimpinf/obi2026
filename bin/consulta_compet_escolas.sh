#!/bin/sh

for i in `seq 2005 2019`;
do echo $i;
   psql -d obi$i -U obi -c "\copy (select compet_id,compet_type,compet_name,compet_sex,compet_year,compet_points_fase1,compet_points_fase2,compet_points_fase3, compet_rank_final, school_id,school_name,school_zip,school_city,school_state from compet, school where compet_school_id=school_id and compet_rank_final < 500 order by compet_type, compet_rank_final) to '/tmp/obi$i.csv' CSV HEADER"
done


   


