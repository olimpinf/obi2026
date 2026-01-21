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

def desclassif_compet(compet, school_id, reason, phase):
    c = CompetDesclassif()
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
    c.user_id =                      compet.user.id
    c.desclassif_phase  =            phase
    c.desclassif_reason =            reason
    c.save()

    user = compet.user
    compet.delete()
         
    if CompetCfObi.objects.filter(compet=compet.compet_id).exists():
        cf = CompetCfObi.objects.get(compet=compet.compet_id)
        c.compet_type_cf = cf.compet_type
        c.compet_points_cf = cf.compet_points
        c.compet_rank_cf = cf.compet_rank
        c.compet_medal_cf = cf.compet_medal
        c.compet_classif_cf = cf.compet_classif
        print(f'eliminating CF',file=sys.stderr)
        logger.info(f'eliminating CF')
        c.save()
        cf.delete()

    user.is_active = False
    user.save()
    
def desclassif_compets(filename):

    PHASE = {
        'fase-1': "Fase 1",
        'fase-2': "Fase 2",
        'fase-2b': "Fase 2 Turno B",
        'fase-3': "Fase 3",
        'fase-cf': "Competição Feminina",
    }
    with open(filename,"r") as f:
        lines = f.readlines()

    schools_compets = {}
    compet_ids = set()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0] == '#':
            continue
        tks = line.split(",")
        compet_id = tks[0].strip()
        if not compet_id:
            continue
        if compet_id.lower() == 'compet_id':
            continue

        compet_id_full = compet_id
        

        try:
            school_id = tks[1].strip()
            school_id = int(school_id)
        except:
            school_id = 0

        try:
            reason = tks[2].strip()
        except:
            reason = ""

        try:
            phase = tks[3].strip()
        except:
            phase = ""
            
        compet_ids.add((compet_id_full,school_id,reason,phase))

    count = 0
    failed = 0
    already_eliminated = 0
    all_seen = len(compet_ids)
    
    for compet_id_full,school_id,reason,phase in compet_ids:
        if Compet.objects.filter(compet_id_full=compet_id_full).exists():
            #print(compet_id_full)
            c = Compet.objects.get(compet_id_full=compet_id_full)
            check_school_id = c.compet_school.pk
            if check_school_id != school_id:
                print(f'failed, wrong school, {compet_id_full}, {c.compet_school.pk} {school_id}',file=sys.stderr)
                logger.info(f'failed, wrong school, {compet_id_full}, {c.compet_school.pk} {school_id}')
                failed += 1
                continue
            if school_id in schools_compets.keys():
                schools_compets[school_id].append((c.compet_id_full,c.compet_name,reason,phase))
            else:
                schools_compets[school_id] = [(c.compet_id_full,c.compet_name,reason,phase)]
            print(f'eliminating compet: {compet_id_full}, phase: {phase}, reason: {reason}',file=sys.stderr)
            logger.info(f'eliminating compet: {compet_id_full}, phase: {phase}, reason: {reason}')
            desclassif_compet(c,school_id,reason,phase)
            count += 1
        elif CompetDesclassif.objects.filter(compet_id_full=compet_id_full).exists():
            c = CompetDesclassif.objects.get(compet_id_full=compet_id_full)
            #print(f'already eliminated',file=sys.stderr)
            #logger.info(f'already eliminated')
            already_eliminated += 1
        else:
            print(f'failed! not in compet or compet_desclassif',file=sys.stderr)
            logger.info(f'failed!, not in compet or compet_desclassif')
            failed += 1
        

    fname = os.path.basename(filename)
    with open(f"school_{fname}","w") as f:
        for s in schools_compets.keys():
            # use ";" for separating compets and "," to separate submissions
            print(s,";".join([str(i) for i in schools_compets[s]]),sep=";", file=f)
        
    return all_seen, count, already_eliminated, failed

class Command(BaseCommand):
    help = 'Desclassif compets'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        #parser.add_argument('contestname', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        #contestname = options['contestname'][0]
        all_seen, count,already_eliminated,failed = desclassif_compets(filename)
        self.stderr.write(self.style.SUCCESS(f'{all_seen} compets in file, desclassif {count}, already_eliminated {already_eliminated}, failed: {failed}'))
