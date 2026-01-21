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
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS
from cms.check_duplicates import check_duplicates
from obi.settings import BASE_DIR

logger = logging.getLogger(__name__)


COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}
EXCEPT_TASKS = []

problem_names = set()

def copy_submissions(base_dir,contest_id):
    print("copy submissions")
    count = 0
    count_all = 0
    
    TMPBASE = os.path.join(base_dir, "submissions")
    TMPBASE_ALL = os.path.join(base_dir, "submissions_all")

    try:
        shutil.rmtree(TMPBASE)
    except:
        pass
    try:
        shutil.rmtree(TMPBASE_ALL)
    except:
        pass
    os.mkdir(TMPBASE)
    os.mkdir(TMPBASE_ALL)
        
    
    for l in EXTENSIONS.keys():
        os.mkdir(os.path.join(TMPBASE,EXTENSIONS[l]))
        os.mkdir(os.path.join(TMPBASE_ALL,EXTENSIONS[l]))

    local_submissions = LocalSubmissions.objects.filter(contest_id=contest_id).order_by('-submission_id')
    print('len(local_submissions)',len(local_submissions))
    #compets = Compet.objects.filter(compet_type=level)
    seen = set()
    for sub in local_submissions:
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
        filename = f'{sub.compet_id}-{sub.task_name}-sub{sub.id}.{EXTENSIONS[sub.language]}'
        filename_all = f'{sub.compet_id}-{sub.task_name}-sub{sub.id}_{EXTENSIONS[sub.language]}.txt'
        dirname = os.path.join(TMPBASE,EXTENSIONS[sub.language],sub.task_name)
        dirname_all = os.path.join(TMPBASE_ALL,EXTENSIONS[sub.language],sub.task_name)
        problem_names.add(sub.task_name)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if not os.path.exists(dirname_all):
            os.mkdir(dirname_all)
        source = bytes(sub.source)
        
        with open(os.path.join(dirname_all,filename_all),'wb') as f:
            f.write(source)
            count_all += 1

        if short_filename in seen:
            continue
        seen.add(short_filename)

        with open(os.path.join(dirname,filename),'wb') as f:
            f.write(source)
            count += 1

    return count, count_all, problem_names

def process_submissions(base_dir, MIN_LINES, DO_CLEAN):

    check_duplicates(base_dir, MIN_LINES, DO_CLEAN)
    
    
def process_results(base_dir, base_dir_results, contest_id, MIN_LINES, DO_CLEAN, ONLY_SAME_SCHOOL):

    print("process check_duplicates results")
    compets = set()
    with open(os.path.join(base_dir,"clusters.csv"), "r") as f:
        lines = f.readlines()

    try:
        shutil.move(os.path.join(base_dir,"clusters.csv"),os.path.join(base_dir_results,"clusters.csv"))
    except:
        print("move clusters.csv failed")
        sys.exit(-1)
        
    if contest_id == 1:
        PHASE = 1
    elif contest_id == 2:
        PHASE = 2
    elif contest_id == 3:
        PHASE = 3
    else:
        print('Unknown phase')
        sys.exit(-1)
        
    compet_occurrencies = {}
    task_occurrencies = {}
    cur_cluster_num = ''
    cluster = []
    clusters = []
    for line in lines:
        line = line.strip().split(",")
        cluster_num = line[0]


        if cur_cluster_num != cluster_num:
            # end of a cluster, check if is a valid cluster considering arguments
            # first will check if cluster is due to repeated submission from same contestant
            compets_in_cluster = set()
            schools_in_cluster = set()
            for c_num,compet_id_full,school_id,task_name,entry in cluster:
                compets_in_cluster.add(compet_id_full)
                schools_in_cluster.add(school_id)

            # now consider school argument

            if ONLY_SAME_SCHOOL:
                if len(schools_in_cluster) == 1:
                    school_ok = True
                else:
                    school_ok = False
            else:
                school_ok = True
                
            if len(compets_in_cluster) != 1 and school_ok and cluster:
                clusters.append(cluster)
                #sys.exit(-1)
                # now do some statistics
                for c_num,compet_id_full,school_id,task_name,entry in cluster:
                    # compet occurrencies
                    if compet_id_full in compet_occurrencies.keys():
                        compet_occurrencies[compet_id_full].append(task_name)
                    else:
                        compet_occurrencies[compet_id_full] = [task_name]
                    # task occurrencies
                    if task_name in task_occurrencies.keys():
                        task_occurrencies[task_name].append(compet_id_full)
                    else:
                        task_occurrencies[task_name] = [compet_id_full]
            #else:
            #    print("skipping cluster", cluster_num)
                
            cluster = []
            cur_cluster_num = cluster_num        

        task_name = line[1]
        lang = line[2]
        compet_id = line[3]
        submission_id = line[4]
        filepath = line[5]

        try:
            compet = Compet.objects.get(compet_id=compet_id)
        except:
            # already eliminated
            continue
        try:
            local_subm_result = LocalSubmissionResults.objects.get(local_subm_id=submission_id)
            public_score = local_subm_result.public_score
        except:
            public_score = -1
            print("compet result problem, compet", compet_id, file=sys.stderr)
            print("BAD",public_score, file=sys.stderr)

        if compet.compet_type == CF:
            c = CompetCfObi.objects.get(compet_id=compet_id)
            level = COMPET_LEVEL[c.compet_type]
        else:
            try: ## still a problem
                level = COMPET_LEVEL[compet.compet_type]
            except:
                print(compet.compet_id_full,compet.compet_type)
                continue


        entry = f"{task_name}.{lang};{level};{compet.compet_id_full};{compet.compet_name};{compet.compet_school.school_name};{public_score};https:olimpiada.ic.unicamp.br//{filepath}"
        #entry = f"{task_name}.{lang};{level};{compet.compet_id_full};{compet.compet_name};{compet.compet_school.school_name};{public_score},{submission_id}"
        cluster.append([cur_cluster_num,compet.compet_id_full,compet.compet_school_id,task_name,entry])

    filename = os.path.join(base_dir_results,f"duplicates.csv")

    compets = set()
    with open(filename,"w") as f:
        print("cluster;task; compet_type; compet_id; compet_name; school; score", file=f)
        cur_cluster_num = ''
        for cluster in clusters:
            for cluster_num,compet_id_full,school_id,task_name,entry in cluster:
                compets.add((compet_id_full,school_id,"cópia"))
                if cur_cluster_num != cluster_num:
                    print(f"{cluster_num};", file=f)
                    cur_cluster_num = cluster_num
                print(f";{entry}", file=f)
                

    print(len(compets))
    compet_school = {}
    with open(os.path.join(base_dir_results,'desclassifica.csv'), 'w') as f:
        print(f"# min_lines = {MIN_LINES}, do_clean = {DO_CLEAN}", file=f)
        compets = sorted(list(compets))
        for compet in compets:
            print(f"{compet[0]},{compet[1]},{compet[2]},{PHASE}", file=f)
            compet_school[compet[0]] = compet[1]

        
    count1, compet1 = 0,set()
    count2, compet2 = 0,set()
    count3, compet3 = 0,set()
    count4, compet4 = 0,set()

    with open(os.path.join(base_dir_results,'ocorrencias_compets.csv'), 'w') as f:
        print(f"# min_lines = {MIN_LINES}, do_clean = {DO_CLEAN}", file=f)
        for key in sorted(compet_occurrencies.keys()):
            print(f"{key},", ",".join(compet_occurrencies[key]), file=f)
            if len(compet_occurrencies[key]) == 4:
                compet1.add(key)
                compet2.add(key)
                compet3.add(key)
                compet4.add(key)
                count4 += 1
                count3 += 1
                count2 += 1
                count1 += 1
            elif len(compet_occurrencies[key]) == 3:
                compet1.add(key)
                compet2.add(key)
                compet3.add(key)
                count3 += 1
                count2 += 1
                count1 += 1
            elif len(compet_occurrencies[key]) == 2:
                compet1.add(key)
                compet2.add(key)
                count2 += 1
                count1 += 1
            else:
                compet1.add(key)
                count1 += 1

    
    print('Ocorrencias compets')
    print("count1:", count1)
    print("count2:", count2)
    print("count3:", count3)
    print("count4:", count4)
    print()

    with open(os.path.join(base_dir_results,'desclassifica4.csv'), 'w') as f:
        print(f"# min_lines = {MIN_LINES}, do_clean = {DO_CLEAN}, quatro tarefas iguais", file=f)
        compets = sorted(list(compet4))
        for compet in compets:
            print(f"{compet},{compet_school[compet]},cópia,{PHASE}", file=f)    
    
    with open(os.path.join(base_dir_results,'desclassifica.csv3'), 'w') as f:
        print(f"# min_lines = {MIN_LINES}, do_clean = {DO_CLEAN}, três tarefas iguais", file=f)
        compets = sorted(list(compet3))
        for compet in compets:
            print(f"{compet},{compet_school[compet]},cópia,{PHASE}", file=f)    
    
    with open(os.path.join(base_dir_results,'desclassifica2.csv'), 'w') as f:
        print(f"# min_lines = {MIN_LINES}, do_clean = {DO_CLEAN}, duas tarefas iguais", file=f)
        compets = sorted(list(compet2))
        for compet in compets:
            print(f"{compet},{compet_school[compet]},cópia,{PHASE}", file=f)    
    
    print('Ocorrencias tasks')
    
    with open(os.path.join(base_dir_results,'ocorrencias_tarefas.csv'), 'w') as f:
        for key in sorted(task_occurrencies.keys()):
            print(f"{key},", ",".join(task_occurrencies[key]), file=f)
            print(key,len(task_occurrencies[key]))

class Command(BaseCommand):
    help = 'Check exact copy'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)
        parser.add_argument('base_dir', nargs='+', type=str)
        parser.add_argument('min_lines', nargs='+', type=int)
        parser.add_argument('--do_clean', action=argparse.BooleanOptionalAction)
        parser.add_argument('--only_same_school', action=argparse.BooleanOptionalAction)

    def handle(self, *args, **options):
        print(options)
        contest_id = options['contest_id'][0]
        base_dir = options['base_dir'][0]
        min_lines = options['min_lines'][0]
        do_clean = options['do_clean']
        only_same_school = options['only_same_school']

        base_dir_results = os.path.join(base_dir,f'{min_lines}-lines')
        if do_clean:
            base_dir_results = f'{base_dir_results}-clean'
        else:
            base_dir_results = f'{base_dir_results}-no-clean'
            
        if only_same_school:
            base_dir_results = f'{base_dir_results}-same-school'
        else:
            base_dir_results = f'{base_dir_results}-no-same-school'


        #try:
        #    shutil.rmtree(base_dir)
        #except:
        #    pass
        #os.mkdir(base_dir)
            
        try:
            shutil.rmtree(base_dir_results)
        except:
            pass
        
        os.mkdir(base_dir_results)

        count,count_all,problem_names = copy_submissions(base_dir,contest_id)
        print(f"count={count}, count_all={count_all}, problem_names={problem_names}")
        process_submissions(base_dir, min_lines, do_clean)
        print("ended process_submissions")
        process_results(base_dir, base_dir_results, contest_id, min_lines, do_clean, only_same_school)

        print()
        print("contest_id", contest_id)
        print("base_dir", base_dir)
        print("min_lines", min_lines)
        print("do_clean", do_clean)
        print("only_same_school", only_same_school)
        print("results in", base_dir_results)
        print("finished")
