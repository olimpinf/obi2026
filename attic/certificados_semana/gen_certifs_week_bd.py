#!/usr/bin/env python

# print certificates
import os
import shlex
import subprocess
import sys
import tempfile
import time
import qrcode
import re

import psycopg2
import psycopg2.extras

YEAR = 2025
FIRST_YEAR_WITH_HASH=2021

from tempfile import TemporaryDirectory

#print('\n'.join(sys.path))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')

DB_HOST="localhost"
print("executing in a MAC")
BASE_CERTIFS="/Users/ranido/Documents/OBI/django3.2/obi2021/attic/certifs/"
BASE_CERTIFS="/Users/ranido/Documents/SBC/OBI/django3.2.nosync/obi2022/attic/certifs/"
BASE_CERTIFS="/Users/ranido/Projects/obi2022/attic/certificados_semana"

PDFLATEX = "/opt/homebrew/bin/pdflatex"
#from medal_cuts import medal_cuts
#from utils import slugfy

roman_year={2005:'VII',2006:'VIII',2007:'IX',2008:'X',2009:'XI',2010:'XII',2011:'XIII',2012:'XIV',2013:'XV',2014:'XVI',2015:'XVII',2016:'XVIII',2017:'XIX',2018:'XX',2019:'XXI',2020:'XXII',2021:'XXIII',2022:'XXIV',2023:'XXV',2024:'XXVI',2025:'XXVII'}
space_left={2005:0,2006:0,2007:28,2008:28,2009:28,2010:28,2011:14,2012:14,2013:14,2014:14,2015:14,2016:14,2017:14,2018:14,2019:14,2020:14,2021:14,2022:14,2023:14,2024:14,2025:14}
WEEK_DATE = {2019: 'no Instituto de Computação da Unicamp de 1 a 7 de dezembro de 2019', 2020: 'online de 6 a 10 de dezembro de 2021', 2021: 'online de 6 a 10 de dezembro de 2021', 2022: 'no Instituto de Computação da Unicamp, de 4 a 10 de dezembro de 2022', 2023: 'no Instituto de Computação da Unicamp, de 3 a 9 de dezembro de 2023',2024: 'no Instituto de Computação da Unicamp, de 2 a 8 de dezembro de 2024',2025: 'no Instituto de Computação da Unicamp, de 30 de novembro a 6 de dezembro de 2025'}


def gen_certif_week_compets(year,compet_type):
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur_dir = os.getcwd()
    # with tempfile.TemporaryDirectory() as tmpdirname:
    #    os.chdir(tmpdirname)
    if True:
            
        # build the tex file
        f = open(f'certif_{compet_type}.tex','w')
        f.write(head_text % os.path.join(f"FundoCertif{year}.pdf"))
        
        comm = f"select * from compet as c, week as w , level as l where l.id=compet_type and c.compet_id=w.compet_id and w.compet_id=c.compet_id and w.partic_level = {compet_type} order by w.partic_level, compet_name"
        curs.execute(comm)

        alldata = curs.fetchall()
        for data in alldata:
            compet_id=data['compet_id']
            compet_name=data['compet_name']
            partic_level=data['partic_level']
            tmp1=data['name']
            level_name_full=f"{tmp1}"
            print(compet_name, file=sys.stderr)

            if partic_level == 1:
                f.write(week_body_text_i1 % (space_left[year], 'LARGE', compet_name, level_name_full, roman_year[year], year, WEEK_DATE[year]))
                f.write(end_text_no_picture)
            elif partic_level == 2:
                f.write(week_body_text_i2 % (space_left[year], 'LARGE', compet_name, level_name_full, roman_year[year], year, WEEK_DATE[year]))
                f.write(end_text_no_picture)
            elif partic_level == 3:
                f.write(week_body_text_p1 % (space_left[year], 'LARGE', compet_name, level_name_full, roman_year[year], year, WEEK_DATE[year]))
                f.write(end_text_no_picture)
            elif partic_level == 4:
                f.write(week_body_text_p2 % (space_left[year], 'LARGE', compet_name, level_name_full, roman_year[year], year, WEEK_DATE[year]))
                f.write(end_text_no_picture)
            elif partic_level == 5:
                f.write(week_body_text_pj % (space_left[year], 'LARGE', compet_name, level_name_full, roman_year[year], year, WEEK_DATE[year]))
                f.write(end_text_no_picture)

        f.write(tail_text)
        f.close()
        with open(f"certif_{partic_level}.tex", "r") as f:
            lines = f.readlines()
        
        # build pdf
        build_pdf(f'certif_{partic_level}.tex')
        # return the certificate
        try:
            imgf=open(f'certif{partic_level}.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(cur_dir)
    return(data)

head_text = '''\\documentclass[landscape,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[portuges]{babel}
\\usepackage[landscape]{geometry}
\\usepackage{graphicx}
\\usepackage{eso-pic}
\\pagestyle{empty}

\\setlength{\\textwidth}{8in}           
\\setlength{\\topmargin}{0.4in}         
\\setlength{\\leftmargin}{0.0in}        
\\setlength{\\parskip}{1.2ex}
\\setlength{\\parindent}{0mm}

\\newcommand\BackgroundPic{
  \\put(0,0){
    \\parbox[b][\\paperheight]{\\paperwidth}{
      \\vfill
      \\centering
      \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{%s}
      \\vfill
    }
  }
}


\\newcommand{\\esimo}{\\mbox{\\raisebox{1ex}{\\rm\\b{\\small o}}}}

\\begin{document}
\AddToShipoutPicture{\BackgroundPic}
'''

tail_text = '''
\\end{document}
'''

end_text_no_picture='''.

\\end{minipage}
\\vfill
\\hspace{10mm}
\\newpage
'''


week_body_text_i1 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \emph{Introdução à Programação de Computadores em C++} durante a Semana Olímpica da OBI, 
para os melhores colocados da Modalidade %s da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, totalizando 35 horas'''

week_body_text_i2 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \emph{Introdução à Programação de Computadores em C++} durante a Semana Olímpica da OBI, 
para os melhores colocados da Modalidade %s da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, totalizando 35 horas'''

week_body_text_pj = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \emph{Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos} durante a Semana Olímpica da OBI, 
para os melhores colocados da Modalidade %s da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, totalizando 35 horas'''

week_body_text_p1 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \emph{Técnicas de Programação, Estruturas de Dados e Algoritmos} durante a Semana Olímpica da OBI, 
para os melhores colocados da Modalidade %s da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, totalizando 35 horas'''

week_body_text_p2 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou da \emph{Seletiva para Competições Internacionais}
para os melhores colocados da Modalidade %s da %s Olimpíada Brasileira
de Informática (OBI%d). A Seletiva foi realizada durante a Semana Olímpica da OBI,  %s, e consistiu
de aulas teóricas e atividades práticas, totalizando 35 horas'''


week_monitor_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI, 
oferecida aos melho\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos
em Programação de Computadores, Estrutura de Dados e Algoritmos. 
O trabalho dos monitores foi auxiliar os alunos durante as 
atividades práticas, totalizando %d horas de monitoria'''

week_monitor_seletiva_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI -- Seletiva Competições Internacionais, 
oferecida aos melho\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Seletiva Competições Internacionais ocorreu
no Instituto de Computação da Unicamp, entre os dias 1 e 7 de maio de 2022. 
O trabalho dos monitores foi auxiliar os alunos durante as 
atividades práticas, totalizando %d horas de monitoria'''

week_professor_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como PROFESSOR%s durante a Semana Olímpica da OBI,
oferecida aos melho\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s), tendo ministrado o curso \emph{%s}. O curso
foi constituído por aulas teóricas e atividades práticas monitoradas,
totalizando 35 horas de atividades didáticas'''

#---------------------------------------------------------------------------

def build_pdf(texfile):
    #old = os.getcwd()
    #os.chdir(BASE_CERTIFS)
    #print('build_pdf')
    result = subprocess.call([PDFLATEX, "-interaction=nonstopmode", "-halt-on-error", texfile],timeout=15)
    '''
    with open('/dev/null', 'w') as dev_null:
        result = subprocess.call(["pdflatex", "%s" % texfile],
                           stdin = dev_null,
                           stdout = dev_null,
                           stderr = dev_null)
    '''
    if result !=0:
      print("cannot build pdf:", result, file=sys.stderr)
    #os.chdir(old)

#---------------------------------------------------------------------------

def get_medal(rank):
    global gold,silver,bronze,honor
    if not rank:
      return ''
    if (rank<=gold):
        medal='Medalha de Ouro'
    elif (rank<=silver):
        medal='Medalha de Prata'
    elif (rank<=bronze):
        medal='Medalha de Bronze'
    elif (rank<=honor):
        medal='Honra ao Mérito'
    else:
        medal=''
    return medal

#---------------------------------------------------------------------------

def CurrentTime():
  return time.strftime('%Hh%Mm%Ss',time.localtime(time.time()))

#---------------------------------------------------------------------------

def CurrentDate():
  return time.strftime('%Y-%m-%d',time.localtime(time.time()))

#---------------------------------------------------------------------------

def write_log(msg):
    with open(os.path.join(BASE_CERTIFS,'LOG'), 'a') as f:
      f.write(CurrentDate()+" "+CurrentTime()+": %s\n" % msg)

#---------------------------------------------------------------------------


if __name__=="__main__":
    year = YEAR
    gen_certif_week_compets(year=year, compet_type=1)
    gen_certif_week_compets(year=year, compet_type=2)
    gen_certif_week_compets(year=year, compet_type=3)
    gen_certif_week_compets(year=year, compet_type=4)
    gen_certif_week_compets(year=year, compet_type=5)
