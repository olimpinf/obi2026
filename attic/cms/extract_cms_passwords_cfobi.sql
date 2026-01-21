\copy (select c.compet_id_full, p.password, c.compet_name from compet as c inner join password_cms as p on p.compet_id=c.compet_id inner join compet_cfobi as f on c.compet_id=f.compet_id where f.compet_type = 5 order by c.compet_id) to 'users_cfobi_pj.csv' csv;

\copy (select c.compet_id_full, p.password, c.compet_name from compet as c inner join password_cms as p on p.compet_id=c.compet_id inner join compet_cfobi as f on c.compet_id=f.compet_id where f.compet_type = 3 order by c.compet_id) to 'users_cfobi_p1.csv' csv;

\copy (select c.compet_id_full, p.password, c.compet_name from compet as c inner join password_cms as p on p.compet_id=c.compet_id inner join compet_cfobi as f on c.compet_id=f.compet_id where f.compet_type = 4 order by c.compet_id) to 'users_cfobi_p2.csv' csv;
