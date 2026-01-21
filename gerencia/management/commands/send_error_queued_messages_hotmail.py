import os
import sys
import logging
from email.message import EmailMessage
import base64
import smtplib
import mimetypes
import ssl

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

SMTP_SERVER = "taquaral.ic.unicamp.br" # "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "olimpinf"
SMTP_PASSWORD = "pric23weg"


def send_queued_messages(msg_id):
    # with open(os.path.join(BASE_DIR,'email_errors3.txt')) as f:
    #     lines = f.readlines()
    # errors = []
    # for line in lines:
    #     errors.append(line.strip())

    #print("queue Message")
    #m = QueuedMail(subject="subject", body="body", from_addr=DEFAULT_FROM_EMAIL, to_addr=DEFAULT_FROM_EMAIL)
    #m.save()

    count = 0
    messages = QueuedMail.objects.filter(sent=True,to_addr__contains="hotmail.com").order_by("id")
    print("found",len(messages),"messages")
    for m in messages:
        if msg_id != 0 and m.id != msg_id:
            continue

        print("will resend -------------", m.to_addr)
        date = m.time_out.strftime("%d-%b-%y %Hh%Mm%Ss")
        body = f"(Estamos reenviando esta mensagem porque detectamos que a mensagem original provavelmente foi bloqueada por seu servidor por ter sido considerada 'mensagem não solicitada'. A mensagem original foi enviada {date}. Se a mensagem original foi recebida corretamente, por favor ignore esta mensagem.)\n-------------------\n\n" + m.body
        subject = m.subject + " (reenvio)"
        # print(subject)
        # print(body)
        # print()

        msg = EmailMessage()
        msg.set_charset("utf-8")
        subject = subject
        subject_bytes = subject.encode('utf-8')
        subject_base64bytes = base64.standard_b64encode(subject_bytes)
        subject = subject_base64bytes.decode('ascii')
        msg['Subject'] = '=?utf-8?B?' + subject + '?='
        msg['To'] = m.to_addr
        msg['From'] = DEFAULT_FROM_EMAIL
        msg['Reply-To'] = DEFAULT_REPLY_TO_EMAIL

        msg.set_content(body)

        mail = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        context=ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.set_ciphers('DEFAULT@SECLEVEL=1')
        mail.starttls(context=context)
        mail.login(SMTP_USERNAME, SMTP_PASSWORD)
        composed=msg.as_string().replace("us-ascii","utf-8")
        mail.send_mail(DEFAULT_FROM_EMAIL, m.to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL], composed)
        #mail.sendmail(DEFAULT_FROM_EMAIL, 'ranido@unicamp.br', composed)
        mail.quit()

        print('id={}, to_addr={} - sent'.format(m.id, m.to_addr))
        sys.stdout.flush()
        count += 1
        sleep(3)

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
