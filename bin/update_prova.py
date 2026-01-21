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

def save_file(path,title,body,template):
    dirs,fname=os.path.split(path)
    try:
        os.makedirs(dirs,exist_ok=True)
    except:
        pass
        #error('could not create directories {}'.format(dirs))
    with open(path,'w') as fout:
        fout.write('title:{}\n'.format(title))
        fout.write('template:{}\n'.format(template))
        fout.write(body)
    print('saved',path)

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

    #pattern_prova = re.compile(r'(?P<year>ProvaOBI\d{4})_inic_f(?P<phase>\d)n(?<Plevel>\d).pdf',re.MULTILINE|re.DOTALL)
    #pattern_prova_inic = re.compile(r'(?P<year>ProvaOBI\d{4})_inic_f(?P<phase>\d)n(?P<level>[1-2]).pdf',re.MULTILINE|re.DOTALL)
    #pattern_prova_inic = re.compile(r'(?P<year>ProvaOBI\d{4})_f(?P<phase>\d)i(?P<level>[1-2])"',re.MULTILINE|re.DOTALL)
    pattern_prefix_prova = re.compile(r'"(?P<prefix>pdf/provas/)',re.MULTILINE|re.DOTALL)
    data1 = re.sub(pattern_prefix_prova,'/static/extras/provas/',data)
    #pattern_prova_prog = re.compile(r'(?P<year>ProvaOBI\d{4})_prog_f(?P<phase>\d)n(?P<level>[1-2]|j|s|u).pdf',re.MULTILINE|re.DOTALL)
    #pattern_prova_prog = re.compile(r'(?P<year>ProvaOBI\d{4})_f(?P<phase>\d)p(?P<level>[1-2]|j|s|u)"',re.MULTILINE|re.DOTALL)
    #data1 = re.sub(pattern_prova_prog,'\g<year>_f\g<phase>p\g<level>.pdf"',data1)
    if data1!=data:
        print('update',fname)
        try:
            with open(fname,"w") as f:
                f.write(data1)
        except:
            error('cannot write data, encoding bad?')
            usage()

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
