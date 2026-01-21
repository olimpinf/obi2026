import logging
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.utils.get_certif import (get_week_certif_compet,)

class Command(BaseCommand):
    help = 'generate certificate'

    def add_arguments(self, parser):
        parser.add_argument('compet_id', nargs='+', type=int)
        parser.add_argument('compet_type', nargs='+', type=int)
        parser.add_argument('year', nargs='+', type=int)

    def handle(self, *args, **options):
        compet_id = options['compet_id'][0]
        compet_type = options['compet_type'][0]
        year = options['year'][0]
        data = get_week_certif_compet(compet_id,compet_type,year)
        with open(f"/tmp/Certif_{compet_id}_{year}.pdf",'wb') as f:
            f.write(data)
        self.stdout.write(self.style.SUCCESS(f'Generated certif in /tmp/Certif_{compet_id}_{year}.pdf'))
