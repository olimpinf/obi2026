#!/bin/sh                                                                                                                                                                               

for year in `seq 2005 2020`; do
    echo ${year}
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(school_id)/(select count(*) from compet) from compet,school where school_id=compet_school_id and school_type=1) to 'partic_publicas_${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(school_id)/(select count(*) from compet where compet_medal is not null) from compet,school where school_id=compet_school_id and school_type=1 and compet_medal is not null) to 'partic_publicas_medalha${year}.csv' csv;"
    #psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(school_id)/(select count(*) from compet,school where school_id=compet_school_id and compet_medal is not null) from compet where compet_school_id=school_id and compet_medal is not null) to 'partic_publicas_medalhas${year}.csv' csv;"
done
