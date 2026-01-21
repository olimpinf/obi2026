\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=1 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/i1.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=2 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/i2.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=3 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/p1.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=4 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/p2.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=5 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/pj.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=6 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/ps.csv' CSV HEADER;

\copy (select compet_id_full,compet_points_fase1,compet_points_fase2,compet_points_fase3 from compet where compet_type=7 and compet_points_fase3 is not null order by compet_points_fase3 desc, compet_points_fase2 desc,compet_points_fase1 desc) to '/tmp/ij.csv' CSV HEADER;
