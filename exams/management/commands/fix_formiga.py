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

def fix_compet_exam(exam_descriptor, exam, compet):
    if compet.compet_type == 3:
        problem_name = 'provaf2p1_formiga'
        problem_name_new = 'provaf2p1_formiga2'
    elif compet.compet_type == 4:
        problem_name = 'provaf2p2_formiga'
        problem_name_new = 'provaf2p2_formiga2'
    elif compet.compet_type == 6:
        problem_name = 'provaf2ps_formiga'
        problem_name_new = 'provaf2ps_formiga2'
    else:
        print('bad compet type',compet,compet.compet_type)
        return 0
    
    sub = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(team_id=compet.compet_id,problem_name=problem_name).using(EXAMS[exam_descriptor]['exam_db'])
    if len(sub) == 0:
        print('compet',compet, 'no submission', problem_name)
        return 0
    if len(sub) != 1:
        print('compet',compet, 'more than one submission', problem_name)
        return 0
    sub = sub[0]
    print("Copying submission, {}, compet {}, level {}, {}, {}".format(exam_descriptor,compet.compet_id,compet.compet_type, sub.sub_id, sub.problem_name))

    # when re-marking, remove previous accepted solution
    try:
        old = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(problem_name=problem_name_new,team_id=compet.compet_id).using(EXAMS[exam_descriptor]['exam_db'])
        if len(old) == 1:
            print('found old submission, removing')
            old[0].delete()
    except:
        pass
    s = EXAMS[exam_descriptor]['exam_table_submissions_judge']()
    s.pk = 10000+sub.pk
    s.sub_id = 10000+sub.sub_id
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
    print('saved',s.problem_name,s.sub_id,'using',EXAMS[exam_descriptor]['exam_db'])
    return 1

def fix_exams(descriptor,level,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    compet_type = LEVEL[level.upper()]
    if compet_id != 0:
        compet = Compet.objects.get(compet_id=compet_id,compet_type=compet_type)
    else:
        print('compet_type',compet_type)
        compet_exams = exam.objects.filter(compet__compet_type=compet_type,time_start__isnull=False).order_by('time_start')
        count = 0
        print('descriptor',descriptor)
        print('len compet_exams',len(compet_exams))
        for compet_exam in compet_exams:
            compet = Compet.objects.get(compet_id=compet_exam.compet_id,compet_type=compet_type)
            print(compet.compet_id)
            res = fix_compet_exam(descriptor,compet_exam, compet)
            count += res
    return count

class Command(BaseCommand):
    help = 'Insert or update one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        level = options['level'][0]
        compet_id = options['compet_id'][0]
        fixed = fix_exams(descriptor,level,compet_id)
        self.stdout.write(self.style.SUCCESS('Fixed {} exams.'.format(fixed)))
