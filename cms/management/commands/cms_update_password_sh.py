import logging
import os
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL, PJ, P1, P2, PS
from principal.utils.cms import (cms_update_password)
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update cms passwords'

    def add_arguments(self, parser):
        parser.add_argument('compet', nargs='+', type=str)

    def handle(self, *args, **options):
        compet_id_full = options['compet'][0]
        compet_id, ext = verify_compet_id(compet_id_full)
        compet = Compet.objects.get(compet_id=int(compet_id))
        count = cms_update_password(compet)
        self.stdout.write(self.style.SUCCESS('Updated {} cms users.'.format(count)))
