#!/usr/bin/env python3
# change urls in pages

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

#<li>A
#       Bondinho: <a href="../../extras/solucoes/2017f1pj_bondinho/bondinho.cpp">C++</a>,
    # 2017
    pattern = re.compile(r'<li>\s*(?P<name>[^:&]*?):\s*<a href=.*?/(?P<year>[0-9]{4})f(?P<phase>[123s])p(?P<level>[12ju])_(?P<pname>[^/]*)/*?>',re.MULTILINE|re.DOTALL)
    # pre 2017
    #pattern = re.compile(r'<li>\s*(?P<name>[^:]*?):\s*<a href=.*?/(?P<year>[0-9]{4})f(?P<phase>[123s])p(?P<level>[12ju])_(?P<pname>[^/]*)/.*?>',re.MULTILINE|re.DOTALL)
    # pre 2013
    pattern = re.compile(r'<li>\s*(?P<name>[^:&]*?):\s*<a href=.*?/(?P<year>[0-9]{4})f(?P<phase>[123s])p(?P<level>[12ju])_(?P<pname>[^.]*).zip',re.MULTILINE|re.DOTALL)
    matches = re.findall(pattern,data)
    for match in matches:
        print('{}f{}p{}_{}'.format(match[1],match[2],match[3],match[4]), match[0])
#         try:
#             with open(fname,"w") as f:
#                 f.write(data1)
#         except:
#             error('cannot write data, encoding bad?')
#             usage()

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
