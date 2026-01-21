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

from restrito.views import queue_email
from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL
from principal.utils.utils import obi_year
from principal.models import IJ, I1, I2, PJ, P1, P2, PS, School, Compet
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
    elif msg_to_addresses == 'medals':        
        #compets = Compet.objects.using('obi2023').filter(compet_year__in=('F9','M1','M2'),compet_medal__isnull=False).order_by('compet_id')
        compets = Compet.objects.using('obi2023').filter(compet_id=29638)
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
    elif msg_to_addresses == 'inif2':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase1=True,compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'inif3':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True,compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'cfobi':
        compets = Compet.objects.filter(compet_type__in=(3,4,5),compet_email__isnull=False,compet_sex__in=('F','O')).order_by('compet_id')
    elif msg_to_addresses == 'maratona':
        compets = Compet.objects.filter(compet_type__in=(2,3,4,5),compet_email__isnull=False).order_by('compet_id')
    elif msg_to_addresses == 'prog-fase2':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase1=True).order_by('compet_id')
    elif msg_to_addresses == 'puc-rj':
        compets = Compet.objects.filter(compet_year='M1',compet_email__isnull=False, compet_school__school_state='RJ').order_by('compet_id')

    elif msg_to_addresses == 'week':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,4,5,7,8),compet__compet_email__isnull=False).order_by('compet_id')
        compets = []
        for t in tmp:
            c = t.compet
            #print(c.compet_id_full,c.compet_type, t.partic_level)
            #if t.partic_level != c.compet_type:
            #    print("^^^")
            c.partic_level = t.partic_level
            compets.append(c)

    elif msg_to_addresses == 'week-info':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,4,5,7,8),compet__compet_email__isnull=False,form_info=True).order_by('compet_id')
        compets = []
        for t in tmp:
            c = t.compet
            print(c.compet_id_full,t.partic_level)
            if not t.form_info:
                continue
            c.partic_level = t.partic_level
            compets.append(c)

    elif msg_to_addresses == 'ajuda-sede-fase3-prog':
        school_ids = (967, # Ceres/GO
                      651, # Guanambi/BA
                      592, # Teresina/PI
                      926, # Barra do Garças/MT
                      1149, # Pau dos Ferros/RN
                      690) # Teste

        compets = Compet.objects.filter(compet_school_id__in=school_ids,compet_classif_fase2=True,compet_type__in=(PJ,P1,P2,PS))
    elif msg_to_addresses == 'fase3-ini':
        compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(IJ,I1,I2))
        #compets = Compet.objects.filter(compet_id=67120)
    elif msg_to_addresses == 'fase3-prog':
        compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(PJ,P1,P2,PS))
    elif msg_to_addresses == 'test':
        # a test with a test user
        compets = Compet.objects.filter(compet_id=30515).order_by('compet_id')
    else:
        return -1
    
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

    sent_file = "lembrete_fase2_enviados.txt"
    sent = set()

    for c in compets:
        if c.compet_email in coord_emails:
            print('not sent, coord email', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue
        if c.compet_email in sent:
            print('not sent, already sent', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue

        if (not c.compet_email or not c.compet_email.strip()) and (not c.user or not c.user.email):
            print('failed, no email', c.compet_id, c.compet_name, 'email:',c.compet_email,'user:',c.user, 'school:', c.compet_school_id)
            continue
        sent.add(c.compet_email)
        try:
            user = c.user
        except:
            print('failed, no user', c.compet_id, c.compet_name, 'email:',c.compet_email, 'school:', c.compet_school_id)
            continue
        to_name = c.compet_name
        if c.compet_sex == 'F':
            greetings = 'Cara Competidora'
            suffix = 'a'
        else:
            greetings = 'Caro Competidor'
            suffix = 'o'
        s = schools.get(pk=c.compet_school_id)
        #if c.compet_id < 60449:
        #    continue
        #print(c.compet_id_full, c.compet_name, s.school_name)
        #if c.compet_type not in (3,5):
        #    print(c,c.compet_type)
        #    break
        #else:
        #    continue

        to_address = c.compet_email
        if to_address == None or to_address.strip() =='':
            print('warning, no compet email:', c.compet_email)
        if c.user == None:
            print('warning, no compet user:', c.compet_id)  
        elif to_address.lower() != c.user.email.lower():
            print('warning, different emails compet email:', c.compet_email, 'user email:', c.user.email, 'user:',c.user)

        if not to_address:
            #print('no email -- compet_email:', c.compet_email, 'user:',c.user)
            continue

        context = {'compet': c, 'school': s, 'greetings':greetings, 'suffix': suffix}

        if msg_to_addresses in ('ajuda-sede-fase3-prog',):
            context['mod_name'] = 'Programação'
            context['mod_date'] = '1 de outubro'

        body = template.render(context)
        #print(to_address)
        #print(body)
        #print('----------')
        subject = msg_subject
        queue_email(
            subject,
            body,
            DEFAULT_FROM_EMAIL,
            to_address,
            priority=1,
        )
        count += 1
    
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
