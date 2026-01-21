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
from exams.views import _task_score_max_subtask

from cms.models import LocalSubmissionResults

def compute_points_compets(self,descriptor,level,school_id,compet_id):
    if compet_id != 0:
        compets = Compet.objects.filter(compet_type=level,compet_id=compet_id,compet_school_id=school_id,compet_classif_fase1=True)
    elif school_id != 0:
        compets = Compet.objects.filter(compet_type=level,compet_school_id=school_id,compet_classif_fase1=True).order_by('compet_id')
    else:
        compets = Compet.objects.filter(compet_type=level,compet_classif_fase1=True).order_by('compet_id')

    ## should first zero points ??
    #results_table = EXAMS[descriptor]['exam_table_results_judge']
    #results = results_table.objects.all().using('corretor')

    exam_contest_id = EXAMS[descriptor]['exam_contest_id']
    partic_table = EXAMS[descriptor]['exam_object'] # to define participation
    print("partic_table", partic_table)
    print("contest_id", exam_contest_id)
    partic = partic_table.objects.filter(time_start__isnull=False)
    tot = len(compets)
    seen = 0
    new = 0
    updated_to_smaller = 0
    updated_to_greater = 0
    print('len(compets)',len(compets))
    print('len(partic)',len(partic))
    for c in compets:
        try:
            partic_subm = partic.get(compet_id = c.compet_id)
        except:
            continue

        seen += 1
        points = 0
        seen_problems = []
        #compet_subm = results.filter(team_id = c.compet_id)

        local_submission_results = LocalSubmissionResults.objects.filter(compet_id=c.compet_id,compet_type=c.compet_type,contest_id=exam_contest_id).order_by("-submission_id")
        scores = {}
        task_titles = {}
        for s in local_submission_results:
            task = s.local_subm.task_name
            if task in scores.keys():
                scores[task].append((s.public_score,s.public_score_details,False))
            else:
                scores[task] = [(s.public_score,s.public_score_details,False)]
                task_titles[task] = s.local_subm.task_title
        total_points = 0
        for task in scores.keys():
            total_points += _task_score_max_subtask(scores[task])
        total_points = int(total_points)

        if c.compet_points_fase2b==None:
            c.compet_points_fase2b = total_points
            c.save()
            new += 1
            #self.stdout.write(self.style.SUCCESS('******** NEW {} {}'.format(c.compet_id,c.compet_points_fase2b)))
        elif c.compet_points_fase2b < total_points:
            self.stdout.write(self.style.SUCCESS('******** UPDATE to greater {} {} --> {}'.format(c.compet_id,c.compet_points_fase2b,total_points)))
            c.compet_points_fase2b = total_points
            c.save()
            updated_to_greater += 1
        elif c.compet_points_fase2b > total_points:
            self.stdout.write(self.style.SUCCESS('===== UPDATE to smaller {} {} --> {}'.format(c.compet_id,c.compet_points_fase2b,total_points)))
            c.compet_points_fase2b = total_points
            c.save()
            updated_to_smaller += 1
            
    return tot, seen

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = 'provaf2b'
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        school_id = int(options['school_id'][0])
        compet_id = int(options['compet_id'][0])
        total_compets, seen_compets = compute_points_compets(self,descriptor,level_num,school_id,compet_id)
        self.stdout.write(self.style.SUCCESS('Compets seen = {} (total = {}).'.format(seen_compets, total_compets)))
