#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2.extras

# Consulta BD
ano = 2021
ID = False

conn = psycopg2.connect(f'host=localhost dbname=obi{ano} user=obi password=guga.LC')
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    new = s.replace(u'\302\260','\\raisebox{2ex}{\\tiny {o}} ')
    new = new.replace(u'N\272','\\raisebox{2ex}{\\tiny {o}} ')
    new = new.replace(u'\302\226','--')
    return new

#comm = '''select DISTINCT
#    s.school_id,
#    s.school_name,
#    s.school_deleg_phone,
#    s.school_deleg_email
#from school as s
#inner join week as w
#on s.school_id = w.school_id
#where w.shirt_size is not null and w.tax_paid = 't'
#order by s.school_id'''

comm = '''select
    school_id,
    school_name,
    school_deleg_phone,
    school_deleg_email
from school
where school_id IN (58, 63, 103, 126, 224, 263, 354, 853, 895, 1092, 1181, 1280)
order by school_id'''

curs.execute(comm)
bdata = curs.fetchall()
print('schools found:', len(bdata),file=sys.stderr)
schools = []

for data in bdata:
    schools.append([clean(data['school_name'].title()), clean(data['school_deleg_phone']), clean(data['school_deleg_email'].lower()), data['school_id']])

for s in schools:
    print(f'({s[3]}) ' if ID else '', '\\textbf{\\textcolor{red}{ATENÇÃO:}} este pacote contém camisetas da Olimpíada Brasileira de Informática (OBI) para alunos da escola ', s[0], '.', sep='', end= ' ')
    print(f'O destinatário é o(a) professor(a) que inscreveu a escola na OBI{ano}. Se não reconhecer o nome, por favor entre em contato com ele(a) antes de devolver o pacote ao remetente:')
    print('Telefone:', s[1])
    print('E-mail:', s[2])
    print()
