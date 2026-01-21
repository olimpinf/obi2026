#!/bin/bash

for d in `seq 2005 2024`
	 do echo $d
	 pg_dump -c -U obi -d obi$d > attic/postgres/databases/OBI$d.sql
	 gzip attic/postgres/databases/OBI$d.sql
done
