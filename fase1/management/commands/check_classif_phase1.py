import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.models import Q
from principal.models import LEVEL, Compet, School
from fase1.views import compute_classif_one_school, MINIMUM_POINTS, MAXIMUM_POINTS

MIN_POINTS = {1: 9, 2: 10, 3: 200, 4: 230, 5: 200, 6: 260, 7: 8}

def check_classif_one_school(school,level):
    #print('.',end="")
    count = 0
    all_compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type=level)
    compets_classif = all_compets.filter(compet_classif_fase1=True).order_by('compet_points_fase1')
    compets_not_classif = all_compets.filter(Q(compet_classif_fase1=None)|Q(compet_classif_fase1=False)).order_by('-compet_points_fase1')

    min_points = 1000
    changed = []
    if len(compets_classif) > 0:
        min_points = compets_classif[0].compet_points_fase1

    for c in compets_not_classif:
        if c.compet_points_fase1 and (c.compet_points_fase1 >= min_points or c.compet_points_fase1 >= MIN_POINTS[level]):
            c.compet_classif_fase1 = True
            count += 1
            changed.append(c)
            c.save()

        elif c.compet_points_fase1:
            break

    if count > 0:
        print("school", school.school_id, school.school_name, school.school_city, school.school_state)
        for c in changed:
            print(f"\t{c.compet_id_full}, points: {c.compet_points_fase1}")
        print("\tcompets_classif",len(compets_classif))
        print("\tcompets_not_classif",len(compets_not_classif))
        print()
            
    return count


def check_classif_all_schools(self,level):
    schools = School.objects.filter(school_ok=True).order_by('school_id')
    classif = 0
    for s in schools:
        #n, c, minimum = compute_classif_one_school_addonly(s.school_id,level)
        classif += check_classif_one_school(s,level)
    return classif


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        count = check_classif_all_schools(self,level_num)
        self.stdout.write(self.style.SUCCESS('Compets newly classified = {}.'.format(count)))

