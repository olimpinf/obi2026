#!/usr/bin/env python3
# copy gabaritos from old site

import getopt
import html
import os
import re
import shutil
import sys


def usage():
    print('usage:{} page.html'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)

def error(s):
    print('error:{}'.format(s), file=sys.stderr)
    usage()

def generate_pages(fname):
    if not os.path.isdir(fname):
        print("error: -a needs a directory as argument")
        usage()
    for root, dirs, files in os.walk(fname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext in [".cpp",".c",".py",".java"]:
                generate_page(os.path.join(root,name))

def generate_page(path):
    '''Generates gabarito directory from old site'''
    print(path)
    DEST_DIR = 'obi/static/extra/solucoes/'
    DEST_DIR = '/tmp/solucoes'
    pattern = re.compile(r'utf8.*OBI(?P<year>\d{4})/res_fase(?P<phase>[12])_prog/programacao_n(?P<level>[12jus])/solucoes/(?P<pname>[^._0-9]*)(?P<version>_?[^.]*)\.(?P<lang>cpp|c|py|pas|java)')
    dir = re.sub(pattern,'\g<year>f\g<phase>p\g<level>_\g<pname>.\g<lang>',path)
    if dir!=path:
        #print(fname)
        #shutil.copy(path, fname)

        # hack to create problem directory in solutions
        dir = re.sub(pattern,'\g<year>f\g<phase>p\g<level>_\g<pname>',path)
        dir = os.path.join(DEST_DIR,dir)
        os.makedirs(dir,exist_ok=True)
        fname = re.sub(pattern,'\g<pname>\g<version>.\g<lang>',path)
        newpath = os.path.join(dir,fname)
        print(dir)
        print(newpath)
        print()
        shutil.copy(path, newpath)

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
        generate_pages(fname)
    else:
        generate_page(fname)

if __name__ == "__main__":
    main()
