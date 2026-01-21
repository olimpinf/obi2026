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

def close_compet_exam(descriptor, exam, duration, compet):
    #print(descriptor,exam,duration,compet)
    if exam and exam.time_start and not exam.time_finish:
        now = make_aware(datetime.now())
        if now - exam.time_start > timedelta(minutes=duration+30):
            print('\nclosing', exam.compet_id)
            print('start:',exam.time_start)
            print('gap:',now - exam.time_start)
            exam.time_finish = now
            exam.save()
            mark_exam(descriptor,compet)
            return 1

    # not started
    return 0


def close_exams(descriptor,level,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    duration = EXAMS[descriptor]['exam_duration'][level]
    compet_type = LEVEL[level.upper()]
    if compet_id != 0:
        try:
            compet_exam = exam.objects.get(compet_id=compet_id)
        except:
            print('compet not authorized', compet_id)
            return 0
        if compet_exam.time_finish:
            print('already closed', compet_id, compet_exam.id, compet_exam.time_start, compet_exam.time_finish)
            return 0
        if not compet_exam.time_start:
            print('not started', compet_id)
            return 0
        compet = Compet.objects.get(compet_id=compet_id,compet_type=compet_type)
        count = close_compet_exam(descriptor, compet_exam, duration, compet)
    else:
        compet_exams = exam.objects.filter(compet__compet_type=compet_type,time_start__isnull=False,time_finish__isnull=True).order_by('time_start')
        count = 0
        print('open exams:',len(compet_exams))
        for compet_exam in compet_exams:
            compet = Compet.objects.get(compet_id=compet_exam.compet_id,compet_type=compet_type)
            #print(compet.compet_id,descriptor, compet_exam, duration, compet)
            res = close_compet_exam(descriptor,compet_exam, duration, compet)
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
        closed = close_exams(descriptor,level,compet_id)
        self.stdout.write(self.style.SUCCESS('Closed {} exams.'.format(closed)))
