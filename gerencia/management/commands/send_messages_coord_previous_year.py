from time import sleep
from itertools import chain
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader

from principal.utils.utils import obi_year
from principal.models import School, Colab

from obi.settings import DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL, YEAR

DB = f'obi{YEAR-1}'
# To test, use
# ./manage.py send_messages_compet "subject" "gerencia/template.html" --settings obi.settings_debug


def send_messages(msg_subject,msg_template,recipients):
    '''Send message to coord
    '''
    connection = mail.get_connection()
    template = loader.get_template(msg_template)
    connection.open()
    count = 0

    if recipients == 'all':
        schools = School.objects.filter(school_ok=True).order_by('school_id').using(DB)
    else:
        # testing
        #schools = School.objects.filter(school_id=1).order_by('school_id').using(DB)
        schools = School.objects.filter(school_id=1378).order_by('school_id').using(DB)
    print('num_emails:',len(schools))
    for s in schools:
        to_address = s.school_deleg_email
        greeting = "Caro(a) Prof(a)."
        context = {'school':s, 'greeting':greeting}
        body = template.render(context)
        email = mail.EmailMessage(
            msg_subject,
            body,
            DEFAULT_FROM_EMAIL,
            [to_address],
            reply_to=[DEFAULT_REPLY_TO_EMAIL],
            connection=connection
        )
        #if attachment_data:
        #    email.attach('arquivo', attachment_data, 'image/png')
        try:
            email.send()
            print('{} {} - sent'.format(to_address, s.school_deleg_name))
        except:
            print('{} {} *********** failed'.format(to_address, s.school_deleg_name))

        count += 1
        if count % 2 == 0:
            sleep(1)
    connection.close()
    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_subject', nargs='+', type=str)
        parser.add_argument('msg_template', nargs='+', type=str)
        parser.add_argument('recipients', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_subject = options['msg_subject'][0]
        msg_template = options['msg_template'][0]
        recipients = options['recipients'][0]
        count = send_messages(msg_subject, msg_template, recipients)
        self.stdout.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
