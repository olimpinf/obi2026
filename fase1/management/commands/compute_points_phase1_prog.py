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
from cms.models import LocalSubmissionResults

def compute_points_compets(self,descriptor,level,school_id,compet_id):
    if compet_id != 0:
        compets = Compet.objects.filter(compet_type=level,compet_id=compet_id,compet_school_id=school_id)
    elif school_id != 0:
        compets = Compet.objects.filter(compet_type=level,compet_school_id=school_id).order_by('compet_id')
    else:
        compets = Compet.objects.filter(compet_type=level).order_by('compet_id')
    ## should first zero points ??
    #results_table = EXAMS[descriptor]['exam_table_results_judge']
    #results = results_table.objects.all().using('corretor')

    exam_contest_id = EXAMS[descriptor]['exam_contest_id']
    partic_table = EXAMS[descriptor]['exam_object'] # to define participation
    partic = partic_table.objects.filter(time_start__isnull=False)
    tot = len(compets)
    seen = 0
    print('len(compets)',len(compets))
    print('len(partic)',len(partic))
    for c in compets:
        try:
            partic_subm = partic.get(compet_id = c.compet_id)
        except:
            #print("no partic", c.compet_id)
            continue

        exam_contest_id = 1
        seen += 1
        points = 0
        seen_problems = []
        #compet_subm = results.filter(team_id = c.compet_id)

        compet_results = LocalSubmissionResults.objects.filter(compet_id=c.compet_id,compet_type=c.compet_type,contest_id=exam_contest_id).order_by("-submission_id")
        scores = {}
        for s in compet_results:
            task = s.local_subm.task_name
            if task in scores.keys():
                if s.public_score:
                    scores[task] = max(s.public_score, scores[task])
            else:
                if s.public_score:
                    scores[task] = s.public_score
                else:
                    scores[task] = 0
        points = 0
        for k in scores:
            points += int(scores[k])
        
        if c.compet_points_fase1==None:
            self.stdout.write(self.style.SUCCESS('NEW {} {} -> {}'.format(c.compet_id,c.compet_points_fase1, points)))
            c.compet_points_fase1 = points
            #c.save()
        elif c.compet_points_fase1==points:
            #self.stdout.write(self.style.SUCCESS('SAME {} {} -> {}'.format(c.compet_id,c.compet_points_fase1, points)))
            continue
        elif c.compet_points_fase1 < points:
            self.stdout.write(self.style.SUCCESS('UPDATE {} {} -> {}'.format(c.compet_id,c.compet_points_fase1,points)))
            c.compet_points_fase1 = points
            #c.save()
        else:
            self.stdout.write(self.style.ERROR('{} {} > {}'.format(c.compet_id,c.compet_points_fase1,points)))
            
    return tot, seen

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        level = options['level'][0]
        descriptor = options['descriptor'][0]
        level_num = LEVEL[level.upper()]
        school_id = int(options['school_id'][0])
        compet_id = int(options['compet_id'][0])
        self.stdout.write(self.style.SUCCESS(f'Computing points for {descriptor} level_num={level_num}, school_id={school_id}, compet_id={compet_id}.'))
        total_compets, seen_compets = compute_points_compets(self,descriptor,level_num,school_id,compet_id)
        self.stdout.write(self.style.SUCCESS('Compets seen = {} (total = {}).'.format(seen_compets, total_compets)))
