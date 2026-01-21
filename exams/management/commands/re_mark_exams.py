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
from exams.views import mark_exam, re_mark_exam
from exams.settings import EXAMS



def re_mark_exams(descriptor,level,compet_id):
    exam = EXAMS[descriptor]['exam_object']
    duration = timedelta(minutes=EXAMS[descriptor]['exam_duration'][level])
    compet_type = LEVEL[level.upper()]
    count = 0
    if compet_id != 0:
        try:
            compet_exam = exam.objects.get(compet_id=compet_id)
        except:
            print('compet not authorized', compet_id)
            return 0
        if not compet_exam.time_start:
            print('not started', compet_id)
            return 0
        if not compet_exam.answers:
            print('no answers', compet_id)
            return 0
        compet = Compet.objects.get(compet_id=compet_id,compet_type=compet_type)
        count +=  re_mark_exam(descriptor,compet_exam,compet)

    else:
        compets = Compet.objects.filter(compet_type=compet_type)
        compet_exams = exam.objects.filter(compet__compet_type=compet_type,answers__isnull=False).order_by('time_start')
        count = 0
        for compet_exam in compet_exams:
            if not compet_exam.time_finish:
                print("Compet {}, exam not finished".format(compet_exam.compet_id))
                continue
            compet = compets.get(compet_id=compet_exam.compet_id,compet_type=compet_type)
            count += re_mark_exam(descriptor, compet_exam, compet)
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
        marked = re_mark_exams(descriptor,level,compet_id)
        self.stdout.write(self.style.SUCCESS('Re-marked {} exams.'.format(marked)))
