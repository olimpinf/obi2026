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
            if ext == ".zip":
                generate_page(os.path.join(root,name))

def generate_page(path):
    '''Generates gabarito directory from old site'''
    DEST_DIR = '/tmp/gabaritos/'
    #pattern = re.compile(r'utf8.*OBI(?P<year>\d{4})/res_prog(?P<phase>[12])_prog/programacao_n(?P<level>[12jus])/gabaritos/(?P<pname>.*)\.zip')
    # utf8.olimpiada.ic.unicamp.br/passadas/OBI2004/res_prog/gabaritos/furos.zip
    #pattern = re.compile(r'utf8.*OBI(?P<year>\d{4})/res_prog/programacao_n(?P<level>[12jus])/gabaritos/(?P<pname>.*)\.zip')
    pattern = re.compile(r'utf8.*OBI(?P<year>\d{4})/res_prog/gabaritos/(?P<pname>.*)\.zip')
    #fname = re.sub(pattern,'\g<year>f\g<phase>p\g<level>_\g<pname>.zip',path)
    #fname = re.sub(pattern,'\g<year>f1p\g<level>_\g<pname>.zip',path)
    fname = re.sub(pattern,'\g<year>f1p2_\g<pname>.zip',path)
    if fname!=path:
        fname = os.path.join(DEST_DIR,fname)
        print(fname)
        shutil.copy(path, fname)

        # hack to create problem directory in solutions
        # DEST_DIR = '/tmp/gabaritos'
#         fname = re.sub(pattern,'\g<year>f1p\g<level>_\g<pname>',path)
#         fname = os.path.join(DEST_DIR,fname)
#         os.makedirs(fname,exist_ok=True)
#         print(fname)

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
