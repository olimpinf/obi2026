#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2
from psycopg2.extras import DictCursor
from reportlab.graphics import shapes

from reportlab.pdfgen.canvas import Canvas


HOST = 'localhost' #'10.0.0.16'
YEAR = '2025'

# Consulta BD

conn = psycopg2.connect(f"host={HOST} dbname=obi{YEAR} user=obi password=guga.LC")
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    return s

#comm = '''select 
#    school_id,
#    school_name,
#    school_deleg_name,
#    compet_name,
#    compet_type, 
#    compet_medal 
#    from school,compet 
#    where compet_school_id=school_id and school_ok and compet_medal in ('o','p','b')
#    order by compet_school_id,compet_type,compet_rank_final,compet_medal,compet_name'''

# comm = """select compet_id from compet_cfobi where compet_medal in ('o','p','b') and compet_id not in (select compet_id from week where compet_id is not null)"""
# curs.execute(comm)
# compets = curs.fetchall()
# print('compets found:', len(compets),file=sys.stderr)

# comm = '''select 
#     school_id,
#     school_name,
#     school_deleg_name,
#     compet_name,
#     f.compet_type, 
#     f.compet_medal 
#     from school as s,compet as c, compet_cfobi as f 
#     where f.compet_id=c.compet_id and c.compet_school_id=s.school_id and f.compet_medal in ('o','p','b') and c.compet_id in (select c.compet_id from week where c.compet_id is  not null)
#     order by c.compet_school_id,f.compet_type,f.compet_rank,f.compet_medal,compet_name'''

# curs.execute(comm)
# data = curs.fetchall()
# print('compets found:', len(data),file=sys.stderr)

comm = '''select 
    school_id,
    school_name,
    school_deleg_name,
    compet_name,
    f.compet_type, 
    f.compet_medal 
    from school as s,compet as c, compet_cfobi as f 
    where f.compet_id=c.compet_id and c.compet_school_id=s.school_id and f.compet_medal in ('o','p','b')
    order by c.compet_school_id,f.compet_type,f.compet_rank,f.compet_medal,compet_name'''


curs.execute(comm)
data = curs.fetchall()
print('compets found:', len(data),file=sys.stderr)
LEVEL_NAME = {'ij':'Iniciação Júnior', 'i1':'Iniciação 1', 'i2':'Iniciação 2', 'pj':'Programação Júnior', 'p1':'Programação 1', 'p2':'Programação 2', 'ps':'Programação Sênior'}


def write_report(myfile, school): #_name, ij, i1, i2, pj, p1, p2, ps):
    myfile.drawString(540, 800, '{}'.format(school['school_id']))
    myfile.drawString(200, 750, f'Relação de Medalhas - Competição Feminina OBI{YEAR}')
    line = 0
    myfile.drawString(60, 700-line, 'Escola: {}'.format(school['school_name']))
    line += 18
    myfile.drawString(60, 700-line, 'Coordenador Local: {}'.format(school['school_deleg_name']))
    line += 30
    for mod in ('ij','i1','i2','pj','p1','p2','ps'):
        if school[mod]:
            myfile.drawString(60, 700-line, LEVEL_NAME[mod])
            line += 22
            for compet in school[mod]:
                print('compet',compet[0],compet[1])
                myfile.drawString(80, 700-line, compet[0])
                myfile.drawString(400, 700-line, compet[1])
                line += 16
            line += 10

myfile = Canvas('lista_conteudo_cf.pdf')

LEVEL = {7:'ij', 1:'i1', 2:'i2', 5:'pj', 3:'p1', 4:'p2', 6:'ps'}
MEDAL = {'o':'ouro', 'p':'prata', 'b':'bronze', 'h':'honra ao mérito'}
schools = []
cur_school_id = 1
school = {'ij':[], 'i1':[], 'i2':[], 'pj':[], 'p1':[], 'p2':[], 'ps':[]}

school_name = clean(data[0]['school_name'])
school_deleg_name = clean(data[0]['school_deleg_name'])
school_id = data[0]['school_id']
school['school_name'] = school_name
school['school_deleg_name'] = school_deleg_name
school['school_id'] =  school_id

for d in data:

    if d['school_id'] != cur_school_id:
        schools.append(school)
        cur_school_id = d['school_id']
        school = {'ij':[], 'i1':[], 'i2':[], 'pj':[], 'p1':[], 'p2':[], 'ps':[]}
        school_name = clean(d['school_name'])
        school_deleg_name = clean(d['school_deleg_name'])
        school_id = d['school_id']
        school['school_name'] = school_name
        school['school_deleg_name'] = school_deleg_name
        school['school_id'] =  school_id
    school[LEVEL[d['compet_type']]].append([d['compet_name'],MEDAL[d['compet_medal']]])

school['school_name'] = school_name
school['school_deleg_name'] = school_deleg_name
school['school_id'] = cur_school_id
schools.append(school)


for school in schools:
    print('----')
    print(school)
    print('----')
    print()
    write_report(myfile, school) #['school_name'],school['ij'],school['i1'],school['i2'],school['pj'],school['p1'],school['p2'],school['ps'])
    myfile.showPage()

myfile.save()
