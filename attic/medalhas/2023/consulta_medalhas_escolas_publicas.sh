#!/bin/sh

for year in `seq 2010 2019`; do
    echo ${year}
    psql -d obi${year} -U obi -c "\copy (select '${year}',count(*),compet_medal,school_name,school_city,school_state from compet,school where compet_school_id=school_id and compet_medal is not null and school_type in (1) and compet_type not in (6) group by school_name,school_city,school_state,compet_medal order by count(*) desc) to 'medalhas_publicas_detalhe_${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',count(*),school_name,school_city,school_state from compet,school where compet_school_id=school_id and compet_medal is not null and school_type in (1) and compet_type not in (6) group by school_name,school_city,school_state order by count(*) desc) to 'medalhas_publicas_${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',count(compet_id),compet_medal,school_type from compet,school where compet_school_id=school_id and compet_medal is not null and school_type in (1,2) and compet_type not in (6) group by school_type,compet_medal) to 'total_medalhas_${year}.csv' csv;"
done

cat medalhas_publicas_detalhe_*.csv > medalhas_publicas_detalhe.csv
cat medalhas_publicas_*.csv > medalhas_publicas.csv
cat total_medalhas_*.csv > total_medalhas.csv

