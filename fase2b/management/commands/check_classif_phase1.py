import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from fase1.views import compute_classif_one_school


def check_classif_one_school(school_id,level):
    print('.',end="")
    all_compets = Compet.objects.filter(compet_school_id=school_id, compet_type=level)
    compets_classif = all_compets.filter(compet_classif_fase1=True).order_by('compet_points_fase1')
    compets_not_classif = all_compets.filter(compet_classif_fase1=False).order_by('-compet_points_fase1')

    if len(compets_classif) > 0:
        min_points = compets_classif[0].compet_points_fase1
    else:
        return
        
    for c in compets_not_classif:
        if c.compet_id=4950:
            print("***")
        if c.compet_points_fase1 >= min_points:
            print("points {} (min={}), compet {}, school {}".format(c.compet_points_fase1, min_points,c.compet_id,c.compet_school_id))
            c.compet_classif_fase1 = True
            #c.save()
        else:
            break
    return 



def check_classif_all_schools(self,level):
    schools = School.objects.all().order_by('school_id')
    tot,classif = 0,0
    for s in schools:
        #n, c, minimum = compute_classif_one_school_addonly(s.school_id,level)
        check_classif_one_school(s.school_id,level)
    return


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        check_classif_all_schools(self,level_num)
        print()
