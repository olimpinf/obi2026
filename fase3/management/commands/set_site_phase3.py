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
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('site_type', nargs='+', type=int)

    def handle(self, *args, **options):
        school_city = options['school_city'][0]
        school_state = options['school_state'][0]
        school_id = options['school_id'][0]
        site_type = options['site_type'][0]
        site = School.objects.get(pk=school_id)
        if site_type in (0,1,2,3):
            site.school_site_phase3_type=site_type
        else:
            self.stdout.write(self.style.SUCCESS('site_type must be 0 (remove), 1 (site for ini+prog), 2 (site for ini), 3 (site for prog). No change.'))
            return

        if site_type == 0:
            # will not be a phase 3 site, remove if it currently is 
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_school__school_city__icontains=school_city,compet_school__school_state=school_state).only('compet_school_id').distinct()
        elif site_type == 1:
            # will be a phase 3 site for ini+prog
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_school__school_city__icontains=school_city,compet_school__school_state=school_state).only('compet_school_id').distinct()
        elif site_type == 2:
            # will be a phase 3 site for ini
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(1,2,7),compet_school__school_city__icontains=school_city,compet_school__school_state=school_state).only('compet_school_id').distinct()
        else:
            # will be a phase 3 site for prog
            compets = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(3,4,5,6),compet_school__school_city__icontains=school_city,compet_school__school_state=school_state).only('compet_school_id').distinct()
            
        print(f'compets: {len(compets)}')
        school_ids = []
        for x in compets:
            school_ids.append(x.compet_school_id)

        #schools = School.objects.filter(school_ok=True,school_city__icontains=school_city,school_state=school_state)
        schools = School.objects.filter(school_id__in=school_ids)
        print('Escolas:')
        for s in schools:
            print(s.school_id,s.school_name)
        self.stdout.write(self.style.SUCCESS(f'Sede: {site.school_id} {site.school_name}'))
        self.stdout.write(self.style.SUCCESS(f'Comando: {site_type} (0=remove, 1=ini+prog, 2=ini, 3=prog)'))
        print("  --- y/n?", end=' ')
        go = input()
        if go != 'y':
            self.stdout.write(self.style.SUCCESS('No change'))
            return
        for s in schools: # does not work for site, due to open connection??
            if s.school_id==site.school_id:
                continue
            if site_type == 0:
                s.school_site_phase3_prog = 0
                s.school_site_phase3_ini = 0
            elif site_type == 1:
                s.school_site_phase3_ini = school_id
                s.school_site_phase3_prog = school_id
            elif site_type == 2:
                s.school_site_phase3_ini = school_id
            elif site_type == 3:
                s.school_site_phase3_prog = school_id
            else:
                print("wrong site_type", file=sys.stderr)
                sys.exit(0)
            s.save()

        site.school_site_phase3_type=site_type
        if site_type == 0:
            site.school_site_phase3_prog = 0
            site.school_site_phase3_ini = 0
        elif site_type == 1:
            site.school_site_phase3_ini = school_id
            site.school_site_phase3_prog = school_id
        elif site_type == 2:
            site.school_site_phase3_ini = school_id
        elif site_type == 3:
            site.school_site_phase3_prog = school_id
        else:
            print("wrong site_type", file=sys.stderr)
            sys.exit(0)
        site.save()
        self.stdout.write(self.style.SUCCESS('OK'))
        if site_type == 0:
            site.school_site_phase3_show = False
        else:            
            print("show site  --- y/n?", end=' ')
            go = input()
            if go != 'y':
                self.stdout.write(self.style.SUCCESS('Show = false'))
                site.school_site_phase3_show = False
            else:
                site.school_site_phase3_show = True
                self.stdout.write(self.style.SUCCESS('Show = true'))
        site.save()
