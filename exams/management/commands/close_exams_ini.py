import getopt
import os
import re
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware, timezone

from principal.models import LEVEL, Compet, IJ, I1, I2, LEVEL_NAME
from exams.models import Alternative, Question, Task
from exams.views import check_exam_finished
from exams.settings import EXAMS

def check_and_close_compet_exam(exam_descriptor, exam, duration, compet):
    print(exam_descriptor,exam,duration,compet)
    try:
        compet_exam = exam.objects.get(compet_id=compet.compet_id)
    except:
        print('compet not authorized', compet.compet_id)
        return 0
    if compet_exam.time_finish:
        print('already closed', compet.compet_id, compet_exam.id, compet_exam.time_start, compet_exam.time_finish)
        return 0
    if compet_exam.time_start:
        print('checking', compet.compet_id, end=' ')
        finished,status,msg = check_exam_finished(exam_descriptor, compet_exam, compet)
        print(finished, status, msg)
        if finished:
            return 1
    return 0


def close_exams(descriptor,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    if compet_id != 0:
        compet = Compet.objects.get(compet_id=compet_id,compet_type__in=(IJ,I1,I2))
        level_name = LEVEL_NAME[compet.compet_type].lower()
        duration = EXAMS[descriptor]['exam_duration'][level_name]
        res = check_and_close_compet_exam(descriptor, exam, duration, compet)
        return res
    else:
        compet_exams = exam.objects.filter(compet__compet_type__in=(IJ,I1,I2),time_start__isnull=False,time_finish__isnull=True).order_by('time_start')
        count = 0
        print('open exams:',len(compet_exams))
        for compet_exam in compet_exams:
            compet = Compet.objects.get(compet_id=compet_exam.compet_id,compet_type__in=(IJ,I1,I2))
            #print(compet.compet_id,descriptor, compet_exam, duration, compet)
            level_name = LEVEL_NAME[compet.compet_type].lower()
            duration = EXAMS[descriptor]['exam_duration'][level_name]
            res = check_and_close_compet_exam(descriptor, exam, duration, compet)
            count += res
    return count

class Command(BaseCommand):
    help = 'Insert or update one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        compet_id = options['compet_id'][0]
        closed = close_exams(descriptor,compet_id)
        self.stdout.write(self.style.SUCCESS('Closed {} exams.'.format(closed)))
