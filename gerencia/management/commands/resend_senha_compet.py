import os
import sys
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
from principal.models import School, Compet

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def send_messages(compets):
    year = '2022'
    msg_subject = 'OBI' + year + ' - inscrição'
    reason = 'realizar sua inscrição'
    msg_template = 'mensagem_reenvio_senha.html'
    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))
    count = 0


    schools = School.objects.all()
    school_emails = set()
    for s in schools:
        school_emails.add(s.school_deleg_email)
    print('len school_emails',len(school_emails))

    for c in compets:
        if not c.compet_conf:
            print(c,'missing password')
            sys.exit(0)
        if not c.compet_id_full:
            print(c,'missing id_full')
            sys.exit(0)
        if not c.compet_email:
            print(c,'missing email address')
            continue
        if c.compet_email in school_emails:
            print(c,'email coord',c.compet_email)
            continue

        s = c.compet_school
        if c.compet_sex == 'F':
            greeting = 'Prezada Competidora'
        else:
            greeting = 'Prezado Competidor'
        context = {'c': c, 's': s, 'greeting': greeting, 'reason': reason, 'year': year}
        body = template.render(context)
        connection = mail.get_connection()
        connection.open()
        to_address = c.compet_email
        email = mail.EmailMessage(
            msg_subject,
            body,
            DEFAULT_FROM_EMAIL,
            [to_address],
            reply_to=[DEFAULT_REPLY_TO_EMAIL],
            connection=connection
        )

        #if attachment_data:
        #    email.attach('convite.png', attachment_data, 'image/png')
        try:
            email.send()
            print('{} - sent'.format(c.compet_email))
        except:
            print('{} - FAILED'.format(s.school_deleg_email))

        count += 1
        connection.close()
        sleep(2)
    return count


class Command(BaseCommand):
    help = 'Send invitation messages to last year schools'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('fname', nargs='+', type=str)

    def handle(self, *args, **options):
        #fname = options['fname'][0]
        #with open(fname,'r') as f:
        #    compets = f.readlines()
        #compets = Compet.objects.filter(compet_id__gt=24908,compet_id__lt=32517)
        compets = Compet.objects.filter(compet_school_id=368)
        print('compets',len(compets))
        count = send_messages(compets)
        self.stdout.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
