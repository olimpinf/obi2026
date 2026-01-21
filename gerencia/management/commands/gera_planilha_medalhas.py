import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from principal.utils.medal_cuts import medal_cuts
import psycopg2
import psycopg2.extras

def gera_planilha(self):
    
    schools_all = School.objects.all().order_by("school_state", "school_city","school_name")
    compets_all = Compet.objects.filter(compet_points_fase3__gte=0).order_by('compet_rank_final')

    for s in schools_all:
        num_medals = {1:{'o':0, 'p':0, 'b':0},
                      2:{'o':0, 'p':0, 'b':0},
                      3:{'o':0, 'p':0, 'b':0},
                      4:{'o':0, 'p':0, 'b':0},
                      5:{'o':0, 'p':0, 'b':0},
                      6:{'o':0, 'p':0, 'b':0},
                      7:{'o':0, 'p':0, 'b':0}
                      }
        has_medal = False
        compets = compets_all.filter(compet_school_id=s.school_id)
        for c in compets:
            if c.compet_medal == 'o':
                num_medals[c.compet_type]['o'] += 1
                has_medal = True
            elif c.compet_medal == 'p':
                num_medals[c.compet_type]['p'] += 1
                has_medal = True
            elif c.compet_medal == 'b':
                num_medals[c.compet_type]['b'] += 1
                has_medal = True
            else:
                continue
        if not has_medal:
            continue
        print(s.school_id,s.school_state,s.school_city,s.school_name,sep=';', end=';')
        for i in [7,1,2,5,3,4,6]:
            print(num_medals[i]['o'],num_medals[i]['p'],num_medals[i]['b'],sep=';', end=';')
        print()
    
class Command(BaseCommand):
    help = 'set medals'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('year', nargs='+', type=int)

    def handle(self, *args, **options):
        gera_planilha(self)
  
