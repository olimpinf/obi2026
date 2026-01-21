#!/usr/bin/env python3

VERSION= 0.1

import getopt
import os
import os.path
import shutil
import subprocess
import sys, re
from glob import glob
from tempfile import NamedTemporaryFile

# languages
EN=0
PT=1

    
def build_class_list(course_name_full,course_id,base):
    u"Build page."
    class_idx = 1
    page = '<h1>{}</h1>\n'.format(course_name_full)
    page += '<ul>\n'
    while True:
        dir=os.path.join('cursos',course_id,str(class_idx))
        try:
            exec(open(os.path.join(base, dir, 'info')).read(),globals())
        except:
            break
        if public == 'yes':
            page += '<li><a href="/saci/cursos/{}/{}/">{}</a>'.format(course_id,index,title)
        class_idx += 1
    page += '</ul>\n'
    return page
        

def parse_arguments():
    optlist, args = getopt.gnu_getopt(sys.argv[1:], 'bemvu:c:p')
    minify,lang,prog_lang,blockly=False,PT,'js',False
    for flag, arg in optlist:
        if flag == '-v':
            print("build version %s" % VERSION, file=sys.stderr)
            sys.exit(0)
        if flag == '-b':
            blockly=True;
        if flag == '-m':
            minify=True;
        if flag == '-u':
            user=arg
        if flag == '-c':
            course=arg
        if flag == '-e':
            lang=EN
        if flag == '-p':
            prog_lang='py'
    if lang==EN:
        user,course_name_full,course_name_short='notregistered@saci','Introduction do computer programming','intro_js'
    else:
        user,course_name_full,course_name_short='naoregistrado@saci','Introdução à programação de computadores','intro_js'

    if len(args) != 2:
        usage()
    course_name_short = args[0]
    class_index = args[1]
    course_name_full = 'Nome do curso'
    return course_name_full,course_name_short,class_index,user,minify,lang,prog_lang,blockly

def usage():
    print("usage: {} course class".format(sys.argv[0]),file=sys.stderr)
    sys.exit(-1)
    
def _main():
    pass
    # course_name_full,course_name_short,class_index,user,minify,lang,prog_lang,blockly = parse_arguments()
    # base=os.path.dirname('.');
    # print('building', course_name_short, class_index, file=sys.stderr)
    # txt=build_page(course_name_full,course_name_short,class_index,user,base,minify,lang,prog_lang,blockly)
    # if txt: print(txt)

if __name__ == '__main__':
    _main()

