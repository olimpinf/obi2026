import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from cadastro.models import LEVEL, Compet, School


def compute_classif_one_state(level,state):
    compets = Compet.objects.filter(compet_type=level)
    compets = compets.filter(compet_school_id__school_state=state)
    compets = compets.filter(compet_points_fase2__isnull=False).order_by('-compet_points_fase2')
    tot = len(compets)
    min_num_classif = round(30*tot/100)
    num_classif=0
    min_points=100000
    for c in compets:
        if not c.compet_points_fase2 or c.compet_points_fase2 == 0:
            break
        if num_classif<=min_num_classif or min_points==c.compet_points_fase2:
            min_points=c.compet_points_fase2
            c.compet_classif_fase2 = True
            #c.save()
            num_classif += 1

    if num_classif > 0:
        percentage = 100*num_classif//tot
    else:
        percentage = 0
    if num_classif > 0:
        print("<tr><td>{}</td><td>{}</td><td>{} ({}%)</td><td>{}</td></tr>".format(state, tot, num_classif, percentage, min_points))
    return tot, num_classif

def compute_classif_all_states(level):
    states = School.objects.filter().distinct().values('school_state').order_by('school_state')
    tot,classif = 0,0
    print("<table>")
    print("<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format('Estado', 'Participantes', 'Classificados', 'Pont. mínima'))
    for s in states:
        s_tot,s_classif = compute_classif_one_state(level,s['school_state'])
        tot += s_tot
        classif += s_classif
    print("</table>")
    return tot, classif

def compute_classif_all_compets(self,level):
    compets = Compet.objects.filter(compet_type=level)
    compets = compets.filter(compet_points_fase2__isnull=False).order_by('-compet_points_fase2')
    
    tot = len(compets)
    min_num_classif = round(5*tot/100)
    num_classif,new_classif=0,0
    min_points=100000
    for c in compets:
        if not c.compet_points_fase2 or c.compet_points_fase2 == 0:
            break
        if num_classif <= min_num_classif or min_points == c.compet_points_fase2:
            min_points=c.compet_points_fase2
            if c.compet_classif_fase2 == False:
                self.stdout.write(self.style.SUCCESS('New classif id={}, points={}'.format(c.compet_id,c.compet_points_fase2)))
                print('classificado extra com {} pontos'.format(c.compet_points_fase2),file=sys.stderr)
                c.compet_classif_fase2 = True
                #c.save()
                new_classif += 1
            num_classif += 1
    print('\nnum_classif={}, new_classif={}'.format(num_classif,new_classif),file=sys.stderr)
    return min_points, num_classif, new_classif

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('level', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        #tot,classif_states = compute_classif_all_states(level_num)
        #print("Classif by states: tot={}, classif_states={}".format(tot,classif_states))
        self.stdout.write(self.style.SUCCESS('Teste'))
        min_points,possible_classif,new_classif = compute_classif_all_compets(self,level_num)
        print("Extra classif: tot2={}, possible new classif={}, new_classif={}, min_points={}".format(tot,possible_classif,new_classif,min_points))
        self.stdout.write(self.style.SUCCESS('Total = {}, classif = {} ({}) .'.format(
                    tot,classif_states+new_classif,100*(classif_states+new_classif)/tot)))
