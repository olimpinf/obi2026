import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, CompetCfObi, School
from principal.utils.medal_cuts import medal_cuts_cf
import psycopg2
import psycopg2.extras

def set_medals(self,year,compet_type):
    if compet_type==0:
      if year >= 2018:
          compet_types = (1,2,3,4,5,6,7)
      elif year >= 2014:
          compet_types = (1,2,3,4,5,6)
      elif year >= 2008:
          compet_types = (1,2,3,4,5)
      elif year >= 2005:
          compet_types = (1,2,3,4)
      else:
          # 1999-2001
        compet_types = (4,)
    else:
        compet_types = (int(compet_type),)


    schools_all = School.objects.all()
    compets_all = CompetCfObi.objects.filter(compet_points__gte=0).order_by('compet_rank')
    for compet_type in compet_types:
        nmedals = {'o': 0, 'p': 0, 'b': 0, 'h': 0, 'x':0}
        gold,silver,bronze,honor,mod,level,total=medal_cuts_cf(compet_type,year)

    num_gold,num_silver,num_bronze,num_honor = 0,0,0,0
    compets = compets_all.filter(compet_type=compet_type)
    for c in compets:
        rank = c.compet_rank
        if not rank:
            continue
        if (rank<=gold):
            medal='o'
            print('ouro',rank,c.compet.compet_name)
            num_gold += 1
        elif (rank<=silver):
            medal='p'
            print('prata',rank,c.compet.compet_name)
            num_silver += 1
        elif (rank<=bronze):
            medal='b'
            print('bronze',bronze,rank,c.compet.compet_name)
            num_bronze += 1
        else:
            continue
        if medal:
            nmedals[medal] += 1
            if c.compet_medal  and c.compet_medal != medal:
                self.stdout.write(self.style.ERROR('Level={}, compet_id={}, current_medal={}, medal={}.'.format(compet_type,c.compet_id,c.compet_medal,medal)))
                #sys.exit(-1)
                break
        c.compet_medal = medal
        if medal != 'h':
            school = schools_all.get(school_id=c.compet.compet_school_id)
            school.school_has_medal = True
            school.save()
        else:
            break
        c.save()
        #self.stdout.write(self.style.SUCCESS('Level={}, gold={}, silver={}, bronze={}, honor={}.'.format(compet_type,nmedals['o'],nmedals['p'],nmedals['b'],nmedals['h'])))
    print("num_gold", num_gold )
    print("num_silver", num_silver )
    print("num_bronze", num_bronze )
    print("num_honor", num_honor )
    
class Command(BaseCommand):
    help = 'set medals'

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='+', type=int)
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        year = options['year'][0]
        level = options['level'][0]
        if level == 'all':
          level_num = 0
        else:
          level_num = LEVEL[level.upper()]
        set_medals(self,year,level_num)
  
