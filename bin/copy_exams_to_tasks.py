#!/usr/bin/env python3
# change urls in pages

import getopt
import html
import os
import re
import sys

YEAR = 2021

def usage():
    print('usage:{} page.html'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error:{}'.format(s), file=sys.stderr)
    usage()

def update_pages(fname):
    if not os.path.isdir(fname):
        print("error: -a needs a directory as argument")
        usage()
    for root, dirs, files in os.walk(fname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                update_page(os.path.join(root,name))

def update_page(fname):
    '''update urls from page'''
    try:
        with open(fname,"r") as f:
            data = f.read()
    except:
        error('cannot read data, encoding bad?')
        usage()

    print("update",fname)
    #  html_exams/provaf1/i1/provaf1i1_
    #pattern = re.compile(r'html_exams/provaf(?P<phase>[123s])(?P<mod>[ip])(?P<level>[12ju])_(?P<pname>[^.]*).html',re.DOTALL)
    pattern = re.compile(r'html_exams/provaf(?P<phase>[123s])/(?P<mod>[ip])(?P<level>[12ju])/(?P<prename>prova[^.]*)_(?P<pname>[^.]*).html',re.DOTALL)
    matches = re.findall(pattern,fname)
    for match in matches:
        phase = match[0]
        mod = match[1]
        level = match[2]
        prename = match[3]
        name = match[4]
        orig_name = f'html_exams/provaf{phase}/{mod}{level}/{prename}_{name}.html'
        if mod == 'i':
            dest_name = f'html_tasks/ini/{YEAR}/{YEAR}f{phase}{mod}{level}_{name}.html'
        else:
            dest_name = f'html_tasks/prog/{YEAR}/{YEAR}f{phase}{mod}{level}_{name}.html'

        os.system(f"cp {orig_name} {dest_name}")
        os.system(f"sed -i s/template:exams/template:tasks/ {dest_name}")
        os.system(f"sed -i 's/order:.*$//' {dest_name}")
        os.system(f"sed -i 's/task_images\/prova/task_images\/{YEAR}/' {dest_name}")
        try:
            # only if it has image
            os.system(f"cp static/img/task_images/provaf{phase}{mod}{level}_{name}.png static/img/task_images/{YEAR}f{phase}{mod}{level}_{name}.png")
            os.system(f"mv static/img/task_images/provaf{phase}{mod}{level}_{name}.png static/img/task_images/old_prova{YEAR}f{phase}{mod}{level}_{name}.png")
        except:
            pass
def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "au", ["all", "update"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    all = False
    update = False
    for o, a in opts:
        if o in ("-a", "--all"):
            all = True
        elif o in ("-u", "--update"):
            update = True
        else:
            assert False, "unhandled option"

    try:
        fname = args[0]
    except:
        print('error: need a filename',file=sys.stderr)
        usage()
    if os.path.isdir(fname):
        update_pages(fname)
    else:
        update_page(fname)

if __name__ == "__main__":
    main()
