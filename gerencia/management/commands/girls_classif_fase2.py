import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import School, Compet, LEVEL_NAME



def do_it(first_year, last_year):
    print(",".join(["Ano", "IJ", "I1", "I2", "PJ", "P1", "P2", "PS"]))
    for year in range(first_year, last_year+1):
        compets = Compet.objects.using(f'obi{year}').all()

        if year >= 2018:
            competsIJ = compets.filter(compet_type=7,compet_classif_fase2=True)
        competsI1 = compets.filter(compet_type=1,compet_classif_fase2=True)
        competsI2 = compets.filter(compet_type=2,compet_classif_fase2=True)
        competsPJ = compets.filter(compet_type=5,compet_classif_fase2=True)
        competsP1 = compets.filter(compet_type=3,compet_classif_fase2=True)
        competsP2 = compets.filter(compet_type=4,compet_classif_fase2=True)
        competsPS = compets.filter(compet_type=6,compet_classif_fase2=True)

        if year >= 2018:
            girlsIJ = compets.filter(compet_type=7, compet_sex='F',compet_classif_fase2=True)
        girlsI1 = compets.filter(compet_type=1, compet_sex='F',compet_classif_fase2=True)
        girlsI2 = compets.filter(compet_type=2, compet_sex='F',compet_classif_fase2=True)
        girlsPJ = compets.filter(compet_type=5, compet_sex='F',compet_classif_fase2=True)
        girlsP1 = compets.filter(compet_type=3, compet_sex='F',compet_classif_fase2=True)
        girlsP2 = compets.filter(compet_type=4, compet_sex='F',compet_classif_fase2=True)
        girlsPS = compets.filter(compet_type=6, compet_sex='F',compet_classif_fase2=True)


        if year >= 2018:
            percentIJ = 100.0*len(girlsIJ)/len(competsIJ)
        else:
            percentIJ = 0.0
        percentI1 = 100.0*len(girlsI1)/len(competsI1)
        percentI2 = 100.0*len(girlsI2)/len(competsI2)
        percentPJ = 100.0*len(girlsPJ)/len(competsPJ)
        percentP1 = 100.0*len(girlsP1)/len(competsP1)
        percentP2 = 100.0*len(girlsP2)/len(competsP2)
        percentPS = 100.0*len(girlsPS)/len(competsPS)
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
