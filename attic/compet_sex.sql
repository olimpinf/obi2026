select current_database();

\echo 'Iniciação - total';
select count(*) from compet, school where school_id=compet_school_id and compet_type in (1,2,7);

\echo 'Iniciação - meninas';
select count(*) from compet, school where school_id=compet_school_id and compet_type in (1,2,7) and compet_sex<>'M';

\echo 'Sênior - total';
select count(*) from compet, school where school_id=compet_school_id and compet_type in (6);

\echo 'Sênior - meninas';
select count(*) from compet, school where school_id=compet_school_id and compet_type in (6) and compet_sex<>'M';

\echo
