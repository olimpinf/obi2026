#!/usr/local/bin/python3

import csv
import os
import os.path
import string
import sys
import tempfile

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

#from projectobi.settings import BASE_DIR
# to execute outside django, only in case of obi (to insert logo)
# uncomment line below
BASE_DIR = '/Users/ranido/Documents/SBC/OBI/django.nosync/obi'

# constants for the layout
tradius = 6
vspace = 17
hspace = 17
width, height = A4

# utility constants
letter_to_num={'A':0,'B':1,'C':2,'D':3,'E':4,'F':5,'G':6,'H':7,'I':8,'J':9}
num_to_letter={0:'A', 1:'B',2:'C',3:'D',4:'E',5:'F',6:'G',7:'H',8:'I',9:'J'}

def error(s):
    print(s, file=sys.stderr)
    sys.exit(-1)

def draw_id_qrcode(myCanvas,rightmargin,topmargin,id,obi):
    column_width = 27
    id = str(id)
    # rectangle area for id marks
    myCanvas.setLineWidth(2)
    myCanvas.rect(rightmargin, topmargin-185-25-5, -column_width*7, 185, stroke=1, fill=0)

    # area for id as number
    myCanvas.setLineWidth(1)
    myCanvas.rect(rightmargin, topmargin-25, -column_width*7, 25, stroke=1, fill=0)

    # rectangle area for id marks
    qrw = QrCodeWidget(id)
    qrsize=120
    b = qrw.getBounds()
    w=b[2]-b[0]
    h=b[3]-b[1]
    d = Drawing(qrsize,qrsize,transform=[qrsize/w,0,0,qrsize/h,0,0])
    d.add(qrw)
    renderPDF.draw(d,myCanvas,rightmargin-30-120,topmargin-55-120)

    # print identification label text last
    myCanvas.setLineWidth(1) 
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)
    if obi:
        myCanvas.rect(rightmargin-3, topmargin-5, -80, 10, stroke=0, fill=1)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Inscrição")
    else:
        myCanvas.rect(rightmargin-3, topmargin-5, -92, 10, stroke=0, fill=1)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Identificação")

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

def draw_id_marks(myCanvas,rightmargin,topmargin,numdigits,check,id,obi):
    # Marks for identification number
    option_letters = ['A','B','C','D','E','F','G','H','I','J']
    option_numbers = ['0','1','2','3','4','5','6','7','8','9']

    column_width = 27

    # rectangle area for id marks
    myCanvas.setLineWidth(2)
    myCanvas.rect(rightmargin, topmargin-185-25-8, -column_width*(numdigits+check), 185, stroke=1, fill=0)

    # area for id as number
    myCanvas.setLineWidth(1)
    myCanvas.rect(rightmargin, topmargin-25, -column_width*(numdigits+check), 25, stroke=1, fill=0)

    for i in range(1,numdigits+check):
        myCanvas.line(rightmargin-i*column_width, topmargin-25, rightmargin-i*column_width, topmargin )
        myCanvas.line(rightmargin-i*column_width, topmargin-25-185-8, rightmargin-i*column_width, topmargin-25-8 )

    # print id numerals
    myCanvas.setFont("Courier", 12)
    if id!='':
        tmpstr="0%dd" % (numdigits)
        tmpstr="%"+tmpstr
        idstr=tmpstr % (int(id))
        for i in range(0,numdigits):
            myCanvas.drawString(rightmargin-column_width*(check+numdigits)+i*column_width+column_width/2-3, topmargin-16, idstr[i])
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
        myCanvas.rect(rightmargin-3, topmargin-5, -80, 10, stroke=0, fill=1)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Inscrição")
    else:
        myCanvas.rect(rightmargin-3, topmargin-5, -92, 10, stroke=0, fill=1)
        myCanvas.setFillColorRGB(0,0,0)
        myCanvas.drawRightString(rightmargin-5, topmargin-2, "Número de Identificação")


    myCanvas.setFillColorRGB(0.2,0.2,0.2)

    for i in range(0,numdigits):
        if id!='':
            draw_option_list_ver(myCanvas, rightmargin-column_width*(check+numdigits)+i*column_width+column_width/2, topmargin-25-20, option_numbers,int(idstr[i]))
        else:
            draw_option_list_ver(myCanvas, rightmargin-column_width*(check+numdigits)+i*column_width+column_width/2, topmargin-25-20, option_numbers)

    if check==1:
        if id!='':
            if obi:
                chk = check_id_obi(id)
            else:
                chk = check_id(id)
            draw_option_list_ver(myCanvas, rightmargin-column_width/2, topmargin-25-20, option_letters, letter_to_num[chk])
        else:
            draw_option_list_ver(myCanvas, rightmargin-column_width/2, topmargin-25-20, option_letters)

def draw_option_mark(myCanvas,x,y,carac,fill):
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
        # to test errors, faded marks
        #from random import randint
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

def draw_option_list_ver(myCanvas, x,y,options,value=-1):
    myCanvas.setFont("Helvetica", 10) 
    myCanvas.setFillColorRGB(0,0,0)
    for j in range(len(options)):
        if j==value:
            draw_option_mark(myCanvas, x, y-vspace*j, options[j],1)
        else:
            draw_option_mark(myCanvas, x, y-vspace*j, options[j],0)

def draw_option_list_hor(myCanvas, x,y,i,n,options):
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(0,0,0)
    if n >= 100:
        myCanvas.drawString(x-4.2*tradius, y-3-vspace*i, "%02d" % n)
    else:
        myCanvas.drawString(x-3.5*tradius, y-3-vspace*i, "%02d" % n)
    myCanvas.setFont("Helvetica", 8) 
    # to test errors
    #from random import randint
    #if randint(0,100)>90:
    #    chosen = [] # error, blank
    #else:
    #    chosen = [randint(0,4)]
    #if randint(0,100)>90:
    #    chosen.append(randint(0,4)) # error, more than one chosen
    #if randint(0,100)>95:
    #    chosen.append(randint(0,4)) # error, more than one chosen
    for j in range(len(options)):
        #if j in chosen:
        #    draw_option_mark(myCanvas, x+j*hspace, y-vspace*i, options[j],1)
        #else:
            draw_option_mark(myCanvas, x+j*hspace, y-vspace*i, options[j],0)
            
def draw_name_rect(myCanvas, x1,y1,w,h,txt):
    myCanvas.rect(x1, y1, w, h, stroke=1, fill=0)
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(x1+4, y1+h-6, 28, 10, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)
    myCanvas.drawString(x1+8, y1+h-2, "Nome")
    if txt != "":
        myCanvas.setFont("Courier", 10) 
        myCanvas.drawString(x1+5, y1+h-15, txt[:69])

def draw_signature_rect(myCanvas, x1,y1,w,h):
    myCanvas.rect(x1, y1, w, h, stroke=1, fill=0)
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(x1+4, y1+h-6, 45, 10, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)
    myCanvas.drawString(x1+8, y1+h-2, "Assinatura")

def draw_date_rect(myCanvas, x1,y1,w,h,txt):
    myCanvas.rect(x1, y1, w, h, stroke=1, fill=0)
    myCanvas.setFont("Helvetica", 8) 
    myCanvas.setFillColorRGB(1,1,1)
    myCanvas.rect(x1+4, y1+h-6, 24, 10, stroke=0, fill=1)
    myCanvas.setFillColorRGB(0,0,0)
    myCanvas.drawString(x1+8, y1+h-2, "Data")
    if txt != "":
        myCanvas.setFont("Courier", 10) 
        myCanvas.drawString(x1+5, y1+h-18, txt[:42])

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

def draw_page(myCanvas, label1, label2, label3, label4, numquestions, numdigits, idcheck, numalternatives=5, id='', name='', obi=False, proprietary=True, exam_type=0, exam_texts=None):

    # exam_type is:
    #  0: multiple alternatives
    #  else: blank space
    #     space divided in regions)
    #     text = exam_text[0], exam_text[1], etc
    #     type 1: one writing space
    #     type 2: two writing spaces
    #     type 3: three writing spaces
    # myCanvas.rect(0, 0, 595, 842, stroke=1, fill=0)
    # size is 595x842 

    margin = 50
    marginleft = margin
    marginright = width - margin
    margintop = height - 1.1*margin
    marginbottom = margin
    offset = (width-500)/2
    #rightmargin = width-offset
    rightmargin = marginright

    #myCanvas.rect(marginleft, marginbottom, marginright-margin, margintop-margin, stroke=1, fill=0)
    
    if obi:
        #logo = rpImage(os.path.join(settings.BASE_DIR,'sisca','attic','logo-obi-black.png'),45,45)
        logo = rpImage(os.path.join(BASE_DIR,'sisca','attic','logo-obi-black.png'),45,45)
        logo.drawOn(myCanvas,marginleft,margintop-40)
    elif proprietary:
        logo = rpImage(os.path.join(BASE_DIR,'sisca','attic','logo-univesp-black.png'),549/3,200/3)
        logo.drawOn(myCanvas,marginleft,margintop-62)

    ####################
    # qr code bottom
    if idcheck:
        chk = 'Y'
    else:
        chk = 'N'
    qrw = QrCodeWidget('%d;%d;%c;%d' % (numquestions,numdigits,chk,numalternatives))
    qrsize=82.0
    b = qrw.getBounds()
    w=b[2]-b[0]
    h=b[3]-b[1]
    d = Drawing(qrsize,qrsize,transform=[qrsize/w,0,0,qrsize/h,0,0])
    d.add(qrw)
    # there is an offset, compensate it
    renderPDF.draw(d,myCanvas,marginleft-13,marginbottom-13)
    myCanvas.setLineWidth(1) 


    ####################
    # Exam description
    myCanvas.setFillColorRGB(0,0,0)
    # if below, y=685
    if obi:
        myCanvas.setFont("Helvetica-Bold", 9) 
        myCanvas.drawString(marginleft+5, margintop-48, "OBI2018")
        x = marginleft + 50
        y=margintop-8
    elif proprietary:
        y=margintop-88
        x = marginleft
    else:
        x = marginleft
    
    myCanvas.setFont("Helvetica-Bold", 14) 
    myCanvas.drawString(x, y,  label1)
    myCanvas.setFont("Helvetica", 13) 
    y-=18
    myCanvas.drawString(x, y,  label2)
    myCanvas.setFont("Helvetica", 11) 
    y-=15
    myCanvas.drawString(x, y,  label3)

    y-=15
    myCanvas.drawString(x, y,  label4)

    y-=20
    x = marginleft
    ####################
    # Instructions
    if not proprietary:
        myCanvas.setFont("Helvetica-Bold", 10) 
        myCanvas.drawString(x,y, "Instruções") 
        y -= 14
        myCanvas.setFont("Helvetica", 10) 
        myCanvas.drawString(x,y, "1. Verifique se o código QR no rodapé, à esquerda,  está visível.")
        y -= 12
        myCanvas.drawString(x,y, "    Ele é importante para a correção automatizada.")
        y -= 12
        myCanvas.drawString(x,y, "2. Marque as respostas com caneta de tinta preta ou azul escuro.")
        y -= 12
        myCanvas.drawString(x,y, "3. Preencha completamente a marca correspondente à resposta,")
        y -= 12
        myCanvas.drawString(x,y, "    conforme o modelo: ")
        myCanvas.circle(x+110, y+(tradius/2), tradius-1,  stroke=1, fill=1)
        y -= 12
        myCanvas.drawString(x,y, "4. Marque apenas uma resposta por questão. Mais de uma")
        y -= 12
        myCanvas.drawString(x,y, "    marcação anula a questão.")
        y -= 12
        myCanvas.drawString(x,y, "5. Não amasse, rasgue ou rasure esta Folha de Respostas.")
        y -= 12
        myCanvas.drawString(x,y, "6. Não faça marcas ou escreva fora dos lugares indicados.")

    ###################
    # code128 and marketing

    if not proprietary:
        y-=32
        myCanvas.setFont("Helvetica", 6.5) 
        myCanvas.drawString(x+190, y+9, "Sistema de Correção Automatizada")
        myCanvas.drawString(x+190, y, "https://olimpiada.ic.unicamp.br/sisca")
        barcode_code128 = code128.Code128('%d;%d;%c;%d' % (numquestions,numdigits,chk,numalternatives), barWidth = 1.3)
    else:
        y-=62
        barcode_code128 = code128.Code128('%d;%d;%c;%d' % (numquestions,numdigits,chk,numalternatives), barWidth = 1.3)
    barcode_code128.drawOn(myCanvas,x-18,y)


    ###################
    # name
    myCanvas.setFont("Helvetica", 9) 
    draw_name_rect(myCanvas,marginleft+70,marginbottom+32,marginright-marginleft-70,24,name)
    draw_date_rect(myCanvas,marginleft+70,marginbottom,marginleft+70,24,'')
    draw_signature_rect(myCanvas,marginleft+200,marginbottom,marginright-marginleft-200,24)

    ####################
    # ID
    if idcheck:
        check=1
    else:
        check=0
    MAXDIGITS = 7
    # test for univesp only
    MAXDIGITS = 10
    if (numdigits+check) <= MAXDIGITS:
        draw_id_marks(myCanvas,marginright,margintop,numdigits,check,id,obi)
    elif numdigits <= 40:
        draw_id_qrcode(myCanvas,rightmargin,margintop,id,obi)
    else:
        error("too many digits")

    ####################
    # Marks for answers

    myCanvas.setLineWidth(2)
    myCanvas.setFont("Helvetica", 10) 
    bottom = marginbottom+65
    if exam_type==0:
        myCanvas.rect(marginleft, bottom, width-2*margin, 445, stroke=1, fill=0)
    elif exam_type==1:
        myCanvas.rect(marginleft, bottom, width-2*margin, 445, stroke=1, fill=0)
        myCanvas.drawString(marginleft+8, bottom+445-15, exam_text[0])
    elif exam_type==2:
        myCanvas.rect(marginleft, bottom, width-2*margin, (445/2-5), stroke=1, fill=0)
        myCanvas.rect(marginleft, bottom+445/2+3, width-2*margin, (445/2-5), stroke=1, fill=0)
    elif exam_type==3:
        myCanvas.rect(marginleft, bottom, width-2*margin, (445/3-5), stroke=1, fill=0)
        myCanvas.rect(marginleft, bottom+445/3+3, width-2*margin, (445/3-5), stroke=1, fill=0)
        myCanvas.rect(marginleft, bottom+2*(445/3+3), width-2*margin, (445/3-5), stroke=1, fill=0)
    else:
        print("error drawing answer rectangles", file=sys.stderr)
        usage()

    if exam_type==0:
        myCanvas.rect(marginleft, bottom, width-2*margin, 445, stroke=1, fill=0)
        myCanvas.setLineWidth(1)
        if numalternatives == 4:
            option_letters = ['A', 'B', 'C', 'D']
        else:
            option_letters = ['A', 'B', 'C', 'D', 'E']
        if numquestions==5:
            for i in range(1,6):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+270, i-1, i, option_letters)
        elif numquestions==10:
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+300, i-1, i, option_letters)
        elif numquestions==15:
            for i in range(1,16):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+340, i-1, i, option_letters)
        elif numquestions==20:
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+150, bottom+300, i-1, i, option_letters)
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+280, bottom+300, i-1, i+10, option_letters)
        elif numquestions==25:
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+425, i-1, i, option_letters)
        elif numquestions==30:
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+80, bottom+300, i-1, i, option_letters)
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+300, i-1, i+10, option_letters)
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+360, bottom+300, i-1, i+20, option_letters)
        elif numquestions==40:
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+150, bottom+385, i-1, i, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+290, bottom+385, i-1, i+20, option_letters)
        elif numquestions==50:
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+150, bottom+425, i-1, i, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+290, bottom+425, i-1, i+25, option_letters)
        elif numquestions==60:
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+80, bottom+385, i-1, i, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+220, bottom+385, i-1, i+20, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+360, bottom+385, i-1, i+40, option_letters)
        elif numquestions==70:
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+40, bottom+385, i-1, i, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+160, bottom+385, i-1, i+20, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+280, bottom+385, i-1, i+40, option_letters)
            for i in range(1,11):
                draw_option_list_hor(myCanvas, marginleft+400, bottom+385, i-1, i+60, option_letters)
        elif numquestions==80:
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+40, bottom+385, i-1, i, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+160, bottom+385, i-1, i+20, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+280, bottom+385, i-1, i+40, option_letters)
            for i in range(1,21):
                draw_option_list_hor(myCanvas, marginleft+400, bottom+385, i-1, i+60, option_letters)
        elif numquestions==90:
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+40, bottom+425, i-1, i, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+160, bottom+425, i-1, i+25, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+280, bottom+425, i-1, i+50, option_letters)
            for i in range(1,16):
                draw_option_list_hor(myCanvas, marginleft+400, bottom+425, i-1, i+75, option_letters)
        elif numquestions==100:
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+40, bottom+425, i-1, i, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+160, bottom+425, i-1, i+25, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+280, bottom+425, i-1, i+50, option_letters)
            for i in range(1,26):
                draw_option_list_hor(myCanvas, marginleft+400, bottom+425, i-1, i+75, option_letters)
        else:
            print("error drawing answer marks", file=sys.stderr)
            usage()

    myCanvas.showPage()

def draw_pages(mCanvas, data, label1, label2, label3, label4, numquestions, numdigits, idcheck, obi=False, proprietary=False):
    count = 0
    for id,name in data:
        draw_page(mCanvas,label1, label2, label3, label4, numquestions, numdigits, idcheck, id, name, obi, proprietary)
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
    # to test generating a page
    # command line interface uses only numquestions and id 
    mCanvas = canvas.Canvas('test.pdf', pagesize=A4)
    try:
        numquestions = int(sys.argv[1])
        id = sys.argv[2]
    except:
        print('usage: {} numquestions id'.format(sys.argv[0]),file=sys.stderr)
        sys.exit(1)
    numalternatives = 5 
    numdigits = len(id)
    name = '0123456789 123456789 123456789 123456789 123456789 123456789 123456789'
    exam_type = 3
    exam_text = ['1. Explique porque o espaço abaixo está vazio.']
    page = draw_page(mCanvas,'Rótulo 1','Rótulo 2', 'Rótulo 3', 'Rótulo 4', numquestions=numquestions, numdigits=numdigits, numalternatives=4, idcheck=True, id=id, name=name, proprietary=True,exam_type=exam_type)
    mCanvas.save() 
    sys.exit(0)

    # when not testing, more general command line interface
    try:
        label1 = sys.argv[1]
        label2 = sys.argv[2]
        label3 = sys.argv[3]
        numquestions = int(sys.argv[4])
        numdigits = int(sys.argv[5])
        idcheck = sys.argv[6]
        output_file = sys.argv[7]
    except:
        usage()
    try:
        input_file = sys.argv[8]
    except:
        input_file = None
    id,name = '',''

    mCanvas = canvas.Canvas(output_file, pagesize=A4)

    if idcheck == 'Y':
        idcheck = True
    else:
        idcheck = False
    if not input_file:
        draw_page(mCanvas,label1, label2, label3, label4, numquestions, numdigits, idcheck, id, numalternatives, name, obi=True)
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

        draw_pages(mCanvas, data, label1, label2, label3, label4, numquestions, numdigits, idcheck, numalternatives, obi=True)
    mCanvas.save() 
