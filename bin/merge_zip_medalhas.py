#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import os
import string
import sys
import csv

import psycopg2
from psycopg2.extras import DictCursor

# medal_cuts.py must be linked to principal/utils/medal_cuts.py

HOST = 'localhost'
#HOST = '10.0.0.16'
DBNAME = 'obi2020'

trtable={'Á':'á','É':'é','Í':'í','Ó':'ó','Ú':'ú','À':'à','Ç':'ç','Ã':'ã','Õ':'õ','Â':'â','Ê':'ê','Ô':'ô',"'":"´"}


def usage():
    print('usage: %s [-chs] level file' % sys.argv[0],file=sys.stderr)
    sys.exit(-1)

               
def caps(s):
    #s=s.decode('latin-1').encode('utf-8')
    tks=s.split()
    s=''
    for t in tks:
        t.replace('Á','á')
        t.replace('É','é')
        t.replace('Í','í')
        t.replace('Ó','ó')
        t.replace('Ú','ú')

        t.replace('Â','â')
        t.replace('Ê','ê')
        t.replace('Ô','ô')

        t.replace('Ã','ã')
        t.replace('Õ','õ')

        t.replace('Ç','ç')
        # if t.find('\xc3\x89')>=0:
        #     print >> sys.stderr, 'replacing'
        #     print >> sys.stderr, t
        #     tnew.replace(t,'\xc3\x89','É')
        #     print >> sys.stderr, tnew
        nt=''
        for t1 in t:
            if t1 in trtable.keys(): # does not work :-(
                nt+=trtable[t1]
            else:
                nt+=t1.lower()
        if nt.upper() in ['(FMM)', 'ABC', 'BH', 'CEFET-MG', \
                              'EE', 'EMEF', 'GGE', \
                              'ICMC', 'ICMC/USP', \
                              'IFAL', 'IFBA', 'IFCE', 'IFMT', 'IFPB', 'IFPR', \
                              'IFSP', 'IFTM', 'IFMT','IME-USP', 'ITA', 'SJC', 'UFF', 'UFMG', 'UFPE', \
                              'UFRJ', 'UFRN', 'UFRRJ', 'USP']:
            s+=' '+nt.upper()
        elif nt in ['de','da','do','e','das','dos']:
            s+=' '+nt
        else:
            s+=' '+nt.capitalize()
    return s.strip()

try:
    opts, args = getopt.getopt(sys.argv[1:], 'chms:u')
except:
    print('error')
    usage()
for o, a in opts:
    if True:
        pass
    else:
        usage()

fname_csv = args[0]
fname_out = args[1]
print(fname_csv)
fin=open(fname_csv,'r')
fout=open(fname_out,'w')
ferror=open('errors.txt','w')

reader = csv.reader(fin, delimiter=';')
linenum=0
codes = {}
for r in reader:
    linenum += 1
    if linenum==1: continue
    print(r)
    if len(r)==0:
        continue
    try:
        tmp = r[4].strip().split()
        school_zip = "{:05d}-{}".format(int(tmp[0]),tmp[1])
        print(school_zip)
        codes[school_zip] = r[3].strip()
    except:
        pass

print(codes)

# Abre conexao com BD
conn = psycopg2.connect("host=%s dbname=%s  user=obi password=guga.LC" % (HOST,DBNAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)


comm = "select distinct school_id,school_zip,school_name,school_city,school_state from school as s, compet as c where compet_school_id=school_id and compet_medal in ('o','p','b')"
curs.execute(comm)
data = curs.fetchall()

for item in data:
    school_name = item['school_name']
    school_name = caps(school_name)
    school_city = item['school_city']
    school_id = item['school_id']
    school_state = item['school_state'].strip()
    school_zip = item['school_zip']
    try:
        print(school_name,school_city,school_state,school_zip,codes[school_zip],sep=';',file=fout)
    except:
        print(school_zip, school_name,school_city,school_state,'not found',file=ferror)
conn.close()

