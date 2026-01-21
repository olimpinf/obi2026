select current_database();
select level_short_name, compet_sex, count(*) from school, compet,level where level_id=compet_type and compet_school_id=school_id and school_city ilike 'uberl%dia' group by level_short_name, compet_sex order by level_short_name, compet_sex;

select level_short_name, compet_sex, count(*) from school, compet,level where level_id=compet_type and compet_school_id=school_id and school_city ilike 'uberl%dia' and compet_classif_fase1=1 group by level_short_name, compet_sex order by level_short_name, compet_sex;

select level_short_name, compet_sex, count(*) from school, compet,level where level_id=compet_type and compet_school_id=school_id and school_city ilike 'uberl%dia' and compet_classif_fase2=1 group by level_short_name, compet_sex order by level_short_name, compet_sex;

