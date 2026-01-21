import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School

class Command(BaseCommand):
    help = 'Set phase 3 site for a compet'

    def add_arguments(self, parser):
        parser.add_argument('compet_level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        tmp = options['compet_level'][0]
        level = LEVEL[tmp.upper()]
        compet_id = options['compet_id'][0]
        school_id = options['school_id'][0]
        site = School.objects.get(pk=school_id)
        try:
            compet = Compet.objects.get(pk=compet_id,compet_type=level)
        except:
            self.stdout.write(self.style.ERROR('Wrong compet level'))
            self.stdout.write(self.style.ERROR('No change'))
            return
        school = School.objects.get(pk=compet.compet_school_id)
        print(f'compet: {compet.compet_id_full} - {compet.compet_name}')
        print(f'school: {school.school_name}  ({school.school_city}/{school.school_state})')
        print(f'site: {site.school_name}  ({site.school_city}/{site.school_state})')
        print("\n---> y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.ERROR('No change'))
            return

        compet.compet_school_id_fase3 = site.school_id
        compet.save()
        self.stdout.write(self.style.SUCCESS('Done'))
