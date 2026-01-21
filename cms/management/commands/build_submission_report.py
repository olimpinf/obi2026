import base64
import logging
import os
import re
import shutil
import sys
import argparse
from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetCfObi, LEVEL, PJ, P1, P2, PS, CF
from exams.models import ExamFase1, ExamFase2, ExamFase3, ExamCfObi
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS
from cms.check_duplicates import check_duplicates
from obi.settings import BASE_DIR

logger = logging.getLogger(__name__)

BASE_DIR = "/ext/submissoes"
HTTP_DIR = "submissoes"
COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}
EXCEPT_TASKS = []

problem_names = set()

def copy_submissions(dir_name,contest_id):
    count = 0
    count_all = 0
    
    dir_path = os.path.join(BASE_DIR,dir_name)
    
    for l in EXTENSIONS.keys():
        os.mkdir(os.path.join(dir_path,EXTENSIONS[l]))

    if contest_id == 1:
        exam = ExamFase1.objects.all()
    elif contest_id == 2:
        exam = ExamFase2.objects.all()
    elif contest_id == 3:
        exam = ExamCfObi.objects.all()
    elif contest_id == 4:
        exam = ExamFase3.objects.all()
    else:
        print('??')
        sys.exit(0)
    local_submissions = LocalSubmissions.objects.filter(contest_id=contest_id).order_by('submission_id')
    local_submission_results = LocalSubmissionResults.objects.filter(contest_id=contest_id)
    print('len(local_submissions)',len(local_submissions))
    print('len(local_submission_results)',len(local_submission_results))

    if contest_id == 1:
        compets = Compet.objects.filter(compet_points_fase1__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase1')
    elif contest_id == 2:
        compets = Compet.objects.filter(compet_points_fase2__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase2')
    elif contest_id == 3:
        compets = CompetCfObi.objects.filter(compet_points__gte=0,compet_type__in=(3,4,5)).order_by('-compet_points')
    elif contest_id == 4:
        compets = Compet.objects.filter(compet_points_fase2__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase3')
    else:
        print("??")
        sys.exit(0)

    compets_seen = []
    compet_submissions = {}
    compet_start = {}
    print("len(compets)", len(compets))
    for compet in compets:

        if contest_id == 1:
            id_full = compet.compet_id_full
            points = compet.compet_points_fase1
            compet_type = compet.compet_type
        elif contest_id == 2:
            id_full = compet.compet_id_full
            points = compet.compet_points_fase2
            compet_type = compet.compet_type
        elif contest_id == 3:
            id_full = compet.compet.compet_id_full
            points = compet.compet_points
            compet_type = compet.compet_type
        elif contest_id == 4:
            id_full = compet.compet_id_full
            points = compet.compet_points_fase3
            compet_type = compet.compet_type

        
        compet_local_submissions = local_submissions.filter(compet_id=compet.compet_id)
        if not compet_local_submissions:
            continue
        try:
            start = exam.get(compet_id=compet.compet_id).time_start.strftime("%d/%m %H:%M:%S")
        except:
            print("could not get start time", id_full, compet_type)
            start = "???"
        compet_start[id_full] = start
        compet_submissions[id_full] = []
        compets_seen.append(compet)
        for sub in compet_local_submissions:
        
            if sub.task_name in EXCEPT_TASKS:
                continue
            # group C and C++ together
            if sub.language.find("C")==0:
                sub.language = 'C++20 / g++'

            local_subm_result = local_submission_results.filter(local_subm_id=sub.id)
            if not local_subm_result:
                print("compet result problem, compet", id_full, file=sys.stderr)
                public_score = -1
                print("BAD",public_score, file=sys.stderr)
                sys.exit(1)
            else:
                public_score = str(local_subm_result[0].public_score)
                
            filename = f'{sub.compet_id}-{sub.task_name}-sub{sub.id}_{EXTENSIONS[sub.language]}.txt'
            tmpdir = os.path.join(BASE_DIR,dir_name,EXTENSIONS[sub.language],sub.task_name)
            http_dir = os.path.join(HTTP_DIR,dir_name,EXTENSIONS[sub.language],sub.task_name)
            problem_names.add(sub.task_name)
            if not os.path.exists(tmpdir):
                os.mkdir(tmpdir)
            source = bytes(sub.source)
        
            with open(os.path.join(tmpdir,filename),'wb') as f:
                f.write(source)
            compet_submissions[id_full].append((f'{sub.task_name}.{EXTENSIONS[sub.language]}','https://olimpiada.ic.unicamp.br/'+os.path.join(http_dir,filename),public_score,sub.timestamp.strftime("%d/%m %H:%M:%S")))
            count_all += 1
        print(".", end="", file=sys.stderr)
        sys.stderr.flush()

    return count, count_all, compets_seen, compet_submissions, compet_start

def process_submissions(dir_name, contest_id, compets, compet_submissions, compet_start):

    dir_path = os.path.join(BASE_DIR,dir_name)

    if contest_id == 1:
        compets = Compet.objects.filter(compet_points_fase1__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase1')
    elif contest_id == 2:
        compets = Compet.objects.filter(compet_points_fase2__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase2')
    elif contest_id == 3:
        compets = CompetCfObi.objects.filter(compet_points__gte=0,compet_type__in=(3,4,5)).order_by('-compet_points')
    elif contest_id == 4:
        compets = Compet.objects.filter(compet_points_fase2__gte=0,compet_type__in=(3,4,5,6)).order_by('-compet_points_fase3')
    else:
        print("??")
        sys.exit(0)

    print("process submissions, contest_id",contest_id)
    print(len(compet_submissions))

    with open(os.path.join(dir_path,'pj.csv'), 'w') as fpj,  open(os.path.join(dir_path,'p1.csv'), 'w') as fp1,  open(os.path.join(dir_path,'p2.csv'), 'w') as fp2, open(os.path.join(dir_path,'ps.csv'), 'w') as fps:
        print("Submissões PJ", file=fpj)
        print("Submissões P1", file=fp1)
        print("Submissões P2", file=fp2)
        print("Submissões PS", file=fps)
        for compet in compets:
            if contest_id == 1:
                id_full = compet.compet_id_full
                points = compet.compet_points_fase1
                compet_type = compet.compet_type
            elif contest_id == 2:
                id_full = compet.compet_id_full
                points = compet.compet_points_fase2
                compet_type = compet.compet_type
            elif contest_id == 3:
                id_full = compet.compet.compet_id_full
                points = compet.compet_points
                compet_type = compet.compet_type
            elif contest_id == 4:
                id_full = compet.compet_id_full
                points = compet.compet_points_fase3
                compet_type = compet.compet_type
            if id_full not in compet_submissions.keys():
                    continue
            if compet_type == 5:
                f = fpj
            elif compet_type == 3:
                f = fp1
            elif compet_type == 4:
                f = fp2
            elif compet_type == 6:
                f = fps
            print(file=f)
            print(f'{id_full} ({points} pontos)', file=f)                
            print(",".join(["" for i in range(2)]+["início",compet_start[id_full]]), file=f)
            for submission in compet_submissions[id_full]:
                print(",".join(submission), file=f)
                


    return
        

class Command(BaseCommand):
    help = 'Check exact copy'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)
        parser.add_argument('dir_name', nargs='+', type=str)

    def handle(self, *args, **options):
        contest_id = options['contest_id'][0]
        dir_name = options['dir_name'][0]
        dir_path = os.path.join(BASE_DIR,dir_name)
        try:
            shutil.rmtree(dir_path)
        except:
            pass
        
        os.mkdir(dir_path)

        print("contest_id", contest_id, file=sys.stderr)
        print("dir_path", dir_path, file=sys.stderr)
        print("copying...", file=sys.stderr)
        sys.stderr.flush()
        count,count_all,compets,compet_submissions,compet_start = copy_submissions(dir_name,contest_id)
        print(f"count={count}, count_all={count_all}, len(compet_submissions)={len(compet_submissions)}")
        print("processing...", file=sys.stderr)
        sys.stderr.flush()
        process_submissions(dir_name, contest_id, compets, compet_submissions, compet_start)
        print("finished")
