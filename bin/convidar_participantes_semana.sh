#!/bin/bash

#### Dezembro 2022 ####
compets_pj=(1535 25889 25846) # Bronzes PJ que não são F9

compets_p1=(24262 63453 74769) # Bronzes P1 que não são M1

compets_p2=(260 77542 78350 64178) # Bronzes P2 que são M3
appeals_p2=(56547)
seletiva_egoi_p2=(35606 70012 13534 56533 79422)
all_p2=(${compets_p2[@]} ${appeals_p2[@]} ${seletiva_egoi_p2[@]})

for i in ${compets_pj[@]}; do
    ./manage.py invite_compet_week "pj" $i
done

for i in ${compets_p1[@]}; do
    ./manage.py invite_compet_week "p1" $i
done

for i in ${all_p2[@]}; do
    ./manage.py invite_compet_week "p2" $i
done
