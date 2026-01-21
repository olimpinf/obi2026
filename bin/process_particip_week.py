#!/usr/bin/env python3

import csv
import getopt
import os
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor

DB_HOST = 'localhost'
DB_NAME = 'obi2019'

def usage():
    print('usage: %s file' % sys.argv[0], file=sys.stderr)
    sys.exit(-1)

def compare_columns(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(b[0], a[0]) or cmp(a[1], b[1])

def find_compet_id(name, bd_names, conv_type='convidado'):
    #print('name:',name)
    name = name.strip()
    # try full name
    if conv_type=='convidado':
        for compet in bd_names:
            if name.lower()==compet['compet_name'].lower().strip():
                compet_id = compet['compet_id']
                rank = compet['compet_rank_final']
                #print(compet['compet_name'])
                #print(name,'matched full name')
                return compet_id,rank
    else:
        #print('find chaperone',name.lower())
        for chaperone in bd_names:
            #print(chaperone)
            if name.lower()==chaperone['chaperone_name'].lower().strip():
                chaperone_id = chaperone['chaperone_id']
                rank = 0
                #print(compet['compet_name'])
                #print(name,'matched full name')
                return chaperone_id,rank
            
    name_tokens = name.lower().split()
    max_match, compet_id, rank = 0,0,10000
    max_matched = []
    matched_name = ''
    matched_id = 0
    #print('name_tokens',name_tokens)
    for partic in bd_names:
        #print('.',end='')
        if conv_type=='convidado':
            bd_name_tokens = partic['compet_name'].lower().strip().split()
        else:
            bd_name_tokens = partic['chaperone_name'].lower().strip().split()

        #print('bd_name_tokens',bd_name_tokens)
        length = max(len(name_tokens),len(bd_name_tokens))
        match = 0
        matched=[]
        for i in range(len(name_tokens)):
            for j in range(i,len(bd_name_tokens)):
                #print('comparing',name_tokens[i],bd_name_tokens[j])
                if name_tokens[i] in ('de','do','da') or bd_name_tokens[j] in ('de','do','da'):
                    continue
                if name_tokens[i]==bd_name_tokens[j]:
                    matched.append(name_tokens[i])
                    match += 1
                    break
        if match > max_match:
            max_match = match
            max_matched = matched
            if conv_type=='convidado':
                matched_id = partic['compet_id']
                matched_name = partic['compet_name']
                matched_rank = partic['compet_rank_final']
            else:
                matched_id = partic['chaperone_id']
                matched_name = partic['chaperone_name']
                matched_rank = 0
                
            #print('a match',match,matched,matched_id)
    #print('* max_match=',max_match)
    if max_match >= 3:
        #print('matched_id',matched_id)
        #print(matched_name)
        #print(matched)
        compet_id = matched_id
        rank = matched_rank
    return compet_id,rank

def compare(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(a[1], b[1])


def main():
    try:
        conn = psycopg2.connect("dbname='{}' user='obi' host={} password='guga.LC'".format(DB_NAME, DB_HOST))
    except:
        print("unable to connect")
    conn.set_client_encoding('UTF8')
    curs = conn.cursor(cursor_factory=DictCursor)
    compets_bd = {}
    MAX_RANK={1:42,2:36,5:27,3:25,4:22}
    for i in range(1,6):
        cmd = "select compet_id,compet_name,compet_rank_final from compet where compet_type = {} and compet_rank_final<={}".format(i,MAX_RANK[i])
        curs.execute(cmd);
        compets_bd[i] = curs.fetchall()

    cmd = "select chaperone_id, chaperone_name from chaperone where chaperone_id is not null"
    curs.execute(cmd)
    chaperones_bd = curs.fetchall()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "a", ["acompanhante"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    flag_acompanhante = False
    for o, a in opts:
        if o in ("-a", "--acompanhante"):
            flag_acompanhante = True
        else:
            assert False, "unhandled option"

    try:
        fname = args[0]
    except:
        print('error: need a filename',file=sys.stderr)
        usage()

    LEVEL_NUM = {'iniciação júnior':7,'iniciação 1':1,'iniciação 2':2,'programação júnior':5,'programação 1':3,'programação 2':4,'pu':6}
    SIZES = {'pequeno': 'P','médio': 'M','grande': 'G','extra grande': 'GG'}
    # columns in spreadsheet

    if flag_acompanhante:
        NAME = 2
        DOCUMENT = 4
        ACOMP_TYPE = 6
        SHIRT_SIZE = 7
        ALLERGIES = 8
    else:
        NAME = 3
        LEVEL = 5
        DOCUMENT = 8
        SHIRT_SIZE = 9
        ALLERGIES = 10
    with open(fname, newline='') as f:
        reader = csv.reader(f, dialect='excel')
        linenum = 0

        for r in reader:
            linenum += 1
            if linenum==1 or len(r)==0:
                continue
            if r[NAME].strip().lower()=='nome completo do(a) ':
                continue
            name = r[NAME]
            if flag_acompanhante:
                chaperone_id,rank = find_compet_id(r[NAME],chaperones_bd,conv_type='chaperone')
                acomp_type = r[ACOMP_TYPE].strip()=='Pago'
            else:
                level_num = LEVEL_NUM[r[LEVEL].lower()]
                compet_id,rank = find_compet_id(name,compets_bd[level_num])
                #print(",".join([str(level_num),str(rank),str(compet_id),name]))
                if compet_id == 0:
                    print('could not find compet_id', name, file = sys.stderr)
                    continue
            document = r[DOCUMENT].strip()
            shirt_size = r[SHIRT_SIZE].lower().strip()
            allergies = r[ALLERGIES].strip()

            if flag_acompanhante:
                cmd = "select * from week where chaperone_id={}".format(chaperone_id) 
            else:
                cmd = "select * from week where compet_id={}".format(compet_id)
            curs.execute(cmd)
            exists = curs.fetchall()
            #print('exists',exists)
            if exists:
                if flag_acompanhante:
                    cmd = "update week set document='{}',shirt_size='{}',allergies='{}',paid={},form_info=True where chaperone_id={}".format(document,SIZES[shirt_size],allergies,acomp_type,chaperone_id)
                else:
                    cmd = "update week set document='{}',shirt_size='{}',allergies='{}' where compet_id={}".format(document,SIZES[shirt_size],allergies,compet_id)
            else:
                if flag_acompanhante:
                    cmd = "insert into chaperone (chaperone_name,chaperone_sex) values ('{}','{}') RETURNING chaperone_id".format(r[NAME],'M')

                    #print(cmd)
                    curs.execute(cmd)
                    conn.commit()
                    chaperone_id = curs.fetchone()[0]
                    cmd = "insert into week (chaperone_id,partic_type,form_info,document,shirt_size,allergies,paid) values ({},'{}',{},'{}','{}','{}',{})".format(chaperone_id,'Acompanhante',True,document,SIZES[shirt_size],allergies,acomp_type)
                else:
                    cmd = "insert into week (compet_id,partic_type,form_info,document,shirt_size,allergies) values ({},'{}',{},'{}','{}','{}')".format(compet_id,'Competidor',True,document,SIZES[shirt_size],allergies)
            #print(cmd)
            curs.execute(cmd)
            conn.commit()
            #print('insert failed:', cmd, file=sys.stderr)

if __name__ == "__main__":
    main()


