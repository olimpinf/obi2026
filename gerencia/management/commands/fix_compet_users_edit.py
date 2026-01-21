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

def fix_compet_users():
    compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_email__isnull=False,user__isnull=True,compet_classif_fase1=True)
    count = 0
    for c in compets:
        email = c.compet_email.strip()
        if email != c.compet_email:
            print('******* strip diff',end=' ')
            break
        if email=="":
            #print('blank space email {},{}'.format(c.compet_name,LEVEL_NAME[c.compet_type]))
            continue

        try:
            user = User.objects.get(username=email)
        except:
            print("no user with email",email)
            continue

        logger.info('fixing compet_id:{} - {}, user:{}, email:{}'.format(c.compet_id, c.compet_name, c.user, email))
        print('fixing {} - {}, user:{}'.format(c.compet_id, c.compet_name, c.user))
        c.user_id = user.id
        try:
            c.save()
        except:
            print('FAILED fixing {} - {}, user:{}'.format(c.compet_id, c.compet_name, c.user))
            
        count += 1
    return count

class Command(BaseCommand):
    help = 'Send message'

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
        count = fix_compet_users()
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
