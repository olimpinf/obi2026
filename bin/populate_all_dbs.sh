#!/bin/bash

# run as postgres user

for d in `seq 2006 2023`
do echo $d
   gunzip attic/databases/OBI$d.sql.gz
   psql -U obi -d obi$d -f attic/databases/OBI$d.sql
   gzip attic/databases/OBI$d.sql
done
