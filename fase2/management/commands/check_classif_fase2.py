import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Q
from principal.models import LEVEL, Compet, School
from fase1.views import compute_classif_one_school

#MIN_POINTS_2024 = {1: 12, 2: 12, 3: 230, 4: 240, 5: 130, 6: 282, 7: 9}
MIN_POINTS = {1: 13, 2: 17, 3: 200, 4: 217, 5: 117, 6: 266, 7: 10}

def check_classif_all_compets(self,level):
    min_points = MIN_POINTS[level]
    compets = Compet.objects.filter(compet_classif_fase1=True, compet_type=level, compet_points_fase2__gte=min_points)
    compets = compets.filter(Q(compet_classif_fase2=None)|Q(compet_classif_fase2=False)).order_by('-compet_points_fase2')
    not_classif = len(compets)
    for c in compets:
        print(c.compet_id)
    return not_classif


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        count = check_classif_all_compets(self,level_num)
        self.stdout.write(self.style.SUCCESS('Compets not classified = {}.'.format(count)))

