#!/bin/sh
 
#HOST="localhost"
#YEAR=$(/bin/date +%Y)
YEAR="2025"
DATE=$(/bin/date +%Y_%m_%d)
DATE_RM=$(/bin/date -d "-7day" +%Y_%m_%d)
USER="obi"
DATABASE="obi"$YEAR

echo "creating /home/olimpinf/backups/obi${YEAR}_$DATE.sql.gz"
pg_dump -c -U $USER -d $DATABASE | gzip > /home/olimpinf/backups/obi${YEAR}_$DATE.sql.gz
echo "removing /home/olimpinf/backups/obi${YEAR}_$DATE_RM.sql.gz"
rm -rf /home/olimpinf/backups/obi${YEAR}_$DATE_RM.sql.gz
