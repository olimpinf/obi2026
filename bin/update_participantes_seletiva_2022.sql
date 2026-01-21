UPDATE week SET partic_type = 'Competidor';
UPDATE week SET partic_level = c.compet_type FROM compet AS c WHERE c.compet_id = week.compet_id;
