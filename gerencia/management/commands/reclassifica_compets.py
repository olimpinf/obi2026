import sys
import logging
import os

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetCfObi, LEVEL_NAME, CompetDesclassif, PasswordCms
#from cfobi.models import CompetCfObi
from exams.models import TesteFase1
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger('obi')

def reclassif_compet(compet):
    school_id = compet.compet_school_id
    c = Compet()
    c.compet_id =                    compet.compet_id
    c.compet_name =                  compet.compet_name
    c.compet_id_full = 		     compet.compet_id_full
    c.compet_birth_date = 	     compet.compet_birth_date
    c.compet_school_id =	     school_id
    c.compet_type = 		     compet.compet_type            
    c.compet_sex = 		     compet.compet_sex
    c.compet_email = 		     compet.compet_email
    c.compet_year = 		     compet.compet_year
    c.compet_class = 		     compet.compet_class
				                                
    c.compet_points_fase1 = 	     compet.compet_points_fase1
    c.compet_points_fase2 = 	     compet.compet_points_fase2
    c.compet_points_fase3 = 	     compet.compet_points_fase3
    c.compet_points_fase2b = 	     compet.compet_points_fase2b
    c.compet_points_final = 	     compet.compet_points_final
    c.compet_answers_fase1 = 	     compet.compet_answers_fase1
    c.compet_answers_fase2 = 	     compet.compet_answers_fase2
    c.compet_answers_fase3 = 	     compet.compet_answers_fase3
    c.compet_rank_final = 	     compet.compet_rank_final
    c.compet_medal = 		     compet.compet_medal
    c.compet_classif_fase1 = 	     compet.compet_classif_fase1
    c.compet_classif_fase2 = 	     compet.compet_classif_fase2
    c.compet_classif_fase3 = 	     compet.compet_classif_fase3
    c.compet_classif_fase2a = 	     compet.compet_classif_fase2a
    c.compet_classif_fase2b = 	     compet.compet_classif_fase2b
    c.compet_school_id_fase3 = 	     compet.compet_school_id_fase3
    c.compet_conf =            	     compet.compet_conf

    
    try:
        u = User .objects.get(username=c.compet_id_full)
        print("found user", u.username, u.password)
        u.is_active = True
        u.save
    except:
        print("creating new user")
        u = User(username=c.compet_id_full,first_name=c.compet_name,password=c.compet_conf)
        u.save()

    c.user = u
    c.save()
    compet.delete()
    
    if compet.compet_type_cf:
        cf = CompetCfObi()
        cf.compet_type = compet.compet_type_cf
        cf.compet_points = compet.compet_points_cf
        cf.compet_rank = compet.compet_rank_cf
        cf.compet_medal = compet.compet_medal_cf
        cf.compet_classif = compet.compet_classif_cf
        print(f'restoring CF',file=sys.stderr)
        logger.info(f'restoring CF')
        cf.save()

    
def reclassif_compets(filename):


    print("using", filename, file=sys.stderr)
    compet_ids = set()
    if filename == 'all':
        compets = CompetDesclassif.objects.all()
        for c in compets:
            compet_ids.add(c.compet_id_full)
    else:
        with open(filename,"r") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            tks = line.split(",")
            tmp = tks[0].strip()
            if not tmp:
                continue
            if tmp.lower() == 'compet_id':
                continue
            
            compet_id_full = tmp
            school_id = int(tks[1].strip())
            compet_ids.add((compet_id_full,school_id))
            
    count = 0
    failed = 0

    for compet_id_full,school_id in compet_ids:
        print(f'restoring compet: {compet_id_full}',file=sys.stderr)
        logger.info(f'restoring compet: {compet_id_full}')
        try:
            c = CompetDesclassif.objects.get(compet_id_full=compet_id_full, compet_school_id=school_id)
            reclassif_compet(c)
            count += 1
        except:
           print(f'failed, already restored?',file=sys.stderr)
           logger.info(f'failed, already restored?')
           failed += 1
        
    return count, failed

class Command(BaseCommand):
    help = 'Desclassif compets'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        count,failed = reclassif_compets(filename)
        self.stderr.write(self.style.SUCCESS(f'reclassif {count} compets, failed: {failed}'))
