#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2.extras

# Consulta BD
conn = psycopg2.connect("host=localhost dbname=obi2021 user=obi password=guga.LC")
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
#    s.school_deleg_name,
#    s.school_name,
#    s.school_address,
#    s.school_address_number,
#    s.school_address_complement,
#    s.school_address_district,
#    s.school_zip,
#    s.school_city,
#    s.school_state 
#from school as s
#inner join week as w
#on s.school_id = w.school_id
#where w.shirt_size is not null and w.tax_paid = 't'
#order by s.school_state,s.school_id, s.school_zip'''

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
where school_id IN (406, 58, 903, 895, 126, 383, 853, 263, 77, 222, 1280, 181, 354, 245, 399, 234, 227, 224, 146, 203, 167, 63, 1092, 103, 673, 986, 1181, 81, 798, 453, 162)
order by school_state,school_id, school_zip'''

curs.execute(comm)
bdata = curs.fetchall()
print('schools found:', len(bdata),file=sys.stderr)
schools = []

for data in bdata:
    deleg_name=data['school_deleg_name'].strip().title()
    names=deleg_name.split(' ')
    first=names[0].lower()
    if first.find('prof')==0:
        names=names[1:]
    deleg_name=" ".join(["Prof(a)."]+names)
    schools.append([deleg_name, clean(data['school_name'].title()),data])

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
