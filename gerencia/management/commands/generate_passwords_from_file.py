import csv
import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.contrib.auth.models import Group, User

from principal.models import LEVEL, LEVEL_NAME, Compet, School
#from fase2.utils.check_solutions_file import Error, check_solutions_file
from principal.utils.check_compet_points_batch import check_compet_points_batch
from principal.utils.utils import format_compet_id, csv_sniffer, make_password

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line

def format_line(l, delimiter):
    return '{}'.format(delimiter).join(l)

def validate_compets(f,school_id):
    msg = ''
    errors = []
    seen_compets=set()
    validated_compets=[]

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
                return msg,errors,validated_compets

    # delimiter = None
    # try:
    #     sample = csvf.read()
    # except:
    #     msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1 (também conhecido como ISO-8859).'
    #     return msg,errors,validated_compets
    
    # print(sample)
    # delimiter = csv_sniffer(sample,[3])
    # print('delimiter',delimiter)
    # try:
    #     delimiter = csv_sniffer(sample,[3])
    # except:
    #     msg = 'Problema no formato ou decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1 (também conhecido como ISO-8859).'
    #     return msg,errors,validated_compets
    
    # #delimiter = dialect.delimiter
    # #print('delimiter',delimiter)
    # if not delimiter:
    #     #######
    #     # maybe implement a warning msg variable
    #     #msg = 'Problema no formato do arquivo. Não foi possível determinar qual o caractere separador utilizado. Normalmente o caractere separador do formato CVS é a vírgula, mas também são aceitos ponto-e-vírgula e TAB. Esse erro pode ocorrer quando as linhas do arquivo têm número diferentes de colunas (indicadas pelo caractere separador). Por favor verifique seu arquivo. Estamo usando vírgula como separador, pode não ser o correto e nesse caso outros erros ocorrerão'
    #     print('could not find delimiter, using ;')
    #     delimiter = ';'
        
    # csvf.seek(0)
    delimiter = ';'
    reader = csv.reader(csvf)
    linenum=0
    school_compets = Compet.objects.filter(compet_school_id=school_id)
    for r in reader:
        linenum += 1
        if len(r)==0:
            continue
        elif len(r)!=2:
            errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
            continue
        if r[0].strip().lower()=='num. inscr.':
            continue
        ok_row=True
        msg_row=''
        try:
            username=r[1].strip()
        except:
            errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
            continue
        if not username:
            errors.append(Error(linenum,'falta nome de usuário',format_line(r, delimiter)))
            continue
        try:
            compet_id_full=r[0].strip()
        except:
            errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
            continue
        compet_id = compet_id_full[:-2]
        try:
            compet_id = int(compet_id)
        except:
            errors.append(Error(linenum,'número de inscrição no formato errado',format_line(r, delimiter)))
            continue
        if format_compet_id(compet_id) != compet_id_full:
            errors.append(Error(linenum,'número de inscrição errado',format_line(r, delimiter)))
            continue

        try:
            c = Compet.objects.get(pk=compet_id,compet_school_id=school_id)
        except:
            errors.append(Error(linenum,'número de inscrição não corresponde a competidor da escola',format_line(r, delimiter)))
            continue
        if compet_id in seen_compets:
            errors.append(Error(linenum,'número de inscrição repetido neste arquivo',format_line(r, delimiter)))
        else:
            compet = school_compets.get(compet_id=compet_id)
            seen_compets.add(compet_id)
            validated_compets.append((c,username))

    csvf.close()
    return msg, errors, validated_compets

def build_passwords(archive,school_id):
    msg,errors,compets = validate_compets(archive, school_id)
    if msg or errors:
        for e in errors:
            print(f'linha {e.linenum}: {e.msg}')
            return
    built = []
    count = 0
    for compet, username in compets:
        password = make_password()
        try:
            user = User.objects.get(username=username.lower())
            user.set_password(password)
            #print('user exists, lowercase')
        except:
            try:
                user = User.objects.get(username=username.upper())
                user.set_password(password)
                #print('user exists, uppercase')
            except:
                user = User.objects.create_user(username, username, password)
                user.last_name = compet.compet_name
                user.email = compet.compet_email
        user.is_staff = False
        g = Group.objects.get(name='compet')
        g.user_set.add(user)
        try:
            user.save()
            pass
        except:
            logger.info('duplicate user.id: {}'.format(user.id))
            print('duplicate user.id: {}'.format(user.id))
            return
        compet.user = user
        compet.save()
        print(f"{format_compet_id(compet.compet_id)},{username},{password}")        
        count += 1
    return count

class Command(BaseCommand):
    help = 'Upload points, init compets'

    def add_arguments(self, parser):
        parser.add_argument('archive', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        archive = options['archive'][0]
        school_id = options['school_id'][0]
        count = build_passwords(archive,school_id)
