#!/bin/sh                                                                                                                                                                               

for year in `seq 2005 2020`; do
    echo ${year}
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet) from compet where compet_sex='F') to 'partic_meninas_${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet where compet_medal is not null) from compet where compet_sex='F' and compet_medal is not null) to 'partic_meninas_medalhas${year}.csv' csv;"

    # inic
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet where compet_type in (1,2,7)) from compet where compet_sex='F' and compet_type in (1,2,7)) to 'partic_meninas_inic${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet where compet_type in (1,2,7) and compet_medal is not null) from compet where compet_sex='F' and compet_type in (1,2,7) and compet_medal is not null) to 'partic_meninas_medalhas_inic${year}.csv' csv;"

    # prog
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet where compet_type in (3,4,5,6)) from compet where compet_sex='F' and compet_type in (3,4,5,6)) to 'partic_meninas_prog${year}.csv' csv;"
    psql -d obi${year} -U obi -c "\copy (select '${year}',100*count(compet_sex)/(select count(*) from compet where compet_type in (3,4,5,6) and compet_medal is not null) from compet where compet_sex='F' and compet_type in (3,4,5,6) and compet_medal is not null) to 'partic_meninas_medalhas_prog${year}.csv' csv;"
done
