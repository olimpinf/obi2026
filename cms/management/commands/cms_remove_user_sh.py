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
from cms.utils import cms_remove_user
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Remove cms user'

    def add_arguments(self, parser):
        parser.add_argument('compet_id', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        compet_id_full = options['compet_id'][0]
        level = options['level'][0].upper()
        compet_type = LEVEL[level]
        print(compet_id_full,compet_type)
        count = cms_remove_user(compet_id_full,compet_type)
        self.stdout.write(self.style.SUCCESS('Removed {} cms users.'.format(count)))
