\copy (select school_city,school_state, level_short_name, count(compet_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'total/total_escolas.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, level_short_name, count(compet_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and compet_type in (3,4,5,6) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'prog/total_escolas.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, level_short_name, count(compet_id) from school, compet,level where level_id=compet_type and compet_school_id=school_id and compet_classif_fase2 and compet_type in (1,2,7) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'ini/total_escolas.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and compet_classif_fase2 and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id order by sh.school_state,sh.school_city) to 'total/coord_escolas.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and compet_classif_fase2 and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and compet_type in (1,2,7) order by sh.school_state,sh.school_city) to 'ini/coord_escolas.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and compet_classif_fase2 and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and compet_type in (3,4,5,6) order by sh.school_state,sh.school_city) to 'prog/coord_escolas.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, level_short_name, count(compet_id) from school, compet,level where level_id=compet_type and school_id=compet_school_id and compet_classif_fase2 and compet_type in (1,2,7) group by school_city,school_state,level_short_name order by school_state, school_city, level_short_name) to 'ini/total_escolas.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, school_name,school_address,school_address_number,school_address_district from school where school_is_site_phase3 and school_site_phase3_type in (0) order by school_state, school_city) to 'total/total_sedes.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, school_name,school_address,school_address_number,school_address_district from school where school_is_site_phase3 and school_site_phase3_type in (0,2) order by school_state, school_city) to 'prog/total_sedes.csv' CSV DELIMITER '|';

\copy (select school_city,school_state, school_name,school_address,school_address_number,school_address_district from school where school_is_site_phase3 and school_site_phase3_type in (0,1) order by school_state, school_city) to 'ini/total_sedes.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and school_is_site_phase3 order by sh.school_state,sh.school_city) to 'total/coord_sedes.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and school_is_site_phase3 order by sh.school_state,sh.school_city) to 'total/coord_sedes.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and school_is_site_phase3 and school_site_phase3_type in (0,1) order by sh.school_state,sh.school_city) to 'ini/coord_sedes.csv' CSV DELIMITER '|';

\copy (select distinct sh.school_city,sh.school_state,lat,lng from cities as c, states as s, compet as comp, school as sh where sh.school_id=comp.compet_school_id and c.name=sh.school_city and s.short_name=sh.school_state and c.state_id=s.id and school_is_site_phase3 and school_site_phase3_type in (0,2) order by sh.school_state,sh.school_city) to 'prog/coord_sedes.csv' CSV DELIMITER '|';
