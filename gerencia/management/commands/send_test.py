import os
import sys
import logging

from time import sleep
from datetime import datetime
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader
from django.utils import timezone

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL, EMAIL_BACKEND
from principal.utils.utils import obi_year
from principal.models import School, QueuedMail
from django.db.models import Q

logger = logging.getLogger(__name__)

DO_SEND = True
LAST_MESSAGE_ID = 19094

def send_queued_messages():
    #print("queue Message")

    count = 0

    # to test messages
    #messages = QueuedMail.objects.filter(~Q(to_addr__icontains='hotmail.com'),id=19098).order_by("id")

    messages = QueuedMail.objects.filter(~(Q(to_addr__icontains='hotmail.com')|Q(to_addr__icontains='yahoo.com')),sent=True).order_by("id")
    print('found',len(messages))
    messages = QueuedMail.objects.filter((Q(to_addr__icontains='hotmail.com')|Q(to_addr__icontains='yahoo.com')),sent=True).order_by("id")
    print('found',len(messages))
    messages = QueuedMail.objects.filter(sent=True).order_by("id")
    print('found',len(messages))
    return 0
    for m in messages:
        if not DO_SEND:
            continue
        connection = mail.get_connection()
        connection.open()
        print("opened connection", connection)
        logger.info('opened connection')
        email = mail.EmailMessage(
            m.subject,
            m.body,
            m.from_addr,
            [m.to_addr],
            reply_to=[DEFAULT_REPLY_TO_EMAIL],
            connection=connection
        )
        #if attachment_data:
        #    email.attach('arquivo', attachment_data, 'image/png')
        try:
            email.send()
            logger.info('send to {}'.format(m.to_addr))
            print('{} - sent'.format(m.to_addr))
            sys.stdout.flush()
            count += 1
            m.sent = True
            m.time_out = timezone.now()
            m.save()
        except:
            print('\nto_addr {} *********** failed'.format(m.to_addr))
            logger.info('************* failed {}'.format(m.to_addr))
            sys.stdout.flush()
            connection.close()
            m.sent = True
            m.time_out = timezone.now()
            m.save()
        sleep(2)

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('hotmail', nargs='+', type=bool)

    def handle(self, *args, **options):
        count = send_queued_messages()
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
