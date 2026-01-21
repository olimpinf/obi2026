import sys
import logging

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL_NAME
from exams.models import TesteFase1
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def fix_compet_emails(modality):
    if modality == 'i':
        compets = Compet.objects.filter(compet_type__in=(1,2,7))
    elif modality == 'p':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    else:
        print('wrong modality')
        return 0
    count = 0

    compets = compets.order_by('compet_id')
    print(f'found {len(compets)} to fix)')

    for c in compets:
        if c.compet_email:
            compet_email = c.compet_email.strip()
        
            if compet_email != c.compet_email:
                print('******* strip diff in compet_email',end=' ')
            if compet_email=="":
                print('blank space compet email {},{}'.format(c.compet_name,LEVEL_NAME[c.compet_type]))
                #sys.exit(-1)
                #continue
        else:
            compet_email = ""

        try:
            user = User.objects.get(username=c.compet_id_full)
        except:
            print('user does not exist???', c.compet_id_full)
            sys.exit(1)
        if user.email:
            user_email = user.email.strip()
        
            if user_email != user.email:
                print('******* strip diff in user email',end=' ')
            if user_email=="":
                print('blank space user email {},{}'.format(c.compet_name,LEVEL_NAME[c.compet_type]))
                #sys.exit(-1)
                #continue
        else:
            user_email = ""

            
        if user_email != compet_email:
            user.email = compet_email
            #print(c.compet_id_full, c.compet_name, compet_email, user_email)
            user.save()
            count += 1
            
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        modality = options['modality'][0]
        count = fix_compet_emails(modality)
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
