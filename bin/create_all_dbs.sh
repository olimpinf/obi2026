#!/bin/bash

# run as postgres user

for d in `seq 2005 2024`
do echo $d
   psql postgres -c "DROP DATABASE obi$d"
   psql postgres -c "CREATE DATABASE obi$d OWNER obi ENCODING 'UTF8'"
done
