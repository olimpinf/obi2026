#!/bin/sh

for i in `seq 2005 2020`;
do echo $i;
   psql -d obi$i -U obi -c "select count(*) from compet where compet_sex='F'";
done

   


