import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School
from fase2.models import PointsFase2

MININUM = {1: 6, 2: 6, 3: 130, 4: 130, 5: 130, 6: 130, 7: 6}
MAXIMUM = {1: 20, 2: 20, 3: 400, 4: 400, 5: 400, 6: 400, 7: 20}

def compute_classif_one_state(turn,level,state):
    compets = Compet.objects.filter(compet_type=level,compet_classif_fase1=True)
    compets = compets.filter(compet_school_id__school_state=state)
    if turn == 'A':
        compets_in_turn = PointsFase2.objects.filter(compet__compet_type=level,compet__compet_school__school_state=state, compet__compet_classif_fase1=True, points_a__isnull=False).order_by('-points_a')
    else:
        compets_in_turn = PointsFase2.objects.filter(compet__compet_type=level,compet__compet_school__school_state=state, compet__compet_classif_fase1=True, points_b__isnull=False).order_by('-points_b')
    MIN_POINTS = MININUM[level]
    TARGET_PERCENT = 30

    tot = len(compets_in_turn)
    min_num_classif = round(TARGET_PERCENT*tot/100)
    #print(state, 'total participants in fase2 =', tot, 'target classif =', min_num_classif)
    num_classif=0
    min_points=100000
    for ct in compets_in_turn:
        try:
            c = compets.get(compet_id=ct.compet_id)
        except:
            # the state may not have contestant
            continue
        if turn == 'A':
            points = ct.points_a
            classif = ct.classif_a
        else:
            points = ct.points_b
            classif = ct.classif_b

        if points < MIN_POINTS:
            #print('MIN_POINTS!', points, num_classif)
            break
        
        if num_classif < min_num_classif:
            min_points = points
            num_classif += 1
            if not classif:
                if turn == 'A':
                    ct.classif_a = True
                    c.classif_fase2 = True
                else:
                    ct.classif_b = True
                    c.classif_fase2 = True
                #print("new {} {} -- {}".format(ct.compet_id, points, num_classif))
                ct.save()
                c.compet_classif_fase2 = True
                c.save()
        elif num_classif >= min_num_classif and min_points == points:
            num_classif += 1
            if not classif:
                if turn == 'A':
                    ct.classif_a = True
                    c.classif_fase2 = True
                else:
                    ct.classif_b = True
                    c.classif_fase2 = True
                #print("new (tie)  {} {} -- {}".format(ct.compet_id, points, num_classif))
                ct.save()
                c.compet_classif_fase2 = True
                c.save()
        else:
            #print("TARGET!", num_classif);
            break
                

    #print('num_classif =',num_classif)
    if num_classif > 0:
        percentage = 100*num_classif//tot
    else:
        percentage = 0
    if num_classif > 0:
        #print("<tr><td>{}</td><td>{}</td><td>{} ({}%)</td><td>{}</td></tr>".format(state, tot, num_classif, percentage, min_points))
        print('<tr><td align="center">{}</td><td align="center">{}</td></tr>'.format(state, min_points))
    return tot, num_classif

def compute_classif_all_states(turn, level):
    states = School.objects.filter().distinct().values('school_state').order_by('school_state')
    tot,classif = 0,0
    print('<table class="simple">')
    print('<tr><th align="center">{}</th><th align="center">{}</th></tr>'.format('Estado', 'Pont. mínima'))
    #print("<tr><th>{}</th><th>{}</th><th>{}</th><th>{}</th></tr>".format('Estado', 'Participantes', 'Classificados', 'Pont. mínima'))
    for s in states:
        s_tot,s_classif = compute_classif_one_state(turn, level,s['school_state'])
        tot += s_tot
        classif += s_classif
    print("</table>")
    return tot, classif

def compute_classif_all_compets(self, turn, level):
    if level in (7,):
        TARGET_PERCENT = 42.0
    elif level in (1,2):
        TARGET_PERCENT = 50.0
    elif level in (3,4,5):
        TARGET_PERCENT = 50.0
    elif level in (3,4,5,6):
        TARGET_PERCENT = 50.0
    else:
        TARGET_PERCENT = 50.0
    MIN_POINTS = MININUM[level]

    compets = Compet.objects.filter(compet_type=level, compet_classif_fase1=True)
    #compets_not_null = compets.filter(compet_points_fase2__isnull=False)
    #compets_classif = compets.filter(compet_classif_fase2=True)
    #compets_not_classif = compets_not_null.exclude(compet_classif_fase2=True).order_by('-compet_points_fase2')

    if turn == 'A':
        compets_in_turn = PointsFase2.objects.filter(compet__compet_type=level).order_by('-points_a')
        compets_classif = PointsFase2.objects.filter(compet__compet_type=level, classif_a=True)
        compets_not_classif = PointsFase2.objects.filter(compet__compet_type=level, classif_a=False).order_by('-points_a')
        compets_not_null = PointsFase2.objects.filter(compet__compet_type=level, points_a__isnull=False).order_by('-points_a')
    else:
        compets_in_turn = PointsFase2.objects.filter(compet__compet_type=level).order_by('-points_b')
        compets_classif = PointsFase2.objects.filter(compet__compet_type=level, classif_b=True)
        compets_not_classif = PointsFase2.objects.filter(compet__compet_type=level, classif_b=False).order_by('-points_b')
        compets_not_null = PointsFase2.objects.filter(compet__compet_type=level, points_b__isnull=False).order_by('-points_b')


    tot = len(compets_in_turn)
    num_not_null = len(compets_not_null)
    num_not_classif = len(compets_not_classif)
    num_classif = len(compets_classif)
    if num_not_null:
        self.stdout.write(self.style.SUCCESS('level {}, {:2.2f}% current, {:2.2f}% target'.format(level,100*num_classif/num_not_null,TARGET_PERCENT)))
    self.stdout.write(self.style.SUCCESS(("tot: {}, num_not_null:{}, num_not_classif:{}, num_classif:{}".format(tot, num_not_null, num_not_classif, num_classif))))

    target_num_classif = round(TARGET_PERCENT*num_not_null/100)
    self.stdout.write(self.style.SUCCESS('Número classificados atual: {}'.format(num_classif)))
    self.stdout.write(self.style.SUCCESS('Número classificados alvo: {}'.format(target_num_classif)))
    if target_num_classif <= num_classif:
        self.stdout.write(self.style.SUCCESS('Número classificados é maior que alvo: {} > {}'.format(num_classif, target_num_classif)))
        #self.stdout.write(self.style.SUCCESS('min_points = {}'.format(compets_classif.order_by('compet_points_fase2')[0].compet_points_fase2)))
        return 

    target_num_new_classif = target_num_classif - num_classif
    self.stdout.write(self.style.SUCCESS('Número ideal de novos classificados: {} ({:2.2f}%  {:2.2f}%)'.format(target_num_new_classif, TARGET_PERCENT, 100*target_num_classif/num_not_null)))

    new_classif=0
    min_points=MAXIMUM[level]
    print('len(compet_not_classif)',len(compets_not_classif))

    for c in compets_not_classif:
        if turn == 'A':
            points_fase2 = c.points_a
        else:
            points_fase2 = c.points_b
        if not points_fase2:
            continue
        if points_fase2 < MIN_POINTS:
            break
        if new_classif<target_num_new_classif:
            if min_points > points_fase2:
                print(points_fase2, new_classif)
            min_points=points_fase2
            new_classif += 1
            compet = c.compet
            if compet.compet_classif_fase2 != True:
                compet.compet_classif_fase2 = True
                compet.save()
                self.stdout.write(self.style.SUCCESS('New classif id={}, points={}'.format(c.compet_id,points_fase2)))
        elif min_points==points_fase2:
            new_classif += 1
            compet = c.compet
            if compet.compet_classif_fase2 != True:
                compet.compet_classif_fase2 = True
                compet.save()
                self.stdout.write(self.style.SUCCESS('New classif id={}, points={}'.format(c.compet_id,points_fase2)))
        #elif new_classif>target_num_new_classif and min_points > points_fase2:
        #    print(min_points, new_classif)
        else:
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
        parser.add_argument('turn', nargs='+', type=str)
        parser.add_argument('command', nargs='+', type=str)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        turn = options['turn'][0]
        command = options['command'][0]
        if command == 'state':
            tot,classif_states = compute_classif_all_states(turn, level_num)
            print("Classif by states: tot={}, classif_states={}".format(tot,classif_states))
        elif command == 'national':
            compute_classif_all_compets(self,turn,level_num)
            #print("Possible classif={}, new_classif={}, min_points={}".format(possible_classif,new_classif,min_points))
            #self.stdout.write(self.style.SUCCESS('Total = {}, classif = {} ({}) .'.format(
            #tot,classif_states+new_classif,100*(classif_states+new_classif)/tot)))
