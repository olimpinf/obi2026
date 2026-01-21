import getopt
import os
import re
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware, timezone

from principal.models import LEVEL_NAME, Compet
from exams.models import Alternative, Question, Task
from exams.views import mark_exam
from exams.settings import EXAMS
from principal.models import IJ,I1,I2

def numerate_question(self, tasks):
    count = 0
    num = 0
    for task in tasks:
        if task.order != count + 1:
            self.stdout.write(self.style.ERROR(f'Task order {task.order} is wrong (expected {count+1})'))
        questions = Question.objects.filter(task=task).order_by('num')
        n = 0
        for question in questions:
            num += 1
            n += 1
            if question.num != n and question.num != num: # first time or already renumbered
                self.stdout.write(self.style.ERROR(f'Question num {question.num} is wrong (expected {num})'))
            question.num = num
            question.save()
        count += 1
    self.stdout.write(self.style.SUCCESS(f'Numerated {num} questions from {count} tasks.'))
    return count

def numerate_questions(self,descriptor):
    exam = EXAMS[descriptor]['exam_object']
    count = 0
    for compet_type in (IJ,I1,I2):
        self.stdout.write(self.style.SUCCESS(f'{LEVEL_NAME[compet_type]}:'))
        tasks = Task.objects.filter(exam=descriptor,level=compet_type).order_by('order')
        count += numerate_question(self, tasks)
        self.stdout.write('\n')
    return count

class Command(BaseCommand):
    help = 'Insert or update one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        done = numerate_questions(self,descriptor)
        self.stdout.write(self.style.SUCCESS('Numerated {} exams.'.format(done)))
