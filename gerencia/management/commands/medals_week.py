import os
import sys
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import School, Compet, LEVEL_NAME


def find_medals(name, lines):
    medals = 0
    for i in range(len(lines)):
        if lines[i].find(name) > 0:
            if lines[i-1].find('medalhinha') > 0:
                medals += 1
    return medals
        

def do_it(first_year, last_year, filename):
    with open(filename, 'r') as f:
        names = f.readlines()

    print("IOI")
    ioi = 0
    html = os.path.join(settings.BASE_DIR,'html','competicoes','ioi.html')
    with open(html, 'r') as f:
        lines = f.readlines()

    for name in names:
        name = name.strip()
        ioi += find_medals(name,lines)

    print(ioi)
    print()

    print("EGOI")
    egoi = 0
    html = os.path.join(settings.BASE_DIR,'html','competicoes','egoi.html')
    with open(html, 'r') as f:
        lines = f.readlines()

    for name in names:
        name = name.strip()
        egoi += find_medals(name,lines)
        
    print(egoi)
    print()
    
    print("OII")
    oii = 0
    html = os.path.join(settings.BASE_DIR,'html','competicoes','oii_ciic.html')
    with open(html, 'r') as f:
        lines = f.readlines()

    for name in names:
        name = name.strip()
        oii += find_medals(name,lines)

    print(oii)
    print()
    
    ij_medals = 0
    i1_medals = 0
    i2_medals = 0
    pj_medals = 0
    p1_medals = 0
    p2_medals = 0
    ps_medals = 0
    for year in range(first_year, last_year+1):
        compets = Compet.objects.using(f'obi{year}').filter(compet_medal__in=('o','p','b')).only('compet_type','compet_medal')
        if year >= 2018:
            competsIJ = compets.filter(compet_type=7)
        else:
            competsIJ = None
        competsI1 = compets.filter(compet_type=1)
        competsI2 = compets.filter(compet_type=2)
        competsPJ = compets.filter(compet_type=5)
        competsP1 = compets.filter(compet_type=3)
        competsP2 = compets.filter(compet_type=4)
        if year >= 2014:
            competsPS = compets.filter(compet_type=6)
        else:
            competsPS = None

        for name in names:
            name = name.strip()
            if competsIJ and competsIJ.filter(compet_name__iexact=name).exists():
                ij_medals += 1
            if competsI1.filter(compet_name__iexact=name).exists():
                i1_medals += 1
            if competsI2.filter(compet_name__iexact=name).exists():
                i2_medals += 1
            if competsPJ.filter(compet_name__iexact=name).exists():
                pj_medals += 1
            if competsP1.filter(compet_name__iexact=name).exists():
                p1_medals += 1
            if competsP2.filter(compet_name__iexact=name).exists():
                p2_medals += 1
            if competsPS and competsPS.filter(compet_name__iexact=name).exists():
                ps_medals += 1

    print("OBI")
    print(f"ij: {ij_medals}")
    print(f"i1: {i1_medals}")
    print(f"i2: {i2_medals}")
    print(f"pj: {pj_medals}")
    print(f"p1: {p1_medals}")
    print(f"p2: {p2_medals}")
    print(f"ps: {ps_medals}")
    print(f"Total: {ij_medals+i1_medals+i2_medals+pj_medals+p1_medals+p2_medals+ps_medals}")


    return

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('first_year', nargs='+', type=int)
        parser.add_argument('last_year', nargs='+', type=int)
        parser.add_argument('filename', nargs='+', type=str)
        
    def handle(self, *args, **options):
        first_year= options['first_year'][0]
        last_year= options['last_year'][0]
        filename= options['filename'][0]
        do_it(first_year, last_year, filename)
        #self.stdout.write(self.style.SUCCESS('OK'))
