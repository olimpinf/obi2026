import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.utils.utils import calc_log_and_points, check_answers_file

from obi.settings import BASE_DIR
from principal.models import LEVEL, Compet, School, ResIni, IJ, I1, I2
from exams.settings import EXAMS

def compute_points_compets(self,descriptor,level,compet_id):
    compets = Compet.objects.filter(compet_type=level,compet_classif_fase2=True)
    if compet_id != 0:
        compets = compets.filter(compet_id=compet_id,compet_type=level,compet_classif_fase2=True)
    ## should first zero points ??
    # if compet_id != 0:
    #     results = ResIni.objects.filter(compet_id=compet_id,answers_fase3__isnull=False)
    # else:
    #     results = ResIni.objects.filter(answers_fase3__isnull=False)

    print("len(compets)",len(compets))

    if level == IJ:
        gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3ij.txt')
    elif level == I1:
        gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i1_50.txt')
        num_questions = 50
    elif level == I2:
        num_questions = 60
        gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i2_60.txt')
    else:
        print("bad level")
        return

    errors,numquestions,gab = check_answers_file(gab_file_name)
    print("errors",errors)
    print("gab",gab)
    total_compets = len(compets)
    seen = 0
    updated_to_smaller = 0
    updated_to_greater = 0
    new = 0
    not_updated = 0
    print('total_compets',total_compets)
    for c in compets:
        seen += 1
        try:
            res_ini = ResIni.objects.get(compet_id=c.compet_id)
            answers = eval(res_ini.answers_fase3)
        except:
            continue

        if c.compet_type == 7:
            continue
        if (c.compet_type == 1 and len(answers) == 40):
            continue
        if (c.compet_type == 2 and len(answers) == 50):
            continue
        points, log = calc_log_and_points(gab, answers, show_correct=True)
        if c.compet_points_fase3==None:
            self.stdout.write(self.style.SUCCESS('******** NEW ??? did not insert {} {} --> {}'.format(c.compet_id,c.compet_points_fase3,points)))
            c.compet_points_fase3 = points
            #c.save()
            new += 1
        elif c.compet_points_fase3 < points:
            self.stdout.write(self.style.SUCCESS('===== UPDATE to greater {} {} --> {}'.format(c.compet_id,c.compet_points_fase3,points)))
            c.compet_points_fase3 = points
            c.save()
            updated_to_greater += 1
        elif c.compet_points_fase3 > points:
            #self.stdout.write(self.style.SUCCESS('******** DO NOT UPDATE to smaller {} {} < {}'.format(c.compet_id,points,c.compet_points_fase3)))
            self.stdout.write(self.style.SUCCESS('******** UPDATE to smaller {} {} <-- {}'.format(c.compet_id,points,c.compet_points_fase3)))
            c.compet_points_fase3 = points
            c.save()
            updated_to_smaller += 1
        else:
            self.stdout.write(self.style.SUCCESS('******** SAME {} {} = {}'.format(c.compet_id,points,c.compet_points_fase3)))
            

    return total_compets, seen, new, updated_to_greater,updated_to_smaller,not_updated


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = 'provaf3'
        level = options['level'][0]
        compet_id = options['compet_id'][0]
        level_num = LEVEL[level.upper()]
        total_compets, seen, new, updated_to_greater,updated_to_smaller,not_updated = compute_points_compets(self,descriptor,level_num,compet_id)
        self.stdout.write(self.style.SUCCESS(f'seen:{seen}, new:{new}, updated_to_greater:{updated_to_greater}, updated to smaller:{updated_to_smaller}, not_updated:{not_updated}'))
