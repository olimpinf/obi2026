delete from week;

-- obi2021
\echo 'I1'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,compet_type from compet where compet_type=1 and compet_medal='o';

\echo 'I2'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,compet_type from compet where compet_type=2 and compet_medal='o';

\echo 'PJ'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,compet_type from compet where compet_type=5 and (compet_medal='o' or compet_medal='p');

\echo 'P1'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,compet_type from compet where compet_type=3 and (compet_medal='o' or compet_medal='p');

\echo 'P2'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,compet_type from compet where compet_type=4 and (compet_medal='o' or compet_medal='p');

-- obi2020
--insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,1 from compet where compet_id in (43768,41684,24965,34001,13133,43718,62231,48329,58861,38497,42972);

\echo '2020 I1'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,1 from compet where compet_id in (38497,41684,43718);

--insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,2 from compet where compet_id in (18542,05110,36859,22779,03900,38461,48347,18411,19749,40104,37035,22722,28445,30361,30356,58730,13131,37037,32569,48370);

\echo '2020 I2'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,2 from compet where compet_id in (03900,18411,18542,19707,19749,28445,30356,30361,34139,36859,37035,37037,40104,43633,43768,48329,48347,48370,58730,58861,62231);


--insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,5 from compet where compet_id in (42813,05813,40578,31194,05809,37116,37128);

\echo '2020 PJ'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,5 from compet where compet_id in (13133,22722,23778,24965,31194,34001,42813);

--insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,3 from compet where compet_id in (28446,05825,00128,24203,52648,17266,00127,31451,31402);

\echo '2020 P1'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,3 from compet where compet_id in (05110,05809,05813,13131,22779,32569,37128,38461,40578);

\echo '2020 P2'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,4 from compet where compet_id in (13186,19449,22422,28446,31451,32619,44643,52648);


-- CF-OBI

\echo 'CF-OBI P1'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,3 from compet where compet_id in (3206,3205);
\echo 'CF-OBI PJ'
insert into week (compet_id,school_id,partic_level) select compet_id,compet_school_id,5 from compet where compet_id in (24402,19341,22713,10630,16013);
