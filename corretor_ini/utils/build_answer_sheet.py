#!/usr/local/bin/python3

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

from django.utils import translation
from django.utils.translation import gettext as _

#from scangrader_web.settings import BASE_DIR
from obi.settings import BASE_DIR, YEAR
# to execute outside django:
#BASE_DIR = os.path.join(os.getcwd(),'..','..')

# build a sheet filled, for testing purposes
BUILD_FILLED_TEST = False

IS_HALF_PAGE = 0b001
HAS_KEY_VERSION = 0b010
ID_IS_QRCODE = 0b100
HAS_ID_CHECK = 0b1000
MAX_KEY_VERSIONS = 3
MAX_NUMBER_OF_QUESTIONS = 100
MAX_NUMBER_OF_ALTERNATIVES = 5
MAX_NUMBER_KEY_CONFIG_ALTERNATIVES = 5
MAX_NUMBER_OF_DIGITS = 7

# Global variables
page_width, page_height = (597.6, 842.4) #  use same as IOS, not A4
letter_to_num={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9}
num_to_letter={0:'A', 1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J'}

# For OBI, always use id check
sheet_type = HAS_ID_CHECK

def error(s):
    print(s, file=sys.stderr)
    sys.exit(-1)

#**********************
# compute_answer_circles
#**********************

def compute_answer_circles(num_questions, left, top, scale):
    blocks =  []
        
    if (scale == 1):
        if (num_questions <= 9):
            # cout << "<=9" << endl;
            blocks.append((left+30+40,top+18))
            blocks.append((left+30+190,top+18))
            blocks.append((left+30+380-40,top+18))            
        elif (num_questions == 10):
            # cout << "==10" << endl;
            blocks.append((left+30+20,top+18))      #  30
            blocks.append((left+30+135,top+18)) #  30+125
            blocks.append((left+30+250,top+18)) #  30+250
            blocks.append((left+30+365,top+18)) #  30+375
        elif (num_questions <= 15):
            # cout << "<=15" << endl;
            blocks.append((left+30+40,top+18))
            blocks.append((left+30+190,top+18))
            blocks.append((left+30+380-40,top+18))
        elif (num_questions <= 20):
            # cout << "=20" << endl;
            blocks.append((left+30+20,top+18))      #  30
            blocks.append((left+30+135,top+18)) #  30+125
            blocks.append((left+30+250,top+18)) #  30+250
            blocks.append((left+30+365,top+18)) #  30+375
        elif (num_questions <= 30):
            # cout << "=30" << endl;
            blocks.append((left+30+40,top+18))
            blocks.append((left+30+190,top+18))
            blocks.append((left+30+380-40,top+18))
        elif (num_questions <= 50):
            # cout << "=40" << endl;
            blocks.append((left+30+20,top+18))      #  30
            blocks.append((left+30+135,top+18)) #  30+125
            blocks.append((left+30+250,top+18)) #  30+250
            blocks.append((left+30+365,top+18)) #  30+375
        elif (num_questions <= 75):
            # cout << "=30" << endl;
            blocks.append((left+30+40,top+18))
            blocks.append((left+30+190,top+18))
            blocks.append((left+30+380-40,top+18))
        elif (num_questions <= 100):
            # cout << "=40" << endl;
            blocks.append((left+30+20,top+18))      #  30
            blocks.append((left+30+135,top+18)) #  30+125
        blocks.append((left+30+250,top+18)) #  30+250
        blocks.append((left+30+365,top+18)) #  30+375
    else:
        if (num_questions <= 9):
            blocks.append((left+30+25,top+28))  #  30+15
            blocks.append((left+30+177,top+28)) #  30+180
            blocks.append((left+30+335,top+28)) #  30+345
        elif (num_questions <= 10):
            blocks.append((left+30+80,top+28))
            blocks.append((left+30+280,top+28))
        elif (num_questions <= 15):
            blocks.append((left+30+25,top+28))  #  30+15
            blocks.append((left+30+177,top+28)) #  30+180
            blocks.append((left+30+335,top+28)) #  30+345
        elif (num_questions <= 20):
            blocks.append((left+30+80,top+28))
            blocks.append((left+30+280,top+28))
        elif (num_questions <= 30):
            blocks.append((left+30+25,top+28))  #  30+15
            blocks.append((left+30+177,top+28)) #  30+180
            blocks.append((left+30+335,top+28)) #  30+345
            
    circles = []
    vspace = scale*34/2
    hspace = scale*34/2
        
    for b in blocks:
        num_rows = 25 if scale == 1 else  10
        num_columns = 5
        xstart = b[0]
        ystart = b[1]
        for j in range(num_rows):
            for i in range(num_columns):
                circles.append((xstart+i*hspace, ystart+j*vspace))
    return circles


#**********************
# draw_labeled_rectangle
#**********************

def draw_labeled_rectangle(myCanvas, scale, x, y, width, height, label, content):
    # main rectangle
    myCanvas.rect(x, y, width, height, stroke=1, fill=0)

    # calculate the label size
    
    #template = loader.get_template(os.path.join(BASE_DIR,"core","templates","core", "certif_header_text.html"))
    #header_text = template.render({"lang": lang})

    font_size = 8*scale
    label_width = myCanvas.stringWidth(label, "Helvetica", font_size)
    label_height = font_size - 2

    # blank rectangle to erase part of main rectangle
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(x+9*scale, y+height-label_height/2, label_width+6, label_height, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)

    #label_obj.drawOn(myCanvas,x+9*scale+3,y+height-label_height/2)
    myCanvas.setFont("Helvetica", font_size) 
    #myCanvas.drawString(x+9*scale+3, y+height-label_height/2, label)
    myCanvas.drawString(x+9*scale+3, y+height-label_height/2, label)
    
    if not content:
        return

    # calculate the content size
    font_size = 9*scale
    content_width = myCanvas.stringWidth(content, "Helvetica", font_size)
    label_height = font_size
    while content_width > width-10*scale: 
        font_size -= 0.2
        content_width = myCanvas.stringWidth(content, "Helvetica", font_size)
    #print("content_width",content_width)
    myCanvas.setFont("Helvetica", font_size) 
    myCanvas.drawString(x+8*scale, y+label_height, content)

#**********************
# draw_id_qrcode
#**********************

def draw_id_qrcode(myCanvas,scale,rightmargin,topmargin,id,obi):
    column_width = 27*scale
    width = column_width*7
    height = scale*185
    height2 = scale*25
    separator = 10*scale

    id = str(id)
    # rectangle area for id marks
    myCanvas.setLineWidth(3)
    #myCanvas.rect(rightmargin, topmargin-185-25-5, -column_width*7, scale*185, stroke=1, fill=0)
    myCanvas.rect(rightmargin-width, topmargin-height-height2-separator, width, height, stroke=1, fill=0)
    

    # area for id as number
    myCanvas.setLineWidth(1)
    #markbox_height = 710-518
    #myCanvas.rect(rightmargin, 710, -column_width*(numdigits+check), 25, stroke=1, fill=0)
    # myCanvas.rect(rightmargin, topmargin-25*scale, -column_width*7, 25*scale, stroke=1, fill=0)
    myCanvas.rect(rightmargin-width, topmargin-height2, width, height2, stroke=1, fill=0)

    # rectangle area for id marks
    qrw = QrCodeWidget(id, barLevel='H')
    qrsize=120*scale
    b = qrw.getBounds()
    w=b[2]-b[0]
    h=b[3]-b[1]
    d = Drawing(qrsize,qrsize,transform=[qrsize/w,0,0,qrsize/h,0,0])
    d.add(qrw)
    #renderPDF.draw(d,myCanvas,rightmargin-column_width*7+(column_width*7-w)/2,518+(185-h)/2)
    renderPDF.draw(d,myCanvas,rightmargin-30-120,topmargin-55-120)

    #myCanvas.setLineWidth(1)
    #myCanvas.rect(rightmargin, 710, -column_width*7, 25, stroke=1, fill=0)

    # print identification label text last
    myCanvas.setLineWidth(1) 
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)

    if obi:
        label = "Número de Inscrição"
        #myCanvas.rect(rightmargin-3, topmargin-5, -80, 10, stroke=0, fill=1)
        #myCanvas.setFillColorRGB(0,0,0)
        #myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Inscrição")
    else:
        label = _("Academic ID")
        #myCanvas.rect(rightmargin-3, topmargin-5, -92, 10, stroke=0, fill=1)
        #myCanvas.setFillColorRGB(0,0,0)
        #myCanvas.drawRightString(rightmargin-5, topmargin-2, "Academic ID")


    font_size = 8*scale
    label_width = myCanvas.stringWidth(label, "Helvetica", font_size)
    label_height = font_size - 2

    # blank rectangle to erase part of main rectangle
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(rightmargin-10*scale, topmargin-5*scale, -label_width-10*scale, label_height+2*scale, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)

    #label_obj.drawOn(myCanvas,x+9*scale+3,y+height-label_height/2)
    myCanvas.setFont("Helvetica", font_size) 
    #myCanvas.drawString(x+9*scale+3, y+height-label_height/2, label)
    myCanvas.drawString(rightmargin-label_width-15*scale, topmargin-label_height/2, label)

    myCanvas.setFillColorRGB(0,0,0)        
        
    numdigits = len(id)
    if numdigits <= 10:
        myCanvas.setFont("Courier", 12)
    elif numdigits <= 20:
        myCanvas.setFont("Courier", 10)
    elif numdigits <= 30:
        myCanvas.setFont("Courier", 9)
    else:
        myCanvas.setFont("Courier", 7.5)
    myCanvas.drawRightString(rightmargin-5, topmargin-15, id)
    myCanvas.setFillColorRGB(0.2,0.2,0.2)

def draw_id_marks(myCanvas,scale, rightmargin,topmargin,numdigits,check,id,obi):
    # Marks for identification number
    option_letters = ['A','B','C','D','E','F','G','H','I','J']
    option_numbers = ['0','1','2','3','4','5','6','7','8','9']
    
    if (sheet_type & ID_IS_QRCODE == 0) and numdigits <= MAX_NUMBER_OF_DIGITS:
        tmpwidth = numdigits+check
    else:
        tmpwidth = MAX_NUMBER_OF_DIGITS

    column_width = 27*scale
    width = column_width*tmpwidth
    height = scale*185
    #textRect = CGRect(x: x-width, y: y-height, width: width, height: height)


    height2 = 25*scale
    separator = 10.0*scale
    #textRect = CGRect(x: x-width, y: y-height-height2-separator, width: width, height: height2)

    # rectangle area for id marks
    myCanvas.setLineWidth(3)
    myCanvas.rect(rightmargin-width, topmargin-height-height2-separator, width, height, stroke=1, fill=0)

    # area for id as numbers
    myCanvas.setLineWidth(1)
    myCanvas.rect(rightmargin-width, topmargin-height2, width, height2, stroke=1, fill=0)

    
    # area for id as number
    myCanvas.setLineWidth(1)
    for i in range(1,numdigits+check):
        myCanvas.line(rightmargin-i*column_width, topmargin-height2, rightmargin-i*column_width, topmargin )
        myCanvas.line(rightmargin-i*column_width, topmargin-height-height2-separator, rightmargin-i*column_width, topmargin-height2-separator )

    #for i in range(1,numdigits+check):
    #    myCanvas.line(rightmargin-i*column_width, topmargin-185-25-5, rightmargin-i*column_width, topmargin-25 )
    #    myCanvas.line(rightmargin-i*column_width, topmargin-25-5, rightmargin-i*column_width, topmargin )

    # print id numerals
    myCanvas.setFont("Courier", 12*scale)
    if id!='':
        tmpstr="0%dd" % (numdigits)
        tmpstr="%"+tmpstr
        idstr=tmpstr % (int(id))
        #print >> sys.stderr, '****',idstr
        for i in range(0,numdigits):
            #myCanvas.drawString(rightmargin-column_width*(check+numdigits)+i*column_width+column_width/2-3, 719, idstr[i])
            myCanvas.drawString(rightmargin-column_width*(check+numdigits)+i*column_width+column_width/2-3, topmargin-16*scale, idstr[i])
        if check==1:
            if obi:
                chk = check_id_obi(id)
            else:
                chk = check_id(id)
            myCanvas.drawString(rightmargin-column_width/2-3, topmargin-16, chk)

    # print identification label text last
    myCanvas.setLineWidth(1) 
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)
    if obi:
        label = "Número de Inscrição"
        #myCanvas.rect(rightmargin-3, topmargin-5, -80, 10, stroke=0, fill=1)
        #myCanvas.setFillColorRGB(0,0,0)
        #myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Inscrição")
    else:
        #myCanvas.rect(rightmargin-3, topmargin-5, -92, 10, stroke=0, fill=1)
        #myCanvas.setFillColorRGB(0,0,0)
        #myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Identificação")
        label = _("Academic ID")

    font_size = 8*scale
    label_width = myCanvas.stringWidth(label, "Helvetica", font_size)
    label_height = font_size - 2

    # blank rectangle to erase part of main rectangle
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(rightmargin-10*scale, topmargin-5*scale, -label_width-10*scale, label_height+2*scale, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)

    #label_obj.drawOn(myCanvas,x+9*scale+3,y+height-label_height/2)
    myCanvas.setFont("Helvetica", font_size) 
    #myCanvas.drawString(x+9*scale+3, y+height-label_height/2, label)
    myCanvas.drawString(rightmargin-label_width-15*scale, topmargin-label_height/2, label)


    myCanvas.setFillColorRGB(0,0,0)

    for i in range(0,numdigits):
        if id!='':
            
            draw_option_list_ver(myCanvas, scale, rightmargin-(check+numdigits-i)*column_width+column_width/2, topmargin-height2-separator-15*scale, option_numbers,int(idstr[i]))
        else:
            draw_option_list_ver(myCanvas, scale, rightmargin-(check+numdigits-i)*column_width+column_width/2, topmargin-height2-separator-15*scale, option_numbers)

    if check==1:
        if id!='':
            if obi:
                chk = check_id_obi(id)
            else:
                chk = check_id(id)
            draw_option_list_ver(myCanvas, scale, rightmargin-column_width/2, topmargin-height2-separator-15*scale, option_letters, letter_to_num[chk])
        else:
            draw_option_list_ver(myCanvas, scale, rightmargin-column_width/2, topmargin-height2-separator-15*scale, option_letters)


#**********************
# draw_key_version
#**********************
    
def draw_key_version(myCanvas, scale, x, y):
    global BUILD_FILLED_TEST
    # main rectangle
    myCanvas.setLineWidth(3) 
    myCanvas.setStrokeColorRGB(0,0,0)
    myCanvas.setFillColorRGB(0,0,0)
    myCanvas.rect(x, y, 60*scale, 26*scale)
    #print("in draw_key_version",x,y)


    font_size = 10*scale
    content = "Key Version"
    label_width = myCanvas.stringWidth(content, "Helvetica", font_size)
    label_height = font_size
    myCanvas.setFont("Helvetica", font_size) 
    myCanvas.drawString(x+30*scale-label_width/2, y+26*scale+5*scale, content)

    x1 = x + 13*scale
    hspace = 17.0

    options = ["1", "2", "3"] # , "4", "5"]
    for j in range(0,3):
        filled = False
        if BUILD_FILLED_TEST and j == 2:
            filled = true
        draw_option_mark(myCanvas, scale=scale, x=x1+scale*j*hspace, y=page_height-y-13*scale,
                         label=options[j], filled=filled)

#**********************
# draw_marketing
#**********************

def draw_marketing(myCanvas, scale, x, y):
    logo_scale = 0.6
    logo_width = 130*scale*logo_scale
    logo_height = 28*scale*logo_scale
    logo = rpImage(os.path.join(BASE_DIR,'static','img','LogoWebScanGraderText.png'),logo_width,logo_height)
    logo.drawOn(myCanvas, x, y)
    
#**********************
# draw_option_mark
#**********************

def draw_option_mark(myCanvas, scale, x, y, label, filled):

    font_size = 7*scale
    label_height = font_size
    offsety = 1 if scale == 1 else 1.5
    label_width = myCanvas.stringWidth(label, "Helvetica", font_size)
    myCanvas.setLineWidth(0.5)
    myCanvas.setFont("Helvetica", font_size) 

    myCanvas.setStrokeColorRGB(0.5,0.5,0.5)
    myCanvas.setFillColorRGB(0.5,0.5,0.5)
    # for red
    #myCanvas.setStrokeColorRGB(1,0,0)
    #myCanvas.setFillColorRGB(1,0,0)
    myCanvas.drawString(x-label_width/2, page_height-y-label_height/2 + offsety, label)

    radius = 12*scale

    if filled:
        if BUILD_FILLED_TEST:
            val_rgb = randint(0,100) / 100
            myCanvas.setFillColorRGB(val_rgb,val_rgb,val_rgb)
        else:
            myCanvas.setFillColorRGB(0,0,0)

        myCanvas.setStrokeColorRGB(0,0,0)
        myCanvas.circle(x, page_height-y, radius/2, stroke=1, fill=1)
    else:
        myCanvas.circle(x, page_height-y, radius/2, stroke=1, fill=0)

            
def draw_option_mark_old(myCanvas,x,y,carac,fill):
    '''Draws the option mark circle'''
    DISP_LETTER = {'A':1.0, 'B':1.0, 'C':0.6, 'D':1.0, 'E':1.0, 'F':1.2, 'G':0.2, 'H':0.6, 'I':1.9, 'J':1.3}
    myCanvas.setLineWidth(0.6) 
    myCanvas.setFont("Helvetica", 6.5) 
    myCanvas.setFillColorRGB(0.2,0.2,0.2)
    if carac in string.digits:
        myCanvas.drawString(1.2+x-tradius/2, y+0.5-tradius/2, "%s" % carac)
    else:
        myCanvas.drawString(DISP_LETTER[carac]+x-tradius/2, y+0.5-tradius/2, "%s" % carac)
    if fill==0:
        myCanvas.setFillColorRGB(0.2,0.2,0.2)
        myCanvas.circle(x, y-0.3, tradius, stroke=1, fill=fill)
    else:
        #if randint(0,100)>70:
        #    r=1.0*randint(0,100)/100
        #    g=1.0*randint(0,100)/100
        #    b=1.0*randint(0,100)/100
        #    myCanvas.setFillColorRGB(r,g,b)
        #else:
        #    myCanvas.setFillColorRGB(0,0,0)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.circle(x, y-0.3, tradius, stroke=1, fill=fill)
        myCanvas.setFillColorRGB(0,0,0)

def draw_option_list_ver(myCanvas,scale,x,y,options,value=-1):

    vspace = 17.0*scale
    
    myCanvas.setFillColorRGB(0,0,0)
    for j in range(len(options)):
        if j==value:
            draw_option_mark(myCanvas, scale, x, page_height-y+vspace*j, options[j],1)
        else:
            draw_option_mark(myCanvas, scale, x, page_height-y+vspace*j, options[j],0)

#**********************
# draw_option_list_hor
#**********************

def draw_option_list_hor(myCanvas, scale, x, y, num_choices, i, options, answers):

    hspace = 17.0
    offsetx = 4 + 6   # radius is 6, move 4 further
    offsety = 1 if scale == 1 else 2
    
    # Draw label
    font_size = 9*scale
    label_height = font_size

    myCanvas.setFont("Helvetica", font_size)
    myCanvas.setFillColorRGB(0.5,0.5,0.5)
    #myCanvas.drawString(x+9*scale+3, y+height-label_height/2, label)
    label = f"{i+1}"
    label_width = myCanvas.stringWidth(label, "Helvetica", font_size)
    myCanvas.drawString(x-label_width-offsetx*scale, page_height-y-label_height/2+offsety, label)

    font_size = 6.5*scale
    myCanvas.setFont("Helvetica", font_size)
    
    # # prepare for drawing marks
    # #label_obj = Paragraph(f'<para alignment="center"><font name="helvetica" size="{6.5*scale}">{label}</font>', style)
    # #paragraphStyle.alignment = .center
    # #    attrs = [.font: UIFont(name: "Helvetica", size: 6.5*scale)!,
    # #             .paragraphStyle: paragraphStyle,
    # #             .foregroundColor: UIColor(red: 0.5, green: 0.5, blue: 0.5, alpha: 1.0)]

    # draw marks
    for j in range(num_choices):
        filled = options[j] == answers[i] 
        draw_option_mark(myCanvas, scale, x+scale*j*hspace, y, options[j], filled)

def check_id_obi(id):
    id=int(id)
    d1 = id % 10
    d2 = id % 100 // 10
    d3 = id % 1000 // 100
    d4 = id % 10000 // 1000
    d5 = id // 10000
    digit = (3 * d1 + 2 * d2 + 1 * d3 + 2 * d4 + 3 * d5) % 10
    if digit == 0:
        digit = 10
    return "%c" % chr(digit + 64)

def check_id(id):
    sum = 1
    tmp = int(id)
    while tmp > 0:
        sum += tmp % 10
        tmp //= 10
    digit = sum % 10
    return "%c" % chr(digit + 65)

def usage():
    print('usage: {} label1 label2 label3 numquestions num_digits id_check filename.pdf [data]'.format(sys.argv[0]), file=sys.stderr)
    sys.exit(-1)


def draw_page(myCanvas, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type_arg, id='', name='', obi=True, filled=False):

    global BUILD_FILLED_TEST
    sheet_type = sheet_type_arg
    if obi:
        sheet_type |= HAS_ID_CHECK
        
    if filled:
        BUILD_FILLED_TEST = True
    else:
        BUILD_FILLED_TEST = False

    #print("in draw_page",BUILD_FILLED_TEST)
    if BUILD_FILLED_TEST:
        if id == '':
            id = '12345'

    margin = 50
    marginleft = margin
    marginright = page_width - margin
    margintop = page_height - 1.1*margin
    marginbottom = margin
    #offset = (page_width-500)/2
    rightmargin = marginright

    scale = 1.4 if sheet_type & IS_HALF_PAGE else 1.0
    
    #myCanvas.rect(marginleft, marginbottom, marginright-margin, margintop-margin, stroke=1, fill=0)
    
    if obi:
        logo = rpImage(os.path.join(BASE_DIR,'sisca','attic','logo-obi-black.png'),45,45)
        logo.drawOn(myCanvas,marginleft,margintop-40)
        myCanvas.setFont("Helvetica-Bold", 9) 
        myCanvas.drawString(marginleft+5, margintop-50,  f"OBI{YEAR}")
       
    ####################
    # qr code bottom
    ####################

    qrcode_data = f"{sheet_type} {numquestions} {numalternatives} {numdigits}"
        
    qrw = QrCodeWidget(qrcode_data, barLevel='H')
    qrsize=82.0*scale
    b = qrw.getBounds()
    w=b[2]-b[0]
    h=b[3]-b[1]
    d = Drawing(qrsize,qrsize,transform=[qrsize/w,0,0,qrsize/h,0,0])
    d.add(qrw)
    # there is an offset, compensate it
    renderPDF.draw(d,myCanvas,marginleft-12*scale,marginbottom-16*scale)
    # let imageRect = CGRect(x: marginleft-4*scale, y: marginbottom-60*scale+4*scale,
    #                           width: 65*scale, height: 65*scale) // small white margin on qrcode


    myCanvas.setLineWidth(1) 


    ####################
    # Top of page
    x = marginleft+50
    y=margintop-8

    ####################
    # Exam labels
    myCanvas.setFillColorRGB(0,0,0)

    if obi:
        myCanvas.setFont("Helvetica-Bold", 12)
        limited_label = label1[:35]
    else:
        myCanvas.setFont("Helvetica-Bold", 15)
        limited_label = label1[:30]
    myCanvas.drawString(x, y,  limited_label)
    myCanvas.setFont("Helvetica", 13) 
    y-=18
    limited_label = label2[:40]
    myCanvas.drawString(x, y,  limited_label)
    myCanvas.setFont("Helvetica", 11) 
    y-=15
    limited_label = label3[:45]
    myCanvas.drawString(x, y, limited_label)

    y-=15
    if not obi:
        limited_label = label4[:45]
        myCanvas.drawString(x, y, limited_label)

    y-=20
    x = marginleft

    ####################
    # Instructions
    myCanvas.setFont("Helvetica-Bold", 10) 
    #myCanvas.drawString(x,y, _("Instructions")) 
    myCanvas.drawString(x,y, _("Instruções")) 
    y -= 14
    myCanvas.setFont("Helvetica", 10) 
    #myCanvas.drawString(x,y, _("1. Use a black pencil or a dark ink pen."))
    myCanvas.drawString(x,y, _("1. Use lápis preto ou caneta com tinta escura."))
    y -= 12
    #myCanvas.drawString(x,y, _("2. Fill the bubbles completely."))
    myCanvas.drawString(x,y, _("2. Preencha as bolhas por inteiro."))
    y -= 12
    #myCanvas.drawString(x,y, _("3. Fill only one letter per question."))
    myCanvas.drawString(x,y, _("3. Preencha apenas uma letra por questão."))
    y -= 12
    #myCanvas.drawString(x,y, _("4. Erase marks thoroughly to make changes."))
    myCanvas.drawString(x,y, _("4. Apague completamente as marcas para fazer alterações."))
    y -= 12
    #myCanvas.drawString(x,y, _("5. Do not fold or crumple this sheet."))
    myCanvas.drawString(x,y, _("5. Não rasure, dobre ou amasse esta folha."))

    ####################
    # Examples
    y -= 24

    text = _("Preenchimento correto:")
    myCanvas.drawString(x,y,text) 
    text_width = stringWidth(text, 'Helvetica', 10)

    radius = 12*scale
    #x += text_width+12
    myCanvas.circle(x+text_width+12, y+radius/4, radius/2, stroke=1, fill=1)
    #x += 25
    y -= 15
    
    text = _("Preenchimentos incorretos:")
    myCanvas.drawString(x,y,text) 
    text_width = stringWidth(text, 'Helvetica', 10)
    x += text_width+12
    
    myCanvas.setStrokeColorRGB(0.5,0.5,0.5)
    myCanvas.setLineWidth(1)
    myCanvas.circle(x, y+radius/4, radius/2, stroke=1, fill=0)
    myCanvas.setStrokeColorRGB(0,0,0)
    myCanvas.setLineWidth(2)
    myCanvas.line(x-5*scale, y-radius/2+radius/4, x+6*scale, y+radius/2+radius/4)
    myCanvas.line(x-6*scale, y+radius/2+radius/4, x+6*scale, y-radius/2+radius/3)

    x += 2*radius
    myCanvas.setStrokeColorRGB(0.5,0.5,0.5)
    myCanvas.setLineWidth(1)
    myCanvas.circle(x, y+radius/4, radius/2, stroke=1, fill=0)
    myCanvas.setStrokeColorRGB(0,0,0)
    myCanvas.setLineWidth(2)
    myCanvas.line(x-radius/2+2*scale, y+radius/3, x, y-radius/4+2*scale)
    myCanvas.line(x, y-radius/4+2*scale, x+radius/5+3*scale, y+radius/2+3*scale)
    myCanvas.setLineWidth(1)


    
    ###################
    # code128 and marketing
    #y-=10
    myCanvas.setFont("Helvetica", 6.5) 
    y-=32
    #barcode_code128 = code128.Code128('%d;%d;%c;%d' % (numquestions,numdigits,chk,numalternatives), barWidth = 1.3)
    #barcode_code128.drawOn(myCanvas,x-18,y)
    #myCanvas.drawString(x, y, "SISCA - Sistema de Correção Automatizada - Instituto de Computação/UNICAMP")
    #myCanvas.drawString(x+190, y+18, "Sistema de Correção Automatizada")
    #myCanvas.drawString(x+190, y+9, "Instituto de Computação/UNICAMP")
    #myCanvas.drawString(x+190, y+9, "Sistema de Correção Automatizada")
    #myCanvas.drawString(x+190, y, "https://olimpiada.ic.unicamp.br/sisca")
    
    # as footer
    #myCanvas.setFont("Helvetica", 8)
    #myCanvas.drawCentredString(width/2, marginbottom, "SISCA - Sistema de Correção Automatizada - IC/UNICAMP")

    
    ####################
    # draw labeled rectangles for Name, signature and date
    ####################
    myCanvas.setFont("Helvetica", 9)

    dateWidth = 120 if scale == 1 else 100
    bottom = marginbottom - 5
    nameWidth = marginright-marginleft-65*scale
    #label = _("Date")
    label = _("Data")
    draw_labeled_rectangle(myCanvas, scale=scale, x=marginleft+67*scale, y=bottom, width=dateWidth, height=24*scale, label=label, content="")
    #label = _("Signature")
    label = _("Assinatura")
    draw_labeled_rectangle(myCanvas, scale=scale, x=marginleft+67*scale+dateWidth+4*scale, y=bottom, width=nameWidth - dateWidth - 4*scale, height=24*scale, label=label, content="")
    #label = _("Name")
    label = _("Nome")
    draw_labeled_rectangle(myCanvas, scale=scale, x=marginleft+67*scale, y=bottom+24*scale + 8*scale, width=nameWidth, height=24*scale, label=label, content=name)    

    ####################
    # ID

    check = 1 if sheet_type & HAS_ID_CHECK else 0
    is_alpha = sheet_type & ID_IS_QRCODE != 0

    if is_alpha:
        if numdigits <= 40:
            draw_id_qrcode(myCanvas,scale,rightmargin,margintop,id,obi)
        else:
            error('too many digits')
    elif (numdigits+check) <= MAX_NUMBER_OF_DIGITS:
        draw_id_marks(myCanvas,scale,marginright,margintop,numdigits,check,id,obi)
    else:
        error("too many digits")

    ##################
    # draw key version

    ytmp = page_height-275 if scale == 1 else page_height-427  #-26-13
    if sheet_type & HAS_KEY_VERSION != 0:
        draw_key_version(myCanvas, scale=scale, x=260, y=ytmp)

    ##################
    # draw logo scangrader

    has_customer_logo = False
    if not has_customer_logo:
        draw_marketing(myCanvas, scale, marginleft, ytmp)
    else:
        # draw customer logo
        pass
    #####################
    # draw answer area


    # drawContext.setLineWidth(2)
    # let htmp: CGFloat = (scale == 1) ? 445 : 270
    # ytmp = (scale == 1) ? 730-htmp : 705-htmp
    # let answerRect = CGRect(x: marginleft, y: ytmp,
    #                         width: 499, height: htmp)
    

    # myCanvas.setLineWidth(2)
    # bottom = marginbottom+65
    # myCanvas.rect(marginleft, bottom, width-2*margin, 445, stroke=1, fill=0)
    # myCanvas.setLineWidth(1)

    bottom = marginbottom+65

    # let htmp: CGFloat = (scale == 1) ? 445 : 27# 0
    # ytmp = (scale == 1) ? 730-htmp : 705-htmp
    # let answerRect = CGRect(x: marginleft, y: ytmp,
    #                         width: 499, height: htmp)
        


    
    myCanvas.setLineWidth(3)
    myCanvas.setFillColorRGB(0,0,0)
    myCanvas.setStrokeColorRGB(0,0,0)
    htmp = 445 if scale == 1 else 270
    ytmp = page_height - (730) if scale == 1 else page_height - (705)
    myCanvas.rect(marginleft, ytmp, 499, htmp, stroke=1, fill=0)


    myCanvas.setLineWidth(1)

    option_letters = ["A", "B", "C"]
    if numalternatives >= 4:
        option_letters.append("D")
    if numalternatives == 5:
        option_letters.append("E")
    
    answers = []
    if BUILD_FILLED_TEST:
        j = 0
        for ii in range(100):
            j = randint(0,numalternatives-1)
            answers.append(option_letters[j])
            # j += 1
            # if j == numalternatives:
            #     j = 0
    else:
        for ii in range(100):
            answers.append("X")

    # Calculate the position of answer circles
    circle_top = 285 if scale == 1 else 435
    
    circles = compute_answer_circles(num_questions=numquestions, left=50, top=circle_top, scale=scale)
    #for c in circles:
    #    print("circle", c[0], c[1])

    if (scale == 1.0):
        if (numquestions<=5):
            for i in range(1,numquestions+1):
                draw_option_list_hor(myCanvas,scale=scale, x=circles[(35+i-1)*5][0], y=circles[(35+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)


        elif (numquestions<=9):
            for i in range(1,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(33+i-1)*5][0], y=circles[(33+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions==10):
            for i in range(1,6):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(35+i-1)*5][0], y=circles[(35+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(6,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(60+i-6)*5][0], y=circles[(60+i-6)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
        elif (numquestions<=15):
            for i in range(1,6):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(10+i-1)*5][0], y=circles[(10+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(6,11):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(35+i-6)*5][0], y=circles[(35+i-6)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(60+i-11)*5][0], y=circles[(60+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=20):
            for i in range(1,11):
                    draw_option_list_hor(myCanvas, scale=scale, x=circles[(33+i-1)*5][0], y=circles[(33+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(58+i-11)*5][0], y=circles[(58+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=30):
            for i in range(1,11):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(8+i-1)*5][0], y=circles[(8+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,21):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(33+i-11)*5][0], y=circles[(33+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(21,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(58+i-21)*5][0], y=circles[(58+i-21)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)

        elif (numquestions<=40):
            for i in range(1,21):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(27+i-1)*5][0], y=circles[(27+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(21,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(52+i-21)*5][0], y=circles[(52+i-21)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=50):
            for i in range(1,26):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(25+i-1)*5][0], y=circles[(25+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(26,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(50+i-26)*5][0], y=circles[(50+i-26)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=60):
            for i in range(1,21):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(2+i-1)*5][0], y=circles[(2+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(21,41):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(27+i-21)*5][0], y=circles[(27+i-21)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(41,numquestions+1):
                    draw_option_list_hor(myCanvas, scale=scale, x=circles[(52+i-41)*5][0], y=circles[(52+i-41)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=75):
            for i in range(1,26):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(0+i-1)*5][0], y=circles[(0+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(26,51):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(25+i-26)*5][0], y=circles[(25+i-26)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(51,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(50+i-51)*5][0], y=circles[(50+i-51)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=80):
            for i in range(1,21):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(2+i-1)*5][0], y=circles[(2+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(21,41):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(27+i-21)*5][0], y=circles[(27+i-21)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(41,61):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(52+i-41)*5][0], y=circles[(52+i-41)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(61,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(77+i-61)*5][0], y=circles[(77+i-61)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=100):
            for i in range(1,26):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(0+i-1)*5][0], y=circles[(0+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(26,51):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(25+i-26)*5][0], y=circles[(25+i-26)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(51,76):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(50+i-51)*5][0], y=circles[(50+i-51)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(76,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(75+i-76)*5][0], y=circles[(75+i-76)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
        else:
            print("error in number of questions!")
    else:
        #print('scale',scale)
        if (numquestions<=5):
            for i in range(1,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(17-(numquestions)+i-1)*5][0], y=circles[(17-(numquestions)+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
                
        elif (numquestions<=9):
            for i in range(1,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(19-(numquestions)+i-1)*5][0], y=circles[(19-(numquestions)+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
                
        elif (numquestions<=10):
            for i in range(1,5):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(2+i-1)*5][0], y=circles[(2+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
                for i in range(6,numquestions+1):
                    draw_option_list_hor(myCanvas, scale=scale, x=circles[(12+i-6)*5][0], y=circles[(12+i-6)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
                    
        elif (numquestions<=15):
            for i in range(1,6):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(2+i-1)*5][0], y=circles[(2+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(6,11):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(12+i-6)*5][0], y=circles[(12+i-6)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(22+i-11)*5][0], y=circles[(22+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=20):
            for i in range(1,11):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(0+i-1)*5][0], y=circles[(0+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(10+i-11)*5][0], y=circles[(10+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            
        elif (numquestions<=30):
            for i in range(1,11):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(0+i-1)*5][0], y=circles[(0+i-1)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(11,21):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(10+i-11)*5][0], y=circles[(10+i-11)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)
            for i in range(21,numquestions+1):
                draw_option_list_hor(myCanvas, scale=scale, x=circles[(20+i-21)*5][0], y=circles[(20+i-21)*5][1], num_choices=numalternatives, i=i-1, options=option_letters, answers=answers)


    #     //printGrid(myCanvas, pageRect=pageRect)
        
    # 

    myCanvas.showPage()

def draw_pages(myCanvas, data, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type, obi=True, filled=False):
    count = 0
    for id,name in data:
        draw_page(myCanvas, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type, id=id, name=name, obi=obi, filled=filled)
        count += 1
    return count

def clean_name(s):
    '''if cannot find encoding, strip non-ascii characters '''
    new=''
    for c in s:
        if c in string.ascii_letters+' ':
            new+=c
    return new

if __name__=="__main__":
    # pagesize = (597.6, 842.4) # use same as IOS
    # mCanvas = canvas.Canvas('test.pdf', pagesize=pagesize)
    # numquestions = int(sys.argv[1])
    # id = int(sys.argv[2])
    # numalternatives = 5
    # name = '0123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789 123456789'
    # name = '0123456789 123456789 123456789 123456789 123456789 123456789'
    # scale = 1.0
    # page = draw_page(mCanvas,scale,'Olimpíada Brasileira de Informática','Prova de Matemática', 'MM110 - Prof. Luiz Antônio', 'Turma A', numquestions=numquestions, numalternatives=5, numdigits=len(str(id)), idcheck=False, id=id, name=name, obi=False)
    # mCanvas.save() 
    # sys.exit(0)
    try:
        label1 = sys.argv[1]
        label2 = sys.argv[2]
        label3 = sys.argv[3]
        label4 = sys.argv[4]
        numquestions = int(sys.argv[5])
        numalternatives = int(sys.argv[6])
        numdigits = int(sys.argv[7])
        sheet_type = int(sys.argv[8])
        output_file = sys.argv[9]
    except:
        usage()
    try:
        input_file = sys.argv[10]
    except:
        input_file = None
    id,name = '',''

    pagesize = (597.6, 842.4) # use same as IOS
    mCanvas = canvas.Canvas(output_file, pagesize=pagesize)

    if not input_file:
        draw_page(mCanvas, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type, id, name, obi=False)
    else:
        data = []
        try:
            ifile=open(input_file,"rU")
            reader=csv.reader(ifile)
            for r in reader:
                if len(r)==0:
                    continue
                if r[0].strip().lower()=='ra' or r[1].strip().lower()=='nome':
                    continue
                try:
                    ra=r[0].strip()
                    name=r[1].strip()
                except:
                    ra=0
                    name="DADOS INCOMPLETOS"
                data.append((ra,name))
        except:
            try:
                ifile=open(input_file,"rU",encoding='iso-8859-1')
                reader=csv.reader(ifile)
                for r in reader:
                    if len(r)==0:
                        continue
                    if r[0].strip().lower()=='ra' or r[1].strip().lower()=='nome':
                        continue
                    try:
                        ra=r[0].strip()
                        name=r[1].strip()
                    except:
                        ra=0
                        name="DADOS INCOMPLETOS"
                    data.append((ra,name))
            except:
                ra=0
                name="ERRO AO LER O NOME"
                data.append((ra,name))

        draw_pages(mCanvas, data, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type, obi=False)
    mCanvas.save() 
