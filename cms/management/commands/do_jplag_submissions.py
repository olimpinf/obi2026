import base64
import logging
import os
import re
import shutil
import sys
from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetCfObi, CompetDesclassif, LEVEL, PJ, P1, P2, PS, CF
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS

logger = logging.getLogger(__name__)

#BASE = '/ext/submissions'
LANG = ["c", "cpp", "java", "js", "py"]
JLANG = ["c/c++", "c/c++", "java19", "text", "text", "python3"]
COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}

EXCEPT_TASKS = ["arara"]
SIMILARITY = "99%"

problem_names = set()

def copy_submissions(base_dir,contest_id, min_lines):
    print("copy submissions", min_lines)
    count = 0
    count_all = 0
    try:
        shutil.rmtree(base_dir)
    except:
        pass
    os.mkdir(base_dir)
    
    TMPBASE = os.path.join(base_dir, "submissions")
    TMPBASE_ALL = os.path.join(base_dir, "submissions_all")
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
        dirname = os.path.join(TMPBASE,EXTENSIONS[sub.language],sub.task_name)
        dirname_all = os.path.join(TMPBASE_ALL,EXTENSIONS[sub.language],sub.task_name)
        problem_names.add(sub.task_name)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        if not os.path.exists(dirname_all):
            os.mkdir(dirname_all)
        source = bytes(sub.source)

        try:
            text_src = source.decode("utf-8")
        except:
            text_src = source.decode("latin-1")
                
        num_lines = text_src.count("\n") + (1 if text_src and not text_src.endswith("\n") else 0)

        if num_lines < min_lines:
            #print(f"file too short, {num_lines}, {filename}")
            continue
        
        # append .txt to make it easier to retrieve files
        with open(os.path.join(dirname_all,filename)+'.txt','wb') as f:
            f.write(source)
            count_all += 1

        if short_filename in seen:
            continue
        seen.add(short_filename)

        with open(os.path.join(dirname,filename),'wb') as f:
            f.write(source)
            count += 1

    return count, count_all, problem_names

def process_submissions(base_dir,contest_id,problem_names):

    print("run jplag")
    CODEBASE = os.path.join(base_dir,"submissions")
    TMPBASE = os.path.join(base_dir,"result")
    try:
        os.remove(TMPBASE)
    except:
        pass
    os.mkdir(TMPBASE)
    
    for problem in problem_names:
        for i in range(len(LANG)):
            submissions = os.path.join(CODEBASE,LANG[i],problem,"*")
            result = os.path.join(TMPBASE,f"{LANG[i]}_{problem}")
            #os.system(f'java -jar attic/jplag/jplag-2.12.1-SNAPSHOT-jar-with-dependencies.jar -m {SIMILARITY} -l {JLANG[i]} -r {result} -c {submissions} > /dev/null 2>&1')
            os.system(f'java -jar attic/jplag/jplag-2.12.1-SNAPSHOT-jar-with-dependencies.jar -m {SIMILARITY} -l {JLANG[i]} -r {result} -c {submissions} > /dev/null 2>&1')


def process_results(base_dir,contest_id,problem_names):

    print("process jplag results")
    TMPBASE = os.path.join(base_dir,"result")
    clusters = []
    for problem in problem_names:
        print("problem", problem)
        pattern_problem_name = re.compile(fr"(\d+)-{problem}")
        pattern_submission_id = re.compile(fr"sub(\d+)")
        for lang in LANG:
            prev_cluster = []
            seen_clusters_compets = []
            cur_cluster_compets = set()
            result_name = os.path.join(TMPBASE,f"{lang}_{problem}")
            result_file = os.path.join(result_name,"matches_avg.csv")
            #print("result_name", result_name)
            #print("result_file", result_file)
            lines = []
            try:
                with open(result_file, "r") as f:
                    lines = f.readlines()
                    # order by number of elements desc
                    lines.sort(key=lambda line: len(line.split(";")), reverse=True)
            except:
                print(f"no lines in result_file {result_file}")
                pass
            line_num = -1
            for line in lines:
                line_num += 1
                cluster = []
                submissions = line.split(";")
                similarity = 100.0
                match = re.search(pattern_problem_name,submissions[0])
                compet_id = int(match.groups()[0])
                first = compet_id
                is_desclassif = False
                try:
                    compet = Compet.objects.get(compet_id=compet_id)
                except:
                    # already eliminated?
                    try:
                        compet = CompetDesclassif.objects.get(compet_id=compet_id)
                        is_desclassif = True
                    except:
                        print("error in compet", compet_id)
                        sys.exit(-1)
                    
                match = re.search(pattern_submission_id,submissions[0])
                submission_id = int(match.groups()[0])
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
                        print(compet.compet_id_full,compet.compet_type, file=sys.stderr)
                        continue


                cur_cluster_compets.add(compet.compet_id_full)
                if is_desclassif:
                    s = School.objects.get(school_id=compet.compet_school_id)
                    cluster.append([f"{problem}.{lang}",similarity,level,compet.compet_id_full+" *",compet.compet_name,f'"{s.school_name}"',public_score,f'{submissions[0]}'])
                else:
                    cluster.append([f"{problem}.{lang}",similarity,level,compet.compet_id_full,compet.compet_name,f'"{compet.compet_school.school_name}"',public_score,f'{submissions[0]}'])
                for i in range(2,len(submissions),3):
                    submission = submissions[i]
                    similarity = float(submissions[i+1])
                    if similarity < 60.0:
                        continue                    
                    match = re.search(pattern_problem_name,submission)
                    compet_id = int(match.groups()[0])
                    try:
                        compet = Compet.objects.get(compet_id=compet_id)
                    except:
                        # already eliminated?
                        try:
                            compet = CompetDesclassif.objects.get(compet_id=compet_id)
                            is_desclassif = True
                        except:
                            print("error in compet", compet_id)
                            continue
                        
                    match = re.search(pattern_submission_id,submission)
                    submission_id = int(match.groups()[0])
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
                            print(compet.compet_id_full,compet.compet_type, file=sys.stderr)
                            continue
                        
                    cur_cluster_compets.add(compet.compet_id_full)
                    if is_desclassif:
                        s = School.objects.get(school_id=compet.compet_school_id)
                        cluster.append([f"{problem}.{lang}",similarity,level,compet.compet_id_full+" *",compet.compet_name,f'"{s.school_name}"',public_score,f'{submissions[i]}'])
                    else:
                        cluster.append([f"{problem}.{lang}",similarity,level,compet.compet_id_full,compet.compet_name,f'"{compet.compet_school.school_name}"',public_score,f'{submissions[i]}'])

                # only compet in cluster?
                if len(cur_cluster_compets) == 1:
                    print("only compet in cluster",cur_cluster_compets)
                    cur_cluster_compets = set()
                    continue

                # check if seen cluster
                seen = False
                for c in seen_clusters_compets:
                    if cur_cluster_compets.issubset(c):
                        seen = True
                        break
                if seen:
                    cur_cluster_compets = set()
                    continue

                # all in cluster are desclassif?
                all_desclassif = True
                for cl in cluster:
                    if cl[3].find(" *") < 0:
                        all_desclassif = False
                        break
                if all_desclassif:
                    cur_cluster_compets = set()
                    print("all compets in cluster are desclassif")
                    continue

                seen_clusters_compets.append(cur_cluster_compets)
                cur_cluster_compets = set()
                clusters.append(cluster)

    filename = os.path.join(base_dir,f"clusters.csv")
    with open(filename,"w") as f:
        for cluster in clusters:
            print(cluster, file=f)
    
    filename = os.path.join(base_dir,f"jplag.csv")
    with open(filename,"w") as f:
        print("problem, similarity, compet_type, compet_id, compet_name, school, score",file=f)
        i = 1
        for cluster in clusters:
            print(f"Cluster {i},", file=f)
            for c in cluster:
                print(",".join([str(k) for k in c[:7]]), file=f, end=",")
                submission_link = f'https://olimpiada.ic.unicamp.br/{c[7]}.txt'
                submission_link = submission_link.replace('submissions', 'submissions_all')
                print(submission_link, file=f)
            print(file=f)
            i += 1

class Command(BaseCommand):
    help = 'Do JPLAG'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)
        parser.add_argument('min_lines', nargs='+', type=int)
        parser.add_argument('base_dir', nargs='+', type=str)

    def handle(self, *args, **options):
        contest_id = options['contest_id'][0]
        min_lines = options['min_lines'][0]
        base_dir = options['base_dir'][0]

        count,count_all,problem_names = copy_submissions(base_dir,contest_id,min_lines)
        print(f"count={count}, count_all={count_all}, problem_names={problem_names}")
        process_submissions(base_dir,contest_id,problem_names)
        process_results(base_dir,contest_id, problem_names)
        print("finished")
