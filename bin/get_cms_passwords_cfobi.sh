#!/usr/bin/bash

psql -d obi2025 -U obi -c "\copy (select compet_id_full, password, compet_name from compet_cfobi as cf, compet as c, password_cms as p where c.compet_id=p.compet_id and cf.compet_id=c.compet_id and cf.compet_type=5 order by c.compet_id) to '/tmp/users_pj.csv' CSV;"

psql -d obi2025 -U obi -c "\copy (select compet_id_full, password, compet_name from compet_cfobi as cf, compet as c, password_cms as p where c.compet_id=p.compet_id and cf.compet_id=c.compet_id and cf.compet_type=3 order by c.compet_id) to '/tmp/users_p1.csv' CSV;"

psql -d obi2025 -U obi -c "\copy (select compet_id_full, password, compet_name from compet_cfobi as cf, compet as c, password_cms as p where c.compet_id=p.compet_id and cf.compet_id=c.compet_id and cf.compet_type=4 order by c.compet_id) to '/tmp/users_p2.csv' CSV;"

echo "copying pj"
scp /tmp/users_pj.csv cms@pj.provas.ic.unicamp.br:/tmp
echo "copying p1"
scp /tmp/users_p1.csv cms@p1.provas.ic.unicamp.br:/tmp
echo "copying p2"
scp /tmp/users_p2.csv cms@p2.provas.ic.unicamp.br:/tmp
echo "finished"
