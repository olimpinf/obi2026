import base64
import logging
import os
import re
import shutil
import sys
from time import sleep
from datetime import datetime
from django.utils.timezone import make_aware
from zoneinfo import ZoneInfo

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetDesclassif, CompetCfObi, LEVEL, PJ, P1, P2, PS, CF
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS
from cms.check_duplicates import check_duplicates
from obi.settings import BASE_DIR
from exams.models import ExamFase1, ExamFase2, ExamFase3, ExamCfObi

logger = logging.getLogger(__name__)

#BASE = '/ext/submissions'
LANG = ["c", "cpp", "java", "js", "py"]
JLANG = ["c/c++", "c/c++", "java19", "text", "text", "python3"]
COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}

#EXCEPT_TASKS = ["festa","pizzaria","leite","dieta"] 
EXCEPT_TASKS = []
PHASE = 1

problem_names = set()

def get_submissions(contest_id, compet_id):
    print("get submissions")    
    local_submission = LocalSubmissions.objects.filter(contest_id=contest_id, compet_id=compet_id).order_by("timestamp")
    local_submission_results = LocalSubmissionResults.objects.filter(contest_id=contest_id, compet_id=compet_id)
    print('len(local_submission)',len(local_submission))
    task_name = ''
    source = ''
    submissions = []
    for sub in local_submission:
        # keep only the last submission, overwrite older ones
        #filename = f'{sub.compet_id}-{sub.task_name}-{sub.submission_id}.{EXTENSIONS[sub.language]}'
        short_filename = f'{sub.compet_id}-{sub.task_name}.{EXTENSIONS[sub.language]}'
        
        if sub.compet_id <= 1:
            # test users
            continue

        #print(sub.task_name, end=' ')
        if sub.task_name in EXCEPT_TASKS:
            continue
        # group C and C++ together
        if sub.language.find("C")==0:
            sub.language = 'C++20 / g++'
        compet_id = sub.compet_id
        task_name = f'{sub.task_name}.{EXTENSIONS[sub.language]}'
        try:
            source = bytes(sub.source).decode("utf-8")
        except:
            source = bytes(sub.source).decode("latin-1")
        result = local_submission_results.get(submission_id=sub.submission_id)
        if result.score != result.public_score:
            print(result.score, result.public_score)
            sys.exit(0)
        submissions.append([compet_id,task_name,result.score,sub.timestamp, source])
    return submissions

    
class Command(BaseCommand):
    help = 'Check exact copy'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)
        parser.add_argument('compet_id_full', nargs='+', type=str)

    def handle(self, *args, **options):
        target_timezone = ZoneInfo("America/Sao_Paulo")
        contest_id = options['contest_id'][0]
        compet_id_full = options['compet_id_full'][0]

        try:
            compet = Compet.objects.get(compet_id_full=compet_id_full)
        except:
            compet = CompetDesclassif.objects.get(compet_id_full=compet_id_full)
        submissions = get_submissions(contest_id, compet.compet_id)

        if contest_id == 1:
            exam = ExamFase1
        elif contest_id == 2:
            exam = ExamFase2
        elif contest_id == 3:
            exam = ExamCfObi
        elif contest_id == 4:
            exam = ExamFase3
        else:
            printf(f"contes_id = {contest_id }???")

        try:
            time_start = exam.objects.get(compet_id=compet.compet_id).time_start
        except:
            print("No time start???")
            time_start = datetime.now().astimezone(ZoneInfo("America/Sao_Paulo"))

        timestamps = {}
        for i in range(len(submissions)):
            timestamps[i] = submissions[i][3]

        # summary
        os.system("clear")
        i = 0
        # submissions
        if time_start:
            local_ts = time_start.astimezone(ZoneInfo("America/Sao_Paulo"))
            print(local_ts.strftime('%m-%d %H:%M'))
        else:
            print("No time start???")
            time_start = datetime.now().astimezone(ZoneInfo("America/Sao_Paulo"))

            
        while i < len(submissions):
            compet_id, task_name, score, timestamp, source = submissions[i]
            if i == 0:
                diff = timestamp - time_start
            else:
                diff = timestamp - timestamps[i-1]
            local_ts = timestamp.astimezone(ZoneInfo("America/Sao_Paulo"))
            print(f"{i+1}. ",task_name, f"({score} points)   {local_ts.strftime('%m-%d %H:%M')}", end=" ")
            lapsed = ':'.join(str(diff).split(':')[:2])
            print(f" (lapsed {lapsed})")
            i += 1
        print()
        b = input("Continue? (q to quit) ")
        if b == 'q':
            return
        i = 0
        # submissions
        show_diff = False
        while i < len(submissions):
            compet_id, task_name, score, timestamp, source = submissions[i]
            os.system("clear")
            if show_diff:
                if i == 0:
                    prev_source = ""
                else:
                    # search last submission of same task
                    prev_i = i - 1
                    while prev_i >= 0: 
                        compet_id, prev_task_name, prev_score, prev_timestamp, prev_source = submissions[prev_i]
                        if prev_task_name == task_name:
                            break
                        prev_i -= 1
                    if prev_i < 0:
                        prev_source = "no previous submission\n"
                        prev_task_name = "not found"
                        
                with open("/tmp/previous", "w") as fp, open("/tmp/current", "w") as fc:
                    fp.write(f"***{prev_task_name}***\n")
                    fp.write(prev_source)
                    fc.write(f"***{task_name}***\n")
                    fc.write(source)
                #os.system("diff -y /tmp/previous /tmp/current")
                os.system("diff -wB /tmp/previous /tmp/current")
                print()
                print()
            else:
                print(compet_id, task_name, f"({score} points)")
                print()
                print(source)
                print()
                print()
                
            if i == 0:
                time_lapse = timestamp - timestamp
                prev_task_name = ''
            else:
                time_lapse = timestamp - timestamps[i-1]
                prev_task_name = submissions[i-1][1]
            print(f"{i+1}. ", compet_id, task_name, f"({score} points)   {timestamp.strftime('%m-%d %H:%M')}", end=" ")
            lapsed = ':'.join(str(time_lapse).split(':')[:2])
            print(f" (lapsed {lapsed} {prev_task_name})")
            b = input("Continue? (q to quit, b to previous) ")
            if b == 'q':
                break
            elif b == 'b':
                i -= 1
                if i < 0:
                    i = 0
            elif b == 'd':
                show_diff = True
                continue
            else:
                i += 1
            show_diff = False
