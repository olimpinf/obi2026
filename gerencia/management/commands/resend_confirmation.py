import os
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

def send_messages():
    year = '2022'
    subject = 'OBI' + year + ' - Cadastro finalizado'
    schools = School.objects.filter(school_ok=True)
    compets = Compet.objects.all().only('compet_school_id').distinct()
    print('compets',len(compets))
    school_with_compets = set()
    for c in compets:
        school_with_compets.add(c.compet_school_id)
    count = 0
    print('school_with_compets',len(school_with_compets))


    msg_template = 'mensagem_reenvio_confirmacao.html'
    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))

    for s in schools:
        if not s.school_hash:
            print('no hash: {}'.format(s.school_name))
            continue
        if s.school_id in school_with_compets:
            #print('has compets: {}'.format(s.school_name))
            continue

        context = {'school': s, 'greeting': "Prezado(a) Prof(a). ", 'year': year}
        body = template.render(context)
        connection = mail.get_connection()
        connection.open()
        msg_subject = 'OBI' + year + ' - cadastro'
        to_address = s.school_deleg_email
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
            print('{} - sent'.format(s.school_deleg_email))
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
        #parser.add_argument('dbname', nargs='+', type=str)

    def handle(self, *args, **options):
        count = send_messages()
        self.stdout.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
