import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import School, Compet, LEVEL_NAME



def do_it(first_year, last_year):
    print(",".join(["Ano", "IJ", "I1", "I2", "PJ", "P1", "P2", "PS"]))
    for year in range(first_year, last_year+1):

        if year == 2021:
            compets = Compet.objects.using(f'obi{year}').filter(compet_points_fase2__gt=0).only('compet_type','compet_points_fase1','compet_sex')
        else:
            compets = Compet.objects.using(f'obi{year}').filter(compet_points_fase1__gt=0).only('compet_type','compet_points_fase1','compet_sex')

        if year >= 2018:
            competsIJ = compets.filter(compet_type=7)
        competsI1 = compets.filter(compet_type=1)
        competsI2 = compets.filter(compet_type=2)
        competsPJ = compets.filter(compet_type=5)
        competsP1 = compets.filter(compet_type=3)
        competsP2 = compets.filter(compet_type=4)
        if year >= 2014:
            competsPS = compets.filter(compet_type=6)

        if year >= 2018:
            girlsIJ = compets.filter(compet_type=7, compet_sex='F')
        girlsI1 = compets.filter(compet_type=1, compet_sex='F')
        girlsI2 = compets.filter(compet_type=2, compet_sex='F')
        girlsPJ = compets.filter(compet_type=5, compet_sex='F')
        girlsP1 = compets.filter(compet_type=3, compet_sex='F')
        girlsP2 = compets.filter(compet_type=4, compet_sex='F')
        if year >= 2014:
            girlsPS = compets.filter(compet_type=6, compet_sex='F')
        
        if year >= 2018:
            percentIJ = 100.0*len(girlsIJ)/len(competsIJ)
        else:
            percentIJ = 0.0
        percentI1 = 100.0*len(girlsI1)/len(competsI1)
        percentI2 = 100.0*len(girlsI2)/len(competsI2)
        percentPJ = 100.0*len(girlsPJ)/len(competsPJ)
        percentP1 = 100.0*len(girlsP1)/len(competsP1)
        percentP2 = 100.0*len(girlsP2)/len(competsP2)
        if year >= 2014:
            percentPS = 100.0*len(girlsPS)/len(competsPS)
        else:
            percentPS = 0.0
        
        print(f"{year}, {percentIJ:.2f}, {percentI1:.2f}, {percentI2:.2f}, {percentPJ:.2f}, {percentP1:.2f}, {percentP2:.2f}, {percentPS:.2f}")


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
