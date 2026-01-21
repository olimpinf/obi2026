#!/usr/bin/bash

psql -d obi2025 -U obi -c "\copy (select compet_id_full, compet_conf, compet_name from compet as c where compet_type=5 order by c.compet_id) to '/tmp/users_pj.csv' CSV;"

psql -d obi2025 -U obi -c "\copy (select compet_id_full, compet_conf, compet_name from compet as c where compet_type=3 order by c.compet_id) to '/tmp/users_p1.csv' CSV;"

psql -d obi2025 -U obi -c "\copy (select compet_id_full, compet_conf, compet_name from compet as c where compet_type=4 order by c.compet_id) to '/tmp/users_p2.csv' CSV;"

psql -d obi2025 -U obi -c "\copy (select compet_id_full, compet_conf, compet_name from compet as c where compet_type=6 order by c.compet_id) to '/tmp/users_ps.csv' CSV;"

scp /tmp/users_pj.csv cms@pj.provas.ic.unicamp.br:/tmp
scp /tmp/users_p1.csv cms@p1.provas.ic.unicamp.br:/tmp
scp /tmp/users_p2.csv cms@p2.provas.ic.unicamp.br:/tmp
scp /tmp/users_ps.csv cms@ps.provas.ic.unicamp.br:/tmp


