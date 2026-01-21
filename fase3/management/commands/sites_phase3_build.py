import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import Compet, School

def cities_to_sites_all(filename):
    cities_to_sites('ini', filename)
    cities_to_sites('prog', filename)

def cities_to_sites(mod, filename):
    print("mod",mod)
    if mod == 'ini':
        compet_types = (1,2,7)
    else:
        compet_types = (3,4,5,6)
    cs = Compet.objects.filter(compet_type__in=compet_types,compet_classif_fase2=True).distinct().only('compet_school_id')
    schools_with_compet = set()
    for k in cs:
        schools_with_compet.add(k.compet_school_id)
    schools = School.objects.filter(school_id__in=schools_with_compet)

    with open(filename,"r") as f:
        lines = f.readlines()
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line[0] == '#':
            continue
        tokens = line.split(',')
        site_num = tokens[0].strip()
        if not site_num:
            continue
        site_num = int(tokens[0])
        if site_num == 0:
            continue
        show = True
        if site_num < 0:
            continue
            #show = False
            #site_num = -site_num
        # site may be from a different modality
        print("site_num", site_num)
        site_type = int(tokens[1])
        if site_type == 1 and mod != 'ini':
            # site for ini only
            print("site for ini only")
            continue
        if site_type == 2 and mod != 'prog':
            # site for prog only
            print("site for prog only")
            continue
        site = School.objects.get(school_id=site_num)
        for city in tokens[2:]:
            city = city.strip()
            if not city:
                continue
            city,state = city.split("=")
            #print(f"---------- [{city}]  [{state}]")
            schools_in_city = schools.filter(school_city=city,school_state=state)
            #print(len(schools_in_city))
            for s in schools_in_city:
                print(f"{site.school_name} <- {s.school_name}")
                #s.school_is_site_phase3 = False
                s.school_site_phase3_show = show
                if mod == 'ini':
                    s.school_site_phase3_ini = site_num
                    #print(s.school_id,"s.school_site_phase3_ini =",site_num)
                else:
                    s.school_site_phase3_prog = site_num
                s.save()
        site.school_is_site_phase3 = True
        site.school_site_phase3_show = show
        if mod == 'ini':
            site.school_site_phase3_ini = site_num
        else:
            site.school_site_phase3_prog = site_num
            
        site.save()
        
class Command(BaseCommand):
    help = 'build sites phase 3 from csv file'

    def add_arguments(self, parser):
      parser.add_argument('mod', nargs='+', type=str)
      parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        mod = options['mod'][0]
        filename = options['filename'][0]
        if mod == 'all':
            cities_to_sites_all(filename)
        elif mod in ('ini','prog'):
            cities_to_sites(mod,filename)
        else:
            print("wrong mod", file=sys.stderr)
