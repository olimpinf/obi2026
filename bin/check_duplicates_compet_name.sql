SELECT                            
    compet_name, compet_school_id, COUNT(*)
FROM
    compet
GROUP BY
    compet_name, compet_school_id
HAVING 
    COUNT(*) > 1
;
