%% must copy and paste in a psql prompt...

\COPY (
    SELECT
        s.school_state,
        s.school_city,
        s.school_id,
        s.school_name,
        COUNT(*) FILTER (WHERE c.compet_type = 1) AS I1,
        COUNT(*) FILTER (WHERE c.compet_type = 2) AS I2,
        COUNT(*) FILTER (WHERE c.compet_type = 7) AS IJ
    FROM compet c
    JOIN school s ON c.compet_school_id = s.school_id
    WHERE c.compet_classif_fase2 = TRUE and compet_type in (1,2,7)
    GROUP BY s.school_state, s.school_city, s.school_id, s.school_name
    ORDER BY s.school_state, s.school_city, s.school_name)
    TO 'compets_fase3_ini.csv' WITH CSV HEADER;
