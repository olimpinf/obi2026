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
    print(f'usage: {sys.argv[0]} data.csv]', file=sys.stderr)
    sys.exit(-1)

def draw_page(myCanvas, id):

    ####################
    # qr code bottom
    ####################

    qrcode_data = f"{id}"
    marginleft = -10
    marginbottom = -10
    qrw = QrCodeWidget(qrcode_data, barLevel='H')
    qrsize=100.0
    b = qrw.getBounds()
    w=b[2]-b[0]
    h=b[3]-b[1]
    d = Drawing(qrsize,qrsize,transform=[qrsize/w,0,0,qrsize/h,0,0])
    d.add(qrw)
    # there is an offset, compensate it
    #renderPDF.draw(d,myCanvas,marginleft-12*scale,marginbottom-16*scale)
    renderPDF.draw(d,myCanvas,marginleft,marginbottom)
    myCanvas.showPage()

if __name__=="__main__":
    try:
        input_file = sys.argv[1]
    except:
        usage()
        
    pagesize = (80, 80)

    data = []
    try:
        ifile=open(input_file,"r")
        reader=csv.reader(ifile)
        for r in reader:
            if len(r)==0:
                continue
            if r[3].strip().lower()=='id':
                continue
            try:
                id=r[3].strip()
                data.append(id)
            except:
                usage()
    except:
        try:
            ifile=open(input_file,"r",encoding='iso-8859-1')
            reader=csv.reader(ifile)
            for r in reader:
                if len(r)==0:
                    continue
                if r[3].strip().lower()=='id':
                    continue
                try:
                    ra=r[3].strip()
                    data.append(id)
                except:
                    usage()
        except:
            usage()
            

    print(data)
    for id in data:
        output_file = os.path.join('qrcodes',f"{id}.pdf")
        mCanvas = canvas.Canvas(output_file, pagesize=pagesize)
        draw_page(mCanvas, id)
        mCanvas.save() 
        
