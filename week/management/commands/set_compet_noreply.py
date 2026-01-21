import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from week.models import STATUS, Week
from principal.models import LEVEL, Compet

class Command(BaseCommand):
    help = 'Set compet did not reply to Week form'

    def add_arguments(self, parser):
        parser.add_argument('compet_level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        level_short_name = options['compet_level'][0].upper()
        print(level_short_name)
        level = LEVEL[level_short_name]
        print(level)
        compet_id = options['compet_id'][0]
        try:
            week = Week.objects.get(compet_id=compet_id,compet_type=level)
        except:
            self.stdout.write(self.style.ERROR('Wrong compet level'))
            self.stdout.write(self.style.ERROR('No change'))
            return
        compet = Compet.objects.get(compet_id=compet_id)
        print(f'compet did not reply: {compet.compet_id} - {compet.compet_name} - {level_short_name}')
        print("\n---> y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.ERROR('No change'))
            return

        week.status = STATUS['no_reply']
        week.save()
        self.stdout.write(self.style.SUCCESS('Done'))
