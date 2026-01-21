import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import School

class Command(BaseCommand):
    help = 'Set phase 3 site for a school'

    def add_arguments(self, parser):
        parser.add_argument('mod', nargs='+', type=str)
        parser.add_argument('school_city', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('site_id', nargs='+', type=int)

    def handle(self, *args, **options):
        mod = options['mod'][0]
        school_city = options['school_city'][0]
        school_id = options['school_id'][0]
        site_id = options['site_id'][0]
        site = School.objects.get(pk=site_id)

        try:
            school = School.objects.get(pk=school_id,school_city=school_city)
        except:
            self.stdout.write(self.style.ERROR('Wrong school city'))
            self.stdout.write(self.style.ERROR('No change'))
            return

        print(f'school: {school.school_id} - {school.school_name} - {school.school_city}/{school.school_state}')
        print(f'site: {site.school_id} - {site.school_name} - {site.school_city}/{site.school_state}')
        print("\n---> y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.ERROR('No change'))
            return

        # school_site_phase3: 0 = not defined, 1 = same as city, 2 = custom ini, 3 = custom prog, 4 = custom both

        if mod == 'ini':
            if school.school_site_phase3 in (3, 4):
                school.school_site_phase3 = 4 # custom both
            else:
                school.school_site_phase3 = 2 # custom ini

            school.school_site_phase3_ini = site.school_id
        else:
            if school.school_site_phase3 in (2, 4):
                school.school_site_phase3 = 4 # custom both
            else:
                school.school_site_phase3 = 3 # custom ini

            school.school_site_phase3_prog = site.school_id

        school.save()

        self.stdout.write(self.style.SUCCESS('Done'))
