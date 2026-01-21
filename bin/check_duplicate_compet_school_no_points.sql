select compet_id,compet_name,compet_points_fase1 from compet where compet_name in (
SELECT                            
    compet_name
FROM
    compet
WHERE
    compet_school_id = 494
GROUP BY
    compet_name
HAVING 
    COUNT(*) > 1
)
and compet_id not in (
select distinct compet_id from compet where compet_school_id = 494 and compet_points_fase1 is not null
)
order by compet_name
