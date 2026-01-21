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

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL
from principal.utils.utils import obi_year
from principal.models import School, Compet
from week.models import Week

# To test, use
# ./manage.py send_messages_compet "subject" "template.html" --settings obi.settings_debug


def send_messages(msg_subject,msg_template,msg_to_addresses):
    print('msg_subject:',msg_subject)
    print('msg_template:',msg_template)
    print('msg_to_addresses:',msg_to_addresses)

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))

    if msg_to_addresses == 'all':
        compets = Compet.objects.filter(compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'prog2':
        compets = Compet.objects.filter(compet_type__in=(4,6)).order_by('compet_id')
    elif msg_to_addresses == 'prog1':
        compets = Compet.objects.filter(compet_type__in=(3,5)).order_by('compet_id')
    elif msg_to_addresses == 'prog':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6)).order_by('compet_id')
    elif msg_to_addresses == 'progf3':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True).order_by('compet_id')
    elif msg_to_addresses == 'ini':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'inif3':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True,compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'cfobi':
        compets = Compet.objects.filter(compet_type__in=(3,5),compet_email__isnull=False,compet_sex__in=('F','O')).order_by('compet_id')
    elif msg_to_addresses == 'week':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,5),compet__compet_email__isnull=False).order_by('compet_id')

        compets = []
        for t in tmp:
            c = t.compet
            print(c.compet_id_full,t.partic_level)
            c.partic_level = t.partic_level
            compets.append(c)
    elif msg_to_addresses == 'week':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,5),compet__compet_email__isnull=False).order_by('compet_id')
        compets = []
        for t in tmp:
            c = t.compet
            print(c.compet_id_full,t.partic_level)
            c.partic_level = t.partic_level
            compets.append(c)
    elif msg_to_addresses == 'week-info':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,5),compet__compet_email__isnull=False).order_by('compet_id')
        compets = []
        for t in tmp:
            c = t.compet
            print(c.compet_id_full,t.partic_level)
            if not t.form_info:
                continue
            c.partic_level = t.partic_level
            compets.append(c)

    else:
        # a test with a test user
        compets = Compet.objects.filter(compet_id=66402).order_by('compet_id')

    #compets = compets.filter(compet_id__gt=58447)

    # if Fase 2
    #compets = compets.filter(compet_classif_fase1=True)

    #compets = Compet.objects.filter(compet_type__in=(3,5),compet_sex='F',compet_email__isnull=False)
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase1=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True).order_by('compet_id')
    print('num compets:',len(compets))

    count,failed = 0,0
    
    # do not send to coordinators
    schools = School.objects.all()
    coord_emails = set()
    # for s in schools:
    #     coord_emails.add(s.school_deleg_email)
    # print("coord_emails:", len(coord_emails), file=sys.stderr)

    sent_file = "convite_maratona_tech_enviados.txt"
    sent = set()
    
    connection = mail.get_connection()
    connection.open()

    for c in compets:
        if c.compet_email in coord_emails:
            print('not sent, coord email', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue
        if c.compet_email in sent:
            print('not sent, already sent', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue

        sent.add(c.compet_email)
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
        print(c.compet_id_full, c.compet_name, s.school_name)
        #if c.compet_type not in (3,5):
        #    print(c,c.compet_type)
        #    break
        #else:
        #    continue
        context = {'compet': c, 'school': s, 'greetings':greetings, 'suffix': suffix}
        body = template.render(context)
        #print(body)
        to_address = c.compet_email
        if to_address.lower() != c.user.email.lower():
            print('warning, different emails compet email:', c.compet_email, 'user email:', c.user.email, 'user:',c.user)

        if not to_address:
            #print('failed, no email -- compet_email:', c.compet_email, 'user:',c.user)
            continue

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
            print('{} {} {} - sent'.format(to_address, to_name, c.compet_id),file=sys.stderr)
            sys.stderr.flush()
            with open(sent_file,"a") as sfile:
                print('{} {} {} - sent'.format(c.compet_id_full, to_address, to_name), file=sfile)
                sfile.flush()
            count += 1
            sleep(1.5)
        except:
            pass
            print('{} {} {} *********** failed'.format(to_address, to_name, c.compet_id),file=sys.stderr)
            failed += 1

    connection.close()
            
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
