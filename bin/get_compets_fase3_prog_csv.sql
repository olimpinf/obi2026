%% must copy and paste in a psql prompt...

\COPY (
    SELECT
        s.school_state,
        s.school_city,
        s.school_id,
        s.school_name,
        COUNT(*) FILTER (WHERE c.compet_type = 5) AS PJ,
        COUNT(*) FILTER (WHERE c.compet_type = 3) AS P1,
        COUNT(*) FILTER (WHERE c.compet_type = 4) AS P2,
        COUNT(*) FILTER (WHERE c.compet_type = 6) AS PS
    FROM compet c
    JOIN school s ON c.compet_school_id = s.school_id
    WHERE c.compet_classif_fase2 = TRUE and compet_type in (3,4,5,6)
    GROUP BY s.school_state, s.school_city, s.school_id, s.school_name
    ORDER BY s.school_state, s.school_city, s.school_name)
    TO 'compets_fase3_prog.csv' WITH CSV HEADER;
