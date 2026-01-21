#! /usr/bin/env python
# -*- coding: utf-8 -*-

### #!/usr/local/zopetree/python2.3/bin/python

import base64
import os
import sys

import psycopg2
from psycopg2.extras import DictCursor

school_id = int(sys.argv[1])


# Consulta BD
conn = psycopg1.connect("host=localhost dbname=obi2020 user=obi password=guga.LC")

conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

comm = "select compet_id,compet_name,compet_type,compet_points_fase1 from compet where compet_school_id = %d order by compet_name,compet_id" % (school_id)

curs.execute(comm)
data = curs.dictfetchall()

if not data:
    print("Nada")
    sys.exit(0)

print('found',len(data),'compets')

first_id = ''
name = ''

for c in data:
    if ['compet_type'] in (1,2,7):
        num_subs = 0
    else:
        comm = "select count(*) from sub_fase1 where compet_id=%d" % (c['compet_id'])
        curs.execute(comm)
        num_subs = curs.dictfetchall()[0]['count']
        
    if c['compet_name'].lower() != name:
        print('FIRST',c['compet_id'],c['compet_name'],c['compet_points_fase1'],num_subs)
        first_id = c['compet_id']
        first_points = c['compet_points_fase1']
        first_subs = num_subs
        name = c['compet_name'].lower()
        continue
    # same name, not first
    print(c['compet_id'],c['compet_name'],c['compet_points_fase1'],num_subs)
    print(first_id,name, first_points)
    if first_points != None or first_subs > 0:
        comm = "delete from compet where compet_id=%d and compet_school_id=%d" % (c['compet_id'],school_id)
        curs.execute(comm)
        conn.commit()
        print(comm)
        print('delete',c['compet_id'])
    else:
        comm = "delete from compet where compet_id=%d and compet_school_id=%d" % (first_id,school_id)
        print(comm)
        curs.execute(comm)
        conn.commit()
        print('delete',first_id)
    print()


conn.commit()
conn.close()
sys.exit(0)
