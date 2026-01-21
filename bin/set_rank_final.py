#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import getopt
import os
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor

# medal_cuts.py must be linked to principal/utils/medal_cuts.py
from medal_cuts import medal_cuts

HOST = 'localhost'
#HOST = '10.0.0.16'
DBNAME = 'obi2021'
year = 2021

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
    if school_id in school_medals.keys():
        school_medals[school_id][medal] += 1
    else:
        school_medals[school_id]={i:0 for i in ['o','p','b']}
        school_medals[school_id][medal] += 1
        school_names[school_id]=school_name
        school_cities[school_id]=school_city
    if do_medals:  # mark the school to generate shipping labels
        comm = """update school set school_has_medal=true where school_id=%d""" % (school_id)
        curs.execute(comm)
        comm = """update compet set compet_medal='%s' where compet_id=%d""" % (medal,compet_id)
        #print comm
        curs.execute(comm)
        conn.commit()

def usage():
    print('usage: %s [-chsu] level file' % sys.argv[0],file=sys.stderr)
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
                              'UFRJ', 'UFRN', 'UFRRJ', 'USP']:
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

if lev=='ij':
    level=7
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Iniciação Nível Júnior'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Iniciação Nível Júnior</h1>'

elif lev=='i1':
    level=1
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Iniciação Nível 1'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Iniciação Nível 1</h1>'

elif lev=='i2':
    level=2
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Iniciação Nível 2'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Iniciação Nível 2</h1>'

elif lev=='pj':
    level=5
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Programação Nível Júnior'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Programação Nível Júnior</h1>'

elif lev=='p1':
    level=3
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Programação Nível 1'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Programação Nível 1</h1>'

elif lev=='p2':
    level=4
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Programação Nível 2'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Programação Nível 2</h1>'

elif lev=='pu' or lev=='ps':
    level=6
    title = f'Quadro de Medalhas - OBI{year} - Modalidade Programação Nível Sênior'
    titleh = '<h1>Quadro de Medalhas <br/> Modalidade Programação Nível Sênior</h1>'
else:
    usage()

NUM_POINTS_PHASE_1,NUM_POINTS_PHASE_2,NUM_POINTS_PHASE_3,CUT_GOLD,CUT_SILVER,CUT_BRONZE,CUT_HONORS,mod_str,level_str,total=medal_cuts(level,year,True)

# Abre conexao com BD
conn = psycopg2.connect("host=%s dbname=%s  user=obi password=guga.LC" % (HOST,DBNAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)

if do_update:
    if the_state:
        comm = """update compet set compet_rank_state = NULL where compet_type=%d and compet_school_id in (select school_id from school where school_state ilike '%s')""" % (level,the_state) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase1=-1 where compet_points_fase1 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase2=-1 where compet_points_fase2 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase3=-1 where compet_points_fase3 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
    else:
        comm = """update compet set compet_rank_final = -1 where compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase1=-1 where compet_points_fase1 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase2=-1 where compet_points_fase2 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        comm = """update compet set compet_points_fase3=-1 where compet_points_fase3 is NULL and compet_type=%d""" % (level) 
        curs.execute(comm)
        conn.commit()
        
    curs.execute(comm)
    conn.commit()

if html:
    # order by points3, points2, points1 then by name 
    comm = """select 
C.compet_year, C.compet_birth_date, C.compet_name, C.compet_id, C.compet_id_full,C.compet_points_fase1, C.compet_points_fase2, C.compet_points_fase3,C.compet_rank_final, S.school_type, S.school_name,S.school_city,S.school_state,S.school_id from compet as C, school as S 
where C.compet_type=%d and C.compet_school_id=S.school_id and compet_points_fase3 is not null
order by compet_points_fase3 desc,compet_name,compet_points_fase2 desc,compet_points_fase1 desc""" % (level)
else:
    # order by points3, points2, points1 then by name
    if the_state:
        comm = """select 
C.compet_year, C.compet_birth_date, C.compet_name, C.compet_id, C.compet_id_full, C.compet_points_fase1, C.compet_points_fase2, C.compet_points_fase3,C.compet_rank_final, S.school_type, S.school_name,S.school_city,S.school_state,S.school_id from compet as C, school as S 
where C.compet_type=%d and C.compet_school_id=S.school_id and S.school_state='%s'  and compet_points_fase1 is not null
order by compet_points_fase3 desc,compet_points_fase2 desc,compet_points_fase1 desc,compet_name""" % (level,the_state)
    else:
        comm = """select 
C.compet_year, C.compet_birth_date, C.compet_name, C.compet_id, C.compet_id_full, C.compet_points_fase1, C.compet_points_fase2, C.compet_points_fase3,C.compet_rank_final, S.school_type, S.school_name,S.school_city,S.school_state,S.school_id from compet as C, school as S 
where C.compet_type=%d and C.compet_school_id=S.school_id  and compet_points_fase3 is not null
order by compet_points_fase3 desc,compet_points_fase2 desc,compet_points_fase1 desc,compet_name""" % (level)

# and compet_points_fase3 is not null
# and compet_points_fase3>0 and compet_points_fase2>=0 and compet_points_fase1>0 

curs.execute(comm)
data = curs.fetchall()

type_school={0:'Erro',1:'Publ',2:'Priv',3:'Publ',4:'Priv',5:'Outra'}

num=0
num_se=0
rank=1
rank_medal=1 # rank_medal uses only phase 3 
rank_st=1
cur_points1=0
cur_points2=0
cur_points3=0
cur_points_se=0


print('title: %s' % title, file=fout)
print('template:flatpages_result.html', file=fout)
print('\n<!--%s -->' % titleh, file=fout)
print('''
<p><center>
<img src="/static/img/medalhinha_ouro.gif">=Medalha de Ouro,
<img src="/static/img/medalhinha_prata.gif">=Medalha de Prata,<br>
<img src="/static/img/medalhinha_bronze.gif">=Medalha de Bronze,
HM=Honra ao Merito</p>

<table class="simple">
<tr class="row-header">
<td align="center" colspan="2">Classif.</td>
<td align="center">Nota<sup>1</sup}</td>
<td>Nome</td>
<td>Escola</td>
<td>Cidade</td>
<td>Estado</td>
</tr>
''', file=fout)

print(lev.upper(), file=sys.stderr)
print('Total participants: ',len(data), file=sys.stderr)
line_type=1

for item in data:
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
    #compet_olimp_week= item ['compet_olimp_week']
    compet_olimp_week=None
    points1 = item['compet_points_fase1']
    points2 = item['compet_points_fase2']
    points3 = item['compet_points_fase3']
    if not points1:
        points1 = 0
    if not points2:
        points2 = 0
    if not points2:
        points2 = 0
    if not points3:
        points3 = 0
    #try:
    #    rank_final = int(item['compet_rank_final'])
    #except:
    #    rank_final = -1

    print(compet_id_full)

    #points_final = float(points1)*500.0/float(NUM_POINTS_PHASE_1)+5.0*float(points2)*500.0/float(NUM_POINTS_PHASE_2)+15.0*float(points3)*500.0/float(NUM_POINTS_PHASE_3) 
    if points1:
        nota_fase1 = round(500.0*points1/float(NUM_POINTS_PHASE_1))
    else:
        nota_fase1 = 0
    if points2:
        nota_fase2 = round(500.0*points2/float(NUM_POINTS_PHASE_2))
    else:
        nota_fase2 = 0
    if points3:
        nota_fase3 = round(500.0*points3/float(NUM_POINTS_PHASE_3))
    else:
        nota_fase3 = 0
    #for SE, comment next two lines
    #if not do_state:
        #if points_final<0:
        #    continue
    #if compet_id in [20539,9452,19388,17501]: # if came last year, cannot come
    #    continue
    #print [points, compet_name,compet_id,school_name,school_city,school_state,points1,points2,school_type,compet_birth_year,school_id]
    #thelist.append([points3,point2,points1,points_final,compet_name,compet_id,school_name,school_city,school_state,school_type,compet_birth_date,compet_year,school_id,rank_final,compet_olimp_week])

    state = school_state

    # rank for medalists is different, use only cur_points_3
    if cur_points3!=points3:
        rank_medal=num+1
        #print(f'new rank_medal={rank_medal}')
    if cur_points1!=points1 or cur_points2!=points2 or cur_points3!=points3:
        cur_points1,cur_points2,cur_points3=points1,points2,points3
        rank=num+1
        #print(f'new rank={rank}')
    num+=1

    #print(rank,points3,points2,points1,compet_name,compet_id_full,school_name,school_city,school_state,school_type,compet_birth_date,compet_year,school_id)

    if rank_medal<=CUT_GOLD:
        #print(compet_id,'gold',rank_medal,points3)
        medal='<img src="/static/img/medalhinha_ouro.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'o')
        gold_medals.append(compet_id)
        rank_final = rank_medal
    elif rank_medal<=CUT_SILVER:
        #print('silver')
        medal='<img src="/static/img/medalhinha_prata.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'p')
        silver_medals.append(compet_id)
        rank_final = rank_medal
    elif rank_medal<=CUT_BRONZE:
        #print('bronze')
        medal='<img src="/static/img/medalhinha_bronze.gif">'
        add_medal(school_id,school_name,school_city,compet_id,'b')
        bronze_medals.append(compet_id)
        rank_final = rank_medal
    elif rank_medal<=CUT_HONORS:
        medal='HM'
        honors+=1
        rank_final = rank_medal
    else:
        medal=''
        rank_final = rank
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
            print('<td>%d</td>' % nota_fase3, file=fout) #(points1,points2,points3)
            print('<td>%s</td>' % (compet_name), file=fout)
            print('<td>%s</td>' % (school_name), file=fout)
            print('<td>%s</td>' % (school_city), file=fout)
            print('<td>%s</td>' % (school_state), file=fout)
            print('</tr>', file=fout)

    if do_update:
        if the_state:
            print(f'do_update, compet={compet_id, }rank={rank}, rank_medal={rank_medal}')
            comm = "update compet set compet_rank_state='%d' where compet_id=%d;" % (rank_final,compet_id)
        else:
            comm = "update compet set compet_rank_final='%d' where compet_id=%d;" % (rank_final,compet_id)
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
    print('''</center><p>1. Observação: 
conforme o <a href="/info/regulamento">Regulamento</a>, a classificação final é determinada
pela pontuação da Fase 3.
Em caso de empate, a classificação é decidida pela pontuação da Fase 2. Persistindo
o empate, a classificação é decidida pela pontuação da Fase 1.
A Nota mostrada é equivalente à pontuação obtida
na Fase 3 (a Nota é simplesmente a pontuação normalizada para o valor máximo de 500 pontos, para permitir
comparação com anos anteriores).''', file=fout)

for k in school_medals.keys():
    print(",".join([school_names[k], school_cities[k], str(k),lev,str(school_medals[k]['o']),str(school_medals[k]['p']),str(school_medals[k]['b'])]), file=sys.stderr)

conn.close()

print("gold medals", len(gold_medals), file=sys.stderr)
print("silver medals", len(silver_medals), file=sys.stderr)
print("bronze medals", len(bronze_medals), file=sys.stderr)
print("honors", honors, file=sys.stderr)
print("-------", file=sys.stderr)
print("rank_final",rank, file=sys.stderr)
