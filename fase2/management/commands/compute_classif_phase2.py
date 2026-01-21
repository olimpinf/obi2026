import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School

MININUM = {1: 6, 2: 6, 3: 100, 4: 130, 5: 100, 6: 130, 7: 6}
MAXIMUM = {1: 20, 2: 20, 3: 400, 4: 400, 5: 300, 6: 400, 7: 20}
DO_SAVE = True
DO_CLEAN = False

def compute_classif_one_state(level,state):
    compets = Compet.objects.filter(compet_type=level)
    compets = compets.filter(compet_school_id__school_state=state)
    if DO_CLEAN:
        compets.update(compet_classif_fase2=None)
    compets = compets.filter(compet_points_fase2__isnull=False).order_by('-compet_points_fase2')
    MIN_POINTS = MININUM[level]
    TARGET_PERCENT = 15
    #if level == 5:
    #    TARGET_PERCENT = 35
        
    
    tot = len(compets)
    min_num_classif = round(TARGET_PERCENT*tot/100)
    num_classif=0
    min_points=100000
    for c in compets:
        if not c.compet_points_fase2 or c.compet_points_fase2 < MIN_POINTS:
            break
        if num_classif<=min_num_classif or min_points==c.compet_points_fase2:
            min_points=c.compet_points_fase2
            #print("new {} {}".format(c.compet_id,c.compet_points_fase2))
            c.compet_classif_fase2 = True
            if DO_SAVE:
                c.save()
            num_classif += 1

    if num_classif > 0:
        percentage = 100*num_classif//tot
    else:
        percentage = 0
    if num_classif > 0:
        #print("<tr><td>{}</td><td>{}</td><td>{} ({}%)</td><td>{}</td></tr>".format(state, tot, num_classif, percentage, min_points))
        print("<tr><td>{}</td><td>{}</td></tr>".format(state, min_points))
    return tot, num_classif

def compute_classif_all_states(level):
    states = School.objects.filter().distinct().values('school_state').order_by('school_state')
    tot,classif = 0,0
    print("<table>")
    print("<tr><th>{}</th><th>{}</th></tr>".format('Estado', 'Pont. mínima'))
    #print("<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format('Estado', 'Participantes', 'Classificados', 'Pont. mínima'))
    for s in states:
        s_tot,s_classif = compute_classif_one_state(level,s['school_state'])
        tot += s_tot
        classif += s_classif
    print("</table>")
    return tot, classif

def compute_classif_all_compets(self, level):
    if level in (7,):
        TARGET_PERCENT = 22.0
    elif level in (1,):
        TARGET_PERCENT = 20.0
    elif level in (2,):
        TARGET_PERCENT = 20.0
    elif level in (3,):
        TARGET_PERCENT = 25.0
    elif level in (4,):
        TARGET_PERCENT = 20.0
    elif level in (5,):
        TARGET_PERCENT = 38.0
    elif level in (6,):
        TARGET_PERCENT = 22.0
    else:
        TARGET_PERCENT = 0.0
    MIN_POINTS = MININUM[level]

    compets = Compet.objects.filter(compet_type=level,compet_classif_fase1=True)
    compets_not_null = compets.filter(compet_points_fase2__isnull=False)
    compets_classif = compets_not_null.filter(compet_classif_fase2=True)
    compets_not_classif = compets_not_null.exclude(compet_classif_fase2=True).order_by('-compet_points_fase2')
    tot = len(compets)
    num_not_null = len(compets_not_null)
    num_not_classif = len(compets_not_classif)
    num_classif = len(compets_classif)
    if num_not_null:
        self.stdout.write(self.style.SUCCESS('level {}, {:2.2f}% current, {:2.2f}% target'.format(level,100*num_classif/num_not_null,TARGET_PERCENT)))
    self.stdout.write(self.style.SUCCESS(("tot: {}, num_not_null:{}, num_not_classif:{}, num_classif:{}".format(tot, num_not_null, num_not_classif, num_classif))))

    target_num_classif = round(TARGET_PERCENT*num_not_null/100)
    if target_num_classif <= num_classif:
        self.stdout.write(self.style.SUCCESS('Número classificados é maior que alvo: {} > {}'.format(num_classif, target_num_classif)))
        self.stdout.write(self.style.SUCCESS('min_points = {}'.format(compets_classif.order_by('compet_points_fase2')[0].compet_points_fase2)))
        return 

    target_num_new_classif = target_num_classif - num_classif
    self.stdout.write(self.style.SUCCESS('Número ideal de novos classificados: {} ({:2.2f}%  {:2.2f}%)'.format(target_num_new_classif, TARGET_PERCENT, 100*target_num_classif/num_not_null)))

    new_classif=0
    min_points=MAXIMUM[level]
    for c in compets_not_classif:
        if c.compet_points_fase2 < MIN_POINTS:
            break
        if new_classif<target_num_new_classif or min_points==c.compet_points_fase2:
            if min_points!=c.compet_points_fase2: 
                print(min_points, new_classif)
            if new_classif<target_num_new_classif:
                min_points=c.compet_points_fase2
            #self.stdout.write(self.style.SUCCESS('New classif id={}, points={}'.format(c.compet_id,c.compet_points_fase2)))
            c.compet_classif_fase2 = True
            if DO_SAVE:
                c.save()
            new_classif += 1
        elif new_classif>target_num_new_classif and min_points > c.compet_points_fase2:
            print(min_points, new_classif)
            break
    sub_total = 0

    self.stdout.write(self.style.SUCCESS(
            'Total = {}, not null = {}, old classif = {} ({:2.2f}%), new_classif = {}, total_classif {}, ({:2.2f}%), min_points = {}'.format(
                tot,num_not_null,num_classif,100*num_classif/num_not_null,new_classif,(num_classif+new_classif),100*(num_classif+new_classif)/num_not_null, min_points)))

    return 
    return min_points, num_classif, new_classif

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('command', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        command = options['command'][0]
        if command == 'state':
            tot,classif_states = compute_classif_all_states(level_num)
            print("Classif by states: tot={}, classif_states={}".format(tot,classif_states))
        elif command == 'national':
            compute_classif_all_compets(self,level_num)
        else:
            print('???')
        #print("Possible classif={}, new_classif={}, min_points={}".format(possible_classif,new_classif,min_points))
        #self.stdout.write(self.style.SUCCESS('Total = {}, classif = {} ({}) .'.format(
        #            tot,classif_states+new_classif,100*(classif_states+new_classif)/tot)))
