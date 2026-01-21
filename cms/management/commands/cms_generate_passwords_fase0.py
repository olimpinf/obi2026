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
        if p.password.find('.') > 0:
            print("fix old",compet.compet_id)
            p.password = compet.compet_conf
            p.save()
            return 0,1
        elif p.password != compet.compet_conf:
            print("fix diff",compet.compet_id)
            # user reset password
            p.password = compet.compet_conf
            print("fix",compet.compet_id)
            p.save()
            return 0,1
            
        return 1,0
    except:
        p = PasswordCms()
        p.compet = compet
        p.password = compet.compet_conf
        try:
            p.save()
            return 0,1
        except:
            print("could not save, compet",compet.compet_id)
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
        parser.add_argument('compet', nargs='+', type=int)

    def handle(self, *args, **options):
        compet_id = options['compet'][0]
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6))

        if compet_id > 0:
            compets = compets.filter(compet_id=compet_id)
        elif compet_id == -1:
            # reset passwords
            PasswordCms.objects.all().delete()
            #for p in PasswordCms.objects.all().delete():
            #    p.delete()
            self.stdout.write(self.style.SUCCESS(f'reset {len(compets)} cms passwords.'))
            sys.exit(0)
            

        count = len(compets)
        count_old,count_new = generate_passwords(compets)
        self.stdout.write(self.style.SUCCESS(f'Generated/updated {count_new}, maintained {count_old} cms passwords.'))
