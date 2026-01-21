#!/bin/sh

if [ ! -e total ]
then
    mkdir total
else
    rm -rf total/*
fi

if [ ! -e prog ]
then
    mkdir prog
else
    rm -rf prog/*
fi

if [ ! -e ini ]
then
    mkdir ini
else
    rm -rf ini/*
fi

psql -d obi2022 -U obi -f consultas_sedes.sql

# total
./formata_sedes.py total/escolas_com.csv total/coordenadas.csv > total/info_escolas_com.csv
./formata_sedes.py total/escolas_sem.csv total/coordenadas.csv > total/info_escolas_sem.csv
./formata_sedes.py total/escolas_sede.csv total/coordenadas.csv > total/info_escolas_sede.csv
./gen_data.py total/info_escolas_com.csv total/info_escolas_sem.csv  total/info_escolas_sede.csv > sedes.js

# prog
./formata_sedes.py prog/escolas_com.csv total/coordenadas.csv > prog/info_escolas_com.csv
./formata_sedes.py prog/escolas_sem.csv total/coordenadas.csv > prog/info_escolas_sem.csv
./formata_sedes.py prog/escolas_sede.csv total/coordenadas.csv > prog/info_escolas_sede.csv
./gen_data.py prog/info_escolas_com.csv prog/info_escolas_sem.csv  prog/info_escolas_sede.csv > sedes_prog.js

# ini
./formata_sedes.py ini/escolas_com.csv total/coordenadas.csv > ini/info_escolas_com.csv
./formata_sedes.py ini/escolas_sem.csv total/coordenadas.csv > ini/info_escolas_sem.csv
./formata_sedes.py ini/escolas_sede.csv total/coordenadas.csv > ini/info_escolas_sede.csv
./gen_data.py ini/info_escolas_com.csv ini/info_escolas_sem.csv  ini/info_escolas_sede.csv > sedes_ini.js


echo "copying sedes"

cp sedes.js ../static/js/sedes.js
cp sedes_ini.js ../static/js/sedes_ini.js
cp sedes_prog.js ../static/js/sedes_prog.js

