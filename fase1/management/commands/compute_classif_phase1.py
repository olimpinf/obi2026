import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from fase1.views import compute_classif_one_school, MINIMUM_POINTS, MAXIMUM_POINTS


def compute_classif_one(self,level,school_id):
    s = School.objects.get(school_id=school_id)
    tot = 0
    classif = 0
    n, c, minimum = compute_classif_one_school(s.school_id,level)
    print(n,c,minimum)
    tot += n
    classif += c
    if n > 0:
        percentage = 100*c/n
    else:
        percentage = 0
    print("{}\nTot: {}  Classif: {} MinPoints:{} ({:2.2f}%)\n".format(s.school_name,n,c,minimum,percentage))

def compute_classif_all_schools(self,level,descriptor):
    #schools = School.objects.all().order_by('school_id')

    schools = School.objects.filter(school_ok=True).order_by('school_id')
    
    tot,classif = 0,0
    for s in schools:
        #n, c, minimum = compute_classif_one_school_addonly(s.school_id,level)
        n, c, minimum = compute_classif_one_school(s.school_id,level)
        tot += n
        classif += c
        if n > 0:
            percentage = 100*c/n
        else:
            percentage = 0
        if percentage != 0:
            print("{}\nTot: {}  Classif: {} MinPoints:{} ({:2.2f}%)\n".format(s.school_name,n,c,minimum,percentage))
    return tot, classif

def compute_classif_all_compets(self,level,descriptor):
    if level in (1,):
        TARGET_PERCENT = 26.0
    elif level in (2,):
        TARGET_PERCENT = 27.0
    elif level in (3,):
        TARGET_PERCENT = 40.0
    elif level in (4,):
        TARGET_PERCENT = 31.0
    elif level in (5,):
        TARGET_PERCENT = 54.0
    elif level in (6,):
        TARGET_PERCENT = 39.0
    elif level in (7,):
        TARGET_PERCENT = 23.0
    else:
        TARGET_PERCENT = 20.0

    compets = Compet.objects.filter(compet_type=level)

    MIN_POINTS = MINIMUM_POINTS[level]
    MAX_POINTS = MAXIMUM_POINTS[level]
    
    #####
    # turn
    ####
    print('all compets',len(compets))
    # if level in (1,2,7):
    #     if descriptor == 'provaf1':
    #         compets = compets.filter(compet_school__school_turn_phase1_ini = 'A')
    #     elif descriptor == 'provaf1b':
    #         compets = compets.filter(compet_school__school_turn_phase1_ini = 'B')
    #     else:
    #         print('bad descriptor')
    #         sys.exit(1)
    # else:
    #     if descriptor == 'provaf1':
    #         compets = compets.filter(compet_school__school_turn_phase1_ini = 'A')
    #     elif descriptor == 'provaf1b':
    #         compets = compets.filter(compet_school__school_turn_phase1_prog = 'B')
    #     else:
    #         print('bad descriptor')
    #         sys.exit(1)

    compets_not_null = compets.filter(compet_points_fase1__isnull=False)
    compets_classif = compets_not_null.filter(compet_classif_fase1=True)
    compets_not_classif = compets_not_null.exclude(compet_classif_fase1=True).order_by('-compet_points_fase1')
    tot = len(compets)
    num_not_null = len(compets_not_null)
    num_not_classif = len(compets_not_classif)
    num_classif = len(compets_classif)
    print(f'num_not_null={num_not_null}, num_not_classif={num_not_classif},num_classif={num_classif}')
    self.stdout.write(self.style.SUCCESS('level {}, {:2.2f}% current, {:2.2f}% target'.format(level,100*num_classif/num_not_null,TARGET_PERCENT)))
    self.stdout.write(self.style.SUCCESS(("tot: {}, num_not_null:{}, num_not_classif:{}, num_classif:{}".format(tot, num_not_null, num_not_classif, num_classif))))

    target_num_classif = round(TARGET_PERCENT*num_not_null/100)
    if target_num_classif <= num_classif:
        
        self.stdout.write(self.style.SUCCESS('Número classificados é maior que alvo: {} > {}'.format(num_classif, target_num_classif)))
        self.stdout.write(self.style.SUCCESS('min_points = {}'.format(compets_classif.order_by('compet_points_fase1')[0].compet_points_fase1)))
        return 

    target_num_new_classif = target_num_classif - num_classif
    self.stdout.write(self.style.SUCCESS('Número ideal de novos classificados: {} ({:2.2f}%  {:2.2f}%)'.format(target_num_new_classif, TARGET_PERCENT, 100*target_num_classif/num_not_null)))

    new_classif=0
    min_points=MAX_POINTS
    for c in compets_not_classif:
        if c.compet_points_fase1 < MIN_POINTS:
            break
        if new_classif<=target_num_new_classif or min_points==c.compet_points_fase1:
            if min_points>c.compet_points_fase1: 
                print('points:',min_points, 'classif:',new_classif)
                min_points=c.compet_points_fase1
            #self.stdout.write(self.style.SUCCESS('New classif id={}, points={}'.format(c.compet_id,c.compet_points_fase1)))
            c.compet_classif_fase1 = True
            c.save()
            new_classif += 1
        elif new_classif>target_num_new_classif and min_points > c.compet_points_fase1:
            print(min_points, new_classif)
            break
    sub_total = 0

    self.stdout.write(self.style.SUCCESS(
            'Total = {}, not null = {}, old classif = {} ({:2.2f}%), new_classif = {} ({:2.2f}%), min_points = {}'.format(
                tot,num_not_null,num_classif,100*num_classif/num_not_null,new_classif,100*(num_classif+new_classif)/num_not_null, min_points)))

    return 

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        level = options['level'][0]
        descriptor = options['descriptor'][0]
        school_id = options['school_id'][0]
        level_num = LEVEL[level.upper()]
        #tot,classif = compute_classif_all_schools(self,level_num)
        #self.stdout.write(self.style.SUCCESS('Classif Schools:'))
        #self.stdout.write(self.style.SUCCESS(
        #        'Total = {}, classif = {} ({:2.2f}%)'.format(
        #            tot,classif,100*classif/tot)))

        #self.stdout.write(self.style.ERROR('Classif Compets not executed'))
        # and after schools, classif global compets
        self.stdout.write(self.style.SUCCESS('Classif Compets'))

        if school_id > 0:
            compute_classif_one(self,level_num,school_id)
        elif school_id == 0:
            compute_classif_all_schools(self,level_num,descriptor)
        else:
            compute_classif_all_compets(self,level_num,descriptor)
