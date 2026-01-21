import logging
import os
import sys
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL, PJ, P1, P2, PS,  CompetCfObi
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year, make_password,
                                   verify_compet_id,
                                   format_compet_id,)

from principal.models import PasswordCms

logger = logging.getLogger(__name__)

def generate_password(compet):
    # generate only if not present
    try:
        p = PasswordCms.objects.get(compet=compet)
        return 1,0
    except:
        p = PasswordCms()
        password = make_password(separator='.')
        p.compet = compet
        p.password = password
        p.save()
        return 0,1
    return 0,0

def generate_passwords(compets):
    print("generate_passwords")
    count_old,count_new = 0,0
    for compet in compets:
        res_old,res_new = generate_password(compet)
        count_old += res_old
        count_new += res_new
    return count_old,count_new
    
    
class Command(BaseCommand):
    help = 'Generate cms passwords'

    def add_arguments(self, parser):
        parser.add_argument('contest', nargs='+', type=str)
        parser.add_argument('compet', nargs='+', type=int)

    def handle(self, *args, **options):
        contest = options['contest'][0]
        compet_id = options['compet'][0]
        if contest == 'provaf1':
            compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
        elif contest == 'provaf2':
            compets = Compet.objects.filter(compet_type__in=(3,4,5,6), compet_classif_fase1=True)
        elif contest == 'provaf3':
            compets = Compet.objects.filter(compet_type__in=(3,4,5,6), compet_classif_fase2=True)
        elif contest == 'cfobi':
            competsCF = CompetCfObi.objects.all().only('compet_id')
            print(len(competsCF))
            compets_set = set()
            for competCF in competsCF:
                compets_set.add(competCF.compet_id)
            compets = Compet.objects.filter(compet_id__in=compets_set)                
        if compet_id > 0:
            compets = compets.filter(compet_id=compet_id)
        elif compet_id == -1:
            # reset passwords
            resp = input('delete all cms passwords? [yN]')
            if resp == 'y':
                PasswordCms.objects.all().delete()
                print("deleted")
            else:
                print('not deleted')
            sys.exit(0)
            #for p in PasswordCms.objects.all().delete():
            #    p.delete()
            

        count = len(compets)
        count_old,count_new = generate_passwords(compets)
        self.stdout.write(self.style.SUCCESS(f'Generated/updated {count_new}, maintained {count_old} cms passwords.'))
