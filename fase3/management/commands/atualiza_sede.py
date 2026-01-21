import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.contrib.auth.models import Group, User
from django.core.management import call_command

from principal.models import IJ, I1, I2, PJ, P1, P2, PS, LEVEL, LEVEL_NAME, Compet, School

def update_sedes(mod, city, state, site_id):
    schools = School.objects.filter(school_city=city,school_state=state)

    if len(schools) == 0:
        print(f'Nao ha escolas em {city}/{state}')

    sede = School.objects.get(school_id=site_id)
    call_command('confirm_school_is_site_phase3', mod, sede.school_city, sede.school_id, no_prompt=False)

    # school_site_phase3: 0 = not defined, 1 = same as city, 2 = custom ini, 3 = custom prog, 4 = custom both

    if mod == 'ini':
        school_ids = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(IJ,I1,I2),
                                           compet_school_id__in=School.objects.filter(school_city=city,
                                                                                      school_state=state)).values_list('compet_school_id', flat=True)

        for school in School.objects.filter(school_id__in=school_ids):
            if school.school_site_phase3 in (2, 4):
                print(f'School { school.school_id } has custom site. Skipping...')
                continue

            if school.school_id != sede.school_id:
                school.school_is_site_phase3 = False

            school.school_site_phase3 = 1 # same as city site

            if school.school_site_phase3_ini <= 0:
                print(f'New site for School { school.school_id }: {sede.school_id}')
            elif school.school_site_phase3_ini != sede.school_id:
                print(f'Site changed for School { school.school_id }: from {school.school_site_phase3_ini} to {sede.school_id}')

            school.school_site_phase3_ini = sede.school_id

            school.save()
    else:
        school_ids = Compet.objects.filter(compet_classif_fase2=True, compet_type__in=(PJ,P1,P2,PS),
                                           compet_school_id__in=School.objects.filter(school_city=city,
                                                                                      school_state=state)).values_list('compet_school_id', flat=True)

        for school in School.objects.filter(school_id__in=school_ids):
            if school.school_site_phase3 in (3, 4):
                print(f'School { school.school_id } has custom site. Skipping...')
                continue

            if school.school_id != sede.school_id:
                school.school_is_site_phase3 = False

            school.school_site_phase3 = 1 # same as city site

            if school.school_site_phase3_prog <= 0:
                print(f'New site for School { school.school_id }: {sede.school_id}')
            elif school.school_site_phase3_prog != sede.school_id:
                print(f'Site changed for School { school.school_id }: from {school.school_site_phase3_prog} to {sede.school_id}')

            school.school_site_phase3_prog = sede.school_id

            school.save()

class Command(BaseCommand):
    help = 'Change school_site_phase3_ini or school_site_phase3_prog for one site'

    def add_arguments(self, parser):
        parser.add_argument('mod', nargs='+', type=str) # 'ini' or 'prog'
        parser.add_argument('city', nargs='+', type=str)
        parser.add_argument('state', nargs='+', type=str)
        parser.add_argument('site_id', nargs='+', type=int)

    def handle(self, *args, **options):
        mod = options['mod'][0]
        city = options['city'][0]
        state = options['state'][0]
        site_id = options['site_id'][0]

        update_sedes(mod, city, state, site_id)
        self.stdout.write(self.style.SUCCESS('Update Sites Done'))
