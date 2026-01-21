\pset pager 0
\echo --------
\echo '   PJ'
\echo --------
select compet_points_fase2b as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=5 group by compet_points_fase2b order by "Pontos" desc;

\echo --------
\echo '   P1'
\echo --------
select compet_points_fase2b as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=3 group by compet_points_fase2b order by "Pontos" desc;

\echo
\echo --------
\echo '   P2'
\echo --------
select compet_points_fase2b as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=4 group by compet_points_fase2b order by "Pontos" desc;
\echo
\echo --------
\echo '   PS'
\echo --------
select compet_points_fase2b as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=6 group by compet_points_fase2b order by "Pontos" desc;

\echo --------
\echo '   PJ'
\echo --------
select language, count(*) from local_submissions where compet_type=5 and contest_id = 3 group by language order by count desc;

\echo --------
\echo '   P1'
\echo --------
select language, count(*) from local_submissions where compet_type=3 and contest_id = 3  group by language order by count desc;

\echo
\echo --------
\echo '   P2'
\echo --------
select language, count(*) from local_submissions where compet_type=4 and contest_id = 3  group by language order by count desc;
\echo


\echo
\echo --------
\echo '   P2'
\echo --------
select task_name, sum(score) from local_submissions as s, local_submission_results as r where s.id=r.local_subm_id and compet_type=4 and contest_id = 3  group by task_name order by count desc;
\echo


\echo --------
\echo '   PS'
\echo --------
select language, count(*) from local_submissions where compet_type=6 and contest_id = 3  group by language order by count desc;

