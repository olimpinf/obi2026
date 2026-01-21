\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=1 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_i1.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=2 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_i2.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=7 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_ij.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=5 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_pj.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=3 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_p1.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=4 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_p2.csv' csv header;

\copy (select compet_id_full, compet_name, compet_points_fase3, compet_points_fase2, compet_points_fase1 from compet where compet_classif_fase2 and compet_points_fase3 is not null and compet_type=6 order by compet_points_fase3 desc, compet_points_fase2 desc, compet_points_fase1 desc) to 'medals_ps.csv' csv header;
