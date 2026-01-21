import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import School, Compet, LEVEL_NAME, REGULAR_PUBLIC, REGULAR_PRIVATE, HIGHER_PUBLIC, HIGHER_PRIVATE, SPECIAL

def do_it(first_year, last_year):
    print(",".join(["Ano", "Pública", "Privada"]))
    for year in range(first_year, last_year+1):

        if year == 2021:
            compets = Compet.objects.using(f'obi{year}').filter(compet_points_fase2__gt=0).only('compet_type','compet_points_fase1','compet_sex')
        else:
            compets = Compet.objects.using(f'obi{year}').filter(compet_points_fase1__gt=0).only('compet_type','compet_points_fase1','compet_sex')

        compets_public = compets.filter(compet_school__school_type__in=[REGULAR_PUBLIC,HIGHER_PUBLIC])
        compets_private = compets.filter(compet_school__school_type__in=[REGULAR_PRIVATE,HIGHER_PRIVATE,SPECIAL])
        percent_public = 100.0*len(compets_public)/len(compets)
        percent_private = 100.0*len(compets_private)/len(compets)

        print("compets_public",compets_public)
        print("compets_private",compets_private)
        print(f"{year}, {percent_public:.2f}, {percent_private:.2f}")


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
