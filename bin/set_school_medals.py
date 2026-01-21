#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import os
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor

# medal_cuts.py must be linked to principal/utils/medal_cuts.py
from medal_cuts import medal_cuts

HOST = 'localhost'
#HOST = '10.0.0.16'
DBNAME = 'obi2021'
year = 2021

LEVEL = {7:"IJ",1:"I1",2:"I2",5:"PJ",3:"P1",4:"P2",6:"PS"}
MEDAL = {'o':'ouro', 'p':'prata', 'b':'bronze'}
honors=0
gold_medals=[]
silver_medals=[]
bronze_medals=[]
school_medals={}
school_names={}
school_cities={}


def usage():
    print('usage: %s [-chsu] level file' % sys.argv[0],file=sys.stderr)
    sys.exit(-1)


# def add_medal(school_id,medal,level):
#     global comm,curs
#     if school_id in school_medals.keys():
#         school_medals[school_id][level][medal] += 1
#     else:
#         school_medals[school_id]{level: {i:0 for i in ['o','p','b'] } for level in [1,2,3,4,5,6,7]}
#         school_medals[school_id][medal] += 1
#         school_names[school_id]=school_name
#         school_cities[school_id]=school_city

    

try:
    opts, args = getopt.getopt(sys.argv[1:], 'u')
except:
    print('error')
    usage()
do_update=False
for o, a in opts:
    if o == '-u':
        do_update=True
    else:
        usage()

class School:
    def __init__(self, id):
        self.id = id
        self.medals = {level: {'o':0, 'p':0, 'b':0} for level in (1,2,3,4,5,6,7) }

    
#s = School()
#s.medals[1]['o'] += 1

#schools = {i: School() for i in (10,20)}
#schools[10].medals[1]['b'] += 1

#print(schools[10].medals)

# Abre conexao com BD
conn = psycopg2.connect("host=%s dbname=%s  user=obi password=guga.LC" % (HOST,DBNAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

comm = "update school set school_has_medal = false"
curs.execute(comm)
conn.commit()

comm = "update school set school_has_medal = True where school_id in (select distinct compet_school_id from compet where compet_medal in ('o','p','b'))"
curs.execute(comm)
conn.commit()

comm = "select school_id from school where school_has_medal order by school_id"
curs.execute(comm)
data = curs.fetchall()

sch_ids = []
for d in data:
    sch_ids.append(d['school_id'])
schools = {i: School(i) for i in sch_ids}

# schools[126].medals[1]['o'] = 10
# schools[135].medals[1]['o'] = 5
# print(schools[126])
# print(schools[135])
# print()
# print(schools[126].medals)
# print(schools[135].medals)
# print()
# print(schools[126].medals[1]['o'])
# print(schools[135].medals[1]['o'])


comm = "select compet_medal, compet_type, compet_medal, school_id from compet,school where compet_school_id=school_id and compet_medal in ('o','p','b')"
curs.execute(comm)
data = curs.fetchall()

for d in data:
    school_id = d['school_id']
    schools[school_id].medals[d['compet_type']][d['compet_medal']] += 1
    
    
#for s in schools.keys():
#    print(schools[s].medals)

comm = "select school_id, school_name, school_city, school_state from school where school_has_medal order by school_state,school_city"
curs.execute(comm)
data = curs.fetchall()
for d in data:
    school_id = d['school_id']
    school_city = d['school_city']
    school_state = d['school_state']
    school_name = d['school_name']
    line = ",".join([str(school_id),school_name,school_city,school_state])
    for i in (7,1,2,5,3,4,6):
        for m in ('o','p','b'):

            if schools[school_id].medals[i][m] > 0:
                line = ", ".join([line,f'{LEVEL[i]}: {schools[school_id].medals[i][m]} {MEDAL[m]}'])

    print(line)



conn.close()

# print("gold medals", len(gold_medals), file=sys.stderr)
# print("silver medals", len(silver_medals), file=sys.stderr)
# print("bronze medals", len(bronze_medals), file=sys.stderr)
# print("honors", honors, file=sys.stderr)
