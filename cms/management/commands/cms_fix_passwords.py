import sys
import logging

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL_NAME, PasswordCms
from exams.models import TesteFase1
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def cms_fix_passwords():
    # if modality == 'p':
    #     compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    # else:
    #     print('wrong modality')
    #     return 0
    count = 0

    compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    #compets = compets.filter(compet_email__isnull=False,user__isnull=True)
    print(f'found {len(compets)} to fix')
    passwords = PasswordCms.objects.all()
    in_cms = []
    for p in passwords:
        in_cms.append(p.compet_id)
    print(f'found {len(in_cms)} in_cms')
    for c in compets:
        if c.compet_id in in_cms:
            continue
        #logger.info('fixing compet_id:{} - {}, user:{}'.format(c.compet_id, c.compet_name, c.user))
        #print('-----')
        #print('fixing {} - {}, user:{}'.format(c.compet_id_full, c.compet_name, c.user))
        password = make_password(separator='.')
        p = PasswordCms()
        p.compet_id = c.compet_id
        p.password = password
        p.save()
        count += 1
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        #parser.add_argument('modality', nargs='+', type=str)
        pass
    
    def handle(self, *args, **options):
        #modality = options['modality'][0]
        count = cms_fix_passwords()
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
