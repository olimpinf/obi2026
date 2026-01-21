import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import Compet, School

def cities_to_sites_all(self):
    return

def check_sites(mod):
    if mod == 'ini':
        compet_types = (1,2,7)
    else:
        compet_types = (3,4,5,6)
    cs = Compet.objects.filter(compet_type__in=compet_types,compet_classif_fase2=True).distinct().only('compet_school_id')
    schools_with_compet = set()
    for k in cs:
        schools_with_compet.add(k.compet_school_id)
    schools = School.objects.filter(school_id__in=schools_with_compet).order_by('school_state','school_city')

    count = 0
    for s in schools:
        if mod == 'ini':
            if s.school_site_phase3_ini == 0:
                print(f'Site ini missing for {s.school_id} {s.school_name} - {s.school_city}/{s.school_state}')
                count += 1
        else:
            if s.school_site_phase3_prog == 0:
                print(f'Site prog missing for {s.school_id} {s.school_name} - {s.school_city}/{s.school_state}')
                count += 1

    print(f"site {mod} missing for {count} schools")
    print()
    
class Command(BaseCommand):
    help = 'build sites phase 3 from csv file'

    def add_arguments(self, parser):
      parser.add_argument('mod', nargs='+', type=str)

    def handle(self, *args, **options):
        mod = options['mod'][0]
        if mod == 'all':
            check_sites('ini')
            check_sites('prog')
        elif mod in ('ini','prog'):
            check_sites(mod)
        else:
            print("wrong mod", file=sys.stderr)
