#!/usr/bin/env python3

import csv
import getopt
import os
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor

DB_HOST = 'localhost'
DB_NAME = 'obi2020'

def usage():
    print('usage: %s file' % sys.argv[0], file=sys.stderr)
    sys.exit(-1)

def capitalize_name(s):
    tks = s.split()
    newtks = []
    for t in tks:
      t = t.lower()
      if t in ['de','da','do','e','das','dos']:
        newtks.append(t)
      else:
        newtks.append(t.capitalize())
    return ' '.join(newtks)

def format_compet_id(id):
    try:
        id=int(id)
    except:
        return u"ainda não definido"
    d1 = id % 10
    d2 = id % 100 // 10
    d3 = id % 1000 // 100
    d4 = id % 10000 // 1000
    d5 = id // 10000
    digit = (3 * d1 + 2 * d2 + 1 * d3 + 2 * d4 + 3 * d5) % 10
    if digit == 0:
        digit = 10
    return "%05d-%c" % (id, digit + 64)

def main():
    try:
        conn = psycopg2.connect("dbname='{}' user='obi' host={} password='guga.LC'".format(DB_NAME, DB_HOST))
    except:
        print("unable to connect")
    conn.set_client_encoding('UTF8')
    curs = conn.cursor(cursor_factory=DictCursor)
    compets_bd = {}

    # columns in spreadsheet

    LEVEL = 0
    NAME = 1
    POINTS = 2

    fname = sys.argv[1]
    with open(fname, newline='') as f:
        reader = csv.reader(f, dialect='excel')
        linenum = 0

        for r in reader:
            r = r[0].split(';')
            linenum += 1
            if linenum==1 or len(r)==0:
                continue
            if r[NAME].strip().lower()=='nome':
                continue
            name = r[NAME]            
            cmd = "select compet_id from compet where compet_name ilike '{}'".format(capitalize_name(name))
            curs.execute(cmd)
            data = curs.fetchone()[0]
            print("{},{},{}".format(format_compet_id(data),r[LEVEL],r[POINTS]))
            #conn.commit()
            #print('insert failed:', cmd, file=sys.stderr)

if __name__ == "__main__":
    main()


