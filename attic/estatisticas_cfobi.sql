\pset pager 0
\echo --------
\echo '   PJ'
\echo --------
select compet_points as "Pontos", count(*) as "Num. Alunos" from compet_cfobi where compet_type=5 group by compet_points order by "Pontos" desc;

\echo --------
\echo '   P1'
\echo --------
select compet_points as "Pontos", count(*) as "Num. Alunos" from compet_cfobi where compet_type=3 group by compet_points order by "Pontos" desc;

\echo
\echo --------
\echo '   P2'
\echo --------
select compet_points as "Pontos", count(*) as "Num. Alunos" from compet_cfobi where compet_type=4 group by compet_points order by "Pontos" desc;

\echo --------
\echo '   PJ'
\echo --------
select language, count(*) from local_submissions where contest_id=4 and compet_type=5 group by language order by count desc;

\echo --------
\echo '   P1'
\echo --------
select language, count(*) from local_submissions where contest_id=4 and compet_type=3 group by language order by count desc;

\echo
\echo --------
\echo '   P2'
\echo --------
select language, count(*) from local_submissions where contest_id=4 and compet_type=4 group by language order by count desc;
