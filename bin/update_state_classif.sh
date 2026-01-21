#!/bin/sh

#BASE=/Users/ranido/Documents/OBI/django3/obi
BASE=/home/olimpinf/django3/obi
for s in AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR SC SE SP RJ RN RO RR RS TO; do
    ${BASE}/bin/print_rank_final.py -u -s $s ij /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s i1 /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s i2 /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s pj /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s p1 /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s p2 /tmp/junk ;
    ${BASE}/bin/print_rank_final.py -u -s $s pu /tmp/junk ;
done
