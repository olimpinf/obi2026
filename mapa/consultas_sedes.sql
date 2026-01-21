-------------------------------
-- coordenadas
-------------------------------

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s,  school as sh where c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id order by sh.school_state,sh.school_city) to 'total/coordenadas.csv' CSV DELIMITER '|';

-------------------------------
-- escolas
-------------------------------

-- escolas com classificados sem sede, prog ou inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_site_phase3_ini=0 or school_site_phase3_prog=0) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'total/escolas_sem.csv' CSV DELIMITER '|';

-- escolas com classificados sem sede, prog
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and school_site_phase3_prog=0 and compet_type in (3,4,5,6) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'prog/escolas_sem.csv' CSV DELIMITER '|';

-- escolas com classificados sem sede, inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and school_site_phase3_ini=0 and compet_type in (1,2,7) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'ini/escolas_sem.csv' CSV DELIMITER '|';

-- escolas não sede mas com sede atribuída, prog ou inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=False and school_site_phase3_ini<>0 and school_site_phase3_prog<>0) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'total/escolas_com.csv' CSV DELIMITER '|';

-- escolas não sede mas com sede atribuída, prog
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=False and school_site_phase3_prog<>0) and compet_type in (3,4,5,6) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'prog/escolas_com.csv' CSV DELIMITER '|';

-- escolas não sede mas com sede atribuída, inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=False and school_site_phase3_ini<>0) and compet_type in (1,2,7) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'ini/escolas_com.csv' CSV DELIMITER '|';

-- escolas sede, prog ou inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=True) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'total/escolas_sede.csv' CSV DELIMITER '|';

-- escolas sede, prog
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=True and school_site_phase3_type in (0,2)) and compet_type in (3,4,5,6) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'prog/escolas_sede.csv' CSV DELIMITER '|';

-- escolas sede, inic
\copy (select school_city,school_state, level_short_name,count(compet_id),count(school_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and (school_is_site_phase3=True and school_site_phase3_type in (0,1)) and compet_type in (1,2,7) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'ini/escolas_sede.csv' CSV DELIMITER '|';


