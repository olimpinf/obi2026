#!/usr/bin/env python3
#/usr/local/bin/python3

import csv
import os
import os.path
import string
import sys
import tempfile
from random import randint

from reportlab.graphics import renderPDF
from reportlab.graphics.barcode import code128
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.lib.colors import *
#from django.conf import settings
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import cm, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Image as rpImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT
from reportlab.pdfbase.pdfmetrics import stringWidth


# to execute outside django:
#BASE_DIR = os.path.join(os.getcwd(),'..','..')

# build a sheet filled, for testing purposes

def error(s):
    print(s, file=sys.stderr)
    sys.exit(-1)

def usage():
    print(f'usage: {sys.argv[0]} input.csv output.csv start', file=sys.stderr)
    sys.exit(-1)

def split_name(name):
    names = name.split()
    if (names[0] == 'Ana' and names[1] == 'Júlia') or \
       (names[0] == 'Ana' and names[1] == 'Julia') or \
       (names[0] == 'João' and names[1] == 'Paulo') or \
       (names[0] == 'João' and names[1] == 'Pedro') or \
       (names[0] == 'Maria' and names[1] == 'Clara'):
        first = " ".join(names[:2])
        last = " ".join(names[2:])
    else:
        first = names[0]
        last = " ".join(names[1:])
    return first, last

if __name__=="__main__":
    try:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
        start_number = int(sys.argv[3])
    except:
        usage()
        
    data = []
    try:
        ifile=open(input_file,"r")
        reader=csv.reader(ifile)
    except:
        try:
            ifile=open(input_file,"r",encoding='iso-8859-1')
            reader=csv.reader(ifile)
        except:
            print("cannot open input_file", file=sys.stderr)

    number = start_number
    for r in reader:
        if len(r)==0:
            continue
        person = []
        number += 1
        # name
        first, last = split_name(r[0])
        person.append(first)
        person.append(last)
        # role
        person.append(r[1])
        # id for qr_code
        person.append(number)
        # allergies
        person.append(r[2])
        data.append(person)
            

    with open(output_file, 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        for x in data:
            writer.writerow(x)

        
