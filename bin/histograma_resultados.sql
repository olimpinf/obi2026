select '000-049' as Points,count(points_a) as Count from points_fase2 where points_a between 0 and 49
union (select '050-099' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 50 and 99)
union (select '100-149' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 100 and 149)
union (select '150-199' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 150 and 199)
union (select '200-249' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 200 and 249)
union (select '250-299' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 250 and 299)
union (select '300-349' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 300 and 349)
union (select '350-400' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=3 and points_a between 350 and 400) order by Points;


select '000-049' as Points,count(points_a) as Count from points_fase2 where points_a between 0 and 49
union (select '050-099' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 50 and 99)
union (select '100-149' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 100 and 149)
union (select '150-199' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 150 and 199)
union (select '200-249' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 200 and 249)
union (select '250-299' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 250 and 299)
union (select '300-349' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 300 and 349)
union (select '350-400' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=4 and points_a between 350 and 400) order by Points;

select '000-049' as Points,count(points_a) as Count from points_fase2 where points_a between 0 and 49
union (select '050-099' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 50 and 99)
union (select '100-149' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 100 and 149)
union (select '150-199' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 150 and 199)
union (select '200-249' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 200 and 249)
union (select '250-299' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 250 and 299)
union (select '300-349' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 300 and 349)
union (select '350-400' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=5 and points_a between 350 and 400) order by Points;

select '000-049' as Points,count(points_a) as Count from points_fase2 where points_a between 0 and 49
union (select '050-099' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 50 and 99)
union (select '100-149' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 100 and 149)
union (select '150-199' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 150 and 199)
union (select '200-249' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 200 and 249)
union (select '250-299' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 250 and 299)
union (select '300-349' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 300 and 349)
union (select '350-400' as Points,count(points_a) as Count from points_fase2 as p, compet as c where c.compet_id=p.compet_id and compet_type=6 and points_a between 350 and 400) order by Points;
