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


def main():
    try:
        fname = sys.argv[1]
    except:
        print('error: need a filename',file=sys.stderr)
        usage()
    with open(fname,'r') as fin:
        data = fin.read()
    pat = re.compile(r'<pre>(?P<gab>[^<]*)</pre>',re.MULTILINE|re.DOTALL)
    m = re.search(pat,data)
    if m:
        print(m.group('gab'))
    else:
        print("nothing",file=sys.stderr)

if __name__ == "__main__":
    main()
