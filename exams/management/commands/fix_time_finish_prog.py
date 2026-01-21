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


def fix_time_finish(descriptor,level,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    duration = EXAMS[descriptor]['exam_duration'][level]
    compet_type = LEVEL[level.upper()]
    if compet_id != 0:
        try:
            compet_exam = exam.objects.get(compet_id=compet_id)
        except:
            print('compet not authorized', compet_id)
            return 0
        if not compet_exam.time_start:
            print('not started', compet_id)
            return 0
        compet_exam.time_finish = compet_exam.time_start + timedelta(minutes=duration)
        compet_exam.save()
        count = 1
    else:
        compet_exams = exam.objects.filter(compet__compet_type=compet_type,time_start__isnull=False).order_by('time_start')
        count = 0
        for compet_exam in compet_exams:
            #print(compet.compet_id,descriptor, compet_exam, duration, compet)
            compet_exam.time_finish = compet_exam.time_start + timedelta(minutes=duration)
            compet_exam.save()
            count += 1
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
        if level not in ('pj','p1','p2','ps'):
            self.stdout.write(self.style.SUCCESS('Wrong level: {}.'.format(level)))
            return 0
        fixed = fix_time_finish(descriptor,level,compet_id)
        self.stdout.write(self.style.SUCCESS('Fixed {} exams.'.format(fixed)))
