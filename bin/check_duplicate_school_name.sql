select school_id,school_name from school where school_name in (
SELECT                            
    school_name
FROM
    school
GROUP BY
    school_name
HAVING 
    COUNT(*) > 1
)
and school_id not in (
select distinct compet_school_id from compet
)

