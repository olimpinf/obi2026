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

logger = logging.getLogger(__name__)


def send_queued_messages(msg_id):
    # with open(os.path.join(BASE_DIR,'email_errors3.txt')) as f:
    #     lines = f.readlines()
    # errors = []
    # for line in lines:
    #     errors.append(line.strip())

    print(DEFAULT_FROM_EMAIL)
    #print("queue Message")
    #m = QueuedMail(subject="subject", body="body", from_addr=DEFAULT_FROM_EMAIL, to_addr=DEFAULT_FROM_EMAIL)
    #m.save()

    count = 0
    m = QueuedMail.objects.get(sent=True,id=msg_id)
    #messages = QueuedMail.objects.filter(sent=True,id__gt=300).order_by("id")
    #print("found",len(messages),"messages")
    #for m in messages:
    #    if m.from_addr.find('@obi.ic.unicamp.br') > 0:
    #        print("from_addr already ok",m.from_addr)
    #        continue
    #    if m.to_addr not in errors:
    #        print("to_addr not in errors",m.to_addr)
    #        continue

    if True:
        print("will resend -------------", m.to_addr)
        date = m.time_out.strftime("%d-%b-%y %Hh%Mm%Ss")
        body = f"(Estamos reenviando esta mensagem porque detectamos que a mensagem original provavelmente foi bloqueada por seu servidor por ter sido considerada 'mensagem não solicitada'. A mensagem original foi enviada {date}. Se a mensagem original foi recebida corretamente, por favor ignore esta mensagem.)\n-------------------\n\n" + m.body
        subject = m.subject + "(reenvio)"
        # print(subject)
        # print(body)
        # print()
        connection = mail.get_connection()
        connection.open()
        logger.info('opened connection')
        email = mail.EmailMessage(
            subject,
            body,
            DEFAULT_FROM_EMAIL,
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
        except:
            print('\nto_addr {} *********** failed'.format(m.to_addr))
            logger.info('************* failed {}'.format(m.to_addr))
            sys.stdout.flush()
            connection.close()
            sleep(2)
        else:
            print('\n****************** send to_addr {}'.format(m.to_addr))
            count += 1
        #m.sent = True
        m.time_out = timezone.now()
        #m.save()

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_id', nargs='+', type=int)
        #parser.add_argument('msg_to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_id = int(options['msg_id'][0])
        count = send_queued_messages(msg_id)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
