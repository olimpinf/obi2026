import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import F

from principal.models import LEVEL, Compet, School
from principal.utils.medal_cuts import medal_cuts
import psycopg2
import psycopg2.extras

def set_rank_final(self,year,compet_type):
    DB_HOST = 'localhost'
    db="obi%d" % year 
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
        
          
    for compet_type in compet_types:
        gold,silver,bronze,honour,mod,level,total=medal_cuts(compet_type,year)

        compets = Compet.objects.using(f'obi{year}').filter(compet_points_fase1__gte=0,compet_type=compet_type).order_by(F('compet_points_fase3').desc(nulls_last=True),F('compet_points_fase2').desc(nulls_last=True),F('compet_points_fase1').desc(nulls_last=True), 'compet_name')
        self.stdout.write(self.style.SUCCESS(f'compet_type: {compet_type}, {len(compets)}'))

        num = 0
        rank = 0
        rank_fase3 = 0
        rank_final = 0
        #cur_points_fase1,cur_points_fase2,cur_points_fase3 = compets[0].compet_points_fase1,compets[0].compet_points_fase2,compets[0].compet_points_fase3
        cur_points_fase1,cur_points_fase2,cur_points_fase3 = -1,-1,-1

        for c in compets:
            points_fase1 = c.compet_points_fase1
            points_fase2 = c.compet_points_fase2
            points_fase3 = c.compet_points_fase3
            num += 1

            if points_fase3 != cur_points_fase3:
                rank_fase3=num
                rank=num
            elif points_fase2 != cur_points_fase2 or points_fase1 != cur_points_fase1:
                rank=num
            cur_points_fase1 = points_fase1
            cur_points_fase2 = points_fase2
            cur_points_fase3 = points_fase3

            if rank_fase3 <= honour:
                rank_final = rank_fase3
            else:
                rank_final = rank

            #self.stdout.write(self.style.ERROR(f'rank_fase3: {rank_fase3}, rank: {rank}, rank_final: {rank_final}, cur_rank: {c.compet_rank_final},  num: {num}  {points_fase3}, {points_fase2}, {points_fase1} - {c.compet_name}'))
            # if c.compet_rank_final != rank_final and rank_final <= honour:
            #     self.stdout.write(self.style.ERROR(f'rank_fase3: {rank_fase3}, rank: {rank}, rank_final: {rank_final}, cur_rank: {c.compet_rank_final},  num: {num}  {points_fase3}, {points_fase2}, {points_fase1} - {c.compet_name}'))
            #     sys.exit(-1)
            c.compet_rank_final = rank_final
            c.save()
            
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
        set_rank_final(self,year,level_num)
  
