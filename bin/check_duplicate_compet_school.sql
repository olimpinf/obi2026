select compet_id, compet_name,compet_points_fase1 from compet where compet_name in (
SELECT                            
    compet_name
FROM
    compet
WHERE
    compet_school_id = 490 
GROUP BY
    compet_name
HAVING 
    COUNT(*) > 1
)
order by compet_name,compet_id
