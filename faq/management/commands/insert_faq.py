import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import LEVEL
from faq.models import Item, Topic

def process_questions(data,line,task):
    line += 1
    question_num = 1
    while line < len(data):
        line,found_correct  = process_a_question(data,line,task,question_num)
        if not found_correct:
            print('Question {} of task {} ({}) does not have a correct alternative.'.format(question_num,task.title,task.descriptor))
        question_num += 1

def insert_faqs(dirname, topics, items):
    inserted, updated = 0,0
    for root, dirs, files in os.walk(dirname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                ins,upd = insert_a_faq(os.path.join(root,name), topics, items)
                inserted += ins
                updated += upd
    return inserted, updated

def insert_a_faq(fname, topics, items):
        '''Inserts of updates one faq '''
        inserted, updated = 0,0
        with open(fname,"r",encoding='utf-8') as f:
            data = f.readlines()
        root = os.path.dirname(fname)
        with open(os.path.join(root,"topic"),"r",encoding='utf-8') as f:
            tmp = f.readlines()
            topic_short_name = tmp[0].strip()
            topic_name = tmp[1].strip()
            topic_order = int(tmp[2].strip())
        print('topic_short_name=', topic_short_name)
        try:
            topic_exists = topics.get(name_short=topic_short_name)
        except:
            topic_exists = None
        print('topic_exists=', topic_exists)
        if not topic_exists:
            print('topic {} ({}) does not exist. Create? (y/n)'.format(topic_short_name, topic_name))
            resp = input().strip()
            if resp == 'y':
                t = Topic(name=topic_name, name_short=topic_short_name, order=topic_order)
                t.save()
                topic_exists = t
                print('created topic {}, id={}'.format(topic_name,t.id))
        slug,ext = os.path.splitext(os.path.basename(fname))
        try:
            item_exists = items.get(slug=slug)
        except:
            item_exists = None

        start = fname.find('html_faq/')
        if start < 0:
            print('path to filename is not html_faq/')
            print('hope it is realy a faq')
            #return inserted,updated
            
        tmp = data[0].strip()
        if tmp != '#question':
            print('expected question at first line')
            return inserted,updated
        question = ''
        line = 1
        while line < len(data) and data[line].strip() != '#answer':
            tmp = data[line].strip()
            if tmp:
                question += data[line]
            line += 1
        line += 1
        answer = ''
        while line < len(data) and data[line].strip() != '#order':
            tmp = data[line].strip()
            if tmp:
                answer += data[line]
            line += 1

        line += 1
        try:
            order = int(data[line].strip())
        except:
            order = 1000  # low priority
            
        print('question:\n',question)
        print('answer:\n',answer)
        print('order:\n',order)
        print('slug:\n',slug)
        try:
            item = Item.objects.get(slug=slug)
            item.topic = topic_exists
            item.question = question
            item.answer = answer
            item.order = order
            item.save()
            updated += 1
            print("updating, question=",item.question)
            return inserted, updated
        except:
            print("inserting, question=",question)
            inserted += 1
        faq = Item(slug=slug,question=question,answer=answer,active=True,topic=topic_exists,order=1)
        faq.save()
        return inserted,updated

class Command(BaseCommand):
    help = 'Insert or update one or more faq'

    def add_arguments(self, parser):
        parser.add_argument('fname', nargs='+', type=str)

    def handle(self, *args, **options):
        topics = Topic.objects.all()
        items = Item.objects.all()

        for fname in options['fname']:
            if os.path.isdir(fname):
                inserted, updated = insert_faqs(fname, topics, items)
            else:
                inserted, updated = insert_a_faq(fname, topics, items)
        self.stdout.write(self.style.SUCCESS('Inserted {} faqs, updated {} faqs.'.format(inserted,updated)))
