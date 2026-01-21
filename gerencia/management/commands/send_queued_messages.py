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
from django.core.mail import EmailMessage, EmailMultiAlternatives

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL, EMAIL_BACKEND
from principal.utils.utils import obi_year
from principal.models import School, QueuedMail
from django.db.models import Q

logger = logging.getLogger(__name__)

DO_SEND = True
LAST_MESSAGE_ID = 0

def send_one_message(m):
    connection = mail.get_connection()
    connection.open()
    print("opened connection", connection)
    logger.info('opened connection')

    if m.body_html:
        email = EmailMultiAlternatives(
            m.subject,
            m.body,
            m.from_addr,
            [m.to_addr],
            reply_to=[DEFAULT_REPLY_TO_EMAIL],
            connection=connection
        )
        email.attach_alternative(m.body_html, "text/html")
    else:
        email = mail.EmailMessage(
            m.subject,
            m.body,
            m.from_addr,
            [m.to_addr],
            reply_to=[DEFAULT_REPLY_TO_EMAIL],
            connection=connection
        )
        
    try:
        email.send()
        logger.info('sent id={} to {}'.format(m.id, m.to_addr))
        #print('send id={} to {} - sent'.format(m.id, m.to_addr))
        sys.stdout.flush()
        m.sent = True
        m.time_out = timezone.now()
        m.save()
        return 1
    except:
        #print('\nto_addr {} *********** failed'.format(m.to_addr))
        logger.info('************* failed {}'.format(m.to_addr))
        sys.stdout.flush()
        connection.close()
        m.sent = True
        m.time_out = timezone.now()
        m.save()
        return 0



def send_queued_messages():
    #print("queue Message")

    count = 0

    # to test messages
    #messages = QueuedMail.objects.filter(~Q(to_addr__icontains='hotmail.com'),id=19098).order_by("id")

    # first send all messages with priority = 0
    messages = QueuedMail.objects.filter(~(Q(to_addr__icontains='hotmail.com')|Q(to_addr__icontains='yahoo.com')|Q(to_addr__icontains='outlook.com')|Q(to_addr__icontains='outlook.com')),sent=False,priority=0).order_by("id")
    #messages = QueuedMail.objects.filter(id=32,sent=True,priority=0).order_by("id")
    print("priority 0, count:",len(messages))
    for m in messages:
        if not DO_SEND:
            print(m.to_addr)
            continue
        count += send_one_message(m)
        sleep(2)

    # # then send at most 10 messages with priority = 1
    messages = QueuedMail.objects.filter(~(Q(to_addr__icontains='hotmail.com')|Q(to_addr__icontains='yahoo.com')|Q(to_addr__icontains='outlook.com')|Q(to_addr__icontains='outlook.com')),sent=False,priority=1).order_by("id")
    print("priority 1, count:",len(messages))
    count_non_priority = 0
    for m in messages:
        if not DO_SEND:
            print(m.to_addr)
            continue
        send_one_message(m)
        count_non_priority += 1
        if count_non_priority > 10:
            break
        sleep(2)
        
    return count+count_non_priority


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('hotmail', nargs='+', type=bool)

    def handle(self, *args, **options):
        count = send_queued_messages()
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
