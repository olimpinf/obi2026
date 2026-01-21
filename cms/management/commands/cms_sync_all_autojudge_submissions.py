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
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)

from cms.utils import cms_sync_all_autojudge_submissions


logger = logging.getLogger(__name__)



class Command(BaseCommand):
    help = 'Update cms passwords'

    def add_arguments(self, parser):
        #parser.add_argument('contest_id', nargs='+', type=str)
        parser.add_argument('exam_descriptor', nargs='+', type=str)

    def handle(self, *args, **options):
        exam_descriptor= options['exam_descriptor'][0]
        count = cms_sync_all_autojudge_submissions(exam_descriptor)
        self.stdout.write(self.style.SUCCESS(f'Copied {count} submissions.'))
