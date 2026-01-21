#!/usr/bin/env python3
# generate flatpages from old obi site

import getopt
import html
import os
import re
import sys


def usage():
    print('usage:{} page.html year'.format(sys.argv[0]), file=sys.stderr)
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

def generate_pages(fname, year):
    if not os.path.isdir(fname):
        print("error: -a needs a directory as argument")
        usage()
    for root, dirs, files in os.walk(fname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                generate_page(os.path.join(root,name), year)

def generate_page(fname, year):
    '''Generates a flatpage from old site'''
    print('generate',fname)
    try:
        with open(fname,"r") as f:
            data = f.read()
    except:
        try:
            with open(fname,"r",encoding="latin1") as f:
                data = f.read()
        except:
            error('cannot read data, encoding bad?')
            usage()

    DEST_DIR = 'gene_' + year
    TEMPLATE = 'flatpages_passadas.html'
    try:
        clean_data = clean(data)

        title = ''
        h1 = re.findall('<h1>(.*)</h1>', clean_data)
        title = clean_data.split('\n')[0].replace('title:', '') if len(h1) == 0 or '<!--<h1>' in clean_data else h1[0]
        title = title.split(',')[0]
        title = title.replace(' - OBI' + year, '')

        clean_data = re.sub('(<!--)*<h1>.*</h1>( -->)*', '', clean_data)
        parsed_data = clean_data.split('.html\n')[1]
        body = '\n<!--<h1>OBI'+year+'</h1> -->\n'
        body += '<center><h1>' + title + '</h1></center>' if 'qmerito' in fname else '<h1>' + title + '</h1>'
        body += '\n' + parsed_data

        dest_path = '/'.join([DEST_DIR, fname.split('resultados/')[1]])
        dest_path = dest_path.replace('/cadernos', '')
        save_file(dest_path,title,body,TEMPLATE)
    except:
        print(fname, 'failed', file=sys.stderr)

def clean(s):
    '''clean the page: html accent marks, fix links to extra, etc '''
    s = s.replace('../../../extras/','/extras/')
    s = html.unescape(s)
    s = s.replace("'","&quot;") # flatpages is inserted as sql text
    return s

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
        year = args[1]
    except:
        print('error: need a filename and year',file=sys.stderr)
        usage()
    if os.path.isdir(fname):
        generate_pages(fname, year)
    else:
        generate_page(fname, year)

if __name__ == "__main__":
    main()

