import logging
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL_NAME
from exams.models import TesteFase1
from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
logger = logging.getLogger(__name__)

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"
from exams.models  import ExamFase2

def authorize(self,c,exam):
    school = School.objects.get(school_id=c.compet_school_id)
    exam_compets = exam.objects.filter(school=school)
    try:
        # already authorized?
        ex = exam_compets.get(compet=c,school=school)
        self.stdout.write(self.style.SUCCESS('Autorização já existe para {} - {}.'.format(c.compet_id,c.compet_name)))
    except:
        # not authorized, then authorize, but only if compet has user
        if c.user:
            ex = exam(compet=c,school=school)
            ex.save()
            self.stdout.write(self.style.SUCCESS('Autorização OK para {} - {}.'.format(c.compet_id,c.compet_name)))
        elif c.compet_email and len(c.compet_email.strip()) > 0:
            self.stdout.write(self.style.ERROR('Autorização falhou para {}, não tem usuário criado,  email {}'.format(c,c.compet_email)))
        else:
            pass
            #self.stdout.write(self.style.ERROR('Autorização falhou para {}, não tem usuário criado nem  email'.format(c)))

def fix_compet_auth(self):
    PROG = False
    if PROG:
        levels = (3,4,5,6)
        #compets = Compet.objects.filter(compet_type__in=levels, compet_school__school_turn_phase1_prog='B')
        #schools = School.objects.filter(school_turn_phase1_prog='B').only('school_id','school_name')
    else:
        levels = (1,2,7)
        compets = Compet.objects.filter(compet_type__in=levels, compet_classif_fase1=True).order_by('compet_id')
    print('compets',len(compets))
    authorized = ExamFase2.objects.all().only('compet_id')
    print('authorized',len(authorized))
    count = 0
    for c in compets:
        if not authorized.filter(compet_id=c.compet_id).exists():
            count += 1
            authorize(self,c,ExamFase2)
    return count

class Command(BaseCommand):
    help = 'Fix authorizations'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('msg_subject', nargs='+', type=str)
        #parser.add_argument('msg_body', nargs='+', type=str)
        #parser.add_argument('msg_to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        # msg_subject = options['msg_subject'][0]
        # msg_body = options['msg_body'][0]
        # msg_to_addresses = options['msg_to_addresses'][0]
        # count = send_messages(msg_subject, msg_body, msg_to_addresses)
        count = fix_compet_auth(self)
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
