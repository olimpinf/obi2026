\echo --------
\echo '   IJ'
\echo --------
select compet_points_fase1 as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=7 group by compet_points_fase1 order by "Pontos" desc;

\echo --------
\echo '   I1'
\echo --------
select compet_points_fase1 as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=1 group by compet_points_fase1 order by "Pontos" desc;


\echo
\echo --------
\echo '   I2'
\echo --------
select compet_points_fase1 as "Pontos", count(*) as "Num. Alunos" from compet where compet_type=2 group by compet_points_fase1 order by "Pontos" desc;

