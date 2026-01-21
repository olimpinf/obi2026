#!/usr/bin/env python3

import csv
import getopt
import os
import string
import sys
from get_certif import get_certif_batch_compets

import psycopg2
from psycopg2.extras import DictCursor

HOST = 'localhost'
DB_NAME = 'obi2019'
YEAR = 2019

def usage():
    print('usage: %s file' % sys.argv[0], file=sys.stderr)
    sys.exit(-1)


# Abre conexao com BD
conn = psycopg2.connect("host={} dbname={}  user=obi password=guga.LC".format(HOST,DB_NAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

cmd = "select compet_id from week where compet_id is not null"
curs.execute(cmd)
compets_bd = curs.fetchall()
compets=[]
for c in compets_bd:
    compets.append(c['compet_id'])

get_certif_batch_compets(compets,YEAR)
