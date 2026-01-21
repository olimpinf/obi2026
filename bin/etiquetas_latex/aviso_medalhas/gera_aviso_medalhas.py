#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2.extras

# Consulta BD
ano = 2022
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
    new = new.replace('_', '\_')
    return new

# Remove alunos que receberam a medalha na Semana Olímpica
# Remove alunos de Fortaleza, Etapa SP, Unicamp, IME-USP e ICMC-USP (levaram durante a Escola de Verão da Maratona)
comm = '''select school_id, school_name, school_deleg_phone, school_deleg_email
from school inner join compet on school_id = compet_school_id where
compet_medal in ('o','p','b') and
compet_id not in (select compet_id from week where form_info = TRUE) and
compet_school_id not in (select school_id from school where school_city = 'Fortaleza' and school_state = 'CE') and
compet_school_id not in (select school_id from school where school_name ilike '%Etapa%' and school_city = 'São Paulo') and
compet_school_id not in (1, 512, 1148)
group by school_id
order by school_id;'''

curs.execute(comm)
bdata = curs.fetchall()
print('schools found:', len(bdata),file=sys.stderr)
schools = []

for data in bdata:
    schools.append([clean(data['school_name'].title()), clean(data['school_deleg_phone']), clean(data['school_deleg_email'].lower()), data['school_id']])

for s in schools:
    print(f'({s[3]}) ' if ID else '', '\\textbf{\\textcolor{red}{ATENÇÃO:}} este pacote contém \\textbf{medalhas} da Olimpíada Brasileira de Informática (OBI) para alunos da escola ', s[0], '.', sep='', end= ' ')
    print(f'O destinatário é o(a) professor(a) que inscreveu a escola na OBI{ano}. Se não reconhecer o nome, por favor entre em contato com ele(a) antes de devolver o pacote ao remetente:')
    print('Telefone:', s[1])
    print('E-mail:', s[2])
    print()
