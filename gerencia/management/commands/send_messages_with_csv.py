import os
import sys
from itertools import chain

from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL
from principal.utils.utils import obi_year
from principal.models import School, Colab, Compet, IJ, I1, I2, PJ, P1, P2, PS

from restrito.views import queue_email

DO_SEND = True
DEFAULT_FROM_EMAIL = 'olimpinf@ic.unicamp.br'

def send_messages(filename, msg_subject, msg_template):
    year = '2024'

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia", msg_template+".html"))
    with open(filename,'r') as f:
        lines = f.readlines()

    count = 0
    for line in lines:
        columns = line.strip().split(',')
        email = columns[0]
        name, school_name = "",""
        if len(columns) > 1:
            name = column[1].strip('"')
        if len(columns) > 2:
            school_name = column[2].strip('"')

        #print(school_data)
        
        to_address = email
        body = template.render({'name': name, 'school_name': school_name})
        subject = msg_subject
        queue_email(
            subject,
            body,
            DEFAULT_FROM_EMAIL,
            to_address
        )
        count += 1

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_subject', nargs='+', type=str)
        parser.add_argument('msg_template', nargs='+', type=str)
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_subject = options['msg_subject'][0]
        msg_template = options['msg_template'][0]
        filename = options['filename'][0]
        count = send_messages(filename, msg_subject, msg_template)
        self.stderr.write(self.style.SUCCESS('Enqueued {} messages.'.format(count)))
