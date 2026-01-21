import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import F

from principal.models import LEVEL, School
from principal.models import CompetCfObi
from principal.utils.medal_cuts import medal_cuts_cf
import psycopg2
import psycopg2.extras

def set_rank_final(self,year,compet_type):
    DB_HOST = 'localhost'
    db="obi%d" % year 
    if compet_type==0:
        compet_types = (1,2,3,4,5,6,7)
    else:
        compet_types = (int(compet_type),)
        
          
    for compet_type in compet_types:
        gold,silver,bronze,honour,mod,level,total=medal_cuts_cf(compet_type,year)

        compets = CompetCfObi.objects.using(f'obi{year}').filter(compet_points__gte=0,compet_type=compet_type).order_by(F('compet_points').desc(nulls_last=True), 'compet__compet_name')
        self.stdout.write(self.style.SUCCESS(f'compet_type: {compet_type}, {len(compets)}'))

        num = 0
        rank = 0
        #cur_points_fase1,cur_points_fase2,cur_points_fase3 = compets[0].compet_points_fase1,compets[0].compet_points_fase2,compets[0].compet_points_fase3
        cur_points = -1

        for c in compets:
            points = c.compet_points
            num += 1

            if points != cur_points:
                rank=num
            cur_points = points

            self.stdout.write(self.style.ERROR(f'rank: {rank}, num: {num},   points: {points} - {c.compet.compet_name}'))
            c.compet_rank = rank
            c.save()
            
class Command(BaseCommand):
    help = 'set rank'

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
        set_rank_final(self,year,level_num)
  
