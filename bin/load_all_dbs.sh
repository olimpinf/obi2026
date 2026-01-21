#!/bin/bash

for d in `seq 2005 2024`
	 do echo $d
	 gunzip attic/postgres/databases/OBI$d.sql.gz
	 psql -U obi -d obi$d -f attic/postgres/databases/OBI$d.sql
	 gzip attic/postgres/databases/OBI$d.sql
done
