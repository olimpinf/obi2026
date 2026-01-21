import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from fase1.views import compute_classif_one_school
from exams.settings import EXAMS

def compute_points_compets(self,descriptor,level,compet_id):
    compets = Compet.objects.filter(compet_type=level)
    if compet_id != 0:
        compets = compets.filter(compet_id=compet_id)
    ## should first zero points ??
    exam = EXAMS[descriptor]['exam_object']
    results = exam.objects.all()
    tot = len(compets)
    seen = 0
    for c in compets:
        compet_exam = results.filter(compet_id = c.compet_id)
        if len(compet_exam) != 1:
            continue
        seen += 1
        # check turn
        # try:
        #     s = School.objects.get(school_id=c.compet_school_id,school_turn_phase1_ini='B')
        # except:
        #     print("############################## wrong turn")
        #     print(c.compet_id,c.compet_name,c.compet_school_id)
        #     continue
        #self.stdout.write(self.style.SUCCESS('    {} {}'.format(s.school_name,s.school_turn_phase1_ini)))
        # valid only first time
        #if c.compet_points_fase1:
        #    # competed in Turn A?
        #    self.stdout.write(self.style.SUCCESS('TURN A {} {}'.format(c.compet_id,c.compet_points_fase1)))
        #    continue
        
        total_points = 0
        if compet_exam[0].num_correct_answers:
            num_correct_answers = eval(compet_exam[0].num_correct_answers)
            for k in num_correct_answers.keys():
                total_points += num_correct_answers[k]
        
            if c.compet_points_fase1==None:
                c.compet_points_fase1 = total_points
                c.save()
                self.stdout.write(self.style.SUCCESS('******** NEW {} {}'.format(c.compet_id,c.compet_points_fase1)))
            elif c.compet_points_fase1 < total_points:
                self.stdout.write(self.style.SUCCESS('******** UPDATE {} {} -> {}'.format(c.compet_id,c.compet_points_fase1, total_points)))
                c.compet_points_fase1 = total_points
                c.save()
            #else:
            #    self.stdout.write(self.style.SUCCESS('{} {}'.format(c.compet_id,c.compet_points_fase1)))
    return tot, seen

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        level = options['level'][0]
        compet_id = options['compet_id'][0]
        level_num = LEVEL[level.upper()]
        total_compets, seen_compets = compute_points_compets(self,descriptor,level_num,compet_id)
        self.stdout.write(self.style.SUCCESS('Compets seen = {} (total = {}).'.format(seen_compets, total_compets)))
