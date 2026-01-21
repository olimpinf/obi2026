import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import School, Compet, LEVEL_NAME, REGULAR_PUBLIC, REGULAR_PRIVATE, HIGHER_PUBLIC, HIGHER_PRIVATE, SPECIAL

def do_it(first_year, last_year):
    print(",".join(["Ano", "Pública", "Privada"]))
    for year in range(first_year, last_year+1):

        if year == 2021:
            compets_effective = Compet.objects.using(f'obi{year}').filter(compet_points_fase2__gt=0).only('compet_school_id').distinct()
        else:
            compets_effective = Compet.objects.using(f'obi{year}').filter(compet_points_fase1__gt=0).only('compet_school_id').distinct()

        compets = Compet.objects.using(f'obi{year}').all().only('compet_school_id').distinct()
        school_ids = set()
        for compet in compets:
            school_ids.add(compet.compet_school_id)
        school_ids_effective = set()
        for compet in compets_effective:
            school_ids_effective.add(compet.compet_school_id)
        
        schools_partic = School.objects.using(f'obi{year}').filter(school_id__in=school_ids)
        schools_effective = School.objects.using(f'obi{year}').filter(school_id__in=school_ids_effective)

        schools_public_effective = schools_effective.filter(school_type__in = [REGULAR_PUBLIC, HIGHER_PUBLIC])
        percent_public_effective = 100.0*len(schools_public_effective)/len(schools_effective)
        percent_private_effective = 100.0 - percent_public_effective

        schools_public = schools_partic.filter(school_type__in = [REGULAR_PUBLIC, HIGHER_PUBLIC])
        percent_public = 100.0*len(schools_public)/len(schools_partic)
        percent_private = 100.0 - percent_public

        print("schools_partic", len(schools_partic))
        print("schools_public", len(schools_public))

        #print("schools_effective", len(schools_effective))
        #print("schools_public_effective", len(schools_public_effective))
        #print(f"{year},{percent_public:.2f},{percent_private:.2f},{percent_public_effective:.2f},{percent_private_effective:.2f}")
        print(f"{year},{percent_public_effective:.2f},{percent_private_effective:.2f}")


    return

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('first_year', nargs='+', type=int)
        parser.add_argument('last_year', nargs='+', type=int)
        
    def handle(self, *args, **options):
        first_year= options['first_year'][0]
        last_year= options['last_year'][0]
        do_it(first_year, last_year)
        #self.stdout.write(self.style.SUCCESS('OK'))
