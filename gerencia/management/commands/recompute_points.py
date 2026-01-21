import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from principal.models import LEVEL, Compet, School, ResIni
from fase1.views import compute_classif_one_school
from exams.settings import EXAMS
from obi.settings import BASE_DIR

LEVEL_INT = {'I1': 1, 'I2':2, 'IJ':7}
LEVEL_STR = {1: 'I1', 2: 'I2', 7:'IJ'}
alternative={'A':0,'B':1,'C':2,'D':3,'E':4}
alt_inverted={0:'A',1:'B',2:'C',3:'D',4:'E'}

def calc_points(gab, answer):
    points = 0
    log=''
    if len(answer)!=len(gab):
        log='ERRO: número de respostas é diferente do número de questões'
        print("number of answers does not match number of questions",file=sys.stderr)
        print(len(answer),answer)
        print(len(gab),gab)
        sys.exit(0)
        return points, log
    for i in range(len(gab)):
        log=log+"%d. " % (i+1)
        if i<9 and len(gab)>=10: log+=' '
        accept=gab[i]
        if accept[0]=='-':
            log=log+"Questão anulada"
        elif answer[i]=='X':
            log=log+"Resposta inválida"
        else:
            log=log+"%s" % (answer[i])
        if len(accept)==1: # only one answer possible
            if ((accept[0]=='*') or (answer[i]==accept[0])):
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                # se quiser mostrar os errados...
                #log=log+" (errada)"
                #all_answers[i]['X'] += 1
                log=log+"\n"
        else: # list of correct answers
            if answer[i] in accept:
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                log=log+"\n"
    return points,log

def compute_points_compets(self,phase,level,compet_id):
    if phase == 1:
        compets = Compet.objects.filter(compet_type=level).exclude(compet_points_fase1__isnull=True)
        keys_filename = os.path.join(BASE_DIR, "protected_files", f"gab_f1{LEVEL_STR[level].lower()}.txt")
    elif phase == 2:
        compets = Compet.objects.filter(compet_type=level).exclude(compet_points_fase2__isnull=True)
        keys_filename = os.path.join(BASE_DIR, "protected_files", f"gab_f2{LEVEL_STR[level].lower()}.txt")
    else:
        print("To do!")
        sys.exit(0)
    print("compets:",len(compets), compet_id)
    if compet_id != 0:
        compets = compets.filter(compet_id=compet_id)
    print("compets:",len(compets), compet_id)

    with open(keys_filename, "r") as f:
        lines = f.readlines()
    keys = []
    for line in lines:
        if line[0] == '#':
            continue
        line = line.strip().split(' ')
        keys.append(line[1])
    print(keys)
        
    tot = len(compets)
    seen = 0
    failed = 0
    more = 0
    less = 0
    print("compets:",tot)
    schools = set()
    for c in compets:
        try:
            res_ini = ResIni.objects.get(compet_id=c.compet_id)
            seen += 1
        except:
            # manual marked
            failed += 1
            continue
            #print("school", c.compet_school_id, c.compet_points_fase1, file=sys.stderr)
            #sys.exit(0)
        if phase == 1:
            #log = res_ini.log_fase1
            #print("log",log)
            if not res_ini.answers_fase1:
                continue
            exec("answers = "+res_ini.answers_fase1, globals())
            print(c.compet_id_full, answers)
            old_points = c.compet_points_fase1
        elif phase == 2:
            exec("answers = "+res_ini.answers_fase2, globals())
            print(c.compet_id_full)
            print(answers)
            old_points = c.compet_points_fase2
        else:
            print("to do!")
            sys.exit(-1)
        points, new_log = calc_points(keys, answers)
        print("points", points, old_points, points - old_points)        
        if points == old_points:
            continue
        elif points > old_points:
            more += 1
            #print("more points", c.compet_id_full, points, old_points, points - old_points, file=sys.stderr)
            #schools.add(c.compet_school_id)
        elif points < old_points:
            less += 1
        if phase == 1:
            c.compet_points_fase1 = points
        elif phase == 2:
            c.compet_points_fase2 = points
        else:
            print("to do!")
            sys.exit(-1)
        #c.save()
        
    print("failed", failed, file = sys.stderr)
    print("more", more, file = sys.stderr)
    print("less", less, file = sys.stderr)
    print("equal", seen - more - less, file = sys.stderr)
    #print("schools", schools, file = sys.stderr)
    return tot, seen

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('phase', nargs='+', type=int)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        phase = options['phase'][0]
        level = options['level'][0]
        compet_id = options['compet_id'][0]
        level_num = LEVEL[level.upper()]
        total_compets, seen_compets = compute_points_compets(self,phase,level_num,compet_id)
        self.stdout.write(self.style.SUCCESS('Compets seen = {} (total = {}).'.format(seen_compets, total_compets)))
