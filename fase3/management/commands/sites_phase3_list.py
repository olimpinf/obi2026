import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School

def list_sites(city_name):
    
    schools = School.objects.all()
    compets = Compet.objects.filter(compet_classif_fase2=True)
    print(len(compets), "compets in phase 3")
    cs = Compet.objects.filter(compet_classif_fase2=True).distinct().only('compet_school_id')
    schools_with_compet = set()
    for k in cs:
        schools_with_compet.add(k.compet_school_id)

    sites = School.objects.filter(school_is_site_phase3=True).order_by("school_state","school_city")
        
    schools = School.objects.filter(school_id__in=schools_with_compet).order_by("school_state","school_city")
    groups = {}
    # 0 is not attributed
    groups[0] =  {"ini":[], "prog":[]}
    for s in sites:
        groups[s.school_id] = {"ini":[], "prog":[]}
        
    for s in schools:
        site_id_ini = s.school_site_phase3_ini
        site_id_prog = s.school_site_phase3_prog
        try:
            groups[site_id_ini]["ini"].append(s.school_id)
        except:
            print(f"school {s.school_id} {s.school_city}: site ini missing")
        try:
            groups[site_id_prog]["prog"].append(s.school_id)
        except:
            print(f"school {s.school_id} {s.school_city}: site prog missing")

    for site_id in groups.keys():
        if site_id == 0:
            continue
        site = sites.get(school_id=site_id)
        city = site.school_city
        if city_name != 'all' and city_name != city:
            continue
        group = groups[site_id]

        tmp = schools.filter(school_id__in=group['ini']+group['prog'])
        cities_names = set()
        for c in tmp:
            cities_names.add(f"{c.school_city}/{c.school_state}")
        cities_names = sorted(cities_names)
        compets_ini = compets.filter(compet_school_id__in=group['ini'])
        compets_prog = compets.filter(compet_school_id__in=group['prog'])

        
        print('---------------------------------------')
        print(f'Sede {site.school_city}/{site.school_state} {site.school_name} {site.school_deleg_name,site.school_deleg_email}')
        print(", ".join(cities_names))
        print('---------------------------------------')

        if compets_ini.count():
            print('Iniciação')
            print('   IJ:', compets_ini.filter(compet_type=7).count())
            print('   I1:', compets_ini.filter(compet_type=1).count())
            print('   I2:', compets_ini.filter(compet_type=2).count())
            print('   Total:', compets_ini.filter(compet_type__in=(1,2,7)).count())
            print()

        if compets_prog.count():
            print('Programação')
            print('   PJ:', compets_prog.filter(compet_type=5).count())
            print('   P1:', compets_prog.filter(compet_type=3).count())
            print('   P2:', compets_prog.filter(compet_type=4).count())
            print('   PS:', compets_prog.filter(compet_type=6).count())
            print('   Total:', compets_prog.filter(compet_type__in=(3,4,5,6)).count())
            print()
              
class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('city', nargs='+', type=str)

    def handle(self, *args, **options):
        city = options['city'][0]
        list_sites(city)
        self.stdout.write(self.style.SUCCESS('OK'))
