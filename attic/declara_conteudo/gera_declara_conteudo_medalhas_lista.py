#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2
from psycopg2.extras import DictCursor
from reportlab.graphics import shapes

from pdfmerge import merge
from PyPDF2 import PdfReader, PdfWriter

HOST = 'localhost' #'10.0.0.16'
DB = 'obi2024'
YEAR = '2024'
MONTH = 'dezembro'
DAY = '10'
# Consulta BD

conn = psycopg2.connect("host={} dbname={} user=obi password=guga.LC".format(HOST,DB))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    return s

comm_obi = '''select count(*) as num_medals,
   school_id,
   school_deleg_name,
   school_name,
   school_address,
   school_address_number,
   school_address_complement,
   school_address_district,
   school_zip,
   school_city,
   school_state 
from school,compet
where compet_school_id=school_id and school_ok and school_has_medal and compet_medal is not null
group by school_id, 
   school_deleg_name,
   school_name,
   school_address,
   school_address_number,
   school_address_complement,
   school_address_district,
   school_zip,
   school_city,
   school_state 
order by school_id'''

comm_cf = '''select count(*) as num_medals,
   school_id,
   school_deleg_name,
   school_name,
   school_address,
   school_address_number,
   school_address_complement,
   school_address_district,
   school_zip,
   school_city,
   school_state 
from school as s, compet as c, compet_cfobi as f
where c.compet_id=f.compet_id and c.compet_school_id=s.school_id and s.school_ok and f.compet_medal in ('o','p','b')
group by school_id, 
   school_deleg_name,
   school_name,
   school_address,
   school_address_number,
   school_address_complement,
   school_address_district,
   school_zip,
   school_city,
   school_state 
order by school_id;
'''

# comm = '''select count(*) as num_medals,
#     school_id,
#     school_deleg_name,
#     school_name,
#     school_address,
#     school_address_number,
#     school_address_complement,
#     school_address_district,
#     school_zip,
#     school_city,
#     school_state
# from school inner join compet on school_id = compet_school_id
# where school_id in  (904, 227, 286, 1513, 1149, 532, 334, 1164, 2429)
# group by school_id,
#     school_deleg_name,
#     school_name,
#     school_address,
#     school_address_number,
#     school_address_complement,
#     school_address_district,
#     school_zip,
#     school_city,
#     school_state
# order by school_id'''

curs.execute(comm)
bdata = curs.fetchall()
print('schools found:', len(bdata),file=sys.stderr)

toaddresses=[]

for data in bdata:
    deleg_name=data['school_deleg_name'].strip()
    names=deleg_name.split(' ')
    first=names[0].lower()
    if first.find('prof')==0:
        names=names[1:]
    deleg_name=" ".join(["Prof(a)."]+names)
    deleg_name = clean(deleg_name)
    school_name = clean(data['school_name'])

    toaddress = {}
    toaddress['name'] = deleg_name    # deleg name
    toaddress['address1'] = school_name # school name
    tmp = data['school_address']
    if data['school_address_number']:
        tmp += ', ' + data['school_address_number']
    toaddress['address2'] = tmp
    toaddress['zip'] = data['school_zip']
    toaddress['city']= data['school_city']
    toaddress['state']= data['school_state']
    toaddress['cpf']= ''
    toaddress['num_medals']= 1 #data['num_medals']
    toaddress['id'] = data['school_id']
    toaddresses.append(toaddress)

fromaddress = {'name':'Olimpíada Brasileira de Informática','address1':'Instituto de Computação - UNICAMP','address2':'Av. Albert Einstein, 1251', 'city':'Campinas', 'state':'SP', 'zip':'13083-852', 'cpf':'019.350.398-06', 'cnpj':'29.532.264/0001-78'}

output = PdfWriter()
orig_name = 'formularioA4.pdf'
for t in toaddresses:
    page = merge(orig_name, fromaddress, t, t['num_medals'], DAY, MONTH, YEAR)
    output.add_page(page)
    print('.',end='',file=sys.stderr,flush=True)

outputStream = open('declaracoes_conteudo.pdf', "wb")
output.write(outputStream)
outputStream.close()
