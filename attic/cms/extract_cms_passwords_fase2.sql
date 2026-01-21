\copy (select compet_id_full, password, compet_name from compet as c,password_cms as p where p.compet_id=c.compet_id and compet_classif_fase1 and compet_type = 5 order by c.compet_id) to 'users_pj.csv' csv;

\copy (select compet_id_full, password, compet_name from compet as c,password_cms as p where p.compet_id=c.compet_id and compet_classif_fase1 and compet_type = 3 order by c.compet_id) to 'users_p1.csv' csv;

\copy (select compet_id_full, password, compet_name from compet as c,password_cms as p where p.compet_id=c.compet_id and compet_classif_fase1 and compet_type = 4 order by c.compet_id) to 'users_p2.csv' csv;

\copy (select compet_id_full, password, compet_name from compet as c,password_cms as p where p.compet_id=c.compet_id and compet_classif_fase1 and compet_type = 6 order by c.compet_id) to 'users_ps.csv' csv;

