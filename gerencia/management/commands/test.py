import sys
import os
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL
from principal.utils.utils import obi_year
from principal.models import School, Compet

# To test, use
# ./manage.py send_messages_compet "subject" "template.html" --settings obi.settings_debug


def send_messages(msg_subject,msg_template,msg_to_addresses):

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))
    
    if msg_to_addresses == 'all':
        compets = Compet.objects.filter(compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'prog':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6)).order_by('compet_id')
    elif msg_to_addresses == 'ini':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_email__isnull=False).order_by('compet_id')
    else:
        # a test with a test user
        compets = Compet.objects.filter(compet_id=12945).order_by('compet_id')

    
    #compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase1=True)
    #compets = Compet.objects.filter(compet_type__in=(3,5),compet_sex='F',compet_email__isnull=False)
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase1=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True).order_by('compet_id')
    print('num compets:',len(compets))

    count,failed = 0,0
    
    # do not send to coordinators
    schools = School.objects.all()
    coord_emails = set()
    for s in schools:
        coord_emails.add(s.school_deleg_email)
    print("coord_emails:", len(coord_emails), file=sys.stderr)

    for c in compets:
        if c.compet_email in coord_emails:
            print('not sent, coord email', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue
        try:
            user = c.user
        except:
            print('failed, no user', c.compet_id, c.compet_name, 'email:',c.compet_email, 'school:', c.compet_school_id)
            continue
        if (not c.compet_email or not c.compet_email.strip()) and (not c.user or not c.user.email):
            print('failed, no email', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue
        to_name = c.compet_name
        if c.compet_sex == 'F':
            greetings = 'Cara Competidora'
            suffix = 'a'
        else:
            greetings = 'Caro Competidor'
            suffix = 'o'
        s = schools.get(pk=c.compet_school_id)
        print(c.compet_id_full,s.school_name)
            
    return count, failed


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_subject', nargs='+', type=str)
        parser.add_argument('msg_template', nargs='+', type=str)
        parser.add_argument('msg_to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_subject = options['msg_subject'][0]
        msg_template = options['msg_template'][0]
        msg_to_addresses = options['msg_to_addresses'][0]
        count,failed = send_messages(msg_subject, msg_template, msg_to_addresses)
        self.stdout.write(self.style.SUCCESS('Sent {} messages, {} failed'.format(count,failed)))
