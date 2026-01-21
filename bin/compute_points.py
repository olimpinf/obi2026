#!/usr/bin/env python3

import getopt
import os
import re
import sys
from datetime import datetime
from time import localtime, strftime, time

from psycopg2 import psycopg1

from answer_sheet_utils import check_answers_file

YEAR = 2025
HOST = 'localhost'
HOST = '143.106.73.36'
PHASE = 1

LEVEL_INT = {'I1': 1, 'I2':2, 'IJ':7}
LEVEL_STR = {1: 'I1', 2: 'I2', 7:'IJ'}
alternative={'A':0,'B':1,'C':2,'D':3,'E':4}
alt_inverted={0:'A',1:'B',2:'C',3:'D',4:'E'}


def update_compet(compet_id,phase,level,points,log,conn):
    cursor = conn.cursor()
    comm = "update compet set compet_points_fase{}={} where compet_id={} and compet_type={}".format(phase,points,compet_id, level)    
    cursor.execute(comm)

    comm = "select result from res_fase{} where compet_id={}".format(phase,compet_id)
    cursor.execute(comm)
    data = cursor.dictfetchone()
    if data:
        result_id = data['result']
        comm = "update res_fase{} set result_log='{}' where result={}".format(phase,log,result_id)
        cursor.execute(comm)
    else:
        now = datetime.now()
        comm = "insert into res_fase{} (result_log,result_result,num_total_tests,num_correct_tests,problem_name,res_time,compet_id,sub_id) values ('{}',0,0,0,'tarefa_ini',TIMESTAMP '{}',{},1)".format(phase,log,now,compet_id)
        cursor.execute(comm)
    conn.commit()
        
def usage():
    print('usage: %s [-c compet_id] [-l level] [-r]' % sys.argv[0])
    sys.exit(-1)

def check_compet_id_obi(id):
    d1 = id % 10
    d2 = id % 100 / 10
    d3 = id % 1000 / 100
    d4 = id % 10000 / 1000
    d5 = id / 10000
    digit = (3 * d1 + 2 * d2 + 1 * d3 + 2 * d4 + 3 * d5) % 10
    if digit == 0:
        digit = 10
    return "%c" % (digit + 64)

def check_compet_id(id):
    sum=1
    tmp=id
    while tmp>0:
        sum+=tmp%10
        tmp/=10
    digit=sum%10
    return "%c" % (digit + 65)

def calc_points(gab, answer):
    points = 0
    log=''
    if len(answer)!=len(gab):
        log='ERRO: número de respostas é diferente do número de questões'
        print("number of answers does not match number of questions",file=sys.stderr)
        return points, log
    for i in range(len(gab)):
        log=log+"%d. " % (i+1)
        if i<9 and len(gab)>=10: log+=' '
        accept=gab[i]
        if accept[0]=='-':
            log=log+"Questão anulada"
        elif answer[i]=='X':
            log=log+"Resposta inválida"
        else:
            log=log+"%s" % (answer[i])
        if len(accept)==1: # only one answer possible
            if ((accept[0]=='*') or (answer[i]==accept[0])):
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                # se quiser mostrar os errados...
                #log=log+" (errada)"
                #all_answers[i]['X'] += 1
                log=log+"\n"
        else: # list of correct answers
            if answer[i] in accept:
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                log=log+"\n"
    return points,log

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'c:l:r')
    except getopt.error as err:
        print("OS error: {0}".format(err),file=sys.stderr)
        usage()
    compet_id = ''
    level = ''
    for o, a in opts:
        if o == '-c':
            compet_id = a
        if o == '-l':
            level = LEVEL_INT[a.upper()]

    if not level and not compet_id:
        usage()
    conn = psycopg1.connect("host={} dbname=obi{} user=obi password=guga.LC".format(HOST,YEAR))
    cursor = conn.cursor()

    if compet_id:
        comm = "select * from compet where compet_id={} and compet_classif_fase2".format(compet_id)
        cursor.execute(comm)
        data = cursor.dictfetchone()
        try:
            level = data['compet_type']
        except:
            print('could not find compet {}'.format(compet_id),file=sys.stderr)
            sys.exit(-1)
        if not data['compet_classif_fase2']:
            print('compet {} is not classified'.format(compet_id),file=sys.stderr)
            sys.exit(-1)
        if not data['compet_answers_fase3']:
            print('compet {} does not have answers'.format(compet_id),file=sys.stderr)
            sys.exit(-1)
        exec("answers = "+data['compet_answers_fase3'], globals())
        gab_file_name = os.path.join("protected_files", "gab_f1{}.txt".format(LEVEL_STR[level].lower()))
        errors,numquestions,gab = check_answers_file(gab_file_name)
        if errors:
            print(errors,file=sys.stderr)
            sys.exit(-1)
        points,log = calc_points(gab,answers)
        update_compet(compet_id,PHASE,level,points,log,conn)

    else:
        gab_file_name = os.path.join("protected_files", "gab_f1{}.txt".format(LEVEL_STR[level].lower()))
        errors,numquestions,gab = check_answers_file(gab_file_name)
        if errors:
            print(errors,file=sys.stderr)
            sys.exit(-1)
        comm = "select * from compet where compet_type={} and compet_classif_fase2".format(level)
        cursor.execute(comm)
        data = cursor.dictfetchone()
        ok,not_ok = 0,0
        while data:
            if data['compet_answers_fase1']:
                ok += 1
                exec("answers = "+data['compet_answers_fase1'], globals())
                points,log = calc_points(gab,answers)
                update_compet(data['compet_id'],PHASE,level,points,log,conn)
            else:
                not_ok += 1
            data = cursor.dictfetchone()
        print(ok,not_ok)
        
if __name__=="__main__":
    main()
