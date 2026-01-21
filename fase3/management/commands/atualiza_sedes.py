import csv
import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.contrib.auth.models import Group, User
from django.core.management import call_command

from principal.models import IJ, I1, I2, PJ, P1, P2, PS, LEVEL, LEVEL_NAME, Compet, School
#from fase2.utils.check_solutions_file import Error, check_solutions_file

def le_csv(f):
    msg = ''

    try:
        csvf = open(f,"r", encoding='utf-8')
    except:
        try:
            csvf = open(f,"r", encoding='iso8859-1')
            #print('iso8859-1')
        except:
            try:
                csvf = open(f,"r", encoding='macroman')
                #print('mac os roman')
            except:
                msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                print('ERRO', msg)
                return None

    delimiter = ','
    reader = csv.reader(csvf)
    linenum=0
    schools = []
    for r in reader:
        linenum += 1
        if len(r)==0:
            continue
        if r[0].strip().lower()=='school_city':
            continue

        OK=r[5].strip() == 'TRUE'
        if not OK:
            school_city=r[0].strip()
            school_state=r[1].strip()
            print(school_city,school_state,'NOT OK')
            continue

        try:
            city=r[0].strip()
            state=r[1].strip()
            site_id=int(r[2].strip())
        except:
            print(linenum,'formato incorreto')
            continue

        if site_id <= 0:
            print(city,state,'NOT DEFINED')
            continue

        schools.append[(city,state,site_id)]

    csvf.close()

    return schools

def update_sedes_csv(f, mod):
    for city, state, site_id in le_csv(f):
        call_command('atualiza_sede', mod, city, state, site_id)

class Command(BaseCommand):
    help = 'Change school_site_phase3_ini or school_site_phase3_prog for all CSV sites'

    def add_arguments(self, parser):
        parser.add_argument('file', nargs='+', type=str)
        parser.add_argument('mod', nargs='+', type=str) # 'ini' or 'prog'

    def handle(self, *args, **options):
        file = options['file'][0]
        mod = options['mod'][0]
        update_sedes_csv(file, mod)
        self.stdout.write(self.style.SUCCESS('Update Sites CSV Done'))
