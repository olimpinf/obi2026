#!/usr/bin/env python3
# rename files

import getopt
import html
import os
import re
import sys


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
            if ext == ".pdf":
                update_page(os.path.join(root,name))

def update_page(fname):
    '''update page name'''
    pattern_prova_inic = re.compile(r'(?P<year>ProvaOBI\d{4})_inic_f(?P<phase>\d)n(?P<level>[1-2]).pdf',re.MULTILINE|re.DOTALL)
    new = re.sub(pattern_prova_inic,"\g<year>_f\g<phase>i\g<level>",fname)
    if new!=fname:
        print("{} --> {}".format(fname,new+".pdf"))
        os.rename(fname,new+".pdf")
        return
    pattern_prova_prog = re.compile(r'(?P<year>ProvaOBI\d{4})_prog_f(?P<phase>\d)n(?P<level>[1-2]|j|s|u).pdf',re.MULTILINE|re.DOTALL)
    new = re.sub(pattern_prova_prog,"\g<year>_f\g<phase>p\g<level>",fname)
    if new!=fname:
        print("{} --> {}".format(fname,new+".pdf"))
        os.rename(fname,new+".pdf")


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "au", ["all", "update"])
    except getopt.GetoptError as err:
        print(err, file=sys.stderr) 
        usage()
    # not used...
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
