#!/usr/bin/env python3

import getopt
import os
import string
import sys

from psycopg2 import psycopg1

HOST = 'localhost'
#HOST = '10.0.0.16'


def usage():
    print('usage: %s [-chs] level file' % sys.argv[0], file=sys.stderr)
    sys.exit(-1)

def compare_columns(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(b[0], a[0]) or cmp(a[1], b[1])

def compare_names(a, b):
    return cmp(a[1], b[1])

def compare(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(a[1], b[1])



try:
    opts, args = getopt.getopt(sys.argv[1:], 'chms:u')
except getopt.GetoptError as error:
    print(error)
    usage()

for o, a in opts:
    if o == '-h':
        pass
    else:
        usage()


# Abre conexao com BD
conn = psycopg1.connect("host=%s dbname=obi2018  user=obi password=guga.LC" % HOST)
conn.set_client_encoding('utf-8')
curs = conn.cursor()

############## accepting points_fase2 == 0 !!!
############## accepting points_fase2 == 0 !!!
############## accepting points_fase2 == 0 !!!
############## accepting points_fase2 == 0 !!!
############## accepting points_fase2 == 0 !!!
comm = """select S.school_type, S.school_name,S.school_city,S.school_state, S.school_id 
from school as S 
where S.school_ok
order by S.school_id """ 
curs.execute(comm)
schools = curs.dictfetchall()

for s in schools:
    comm = """select C.compet_name, C.compet_id, compet_type, C.compet_rank_final, 
S.school_type, S.school_name,S.school_city,S.school_state, S.school_id 
from compet as C, school as S 
where C.compet_school_id=S.school_id and compet_points_fase1>0
and S.school_id={}
order by C.compet_rank_final,compet_name """.format(s['school_id'])
    curs.execute(comm)
    data = curs.dictfetchall()
    school_compets = []
    for c in data:
        school_compets.append((c['compet_name'],c['compet_type'],c['compet_id'],c['compet_rank_final']))

    school_compets.sort()
    c = school_compets
    for i in range(1,len(school_compets)):
        if c[i][0] == c[i-1][0]:
            if  c[i][1] == c[i-1][1]:
                continue # could remove
            #print(c[i-1])
            #print(c[i])
            #print()
            if c[i][3] is None:
                if c[i-1][3] is None:
                    continue
                    print('could remove both:')
                    print('remove {}: {}, level={}, {}'.format(c[i-1][2],c[i-1][0],c[i-1][1],c[i-1][3]))
                    print('remove {}: {}, level={}, {}'.format(c[i][2],c[i][0],c[i][1],c[i][3]))
                else:
                    print("delete from compet where compet_name ilike '{}' and compet_type={} and compet_id={}".format(c[i][0],c[i][1],c[i][2],))
                    print('remove {}: {}, level={}, {}'.format(c[i][2],c[i][0],c[i][1],c[i][3]))
            else:
                if c[i-1][3] is None:
                    print("delete from compet where compet_name ilike '{}' and compet_type={} and compet_id={}".format(c[i-1][0],c[i-1][1],c[i-1][2],))
                    print('remove {}: {}, level={}, {}'.format(c[i-1][2],c[i-1][0],c[i-1][1],c[i-1][3]))
                elif c[i-1][3]>c[i][3] :
                    print("delete from compet where compet_name ilike '{}' and compet_type={} and compet_id={}".format(c[i-1][0],c[i-1][1],c[i-1][2],))
                    print('remove {}: {}, level={}, {}'.format(c[i-1][2],c[i-1][0],c[i-1][1],c[i-1][3]))
                else:
                    print("delete from compet where compet_name ilike '{}' and compet_type={} and compet_id={}".format(c[i][0],c[i][1],c[i][2],))
                    print('remove {}: {}, level={}, {}'.format(c[i][2],c[i][0],c[i][1],c[i][3]))
            
            print(c[i-1])
            print(c[i])
            print(s['school_name'],s['school_city'])
            print()
            print()
