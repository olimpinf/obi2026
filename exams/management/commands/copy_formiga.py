import getopt
import os
import re
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware, timezone

from principal.models import LEVEL, Compet
from exams.models import Alternative, Question, Task
from exams.views import mark_exam
from exams.settings import EXAMS

def fix_compet(exam_descriptor, problem_name, compet):
    problem_name_new = problem_name + '2'
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    exam_db = EXAMS[exam_descriptor]['exam_db']
    results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id,num_correct_tests=1,problem_name=problem_name).only('sub_id').order_by('problem_name','-sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    accepted = []
    for r in results:
        accepted.append(r.sub_id)
    submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(sub_id__in=accepted).order_by('problem_name','-sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    seen = set()
    for sub in submissions:
        if sub.problem_name not in seen:
            print("Copying submission, compet {}, {}, {}".format(compet.compet_id,sub.sub_id, sub.problem_name))
            seen.add(sub.problem_name)
            # when re-marking, remove previous accepted solution
            try:
                old = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(problem_name=problem_name_new,team_id=compet.compet_id).using(EXAMS[exam_descriptor]['exam_db'])
                if len(old) == 1:
                    print('found old submission of {}, removing'.format(problem_name_new))
                    old[0].delete()
            except:
                pass
            s = EXAMS[exam_descriptor]['exam_table_submissions_judge']()
            s.pk = sub.pk + 10000
            s.sub_id = sub.sub_id + 10000
            s.sub_lang = sub.sub_lang
            s.sub_source = sub.sub_source
            s.team_id = sub.team_id
            s.sub_file = sub.sub_file
            s.sub_time = sub.sub_time
            s.problem_name = problem_name_new
            s.problem_name_full = sub.problem_name_full
            s.sub_lock = 0
            s.sub_marked = 0
            s.save(using=(EXAMS[exam_descriptor]['exam_db']))
            print('s',s,s.sub_id)
            print('saved',s.problem_name,s.sub_id,'using',EXAMS[exam_descriptor]['exam_db'])
    return 1
        

def fix_compets(descriptor,level,problem_name,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    compet_type = LEVEL[level.upper()]
    if compet_id != 0:
        compet = Compet.objects.get(compet_id=compet_id,compet_type=compet_type)
        res = fix_compet(descriptor,problem_name, compet)
        count = res
    else:
        compet_exams = exam.objects.filter(compet__compet_type=compet_type,time_start__isnull=False).order_by('time_start')
        count = 0
        for compet_exam in compet_exams:
            compet = Compet.objects.get(compet_id=compet_exam.compet_id,compet_type=compet_type)
            res = fix_compet(descriptor, problem_name, compet)
            count += res
        
    return count

class Command(BaseCommand):
    help = 'Insert or update one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('problem_name', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        level = options['level'][0]
        problem_name = options['problem_name'][0]
        compet_id = options['compet_id'][0]
        marked = fix_compets(descriptor,level,problem_name,compet_id)
        self.stdout.write(self.style.SUCCESS('Re-marked {} exams.'.format(marked)))
