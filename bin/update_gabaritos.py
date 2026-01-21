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

    pattern_fname = re.compile(r'OBI(?P<year>\d{4})/fase(?P<phase>[12])/programacao')
    match = re.search(pattern_fname,fname)
    if not match:
        return
    phase = match.group('phase')
    year = match.group('year')
    # new (wrong) href
    pattern = re.compile(r'/static/extras/gabaritos/(?P<year>[0-9]{4})f(?P<phase>[12])p(?P<level>[12j])_(?P<pname>[^._0-9/]*)(?P<version>_?[^./]*)?\.(?P<lang>cpp|c|py|pas|java)')
    match = re.search(pattern,data)
    data1 = data
    if match:
        print('fix name',match.group('pname'),'in file',fname)
        fstr = '/static/extras/solucoes/\g<year>f\g<phase>p\g<level>_\g<pname>/\g<pname>\g<version>.\g<lang>'.format(year,phase)
        data1 = re.sub(pattern,fstr,data)
    # old href
    pattern = re.compile(r'(http:/olimpiada.ic.unicamp.br/passadas/OBI[0-9]{4}/res_fase[12]_prog/)?programacao_n(?P<level>[12j])/solucoes/(?P<pname>[^._0-9]*)(?P<version>_?[^./]*)?\.(?P<lang>cpp|c|py|pas|java)')
    match = re.search(pattern,data)
    if match:
        fstr = '/static/extras/solucoes/{}f{}p\g<level>_\g<pname>/\g<pname>\g<version>.\g<lang>'.format(year,phase)
        data1 = re.sub(pattern,fstr,data1)
        print("************")
    if data != data1:
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
