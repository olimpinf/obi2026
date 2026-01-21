#!/usr/bin/env python3.9

import csv
import sys
import re
import os
import getopt
import shutil
from datetime import datetime
from glob import glob
from functools import cmp_to_key

PROBLEMS_DIR = '../problems'

def usage():
    print('usage:\n  {} [-h] [-u users] contest_description_file'.format(sys.argv[0]))
    sys.exit(2)

def read_users(filename):
    if not os.path.isfile(filename):
        print(f"ERROR: file {filename} not found", file=sys.stderr)
        sys.exit(2)
    try:
        csvf = open(filename,"r", encoding='utf-8')
        #print('utf-8')
    except:
        try:
            csvf = open(filename,"r", encoding='iso8859-1')
            #print('iso8859-1')
        except:
            msg = f'ERROR: Problema na decodificação do arquivo "{filename}". Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
            print(msg, file=sys.stderr)
            sys.exit(2)
    
    reader = csv.reader(csvf) #, delimiter=delimiter)
    linenum=0
    users = []
    for r in reader:
        linenum += 1
        if len(r)==0:
            continue
        try:
            username = r[0].strip()
            password = r[1].strip()
            name = r[2].strip()
        except:
            print(f"ERROR: problem in user file {filename}, line {linenum}: {r}")
            sys.exit(2)
        if id == 'user_id':
            # first line
            continue

        #try:
        #    username = format_compet_id(int(id))
        #except:
        #    # not an obi registration number
        #    username = id
        
        try:
            first = name
            last = r[3].strip()
        except:
            tks = name.split()
            if len(tks) == 2:
                first = tks[0]
                last = tks[1]
            else:
                first = f'{tks[0]} {tks[1]}' 
                last = tks[-1]
            pass
        users.append((username,password,'null',first,last))

    return users

def compare_grp(a,b):
    a = int(os.path.basename(a))
    b = int(os.path.basename(b))
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

def compare_tst(a,b):
    a = int(os.path.basename(a).split('.')[0])
    b = int(os.path.basename(b).split('.')[0])
    if a > b:
        return 1
    elif a < b:
        return -1
    else:
        return 0

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hu:", ["help","users"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)  # will print something like "option -a not recognized"
        usage()
    contest_description = "Contest Description"
    users_file = ""
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-u", "--users"):
            users_file = a
        else:
            assert False, "unhandled option"

    if len(args) == 1:
        contest_descr_file = args[0]
    else:
        usage()

    if not os.path.exists(contest_descr_file):
        usage()

    contest_descr = {}
    with open(contest_descr_file) as f:
        code = compile(f.read(), contest_descr_file, 'exec')
        exec(code,contest_descr)

    contest_name = contest_descr['name']
    contest_description = contest_descr['description']
    if os.path.exists(contest_name):
        print(f'directory {contest_name} exists and will be cleaned. Proceed? [Y/n]', file=sys.stderr, end=' ')
        answer = input().strip()
        if (not answer) or answer in ('Y','y'):
            shutil.rmtree(contest_name)
        else:
            print('directory not cleaned, exiting', file=sys.stderr)
            sys.exit(0)
    os.mkdir(contest_name)
    base = os.curdir

    ##############
    # contest.yaml
    ##############
    fcontest = open(os.path.join(base, contest_name, "contest.yaml"), "w")

    for k in contest_descr.keys():
        if k == '__builtins__':
            continue
        elif k == 'start':
            date = datetime.fromisoformat(contest_descr[k])
            timestamp = int(date.timestamp())
            print(f'{k}: {timestamp}', file=fcontest)
            continue
        elif k == 'stop':
            date = datetime.fromisoformat(contest_descr[k])
            timestamp = int(date.timestamp())
            print(f'{k}: {timestamp}', file=fcontest)
            continue
        try:
            print(f'{k}: {int(contest_descr[k])}', file=fcontest)
        except:
            print(f'{k}: "{contest_descr[k]}"', file=fcontest)
    
    print(f'password_method: "pbkdf2"', file=fcontest)

    # print(f'name: "{contest_name}"', file=fcontest)
    # print(f'description: "{contest_description}"', file=fcontest)
    # print(f'token_mode: disabled', file=fcontest)
    # print(f'min_submission_interval: 60', file=fcontest)
    # print(f'min_user_test_interval: 60', file=fcontest)
    # print(f'max_submission_number: 100', file=fcontest)
    # print(f'max_user_test_number: 100', file=fcontest)

    print(f'tasks:', file=fcontest)
    # problems
    contest_problems = contest_descr['problems']
    all_problems=glob(os.path.join(PROBLEMS_DIR, "*"))
    print(all_problems)
    if contest_problems == 'all':
        problems = all_problems
    else:
        problems = []
        for problem in all_problems:
            pname = os.path.basename(problem)
            if pname in contest_problems:
                problems.append(problem)
    for problem in problems:
        pname = os.path.basename(problem)
        print(pname)
        print(f'  - "{pname}"', file=fcontest)

    # users
    print(f'users:', file=fcontest)
    if users_file == "":
        users = [("u1","p1","null"),("u2","p2","null")]
    else:
        users = read_users(users_file)
    for u in users:
        print(f'  - username: "{u[0]}"', file=fcontest)
        print(f'    password: "{u[1]}"', file=fcontest)
        print(f'    password_method: "pbkdf2"', file=fcontest)
        print(f'    ip: {u[2]}', file=fcontest)
        if len(u) >= 4:
            print(f'    first_name: "{u[3]}"', file=fcontest)
        if len(u) >= 5:
            print(f'    last_name: "{u[4]}"', file=fcontest)

    #######
    # tasks
    #######
    with open("task_titles.csv") as f:
        lines = f.readlines()
    titles = {}
    for line in lines:
        name,title = line.strip().split(';')
        titles[name] = title
        
    for problem in problems:
        pname = os.path.basename(problem)
        print(f"building task {pname}")
        os.mkdir(os.path.join(base,contest_name,pname))
        ftask = open(os.path.join(base,contest_name,pname,"task.yaml"), "w")
        print(f'name: "{pname}"', file=ftask)

        cmsfile = "cms.txt"
        if not os.path.isfile(cmsfile):
            print(f"ERROR: could not find file cms.txt for task {pname} (to fix, create a file called cms.txt in the attic directory)", file=sys.stderr)
            sys.exit(2)

        cmsinfo = {}
        with open(cmsfile) as f:
            code = compile(f.read(), cmsfile, 'exec')
            exec(code,cmsinfo)

        print('pname',pname)
        if pname in titles.keys():
            title = titles[pname]
        else:
            title = pname.capitalize()
            print(f"could not find 'title' for task {pname}, using {pname.capitalize()}")
        print(f'title: "{title}"', file=ftask)
        print(f'    title: "{title}"', file=sys.stderr)

        # statement
        statement = "statement.pdf"
        if not os.path.isfile(statement):
            print(f"ERROR: could not find file statement.pdf for task {pname} (to fix, run 'box check' on the problem)", file=sys.stderr)
            sys.exit(2)
        os.mkdir(os.path.join(base,contest_name,pname,"statement"))
        shutil.copy(statement,os.path.join(base, contest_name, pname, 'statement', f'statement.pdf'))
        
        # task memory limit
        if 'memory_limit' in cmsinfo.keys():
            memory_limit = cmsinfo['memory_limit']
        else:
            memory_limit = 1024
        print(f'memory_limit: {memory_limit}', file=ftask)
        print(f'    memory_limit: {memory_limit}', file=sys.stderr)

        # task time limit
        if 'time_limit' in cmsinfo.keys():
            time_limit = cmsinfo['time_limit']
        else:
            limitsfile = os.path.join(problem,"attic","problem.desc")
            if not os.path.isfile(limitsfile):
                print(f"ERROR: could not find time limit for task {pname} (to fix, specify 'time_limit' in 'cms.txt or 'run 'box check' on the problem)", file=sys.stderr)
                sys.exit(2)
            limits = {}
            with open(limitsfile) as f:
                code = compile(f.read(), limitsfile, 'exec')
                exec(code,limits)
            if 'time_limit_c' in limits.keys():
                time_limit = limits['time_limit_c']
            else:
                print(f"ERROR: could not find time limit for task {pname} (to fix, specify 'time_limit' in 'cms.txt or 'run 'box check' on the problem)", file=sys.stderr)
                sys.exit(2)
        print(f'time_limit: {time_limit}', file=ftask)
        print(f'    time_limit: {time_limit}', file=sys.stderr)

        if 'token_mode' in cmsinfo.keys():
            token_mode = cmsinfo['token_mode']
        else:
            token_mode = 'disabled'
        print(f'token_mode: {token_mode}', file=ftask)

        # input
        os.mkdir(os.path.join(base,contest_name,pname,"input"))
        n_input = 0
        from_dir = os.path.join(PROBLEMS_DIR,pname,'build','tests','[0-9]*')
        groups = glob(from_dir)
        if not groups:
            print(f"ERROR: could not find input files for task {pname}, exiting (to fix, run 'box check' on the problem)", file=sys.stderr)
            sys.exit(3)
        groups.sort(key=cmp_to_key(compare_grp))
        groupnums = []
        for group in groups:
            from_dir = os.path.join(group,'*.in')
            test_cases = glob(from_dir)
            test_cases.sort(key=cmp_to_key(compare_tst))
            testnums = []
            for test_case in test_cases:
                shutil.copy(test_case,os.path.join(base, contest_name, pname, 'input', f'input{n_input}.txt'))
                testnums.append(n_input)
                n_input += 1
            groupnums.append(testnums)

        # scoring
        os.mkdir(os.path.join(base,contest_name,pname,"gen"))

        # try to get the points distribution from testplan.txt file
        scores = []

        if not scores:
            # points not set in testplan, divide evenly
            score = 100//len(groupnums)
            scores = [score for i in range(len(groupnums))]

        if sum(scores) != 100:
            print(f'WARNING: total score is not 100 for task {pname} ({sum(scores)})')
        print('scores',len(scores),scores)
        print('groupnums',len(groupnums),groupnums)

        len_groups = []
        with open(os.path.join(base,contest_name,pname,"gen","GEN"), "w") as fgen:
            for k in range(len(groupnums)):
                g = groupnums[k]
                len_groups.append(len(g))
                print(f'# ST: {scores[k]}', file=fgen)
                for t in g:
                    print(t, file=fgen)
        print(f'    # groups:', len(groupnums), file=sys.stderr)
        print(f'    # tests in each group:', ",".join([str(i) for i in len_groups]), file=sys.stderr)
        print(f'    # points for each group:', ",".join([str(i) for i in scores]), file=sys.stderr)

        
        # task public test cases
        if 'public_testcases' in cmsinfo.keys():
            public_testcases = cmsinfo['public_testcases']
        else:
            tmp = []
            for t in groupnums[0]:
                tmp.append(t)
            public_testcases = ",".join([str(i) for i in tmp])
        print(f'public_testcases: {public_testcases}', file=ftask)
        print(f'    public_testcases: {public_testcases}', file=sys.stderr)

        # output
        os.mkdir(os.path.join(base,contest_name,pname,"output"))
        n_output = 0
        from_dir = os.path.join(PROBLEMS_DIR,pname,'build','tests','[0-9]*')
        groups = glob(from_dir)
        if not groups:
            print(f"ERROR: could not find output files for task {pname}, exiting (to fix, run 'box check' on the problem)", file=sys.stderr)
            sys.exit(3)
        groups.sort(key=cmp_to_key(compare_grp))
        groupnums = []
        for group in groups:
            from_dir = os.path.join(group,'*.sol')
            test_cases = glob(from_dir)
            test_cases.sort(key=cmp_to_key(compare_tst))
            testnums = []
            for test_case in test_cases:
                shutil.copy(test_case,os.path.join(base, contest_name, pname, 'output', f'output{n_output}.txt'))
                testnums.append(n_output)
                n_output += 1
            groupnums.append(testnums)
        if n_input != n_output:
            print(f"ERROR: number of input and output tests differ for task {pname}, exiting", file=sys.stderr)

        # task parameters
        print(f'primary_language: "pt"', file=ftask)
        print(f'infile: ""', file=ftask)  # use stdin for input
        print(f'outfile: ""', file=ftask) # use stdout for output

        # other task parameters defined by the user
        for k in cmsinfo.keys():
            if k in ('__builtins__','title','time_limit','memory_limit','primary_language','token_mode','infile','outpfile'):
                continue
            try:
                print(f'{k}: {int(cmsinfo[k])}', file=ftask)
            except:
                print(f'{k}: "{cmsinfo[k]}"', file=ftask)

if __name__ == "__main__":
    main()
