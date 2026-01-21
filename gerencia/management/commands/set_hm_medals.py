import sys
import pandas as pd

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School, CompetExtra
from principal.utils.medal_cuts import medal_cuts
import psycopg2
import psycopg2.extras

def set_medals(self,filename,level):
    if level == 'i1':
        compet_type = 1
    elif level == 'i2':
        compet_type = 2
    elif level == 'ij':
        compet_type = 7
    else:
        print('wrong level', file=sys.stderr)
        sys.exit(-1)

    compets_all = Compet.objects.filter(compet_points_fase2__gte=0)
    print("len(compets_all)",len(compets_all))
    num_gold,num_silver,num_bronze,num_honor = 0,0,0,0
    schools = School.objects.all()
    creating, existing = 0,0
    
    df = pd.read_csv(filename)
    for row in df.itertuples():
        cidade = row.cidade[:row.cidade.find('/')]
        escola = row.escola.strip()
        print(escola,'---',cidade)
        try:
            #print(row.Index, f'[{row.escola}]')
            school = schools.get(school_name__iexact=escola, school_city__iexact=cidade)
        except:
            print('+++ no school?')
            print(f'[{escola}]')
            print(f'[{cidade}]')
            sys.exit(0)
        try:
            #print(f'[{row.nome}]')
            compet = compets_all.get(compet_name__iexact=row.nome, compet_school_id = school.school_id)
        except:
            print("****** no compet?")
            print(row.Index)
            print(row.nome)

        try:
            extra = CompetExtra.objects.get(compet_id=compet.compet_id)
            print("existing")
            existing += 1
        except:
            extra = CompetExtra(compet=compet)
            print("creating")
            creating += 1
        extra.compet_state_medal = True
        extra.save()
    print("creating", creating)
    print("existing", existing)
    
class Command(BaseCommand):
    help = 'set medals'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        level = options['level'][0]
          
        set_medals(self,filename,level)
  
