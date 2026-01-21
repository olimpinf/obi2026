
import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import LEVEL
from exams.models import Alternative, Question, Task

def delete_tasks(dirname):
    deleted, failed = 0,0
    for root, dirs, files in os.walk(dirname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                ins,fld = delete_task(os.path.join(root,name))
                deleted += ins
                failed += fld
    return deleted, failed

def delete_task(fname):
        '''Deletes one task '''
        #2010f1p2_batalha.html
        pat_modality = re.compile(r'(?P<exam>[a-z]{5})f(?P<phase>[123s])(?P<mod>[ip])(?P<level>[j12us])_(?P<code>.*)\.html')
        #pat_modality = re.compile(r'\d{4}f\d(?P<modality>p|i)[12jus]\_\w*\.html')
        print(os.path.basename(fname), end='')
        m = re.match(pat_modality,os.path.basename(fname))
        if m == None:
            print('wrong descriptor')
        if m.group('mod') == 'p':
            task_type = 'prog'
        elif m.group('mod') == 'i':
            task_type = 'ini'
        else:
            print('unexpected task type')
            sys.exit(-1)
        deleted, failed = 0,0
        descriptor,ext = os.path.splitext(os.path.basename(fname))
        try:
            task = Task.objects.get(descriptor=descriptor)
        except:
            failed += 1
            action = "failed"
        if task_type == 'ini':
            questions = Question(task=task)
            for q in questions:
                alternative = Alternative(question=question)
                alternative.delete()
                q.delete()
        try:
            task.delete() # delete task and associated question+alternatives
            deleted += 1
            action = "deleted"
        except:
            failed += 1
            action = "failed"
        # must save before processing questions
        print(" -- {}".format(action))
        return deleted,failed

class Command(BaseCommand):
    help = 'Delete one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('fname', nargs='+', type=str)

    def handle(self, *args, **options):
        for fname in options['fname']:
            if os.path.isdir(fname):
                deleted, failed = delete_tasks(fname)
            else:
                deleted, failed = delete_task(fname)
        self.stdout.write(self.style.SUCCESS('deleted {} tasks, failed {} tasks.'.format(deleted,failed)))
