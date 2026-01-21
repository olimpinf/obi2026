
import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import LEVEL
from exams.models import Alternative, Question, Task


def process_alternative(data,line,question,a,alternative_num):
    while line < len(data) and (data[line][0] == '#' or data[line][0] == '%'):
        line += 1
    tmp = data[line].find('\correct')
    if tmp > 0:
        correct = True
        end = tmp
    else:
        correct = False
        end = len(data[line])

    init = data[line].find('&') # there must be one (tabular separator)
    text = data[line][init+1:end]
    line += 1
    while line < len(data):
        if data[line][0] != '#' and data[line][0] != '%':
            if data[line].find(a) >= 0:
                break
            else:
                text += data[line]
        line += 1
    alternative = Alternative(question=question, text=text, num=alternative_num, correct=correct)
    alternative.save()
    return line,correct

def process_a_question(data,line,task,question_num):
    question_text = ''
    while line < len(data):
        if data[line][0] != '#' and data[line][0] != '%':
            if data[line].find('(A)') >= 0:
                break
            else:
                question_text += data[line]
        line += 1
    question = Question(task=task, text=question_text, num=question_num)
    question.save()
    alternative_num = 1
    found_correct = False
    for a in ['(B)','(C)','(D)','(E)','\question']:
        line,correct = process_alternative(data,line,question,a,alternative_num)
        alternative_num += 1
        found_correct |= correct
    return line+1, found_correct # last is \question

def process_questions(data,line,task):
    line += 1
    question_num = 1
    while line < len(data) and (data[line][0] != '#' and data[line][0] != '%'):
        line,found_correct  = process_a_question(data,line,task,question_num)
        if not found_correct:
            print('Question {} of task {} ({}) does not have a correct alternative.'.format(question_num,task.title,task.descriptor))
        question_num += 1

def insert_tasks(dirname):
    inserted, updated = 0,0
    for root, dirs, files in os.walk(dirname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                ins,upd = insert_task(os.path.join(root,name))
                inserted += ins
                updated += upd
    return inserted, updated

def insert_task(fname):
        '''Inserts of updates one task '''
        #2010f1p2_batalha.html
        #tfcf1pj_transporte.html
        pat_modality = re.compile(r'(?P<exam>[a-z]+)f(?P<phase>[123s])(?P<mod>[ip])(?P<level>[j12us])_(?P<code>.*)\.html')
        #pat_modality = re.compile(r'\d{4}f\d(?P<modality>p|i)[12jus]\_\w*\.html')
        print(os.path.basename(fname), end='')
        m = re.match(pat_modality,os.path.basename(fname))
        if m == None:
            print(' ******** wrong descriptor')
            sys.exit(-1)
        if m.group('mod') == 'p':
            task_type = 'prog'
        elif m.group('mod') == 'i':
            task_type = 'ini'
        else:
            print('unexpected task type')
            sys.exit(-1)
        inserted, updated = 0,0
        with open(fname,"r",encoding='utf-8') as f:
            data = f.readlines()
        tmp_url = fname
        tmp_title = data[0].strip()
        tmp_template = data[1].strip()
        tmp_order = data[2].strip()
        if tmp_title.find('title:') != 0:
            print(' expected title at first line')
            return inserted,updated
        if tmp_template.find('template:') != 0:
            print(' expected template at second line')
            return inserted,updated
        if tmp_order.find('order:') != 0:
            print(' expected order at third line')
            return inserted,updated
        start = tmp_url.find('html_tasks/')
        if start < 0:
            pass
            #print('path to filename is not html_task/')
            #print('hope it is realy a task')
            #return inserted,updated
        title = tmp_title[6:]
        print(" ({})".format(title), end='')
        template = tmp_template[9:].strip()
        order = tmp_order[6:].strip()
        descriptor,ext = os.path.splitext(os.path.basename(fname))
        statement = ''
        line = 3
        if task_type == 'ini':
            while line < len(data) and data[line].find('\question') != 0:
                if data[line][0] != '#':
                    statement += data[line]
                line += 1
        else:
            while line < len(data):
                if data[line][0] != '#':
                    statement += data[line]
                line += 1
        try:
            task = Task.objects.get(descriptor=descriptor)
            task.delete() # delete task and associated question+alternatives
            updated += 1
            action = "updated"
        except:
            inserted += 1
            action = "inserted"
        task = Task(descriptor=descriptor)
        task.title=title
        task.statement=statement
        task.order=order
        task.template_name=template
        #####################
        # for turn B only
        #####################
        #task.exam = '{}f{}b'.format(m.group('exam'),m.group('phase'))
        task.exam = '{}f{}'.format(m.group('exam'),m.group('phase'))
        task.phase = m.group('phase')
        task.modstr = m.group('mod')
        task.levelstr = m.group('level')
        tmp = "{}{}".format(task.modstr,task.levelstr).upper()
        task.level = LEVEL[tmp]
        task.code = m.group('code')
        task.url = '{}{}/{}/f{}/{}'.format(task.modstr,task.levelstr,task.exam,task.phase,task.code) 
        task.save()
        # must save before processing questions
        if task_type == 'ini':
            process_questions(data,line,task)
        task.save()
        print(" -- {}".format(action))
        return inserted,updated

class Command(BaseCommand):
    help = 'Insert or update one or more tasks'

    def add_arguments(self, parser):
        parser.add_argument('fname', nargs='+', type=str)

    def handle(self, *args, **options):
        for fname in options['fname']:
            if os.path.isdir(fname):
                inserted, updated = insert_tasks(fname)
            else:
                inserted, updated = insert_task(fname)
        self.stdout.write(self.style.SUCCESS('Inserted {} tasks, updated {} tasks.'.format(inserted,updated)))
