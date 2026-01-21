import os
import sys
from itertools import chain

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
from principal.models import School, Colab, Compet, IJ, I1, I2, PJ, P1, P2, PS
from week.models import Week

DO_SEND = True

def send_messages(msg_subject,msg_template,msg_to_addresses):

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))

    if msg_to_addresses == 'all':
        coords = School.objects.filter(school_ok=True).distinct('school_deleg_email').order_by('school_deleg_email').only('school_deleg_email','school_deleg_name')
        colabs = Colab.objects.distinct('colab_email').order_by('colab_email').only('colab_email','colab_name')
        coords = list(chain(coords,colabs))
    elif msg_to_addresses == 'coord':
        coords = School.objects.filter(school_ok=True).only('school_deleg_email','school_deleg_name').distinct()
    elif msg_to_addresses == 'ini':
        schools_with_compet = Compet.objects.filter(compet_type__in=(IJ,I1,I2)).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print(len(schools_with_compet))
        school_ini_set = set()
        for s in schools_with_compet:
            school_ini_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name').distinct()
        print(len(coords))
    elif msg_to_addresses == 'progf2':
        schools_with_compet = Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS),compet_classif_fase1=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print(len(schools_with_compet))
        school_ini_set = set()
        for s in schools_with_compet:
            school_ini_set.add(s.compet_school_id)
        # wrong coords = School.objects.filter(school_id__in=school_ini_set).only('school_deleg_email','school_deleg_name').distinct()
        print(len(coords))
        print(coords)        
    elif msg_to_addresses == 'progf3':
        schools_with_compet = Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS),compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print(len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'inif3':
        schools_with_compet = Compet.objects.filter(compet_type__in=(IJ,I1,I2),compet_classif_fase2=True).only('compet_school_id').distinct('compet_school_id').order_by('compet_school_id')
        print(len(schools_with_compet))
        school_prog_set = set()
        for s in schools_with_compet:
            school_prog_set.add(s.compet_school_id)
        coords = School.objects.filter(school_id__in=school_prog_set).only('school_deleg_email','school_deleg_name').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_prog_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
        print(len(coords))
    elif msg_to_addresses == 'week':
        tmp = Week.objects.filter(compet__compet_type__in=(1,2,3,5))
        compets = []
        for t in tmp:
            c = t.compet
            compets.append(c)
        
        school_week_set = set()
        for c in compets:
            school_week_set.add(c.compet_school_id)
        coords = School.objects.filter(school_id__in=school_week_set).only('school_deleg_email','school_deleg_name').distinct()
        colabs = Colab.objects.filter(colab_school_id__in=school_week_set).only('colab_email','colab_name').distinct()
        coords = list(chain(coords,colabs))
    elif msg_to_addresses == 'test':
        coords = School.objects.filter(school_id=1).only('school_deleg_email','school_deleg_name').distinct()
        #colabs = Colab.objects.distinct('colab_email').order_by('colab_email').only('colab_email','colab_name')
        #coords = list(chain(coords,colabs))
    else:
        print('??')
        return 0
    print('num_emails:',len(coords))

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))
    
    count,failed = 0,0
    for coord in coords:
        try:
            to_address = coord.school_deleg_email
            to_name = coord.school_deleg_name
            to_school_name = coord.school_name
            greetings = "Caro(a) Prof(a)."
        except:
            try:
                to_address = coord.colab_email
                to_name = coord.colab_name
                to_school_name = coord.colab_school.school_name
                if  coord.colab_sex == 'M':
                    greetings = "Caro Prof."
                if  coord.colab_sex == 'F':
                    greetings = "Cara Profa."
                else:
                    greetings = "Caro(a) Prof(a)."
            except:
                print('\nfailed *********** {} failed'.format(coord), file=sys.stderr)
        if not to_address or not to_name or not to_school_name:
            print('******* missing data',to_address,to_name,to_school_name)
            continue
        # fixed to include colabs, must change templates accordingly! It was: context = {"greetings": "Caro(a) Prof(a).",'school': coord}
        context = {"greetings": greetings,'school_name': to_school_name, 'coord_name': to_name}
        body = template.render(context)
        connection = mail.get_connection()
        connection.open()
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
            print('{};{} - sent'.format(to_address, to_name),file=sys.stderr)
            sys.stderr.flush()
            count += 1
            sleep(1.5)
        except:
            print('\nto_address {}, {} *********** failed'.format(to_address, to_name), file=sys.stderr)
            failed += 1

        connection.close()

    #connection.close()
    return count


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
        count = send_messages(msg_subject, msg_template, msg_to_addresses)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
