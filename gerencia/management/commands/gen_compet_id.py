import sys
import logging

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetExtra, LEVEL_NAME
from exams.models import TesteFase1
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

    
def gen_compet_id():
    count = 0
    all = Compet.objects.all()
    compets = Compet.objects.filter(compet_id_full='').order_by('compet_id')
    print("all compets", len(all))
    print("missing compets", len(compets))
    for c in compets:
        print(c.compet_id,c.compet_id_full)
        c.compet_id_full = format_compet_id(c.compet_id)
        print(c.compet_id_full)
        c.save()
        count += 1
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        #modality = options['modality'][0]
        count = gen_compet_id()
        self.stdout.write(self.style.SUCCESS('Found {} compets.'.format(count)))
