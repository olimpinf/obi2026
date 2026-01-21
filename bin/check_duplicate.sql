SELECT                            
    school_id, COUNT(*)
FROM
    school
GROUP BY
    school_id
HAVING 
    COUNT(*) > 1
;
