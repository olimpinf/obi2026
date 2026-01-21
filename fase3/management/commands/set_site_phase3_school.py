import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from fase3.utils.check_solutions_file import Error, check_solutions_file

PHASE = 3

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('school_city', nargs='+', type=str)
        parser.add_argument('school_state', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=int)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        school_city = options['school_city'][0]
        school_state = options['school_state'][0]
        level = options['level'][0]
        school_id = options['school_id'][0]
        site = School.objects.get(pk=school_id)
        if level in (0,1,2):
            site.school_site_phase3_type=level
        else:
            self.stdout.write(self.style.SUCCESS('level must be 0, 1 or 2. No change.'))
            return

        if level == 0:
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_school_id=school_id,compet_school__school_state=school_state).only('compet_school_id').distinct()
        elif level == 1:
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(1,2,7),compet_school_id=school_id,compet_school__school_state=school_state).only('compet_school_id').distinct()
        else:
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(3,4,5,6),compet_school_id=school_id,compet_school__school_state=school_state).only('compet_school_id').distinct()

        print(f'compets: {len(compets)}')
        school_ids = [school_id]
        #schools = School.objects.filter(school_ok=True,school_city=school_city,school_state=school_state)
        schools = School.objects.filter(school_id__in=school_ids)
        print('Escolas:')
        for s in schools:
            print(s.school_id,s.school_name)
        self.stdout.write(self.style.SUCCESS(f'Sede: {site.school_id} {site.school_name}'))
        print("  --- y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.SUCCESS('No change'))
            return
        for s in schools: # does not work for site, due to open connection??
            if s.school_id==site.school_id:
                continue
            s.school_site_phase3 = school_id # do not need anymore...
            if level == 0:
                s.school_site_phase3_prog = school_id
                s.school_site_phase3_ini = school_id
            elif level == 1:
                s.school_site_phase3_ini = school_id
            else: # level == 2
                s.school_site_phase3_prog = school_id
            s.save()

        site.school_site_phase3_type=level
        if level == 0:
            site.school_site_phase3_prog = school_id
            site.school_site_phase3_ini = school_id
        elif level == 1:
            site.school_site_phase3_ini = school_id
        else: # level == 2
                site.school_site_phase3_prog = school_id
        site.save()
        self.stdout.write(self.style.SUCCESS('OK'))
        print("show site  --- y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.SUCCESS('Show = false'))
            site.school_site_phase3_show = False
        else:
            site.school_site_phase3_show = True
            self.stdout.write(self.style.SUCCESS('Show = true'))
        site.save()
