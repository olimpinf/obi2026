import csv
import getopt
import os
import re
import sys
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.contrib.auth.models import Group, User

from principal.models import LEVEL, LEVEL_NAME, Compet, School, Colab, CertifHash, CompetCfObi
from obi.settings import YEAR
#from fase2.utils.check_solutions_file import Error, check_solutions_file
from principal.utils.check_compet_points_batch import check_compet_points_batch
from principal.utils.utils import format_compet_id, csv_sniffer, make_password

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line


def error(s):
    print('error: {}'.format(s), file=sys.stderr)
    sys.exit(-1)

def insert_certif_hash_compet(year, compet_id):
    '''Inserts compet hash in db '''


    if compet_id != 0:
        compets = Compet.objects.filter(compet_id=compet_id)
    else:
        compets = Compet.objects.filter(compet_points_fase1__gte=0)

    print("len(compets)",len(compets))

    count_new, count_update, count_maintain = 0,0,0
    for compet in compets:
        compet_id = compet.compet_id
        compet_name = compet.compet_name
        compet_year = compet.compet_year
        tmp = '{}{}{}'.format(compet_id,compet_name,compet_year)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        compet_hash = f"{year}:{hash}"
        try:
            certif_hash = CertifHash.objects.get(compet_id=compet_id)
            if compet_hash != certif_hash.hash:
                print("error in old certif for compet", compet_id)
                print('new',compet_hash)
                print('old',certif_hash.hash)
                print()
                print(f"updating to {compet_hash}")
                certif_hash.hash = f"{compet_hash}"
                certif_hash.save()
                count_update += 1
            else:
                count_maintain += 1
        except:
            certif_hash = CertifHash(compet_id=compet_id,hash=f'{compet_hash}')
            #certif_hash.save()
            count_new += 1

    return count_new, count_update, count_maintain

def insert_certif_hash_compet_cf(year, compet_id):
    '''Inserts compet hash in db '''


    if compet_id != 0:
        compets = CompetCfObi.objects.filter(compet_id=compet_id)
    else:
        compets = CompetCfObi.objects.all()

    count_new, count_update, count_maintain = 0, 0, 0
    for compet in compets:
        print('compet', compet.id, compet.compet_id)
        compet_name = compet.compet.compet_name
        compet_year = compet.compet.compet_year
        tmp = 'CF{}{}{}'.format(compet.compet_id,compet_name,compet_year)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        compet_hash = f"{year}:{hash}"

        try:
            certif_hash = CertifHash.objects.get(compet_cf__id=compet.id)
            if compet_hash != certif_hash.hash:
                print("error in old certif")
                print('new',compet_hash)
                print('old',certif_hash.hash)
                print()
                print(f"updating to {compet_hash}")
                certif_hash.hash = f"{compet_hash}"
                #certif_hash.save()
                count_update += 1
            else:
                count_maintain += 1
                
        except:
            certif_hash = CertifHash(compet_cf_id=compet.id,hash=f'{compet_hash}')
            #certif_hash.save()
            count_new += 1

    return count_new, count_update, count_maintain

def insert_certif_hash_colab(year, colab_id):
    '''Inserts colab hash in db '''

    #comm = "select distinct colab_school_id from colab"
    if colab_id != 0:
        colabs = Colab.objects.filter(colab_id=colab_id)
    else:
        colabs = Colab.objects.all()

    count_new, count_update, count_maintain = 0, 0, 0
    for colab in colabs:
        colab_id = colab.colab_id
        colab_name = colab.colab_name
        colab_email = colab.colab_email

        tmp = '{}{}{}'.format(colab_id,colab_name,colab_email)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        colab_hash = f"{year}:{hash}"
        try:
            certif_hash = CertifHash(colab_id=colab_id)
        except:
            certif_hash = CertifHash(colab_id=colab_id, hash=f"{colab_hash}")
            #certif_hash.save()
            count_new += 1
    return count, count_update, count_maintain

def insert_certif_hash_coord(year, school_id):
    '''Inserts school hash in db '''

    #comm = "select distinct deleg_school_id from deleg"
    if school_id != 0:
        schools = School.objects.filter(colab_id=colab_id)
    else:
        schools = School.objects.all()

    count_new, count_update, count_maintain = 0, 0, 0
    for school in schools:
        school_id = school.school_id
        deleg_name = school.school_deleg_name
        deleg_email = school.school_deleg_email

        tmp = '{}{}{}'.format(school_id,deleg_name,deleg_email)
        hash = hashlib.sha224(tmp.encode('utf-8')).hexdigest()[:24]
        coord_hash = f"{year}:{hash}"
        try:
            certif_hash = CertifHash(school_id=school_id)
            #certif_hash.save()
            count_update += 1
        except:
            certif_hash = CertifHash(school_id=school_id,hash=coord_hash)
            #certif_hash.save()
            count_new += 1
            pass
    return count, count_update, count_maintain

class Command(BaseCommand):
    help = 'Insert hash for certificates'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('partic', nargs='+', type=str)
        parser.add_argument('id', nargs='+', type=int)

    def handle(self, *args, **options):
        year = options['year'][0]
        partic = options['partic'][0]
        id = options['id'][0]

        count = 0
        if partic == 'compet_cf':
            print("insert cf")
            count_new, count_update, count_maintain = insert_certif_hash_compet_cf(year,id)
            self.stderr.write(self.style.SUCCESS(f'Generated {count_new}, updated {count_update} maintained {count_maintain} for competCF'))
        elif partic == 'compet':
            count_new, count_update, count_maintain = insert_certif_hash_compet(year,id)
            self.stderr.write(self.style.SUCCESS(f'Generated {count_new}, updated {count_update} maintained {count_maintain} for compets'))
        elif partic == 'colab':
            count_new, count_update, count_maintain = insert_certif_hash_colab(year,id)
            self.stderr.write(self.style.SUCCESS(f'Generated {count_new}, updated {count_update} maintained {count_maintain} for colabs'))
        elif partic == 'coord':
            count_new, count_update, count_maintain = insert_certif_hash_coord(year,id)
            self.stderr.write(self.style.SUCCESS(f'Generated {count_new}, updated {count_update} maintained {count_maintain} for coords'))
        else:
            self.stderr.write(self.style.FAILURE(f'bad arguments'))
            
