#!/bin/bash

for i in  AC  AL  AM  AP  BA  CE  DF  ES  GO  MA  MG  MS  MT  PA  PB  PE  PI  PR  RJ  RN  RO  RR  RS  SC  SE  SP  TO
do
    for k in ij i1 i2 pj p1 p2 ps
    do
	bin/set_rank_final.py -u -s $i $k /dev/null
    done
done

