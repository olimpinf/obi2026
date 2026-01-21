#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

from psycopg2 import psycopg1

# Consulta BD
conn = psycopg1.connect("host=localhost dbname=obi2018 user=obi password=guga.LC")
conn.set_client_encoding('utf-8')
curs = conn.cursor()

def usage():
    print(sys.argv[0])

def clean(s):
    new = s.replace(u'\302\260','\\raisebox{2ex}{\\tiny {o}} ')
    new = new.replace(u'N\272','\\raisebox{2ex}{\\tiny {o}} ')
    new = new.replace(u'\302\226','--')
    return new

comm = '''select DISTINCT
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
from school
where school_ok and school_has_medal
order by school_state,school_id, school_zip'''

curs.execute(comm)
bdata = curs.dictfetchall()
print('schools found:', len(bdata),file=sys.stderr)
schools = []

for data in bdata:
    deleg_name=data['school_deleg_name'].strip()
    names=deleg_name.split(' ')
    first=names[0].lower()
    if first.find('prof')==0:
        names=names[1:]
    deleg_name=" ".join(["Prof(a)."]+names)
    schools.append([deleg_name, clean(data['school_name']),data])

# now order by deleg_name, school_name
schools.sort()

for s in schools:
    print(clean(s[0]))    # deleg name
    print(clean(s[1]))    # school name
    if s[2]['school_address']: 
        print(clean(s[2]['school_address']),end=" ")
    if s[2]['school_address_number']:  
        print(clean(s[2]['school_address_number']))
    else:
        print()
    if s[2]['school_address_complement']:  
        print(clean(s[2]['school_address_complement']))
    if s[2]['school_address_district']:  
        print('Bairro', clean(s[2]['school_address_district']))
    print(s[2]['school_zip'], end=' ')
    if s[2]['school_city']!='':  
        print(clean(s[2]['school_city']),end=' ')
    if s[2]['school_state']!='':  
        print(clean(s[2]['school_state']),end=' ')
    print()
    print()
