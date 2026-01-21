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

from principal.utils.utils import obi_year
from principal.models import School, QueuedMail
from obi.settings_debug import DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL

logger = logging.getLogger(__name__)

DO_SEND = True
SMTP_SERVER_HOTMAIL = "taquaral.ic.unicamp.br"
SMTP_PORT_HOTMAIL = 587
SMTP_USERNAME_HOTMAIL = "olimpinf"
SMTP_PASSWORD_HOTMAIL = "pric23weg"

def send_queued_message(id):

    #print("queue Message")
    #m = QueuedMail(subject="subject", body="body", from_addr=DEFAULT_FROM_EMAIL, to_addr=DEFAULT_FROM_EMAIL)
    #m.save()

    count = 0
    messages = QueuedMail.objects.filter(id=id).order_by("id")
    print("found",len(messages),"messages")
    for m in messages:
        if DO_SEND:
            if m.to_addr.find('hotmail.com') > 0:
                print("hotmail message")
                #EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
                #EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
                # SMTP_SERVER = "taquaral.ic.unicamp.br"
                # SMTP_PORT = 587
                # SMTP_USERNAME = "olimpinf"
                # SMTP_PASSWORD = "pric23weg"
                # EMAIL_USE_TLS = True
                # backend = backends.EmailBackend(host=SMTP_SERVER_HOTMAIL,
                #                                      port=SMTP_PORT_HOTMAIL,
                #                                      username=SMTP_USERNAME_HOTMAIL,
                #                                      password=SMTP_PASSWORD_HOTMAIL,
                #                                      use_tls=True, fail_silently=False, use_ssl=True)
                # connection = mail.get_connection(backend=backend)
            else:
                EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
                EMAIL_HOST = "smtp11.xmailer.com.br"
                EMAIL_HOST_PORT = 465
                EMAIL_HOST_USER = "olimpiada@olimpiada.ic.unicamp.br"
                EMAIL_HOST_PASSWORD = "dd7g0c0eyf"
                EMAIL_USE_TLS = True
            connection = mail.get_connection()
            connection.open()
            print("opened connection", connection)
            logger.info('opened connection')
            email = mail.EmailMessage(
                m.subject,
                m.body,
                #m.from_addr,
                DEFAULT_FROM_EMAIL,
                [m.to_addr],
                reply_to=[DEFAULT_REPLY_TO_EMAIL],
                connection=connection
            )
            #if attachment_data:
            #    email.attach('arquivo', attachment_data, 'image/png')
            try:
                email.send()
                logger.info('sent id={} to {}'.format(m.id, m.to_addr))
                print('send id={} to {} - sent'.format(m.id, m.to_addr))
                print(DEFAULT_FROM_EMAIL)
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
        m.sent = True
        m.time_out = timezone.now()
        m.save()

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        pass
        parser.add_argument('id', nargs='+', type=str)

    def handle(self, *args, **options):
        id = int(options['id'][0])
        count = send_queued_message(id)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
