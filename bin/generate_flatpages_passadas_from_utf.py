#!/usr/bin/env python3
# generate flatpages from old obi site

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

def generate_pages(fname):
    if not os.path.isdir(fname):
        print("error: -a needs a directory as argument")
        usage()
    for root, dirs, files in os.walk(fname):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == ".html":
                generate_page(os.path.join(root,name))

def generate_page(fname):
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

    DEST_DIR = 'gene'
    TEMPLATE = 'obi/flatpages_passadas.html'
    pattern_body = re.compile(r'<h1>(?P<title>[^<]*)</h1>.*</div>\s*</td>\s*<td width="\*" valign="top">\s*(<div>)?(?P<body>.*)(?P<tail>(</div>)?\s*<p>&nbsp;</p>\s*</td></tr>\s*</table></td></tr>\s*</table>\s*<table bgcolor="#FFFFF" width="1000" border="0" align="center" cellpadding="0" cellspacing="0">\s*)$',re.MULTILINE|re.DOTALL)
    try:
        body_search = pattern_body.search(data)
        title = clean(body_search.group('title'))
        body = clean(body_search.group('body'))
        body = '<h1>{}</h1>\n'.format(title)+body
        dest_path="/".join([DEST_DIR]+fname.split('/')[1:])
        #title = fname.split('/')[2]
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
    except:
        print('error: need a filename',file=sys.stderr)
        usage()
    if os.path.isdir(fname):
        generate_pages(fname)
    else:
        generate_page(fname)

if __name__ == "__main__":
    main()
