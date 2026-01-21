import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from exams.settings import EXAMS

def compute_points_compets(self,descriptor,level,compet_id):
    compets = Compet.objects.filter(compet_type=level,compet_classif_fase1=True)
    if compet_id != 0:
        compets = compets.filter(compet_id=compet_id)
    ## should first zero points ??
    exam = EXAMS[descriptor]['exam_object']
    results = exam.objects.all()
    total_compets = len(compets)
    seen = 0
    updated = 0
    new = 0
    not_updated = 0
    for c in compets:
        seen += 1
        compet_exam = results.filter(compet_id = c.compet_id)
        if len(compet_exam) != 1:
            continue
        total_points = 0
        if compet_exam[0].num_correct_answers:
            num_correct_answers = eval(compet_exam[0].num_correct_answers)
            for k in num_correct_answers.keys():
                total_points += num_correct_answers[k]
        
            if c.compet_points_fase2==None:
                c.compet_points_fase2 = total_points
                c.save()
                new += 1
                #self.stdout.write(self.style.SUCCESS('******** NEW {} {}'.format(c.compet_id,c.compet_points_fase2)))
            elif c.compet_points_fase2 < total_points:
                c.compet_points_fase2 = total_points
                c.save()
                updated += 1
                self.stdout.write(self.style.SUCCESS('===== UPDATE {} {} < {}'.format(c.compet_id,c.compet_points_fase2,total_points)))
                #self.stdout.write(self.style.SUCCESS('******** UPDATE {} {}'.format(c.compet_id,c.compet_points_fase2)))
            else:
                not_updated += 1
                self.stdout.write(self.style.SUCCESS('===== DO NOT UPDATE {} {} >= {}'.format(c.compet_id,c.compet_points_fase2,total_points)))
                pass

    return total_compets, seen, new, updated,not_updated


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = 'provaf2'
        level = options['level'][0]
        compet_id = options['compet_id'][0]
        level_num = LEVEL[level.upper()]
        total_compets, seen, new, updated,not_updated = compute_points_compets(self,descriptor,level_num,compet_id)
        self.stdout.write(self.style.SUCCESS(f'seen:{seen}, new:{new}, updated:{updated}, not_updated:{not_updated}'))
