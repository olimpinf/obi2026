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
from principal.utils.cms import (cms_add_user, cms_update_password)

logger = logging.getLogger(__name__)


def cms_add_users(self, compet_type, compet_id_full, contest_id):
    compet_id, ext = verify_compet_id(compet_id_full)
    if compet_id == 0:
        # all users
        compets = Compet.objects.filter(compet_type=compet_type)
    else:
        compets = Compet.objects.filter(compet_id=int(compet_id))

    count = 0
    for c in compets:
        print("cms_add_user",c, contest_id)
        count += cms_add_user(c, compet_type, contest_id)
    return count


class Command(BaseCommand):
    help = 'Add CMS users'

    def add_arguments(self, parser):
        parser.add_argument('compet_type', nargs='+', type=str)
        parser.add_argument('compet', nargs='+', type=str)
        parser.add_argument('contest_id', nargs='+', type=str)

    def handle(self, *args, **options):
        compet_type = options['compet_type'][0].upper()
        compet = options['compet'][0]
        compet_type = LEVEL[compet_type]
        contest_id = options['contest_id'][0]
        count = cms_add_users(self, compet_type, compet, contest_id)
        self.stdout.write(self.style.SUCCESS('Added {} cms users.'.format(count)))
