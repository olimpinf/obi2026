#!/usr/bin/env python3
# rename files

import getopt
import html
import os
import re
import sys

oldheader = '''<table border="0" cellpadding="4" cellspacing="0" width="100%"> 
<tr class="row-header">
<td> </td>
<td align="center">Classif.</td>
<td align="center">Pontos</td>
<td>Nome</td>
<td>Escola</td>
<td>Cidade</td>
<td>Estado</td>
</tr>
'''
newheader = '''<table class="basic"> 
<tr>
<th colspan="2" align="center">Classif.</th>
<th align="center">Nota</th>
<th>Nome</th>
<th>Escola</th>
<th>Cidade</th>
<th>Estado</th>
</tr>
'''


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
                print(root,name)
                update_page(os.path.join(root,name))

def update_page(fname):
    '''update table in page'''
    pattern_table_header = re.compile(oldheader,re.MULTILINE)
    with open(fname,'r') as fin:
        data = fin.read()
    newdata = re.sub(pattern_table_header,newheader,data)
    if newdata!=data:
        with open(fname,'w') as fout:
            fout.write(newdata)
        print("updated {}".format(fname))

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
