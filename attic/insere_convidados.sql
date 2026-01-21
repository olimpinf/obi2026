--create table week_may_2022 as (select * from week);


insert into week (compet_id,partic_level,school_id)  (select compet_id,compet_type,compet_school_id from compet where compet_type = 1 and compet_medal='o');

insert into week (compet_id,partic_level,school_id)  (select compet_id,compet_type,compet_school_id from compet where compet_type = 2 and compet_medal='o');

insert into week (compet_id,partic_level,school_id)  (select compet_id,compet_type,compet_school_id from compet where compet_type = 3 and compet_medal in ('o','p'));

insert into week (compet_id,partic_level,school_id)  (select compet_id,compet_type,compet_school_id from compet where compet_type = 4 and compet_medal in ('o','p'));

insert into week (compet_id,partic_level,school_id)  (select compet_id,compet_type,compet_school_id from compet where compet_type = 5 and compet_medal in ('o','p'));

--- CF-OBI

insert into week (compet_id,partic_level,school_id) (select compet_id,compet_type,compet_school_id from compet where compet_type = 3 and compet_id in (00253));

insert into week (compet_id,partic_level,school_id) (select compet_id,compet_type,compet_school_id from compet where compet_type = 4 and compet_id in (39831,00270,26363,00268,64280,00262));

insert into week (compet_id,partic_level,school_id) (select compet_id,compet_type,compet_school_id from compet where compet_type = 5 and compet_id in (17841,36765,31807,59479));

--- extras P2
insert into week (compet_id,partic_level,school_id) (select compet_id,compet_type,compet_school_id from compet where compet_type = 4 and compet_id in (23822,272,56417,56526,24384,69804,24185));
