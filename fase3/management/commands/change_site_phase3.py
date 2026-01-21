import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.db import connection

from principal.models import School

class Command(BaseCommand):
    help = 'Change phase 3 site from school A to school B'

    def add_arguments(self, parser):
        parser.add_argument('mod', nargs='+', type=str)
        parser.add_argument('schoolA_city', nargs='+', type=str)
        parser.add_argument('schoolA_id', nargs='+', type=int)
        parser.add_argument('schoolB_city', nargs='+', type=str)
        parser.add_argument('schoolB_id', nargs='+', type=int)
        parser.add_argument("--no-prompt", default=True, action="store_false")

    def handle(self, *args, **options):
        mod = options['mod'][0]
        schoolA_city = options['schoolA_city'][0]
        schoolA_id = options['schoolA_id'][0]
        schoolB_city = options['schoolB_city'][0]
        schoolB_id = options['schoolB_id'][0]
        prompt = options['no_prompt']

        try:
            schoolA = School.objects.get(pk=schoolA_id,school_city=schoolA_city)
        except:
            self.stdout.write(self.style.ERROR('Wrong school A city'))
            self.stdout.write(self.style.ERROR('No change'))
            return '-1'

        try:
            schoolB = School.objects.get(pk=schoolB_id,school_city=schoolB_city)
        except:
            self.stdout.write(self.style.ERROR('Wrong school B city'))
            self.stdout.write(self.style.ERROR('No change'))
            return '-2'

        print(f'previous site: {schoolA.school_id} - {schoolA.school_name} - {schoolA.school_city}/{schoolA.school_state}')
        print(f'new site: {schoolB.school_id} - {schoolB.school_name} - {schoolB.school_city}/{schoolB.school_state}')

        if prompt:
            print("\n---> y/n?", end=' ')
            go = input()
            if go != 'y':
                self.stdout.write(self.style.ERROR('No change'))
                return '1'

        schoolA.school_is_site_phase3 = False
        schoolA.school_site_phase3 = 0 # not defined
        schoolA.school_site_phase3_show = False
        schoolA.save()

        if mod == 'ini':
            school_cities = School.objects.filter(school_site_phase3_ini=schoolA.school_id).values_list('school_city', 'school_state')
        else:
            school_cities = School.objects.filter(school_site_phase3_prog=schoolA.school_id).values_list('school_city', 'school_state')

        school_cities = set(school_cities | School.objects.filter(school_id=schoolA.school_id).values_list('school_city', 'school_state'))

        for city, state in school_cities:
            call_command('atualiza_sede', mod, city, state, schoolB.school_id)

        self.stdout.write(self.style.SUCCESS('Change Site Done'))
