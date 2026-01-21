import logging
from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.utils.get_certif import (get_week_certif_monitor,)

class Command(BaseCommand):
    help = 'generate certificate'

    def add_arguments(self, parser):
        parser.add_argument('monitor_name', nargs='+', type=str)
        parser.add_argument('monitor_genre', nargs='+', type=str)
        parser.add_argument('year', nargs='+', type=int)

    def handle(self, *args, **options):
        monitor_name = options['monitor_name'][0]
        monitor_genre = options['monitor_genre'][0]
        year = options['year'][0]
        slug = slugify(monitor_name)
        data = get_week_certif_monitor(monitor_name=monitor_name, genre=monitor_genre, hours=35, year=year)

        with open(f"/tmp/Certif_{slug}_{year}.pdf",'wb') as f:
            f.write(data)
        self.stdout.write(self.style.SUCCESS(f'Generated certif in /tmp/Certif_{slug}_{year}.pdf'))
