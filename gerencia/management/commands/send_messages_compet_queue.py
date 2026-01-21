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
from django.contrib.auth.models import User

from restrito.views import queue_email
from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL
from principal.utils.utils import obi_year
from principal.models import IJ, I1, I2, PJ, P1, P2, PS, School, Compet, QueuedMail
from week.models import Week

# To test, use
# ./manage.py send_messages_compet "subject" "template.html" --settings obi.settings_debug


def send_messages(msg_subject,msg_template,msg_to_addresses):

    template_txt = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template+"_txt.html"))
    try:
        template_htm = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template+"_htm.html"))
    except:
        template_htm = ""
        
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

    elif msg_to_addresses == 'week-compet':
        #tmp = Week.objects.filter(partic_type='compet',compet__compet_email__isnull=False).order_by('compet_id')
        tmp = Week.objects.filter(partic_type='compet').order_by('compet_id')
        compets = []
        for t in tmp:
            c = t.compet
            print(c.compet_id_full,c.compet_type, t.partic_level,c.compet_name, c.compet_email)
            if t.partic_level != c.compet_type:
                print(f"^^^ partic.level={t.partic_level}, c.compet_type={c.compet_type}")
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
    elif msg_to_addresses == 'week-all':
        tmp = Week.objects.filter(form_info=True).order_by('week_id')
        participants = []
        for t in tmp:
            if t.compet:
                c = t.compet
                if not c.compet_email or c.compet_email.strip()=='':
                    print("NO EMAIL", c.compet_id, c.compet_name)
                    continue
                participants.append(c)
            elif t.chaperone:
                c = Compet()
                c.compet_name=t.chaperone.chaperone_name
                c.compet_email=t.chaperone.chaperone_email
                c.compet_sex=t.chaperone.chaperone_sex
                participants.append(c)

        compets = participants
        #for c in compets:
        #    print(c.compet_email, c.compet_name, c.compet_sex)
        print(len(compets))
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
    elif msg_to_addresses == 'behring':
        #compets = Compet.objects.filter(compet_classif_fase1=True,compet_year__in=('M2','M3','T4'),compet_school__school_state='RJ')
        compets = Compet.objects.filter(compet_classif_fase1=True,compet_year__in=('F8','F9'),compet_id__lte=117989)
        print(len(compets))
    elif msg_to_addresses == 'test':
        # a test with a test user
        #compets = Compet.objects.filter(compet_id=200000).order_by('compet_id')
        compet = Compet()
        compets = []
        compet.compet_name = "Teste da Silva"
        compet.compet_email = 'ranido@unicamp.br'
        compet.compet_school_id = 1
        compet.user = User.objects.get(id=2)
        compets.append(compet)
        #compet.compet_name = "Marcelo Morais"
        #compet.compet_email = 'marcelo@fundacaobehring.org'
        #compet.compet_school_id = 1
        #compet.user = User.objects.get(id=2)
        #compets.append(compet)

    else:
        return -1,-1
    
    # if Fase 2
    #compets = compets.filter(compet_classif_fase1=True)

    #compets = Compet.objects.filter(compet_type__in=(3,5),compet_sex='F',compet_email__isnull=False)
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase1=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_classif_fase2=True).order_by('compet_id')
    #compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_classif_fase2=True).order_by('compet_id')

    
    print('num target compets:',len(compets))

    count,failed = 0,0

    # do not send to coordinators
    schools = School.objects.all()
    coord_emails = set()
    # for s in schools:
    #     coord_emails.add(s.school_deleg_email)
    # print("coord_emails:", len(coord_emails), file=sys.stderr)

    sent_file = "mensagem_semana_enviados.txt"
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

        # TEMPORARY -- WEEK
        if c.compet_sex == 'F':
            greetings = 'Cara Competidora'
            greetings = 'Cara participante'
            suffix = 'a'
        else:
            greetings = 'Caro Competidor'
            greetings = 'Caro participante'
            suffix = 'o'



        try:
            s = schools.get(pk=c.compet_school_id)
        except:
            s = schools.get(pk=1)
            
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
            print('warning, no compet user:', c.compet_id, c.compet_name)  
        elif to_address and to_address.lower() != c.user.email.lower():
            print('warning, different emails compet email:', c.compet_email, 'user email:', c.user.email, 'user:',c.user)

        if not to_address:
            #print('no email -- compet_email:', c.compet_email, 'user:',c.user)
            continue

        context = {'compet': c, 'school': s, 'greetings':greetings, 'suffix': suffix}

        if msg_to_addresses in ('ajuda-sede-fase3-prog',):
            context['mod_name'] = 'Programação'
            context['mod_date'] = '1 de outubro'

        body_txt = template_txt.render(context)
        if template_htm:
            body_htm = template_htm.render(context)
        else:
            body_htm = ""
        subject = msg_subject
        priority = 1
        m = QueuedMail(\
            subject=subject,
            body=body_txt,
            body_html=body_htm,
            from_addr=DEFAULT_FROM_EMAIL,
            to_addr=to_address,
            priority=priority
        )
        m.save()
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
