import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from week.models import Week
from principal.models import LEVEL, Compet, School


def search_compets(self,compet_type):
  if compet_type==0:
    compet_types = (1,2,3,4,5,6,7)
  else:
    compet_types = (int(compet_type),)

  w = Week.objects.all()
  
  for compet_type in compet_types:
    compets_old = Compet.objects.filter(compet_type=compet_type).only('compet_name','compet_id','compet_type','compet_school_id').using('obi2020')
    compets = Compet.objects.all()
    schools_old = School.objects.all().using('obi2020')
    schools = School.objects.all()
    if compet_type == 1 or compet_type == 2:
      compets_old = compets_old.filter(compet_medal='o')
    elif compet_type == 3 or compet_type == 5:
      compets_old = compets_old.filter(compet_medal__in=('o','p'))
    for c_old in compets_old:
      try:
        c = compets.get(compet_name=c_old.compet_name)
        if w.filter(compet__compet=c).exists():
          print('OK',end=' ')
        print(c.compet_id_full, '-', c.compet_name,c_old.compet_type,c.compet_type, c_old.compet_school.school_name, c.compet_school.school_name,c.compet_birth_date,c_old.compet_birth_date)
      except:
        names = c_old.compet_name.split(' ')
        max_matched = 0
        max_c = 0
        for name in names:
          candidates = compets.filter(compet_name__icontains=name)
          for c in candidates:
            cand_names = c.compet_name.split(' ')
            matched = 0
            for cn in cand_names:
              for n in names:
                if cn.lower() == n.lower():
                  matched += 1
            if matched > max_matched:
              max_matched = matched
              max_c = c
        if max_matched > 2:
          c = max_c
          if w.filter(compet=c).exists():
            print('OK', c.compet_id_full, end=' ')
          print('?',c.compet_id_full, '-', c_old.compet_name, c.compet_name,c_old.compet_type,c.compet_type, c_old.compet_school.school_name, max_c.compet_school.school_name,c.compet_birth_date,c_old.compet_birth_date)
        else:
          print('-------',c_old.compet_name, c_old.compet_school.school_name)
        
class Command(BaseCommand):
    help = 'search compets'

    def add_arguments(self, parser):
      parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        if level == 'all':
          level_num = 0
        else:
          level_num = LEVEL[level.upper()]
        search_compets(self,level_num)
  
