#!/usr/bin/env python3

import csv
import getopt
import os
import re
import string
import sys

import psycopg2
from psycopg2.extras import DictCursor
from process_particip_week import find_compet_id

HOST = 'localhost'
DB_NAME = 'obi2025'
ARRIVAL_DAY = '2025-11-30'
DEPARTURE_DAY = '2025-12-06'

stamp = 0 # Carimbo de data/hora
email = 1 # email
phone = 2 # phone
name = 3 # Nome
tipo = 4 # Tipo
arrival_place = 5 # Local de chegada 
arrival_time = 6 # Horário de chegada
arrival_airliner = 7 # Companhia Aérea
arrival_flight = 8 # Número do Vôo
arrival_flight_from = 9 # Cidade procedência
arrival_flight_time = 10 # Horário de chegada do vôo
arrival_bus = 11 # Empresa de ônibus
arrival_bus_time = 12 # Horário de chegada do ônibus
arrival_bus_from = 13 # Cidade de procedência do ônibus
departure_place = 14 # Selecione o local de partida
departure_day = 15 # Informe o dia de saída do hotel
departure_airliner = 16 # Empresa aérea
departure_flight = 17 # Número do vôo
departure_time = 18 # Horário de partida do vôo
departure_flight_to = 19 # Cidade destino
departure_bus = 20 # Empresa de ônibus
departure_bus_time = 21 # Horário de partida do ônibus
departure_bus_to = 22 # Cidade destino

def usage():
    print('usage: %s file' % sys.argv[0], file=sys.stderr)
    sys.exit(-1)

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
            #if t1 in trtable.keys(): # does not work :-(
             #   nt+=trtable[t1]
            #else:
            #    nt+=t1.lower()
            nt+=t1.lower()
        if nt.upper() in ['(FMM)', 'ABC', 'BH', 'CEFET-MG', \
                              'EE', 'EMEF', 'GGE', \
                              'ICMC', 'ICMC/USP', \
                              'IFAL', 'IFBA', 'IFCE', 'IFMT', 'IFPB', 'IFPR', \
                              'IFSP', 'IFTM', 'IFMT','IME-USP', 'ITA', 'SJC', 'UFF', 'UFMG', 'UFPE', \
                              'UFRJ', 'UFRN', 'UFRRJ', 'UFU', 'USP']:
            s+=' '+nt.upper()
        elif nt in ['de','da','do','e','das','dos']:
            s+=' '+nt
        else:
            s+=' '+nt.capitalize()
    return s.strip()
    
def compare_columns(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(b[0], a[0]) or cmp(a[1], b[1])

def compare_names(a, b):
    return cmp(a[1], b[1])

def compare(a, b):
    # sort on descending index 0, ascending index 1
    return cmp(a[1], b[1])

def get_id(data, name, curs):
    for d in data:
        if d['compet_id']:
            cmd = "select compet_name from compet where compet_id = {}".format(d['compet_id'])
            curs.execute(cmd);
            compet = curs.fetchone()
            if name.strip().lower()==compet['compet_name'].strip().lower():
                return d['week_id']
        elif d['colab_id']:
            cmd = "select colab_name from colab where colab_id = {}".format(d['colab_id'])
            curs.execute(cmd);
            colab = curs.fetchone()
            if name.strip().lower()==colab['colab_name'].strip().lower():
                return d['week_id']
        elif d['chaperone_id']:
            cmd = "select chaperone_name from chaperone where chaperone_id = {}".format(d['chaperone_id'])
            curs.execute(cmd);
            chaperone = curs.fetchone()
            if name.strip().lower()==chaperone['chaperone_name'].strip().lower():
                return d['week_id']
    print('******** NO ID')
    return -1



local_file = '/tmp/arrivals.csv'

# Abre conexao com BD
conn = psycopg2.connect("host={} dbname={}  user=obi password=guga.LC".format(HOST,DB_NAME))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=DictCursor)


cmd = "update week set departure_time = null, departure_place=null, van_departure_time=null"
curs.execute(cmd)
conn.commit()


cmd = "select * from week"
curs.execute(cmd)
data = curs.fetchall()

#compets_bd = []
#MAX_RANK={1:42,2:36,5:27,3:25,4:22}
#for i in range(1,6):
#    cmd = "select compet_id,compet_name,compet_rank_final from compet where compet_type = {} and compet_rank_final<{}".format(i,MAX_RANK[i])
#    curs.execute(cmd)
#    compets_bd += curs.fetchall()
#    print(len(compets_bd))
cmd = "select compet_id, compet_name,compet_rank_final from compet where compet_id in (select compet_id from week where compet_id is not null)"
curs.execute(cmd)
compets_bd = curs.fetchall()
cmd = "select chaperone_id, chaperone_name from chaperone2 where chaperone_id is not null"
curs.execute(cmd)
chaperones_bd = curs.fetchall()

num_persons = 0
with open(local_file, newline='') as f:
    reader = csv.reader(f, dialect='excel')
    linenum = 0
    partic_type = ''
    for r in reader:
        compet_id = 0
        linenum += 1
        if len(r)==0:
            continue
        if r[0].strip().lower()=='carimbo de data/hora':
            continue
        print("line",linenum,file=sys.stderr)
        if r[tipo] == 'Aluno(a) convidado(a)':
            #print('tipo: convidado', file=sys.stderr)
            compet_id,rank = find_compet_id(r[name],compets_bd)
            #print("compet_id",compet_id,file=sys.stderr)
            if compet_id==0:
                print("No match:", r[name], file = sys.stderr)
                continue
            cmd = "select week_id from week where compet_id={}".format(compet_id)
            curs.execute(cmd)
            week_id = curs.fetchone()[0]
            #print("week_id (conv)",week_id,file=sys.stderr)
        else:
            #print('tipo: chaperone', file=sys.stderr)
            chaperone_id,rank = find_compet_id(r[name],chaperones_bd,conv_type='chaperone')
            #print("chaperone_id",chaperone_id,file=sys.stderr)
            if chaperone_id==0:
                print("No match:", r[name], file = sys.stderr)
                continue
            cmd = "select week_id from week where chaperone_id={}".format(chaperone_id)
            curs.execute(cmd)
            week_id = curs.fetchone()[0]
            #print("week_id (other)",week_id,file=sys.stderr)
            # arrivals
        #print("Convidado",file=sys.stderr)
        cmd = "select tax_value from week where week_id={}".format(week_id)
        curs.execute(cmd)
        tax_value = curs.fetchone()[0]
        num_persons += 1
        #print("tax_value",tax_value,file=sys.stderr)
        if not tax_value:
            if compet_id != 0:
                print("*****************")
                print(f"no tax!, compet_id = {compet_id}", file=sys.stderr)
                print("*****************")
            else:
                cmd = "select paying from week where chaperone_id={}".format(chaperone_id)
                curs.execute(cmd)
                paying = curs.fetchone()[0]
                if paying:
                    print("*****************")
                    print(f"no tax!, chaperone_id = {chaperone_id}, {paying}", file=sys.stderr)
                    print("*****************")
            #sys.exit(-1)
        arr_place = 'Não informado'
        arr_from = 'Não informado'
        arr_time = 'Não informado'
        arr_info = 'Não informado'
        if r[arrival_place]=='Diretamente no hotel':
                arr_place = 'Hotel'
                arr_time = r[arrival_time]
                arr_info = '-'
        elif r[arrival_place]=='Aeroporto de Viracopos':
                arr_place = 'Aeroporto'
                arr_time = r[arrival_flight_time]
                num = r[arrival_flight]
                num = re.sub('G3', '', num)
                num = re.sub(' ', '', num)
                num = re.sub('-', '', num)
                num = re.sub('[a-zA-Z]', '', num)
                try:
                    num = int(num)
                except:
                    num = '?'
                    
                if r[arrival_airliner].strip().lower() == 'azul':
                    airliner = 'AD'
                elif r[arrival_airliner].strip().lower() == 'latam':
                    airliner = 'LA'
                elif r[arrival_airliner].strip().lower() == 'gol':
                    airliner = 'G3'
                arr_info = "{} {}".format(airliner,num)
                if arr_info == 'AD 4669':
                    arr_time='16:10'
                elif arr_info == 'AD 4034':
                    arr_time='05:15'
                elif arr_info == 'AD 4508':
                    arr_time='11:45'
                arr_from = r[arrival_flight_from]
                pos = arr_from.find('-')
                if pos > 0:
                    arr_from = arr_from[:pos]
                arr_from = arr_from.strip()
                arr_from = caps(arr_from)
                #print(arr_info,arr_time,arr_from)
        elif r[arrival_place].find('Rodoviária')==0:
                arr_place = 'Rodoviária'
                arr_time = r[arrival_bus_time]
                arr_info = r[arrival_bus].strip().split()[0]
                arr_from = r[arrival_bus_from]
                pos = arr_from.find('-')
                if pos > 0:
                    arr_from = arr_from[:pos]
                arr_from = arr_from.strip()
                arr_from = caps(arr_from)
                #print(arr_info,arr_time,arr_from)
        cmd = f"update week set arrival_time='{ARRIVAL_DAY} {arr_time} -03', arrival_place='{arr_place}', arrival_info='{arr_info}', arrival_from='{arr_from}' where week_id={week_id}"
        curs.execute(cmd)
        conn.commit()

        # departures
        dep_time = ''
        dep_to = 'Não informado'
        dep_place = 'Não informado'
        if r[departure_place].find('Diretamente')==0:
                dep_place = 'Hotel'
                dep_time = '' #r[departure_time]
                if r[departure_day].find('noite')>0:
                    dep_info = 'sexta à noite'
                else:
                    dep_info = 'sábado de manhã'
        elif r[departure_place].find('Aeroporto')==0:
                dep_place = 'Aeroporto'
                dep_time = r[departure_time]
                num = r[departure_flight]
                num = re.sub('G3', '', num)
                num = re.sub(' ', '', num)
                num = re.sub('-', '', num)
                num = re.sub('[a-zA-Z]', '', num)
                try:
                    num = int(num)
                except:
                    num = '?'
                if r[departure_airliner].strip().lower() == 'azul':
                    airliner = 'AD'
                elif r[departure_airliner].strip().lower() == 'latam':
                    airliner = 'LA'
                elif r[departure_airliner].strip().lower() == 'gol':
                    airliner = 'G3'
                dep_info = "{} {}".format(airliner,num)
                dep_to = r[departure_flight_to]
                pos = dep_to.find('-')
                if pos > 0:
                    dep_to = dep_to[:pos]
                dep_to = dep_to.strip()
                dep_to = caps(dep_to)
        elif r[departure_place].find('Rodoviária')==0:
                dep_place = 'Rodoviária'
                dep_time = r[departure_bus_time]
                dep_info = r[departure_bus].strip().split()[0]
                dep_to = r[departure_bus_to]
                pos = dep_to.find('-')
                if pos > 0:
                    dep_to = dep_to[:pos]
                dep_to = dep_to.strip()
                dep_to = caps(dep_to)
        cmd = "update week set departure_time='{} {} -03', departure_place='{}', departure_info='{}', departure_to='{}' where week_id={}".format(DEPARTURE_DAY,dep_time,dep_place,dep_info,dep_to,week_id)
        curs.execute(cmd)
        conn.commit()
        cmd = "update week set form_arrival=True  where week_id={}".format(week_id)
        curs.execute(cmd)
        conn.commit()

cmd = "update week set van_arrival_time=null"
curs.execute(cmd)
conn.commit()

cmd = "update week set van_departure_time=null"
curs.execute(cmd)
conn.commit()

# Transporte chegada, mais tarde primeiro
#############
# aeroporto

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 22:00:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 21:30:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 19:10:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 18:30:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 17:30:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 16:30:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 14:00:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 13:15:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 12:30:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 11:45:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 10:40:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 10:00:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 09:40:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 09:00:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 08:10:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 07:35:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 06:00:00-03' where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '{ARRIVAL_DAY} 05:15:00-03'"
curs.execute(cmd)
conn.commit()


#############
# rodoviária
cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 19:30:00-03' where arrival_time is not null and arrival_place='Rodoviária' and arrival_time <= '{ARRIVAL_DAY} 19:10:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_arrival_time='{ARRIVAL_DAY} 11:30:00-03' where arrival_time is not null and arrival_place='Rodoviária' and arrival_time <= '{ARRIVAL_DAY} 11:00:00-03'"
curs.execute(cmd)
conn.commit()

# to reset
#cmd = "update week set van_arrival_time=NULL where arrival_time is not null and arrival_place='Aeroporto' and arrival_time <= '2024-12-01 21:00:00#-03'"
#curs.execute(cmd)
#conn.commit()


# Transporte partida, mais tarde primeiro

#############
# aeroporto


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 20:25:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 23:30:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 17:40:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 21:20:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 15:25:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 18:10:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 12:00:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 15:45:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 11:05:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 13:25:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()

cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 07:40:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 11:40:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 05:40:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 09:35:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 03:40:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 06:30:00-03'"
curs.execute(cmd)
print(cmd)
conn.commit()

cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 01:20:00-03' where departure_time is not null and departure_place='Aeroporto' and departure_time <= '{DEPARTURE_DAY} 03:40:00-03'"
print(cmd)
curs.execute(cmd)
conn.commit()



#############
# rodoviária

cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 16:30:00-03' where departure_time is not null and departure_place='Rodoviária' and departure_time <= '{DEPARTURE_DAY} 18:00:00-03'"
curs.execute(cmd)
conn.commit()

cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 10:30:00-03' where departure_time is not null and departure_place='Rodoviária' and departure_time <= '{DEPARTURE_DAY} 12:00:00-03'"
curs.execute(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 09:00:00-03' where departure_time is not null and departure_place='Rodoviária' and departure_time <= '{DEPARTURE_DAY} 10:45:00-03'"
curs.execute(cmd)
conn.commit()


cmd = f"update week set van_departure_time='{DEPARTURE_DAY} 07:45:00-03' where departure_time is not null and departure_place='Rodoviária' and departure_time <= '{DEPARTURE_DAY} 09:15:00-03'"
curs.execute(cmd)
conn.commit()


print("num_persons", num_persons)
