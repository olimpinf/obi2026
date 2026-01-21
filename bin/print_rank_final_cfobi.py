#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import os
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor

HOST = 'localhost'
#HOST = '10.0.0.16'
year = 2025
DBNAME = f'obi{year}'

trtable={'Á':'á','É':'é','Í':'í','Ó':'ó','Ú':'ú','À':'à','Ç':'ç','Ã':'ã','Õ':'õ','Â':'â','Ê':'ê','Ô':'ô',"'":"´"}

honors=0
gold_medals=[]
silver_medals=[]
bronze_medals=[]
school_medals={}
school_names={}
school_cities={}

def add_medal(school_id,school_name,school_city,compet_id,medal):
    global comm,curs
    if medal in ('o','p','b'):
        if school_id in school_medals.keys():
            school_medals[school_id][medal] += 1
        else:
            school_medals[school_id]={i:0 for i in ['o','p','b']}
            school_medals[school_id][medal] += 1
            school_names[school_id]=school_name
            school_cities[school_id]=school_city
    if do_medals:  # mark the school to generate shipping labels
        #comm = """update school set school_has_medal=true where school_id=%d""" % (school_id)
        #curs.execute(comm)
        comm = """update compet_cfobi set compet_medal='%s' where compet_id=%d""" % (medal,compet_id)
        #print comm
        curs.execute(comm)
        conn.commit()

def usage():
    print('usage: %s [-chs] level file' % sys.argv[0],file=sys.stderr)
    sys.exit(-1)

def compare_columns(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(b[0], a[0]) or cmp(a[1], b[1])

def compare_names(a, b):
    return cmp(a[1], b[1])

def compare(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(a[1], b[1])


def format_compet_id(id):
    try:
        id=int(id)
    except:
        print("bad compet id", id, file=sys.stderr)
        return id
    d1 = id % 10
    d2 = id % 100 / 10
    d3 = id % 1000 / 100
    d4 = id % 10000 / 1000
    d5 = id / 10000
    digit = (3 * d1 + 2 * d2 + 1 * d3 + 2 * d4 + 3 * d5) % 10
    if digit == 0:
        digit = 10
    return "%05d-%c" % (id, digit + 64)

def caps(s):
    #s=s.decode('latin-1').encode('utf-8')
    tks=s.split()
    s=''
    for t in tks:
        t.replace('Á','á')
        t.replace('É','é')
        t.replace('Í','í')
        t.replace('Ó','ó')
        t.replace('Ú','ú')

        t.replace('Â','â')
        t.replace('Ê','ê')
        t.replace('Ô','ô')

        t.replace('Ã','ã')
        t.replace('Õ','õ')

        t.replace('Ç','ç')
        # if t.find('\xc3\x89')>=0:
        #     print >> sys.stderr, 'replacing'
        #     print >> sys.stderr, t
        #     tnew.replace(t,'\xc3\x89','É')
        #     print >> sys.stderr, tnew
        nt=''
        for t1 in t:
            if t1 in trtable.keys(): # does not work :-(
                nt+=trtable[t1]
            else:
                nt+=t1.lower()
        if nt.upper() in ['(FMM)', 'ABC', 'BH', 'CEFET-MG', \
                              'EE', 'EMEF', 'GGE', \
                              'ICMC', 'ICMC/USP', \
                              'IFAL', 'IFBA', 'IFCE', 'IFMT', 'IFPB', 'IFPR', \
                              'IFSP', 'IFTM', 'IFMT','IME-USP', 'ITA', 'SJC', 'UFF', 'UFMG', 'UFPE', \
                              'UFRJ', 'UFRN', 'UFRRJ', 'UFU,', 'USP']:
            s+=' '+nt.upper()
        elif nt in ['de','da','do','e','das','dos']:
            s+=' '+nt
        else:
            s+=' '+nt.capitalize()
    return s.strip()

the_state=''
try:
    opts, args = getopt.getopt(sys.argv[1:], 'chms:u')
except:
    print('error')
    usage()
do_state=False
do_update=False
do_medals=False
html=False
conv=False # convidados curso
for o, a in opts:
    if o == '-h':
        html=True
    elif o == '-c':
        conv=True
    elif o == '-m':
        do_medals=True
    elif o == '-s':
        do_state=True
        the_state=a.upper()
    elif o == '-u':
        do_update=True
    else:
        usage()
try:
    lev=args[0]
    fname=args[1]
except:
    usage()

fout=open(fname,'w')

if lev=='pj':
    level=5
    title = f'Quadro de Medalhas - CF-OBI{year} - Modalidade Programação Nível Júnior'
    titleh = '<h1>Quadro de Medalhas <br/> Competição Feminina - Modalidade Programação Nível Júnior</h1>'
    CUT_GOLD = 300 # 356
    CUT_SILVER = 261 # 323
    CUT_BRONZE = 207 # 312
    CUT_HONORS = 206 # 205
    mod_str = 'Programação'
    level_str = 'Júnior'
    total = 91 # 91 participantes, 695 inscritas

elif lev=='p1':
    level=3
    title = f'Quadro de Medalhas - CF-OBI{year} - Modalidade Programação Nível 1'
    titleh = '<h1>Quadro de Medalhas <br/> Competição Feminina - Modalidade Programação Nível 1</h1>'
    CUT_GOLD = 400 # 262
    CUT_SILVER = 306 # 234
    CUT_BRONZE = 300 # 218
    CUT_HONORS = 300 # 200
    mod_str = 'Programação'
    level_str = '1'
    total = 159 # 159 participantes, 672 inscritas

elif lev=='p2':
    level=4
    title = f'Quadro de Medalhas - CF-OBI{year} - Modalidade Programação Nível 2'
    titleh = '<h1>Quadro de Medalhas <br/> Competição Feminina - Modalidade Programação Nível 2</h1>'
    CUT_GOLD = 407 # 400
    CUT_SILVER = 243 # 287
    CUT_BRONZE = 218 # 207
    CUT_HONORS = 218 # 134
    mod_str = 'Programação'
    level_str = '2'
    total = 164 # 164 participantes, 1262 inscritas

else:
    usage()

# Abre conexao com BD
conn = psycopg2.connect("host=%s dbname=%s  user=obi password=guga.LC" % (HOST,DBNAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

if do_update:
    comm = """update compet_cfobi set compet_rank = NULL where compet_type=%d""" % (level)
    curs.execute(comm)
    conn.commit()

    # order by points then by points_fase3 then by name
comm = """select
C.compet_year, C.compet_birth_date, C.compet_name, C.compet_id, C.compet_id_full,F.compet_points,C.compet_points_fase3, F.compet_rank,
S.school_type, S.school_name,S.school_city,S.school_state,S.school_id from compet as C inner join compet_cfobi as F on C.compet_id = F.compet_id inner join school as S on C.compet_school_id = S.school_id
where F.compet_type=%d and F.compet_points is not null
order by F.compet_points desc, compet_name""" % (level)
curs.execute(comm)
print(comm)
data = curs.fetchall()

print(len(data))
for d in data:
    print(d)

type_school={0:'Erro',1:'Publ',2:'Priv',3:'Publ',4:'Priv',5:'Outra'}

num=0
num_se=0
rank=1
rank_medal=1 # rank_medal uses only phase 3 
points=0

if html:
    print('title: %s' % title, file=fout)
    print('template:flatpages_result.html', file=fout)
    print('\n<!--%s -->' % titleh, file=fout)
    print('''
<p><center>
<img src="/static/img/medalhinha_ouro.gif">=Medalha de Ouro,
<img src="/static/img/medalhinha_prata.gif">=Medalha de Prata,<br>
<img src="/static/img/medalhinha_bronze.gif">=Medalha de Bronze,
HM=Honra ao Merito</p>

<table class="table table-sm table-striped table-bordered">
<thead class="table-primary"> 
<tr>
<td align="center" colspan="2">Classif.</td>
<td align="center">Nota<sup>1</sup}</td>
<td>Nome</td>
<td>Escola</td>
<td>Cidade</td>
<td>Estado</td>
</tr>
</thead>
''', file=fout)

print(lev.upper(), file=sys.stderr)
print('Total participants: ',len(data), file=sys.stderr)
line_type=1

count = 0
for item in data:
    count += 1
    if count % 100 == 0:
        print('.',end="",file=sys.stderr)
        sys.stderr.flush()
    #if count >= len(data)/2:
    #    break
    compet_name = item['compet_name']
    compet_name = caps(compet_name)
    compet_id = item['compet_id']
    compet_id_full = item['compet_id_full']
    school_name = item['school_name']
    school_name = caps(school_name)
    school_city = item['school_city']
    school_type = item['school_type']
    school_id = item['school_id']
    school_state = item['school_state'].strip()
    school_type=type_school[school_type]
    compet_birth_date= item ['compet_birth_date']
    compet_year= item ['compet_year']
    cur_points = item['compet_points']
    #compet_olimp_week= item ['compet_olimp_week']
    compet_olimp_week=None
    #try:
    #    rank_final = int(item['compet_rank_final'])
    #except:
    #    rank_final = -1

    #points_final = float(points1)*500.0/float(NUM_POINTS_PHASE_1)+5.0*float(points2)*500.0/float(NUM_POINTS_PHASE_2)+15.0*float(points3)*500.0/float(NUM_POINTS_PHASE_3) 
    #for SE, comment next two lines
    #if not do_state:
        #if points_final<0:
        #    continue
    #if compet_id in [20539,9452,19388,17501]: # if came last year, cannot come
    #    continue
    #print [points, compet_name,compet_id,school_name,school_city,school_state,points1,points2,school_type,compet_birth_year,school_id]
    #thelist.append([points3,point2,points1,points_final,compet_name,compet_id,school_name,school_city,school_state,school_type,compet_birth_date,compet_year,school_id,rank_final,compet_olimp_week])

    state = school_state

    if cur_points != points:
        rank_medal=num+1
        points = cur_points
    num+=1

    #print('.',end='')
    #print(rank,points3,points2,points1,compet_name,compet_id_full,school_name,school_city,school_state,school_type,compet_birth_date,compet_year,school_id)

    if cur_points >= CUT_GOLD:
        medal='<img src="/static/img/medalhinha_ouro.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'o')
        gold_medals.append(compet_id)
        rank_final = rank_medal
    elif cur_points >= CUT_SILVER:
        medal='<img src="/static/img/medalhinha_prata.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'p')
        silver_medals.append(compet_id)
        rank_final = rank_medal
    elif cur_points >= CUT_BRONZE:
        medal='<img src="/static/img/medalhinha_bronze.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'b')
        bronze_medals.append(compet_id)
        rank_final = rank_medal
    elif cur_points >= CUT_HONORS:
        medal='HM'
        add_medal(school_id,school_name,school_city,compet_id,'h')
        honors+=1
        rank_final = rank_medal
    else:
        medal=''
        rank_final = rank_medal
        if html:
            break
        if not do_update:
            break

    if conv and rank_medal>CUT_GOLD:
        continue

    line_type=1-line_type

    if html:
        if line_type==1:
            print('<tr class="row-light">', file=fout)
        else:
            print('<tr class="row-dark">', file=fout)
        if conv:
            print('<td>%s</td>' % (compet_name), file=fout)
            print('<td>%s</td>' % (school_name), file=fout)
            print('<td>%s</td>' % (school_city), file=fout)
            print('<td>%s</td>' % (school_state), file=fout)
            print('</tr>', file=fout)
        else:
            print('<td>%s</td>' % (medal), file=fout)
            print('<td>%d</td>' % (rank_medal), file=fout)
            print('<td>%d</td>' % (points), file=fout)
            print('<td>%s</td>' % (compet_name), file=fout)
            print('<td>%s</td>' % (school_name), file=fout)
            print('<td>%s</td>' % (school_city), file=fout)
            print('<td>%s</td>' % (school_state), file=fout)
            print('</tr>', file=fout)

    if do_update:
        comm = "update compet_cfobi set compet_rank='%d' where compet_id=%d;" % (rank_final,compet_id)
        #print(comm)
        curs.execute(comm)
        conn.commit()
        # if rank_final==-1:
        #     print("updating %d better rank=%d (before=%d)" % (compet_id, rank, rank_final), file=sys.stderr)
        #     comm = "update compet set compet_rank_final='%d' where compet_id=%d;" % (rank,compet_id)
        #     curs.execute(comm)
        #     conn.commit()
        # elif rank<rank_final:
        #     print("updating %d better rank=%d (before=%d)" % (compet_id, rank, rank_final), file=sys.stderr)
        #     comm = "update compet set compet_rank_final='%d' where compet_id=%d;" % (rank,compet_id)
        #     curs.execute(comm)
        #     conn.commit()
        # elif rank>rank_final:
        #     print("***** updating %d worse rank=%d (is=%d)" % (compet_id, rank, rank_final), file=sys.stderr)
        #     comm = "update compet set compet_rank_final='%d' where compet_id=%d;" % (rank,compet_id)
        #     curs.execute(comm)
        #     conn.commit()

if html:
    print('</table>', file=fout)

for k in school_medals.keys():
    print(",".join([school_names[k], school_cities[k], str(k),lev,str(school_medals[k]['o']),str(school_medals[k]['p']),str(school_medals[k]['b'])]), file=sys.stderr)

conn.close()

print("gold medals", len(gold_medals), file=sys.stderr)
print("silver medals", len(silver_medals), file=sys.stderr)
print("bronze medals", len(bronze_medals), file=sys.stderr)
print("honors", honors, file=sys.stderr)
print("-------", file=sys.stderr)
print("rank_final",rank, file=sys.stderr)
