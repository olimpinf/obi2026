#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2
from psycopg2.extras import DictCursor
from reportlab.graphics import shapes

from reportlab.pdfgen.canvas import Canvas


HOST = 'localhost' #'10.0.0.16'
DB = 'obi2021'

# Consulta BD

conn = psycopg2.connect("host={} dbname={} user=obi password=guga.LC".format(HOST,DB))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    return s

comm = '''select 
    s.school_id,
    s.school_name,
    s.school_deleg_name,
    c.compet_name,
    compet_type, 
    w.shirt_size
    from school as s,compet as c, week as w
    where c.compet_id=w.compet_id and compet_school_id=s.school_id and w.compet_id=c.compet_id and c.compet_type!=4 and w.tax_paid
    order by compet_school_id,compet_type,compet_name'''

curs.execute(comm)
data = curs.fetchall()
print('compets found:', len(data),file=sys.stderr)
LEVEL_NAME = {'ij':'Iniciação Júnior', 'i1':'Iniciação 1', 'i2':'Iniciação 2', 'pj':'Programação Júnior', 'p1':'Programação 1', 'p2':'Programação 2', 'ps':'Programação Sênior'}


def write_report(myfile, school): #_name, ij, i1, i2, pj, p1, p2, ps):
    myfile.drawString(540, 800, '{}'.format(school['school_id']))
    myfile.drawString(200, 750, 'Relação de Camisetas - Semana Olímpica -- OBI2021')
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
                myfile.drawString(80, 700-line, compet[0])
                myfile.drawString(400, 700-line, compet[1])
                line += 16
            line += 10

myfile = Canvas('lista_conteudo.pdf')

LEVEL = {7:'ij', 1:'i1', 2:'i2', 5:'pj', 3:'p1', 4:'p2', 6:'ps'}
schools = []

# first school id in database
cur_school_id = 29

# first school
school = {'ij':[], 'i1':[], 'i2':[], 'pj':[], 'p1':[], 'p2':[], 'ps':[]}
for d in data:
    if d['school_id'] != cur_school_id:
        school['school_name'] = school_name
        school['school_deleg_name'] = school_deleg_name
        school['school_id'] = cur_school_id
        schools.append(school)
        cur_school_id = d['school_id']

        # new school
        school = {'ij':[], 'i1':[], 'i2':[], 'pj':[], 'p1':[], 'p2':[], 'ps':[]}
    school_name = clean(d['school_name'])
    school_deleg_name = clean(d['school_deleg_name'])
    if not d['shirt_size']:
        d['shirt_size']='*'
    school[LEVEL[d['compet_type']]].append([d['compet_name'],d['shirt_size']])

school['school_name'] = school_name
school['school_deleg_name'] = school_deleg_name
school['school_id'] = cur_school_id
schools.append(school)

for school in schools:
    write_report(myfile, school) #['school_name'],school['ij'],school['i1'],school['i2'],school['pj'],school['p1'],school['p2'],school['ps'])
    myfile.showPage()

myfile.save()
