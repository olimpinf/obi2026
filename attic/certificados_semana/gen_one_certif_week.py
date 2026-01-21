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


from tempfile import TemporaryDirectory

#print('\n'.join(sys.path))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')

DB_HOST="localhost"
print("executing in a MAC")
BASE_CERTIFS="/Users/ranido/Projects/obi2024/attic/certificados_semana"
BASE_CERTIFS="/Users/ranido/OBI/obi2025/attic/certifs"

PDFLATEX = "/opt/homebrew/bin/pdflatex"
PDFLATEX = "/Library/TeX/texbin/pdflatex"

roman_year={2005:'VII',2006:'VIII',2007:'IX',2008:'X',2009:'XI',2010:'XII',2011:'XIII',2012:'XIV',2013:'XV',2014:'XVI',2015:'XVII',2016:'XVIII',2017:'XIX',2018:'XX',2019:'XXI',2020:'XXII',2021:'XXIII',2022:'XXIV',2023:'XXV',2024:'XXVI'}
space_left={2005:0,2006:0,2007:28,2008:28,2009:28,2010:28,2011:14,2012:14,2013:14,2014:14,2015:14,2016:14,2017:14,2018:14,2019:14,2020:14,2021:14,2022:14,2023:14,2024:14}
WEEK_DATE = {2019: 'no Instituto de Computação da Unicamp de 1 a 7 de dezembro de 2019', 2020: 'online de 6 a 10 de dezembro de 2021', 2021: 'online de 6 a 10 de dezembro de 2021', 2022: 'no Instituto de Computação da Unicamp, de 4 a 10 de dezembro de 2022', 2023: 'no Instituto de Computação da Unicamp, de 3 a 9 de dezembro de 2023', 2024: 'no Instituto de Computação da Unicamp, de 1 a 7 de dezembro de 2024'}


def get_week_certif_professor(professor_name, genre, course, year):
    
    write_log('get_week_certif_professor=%s, year=%d' % (professor_name,year))
    print(f'get_week_certif_professor={professor_name}, course={course}, year={year}')
    suffix = ''
    if genre=='F':
        suffix = 'A'

    #with tempfile.TemporaryDirectory() as tmpdirname:
    #    os.chdir(tmpdirname)
        
    # build the tex file
    f = open('certif.tex', 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
    if course == 'Seletiva Competições Internacionais':
        f.write(week_setter_body_text % (space_left[year], 'LARGE', professor_name, suffix, roman_year[year], year, year, WEEK_DATE[year]))
    else:
        f.write(week_professor_body_text % (space_left[year], 'LARGE', professor_name, suffix, roman_year[year], year, year, WEEK_DATE[year]))
    f.write(end_text)
    f.write(tail_text)        
    f.close()
    
    # build pdf
    build_pdf('certif.tex')

def get_week_certif_monitor(monitor_name, genre, hours, year):
    write_log('get_week_certif_monitor=%s, year=%d' % (monitor_name,year))
    suffix = ''
    if genre=='F':
        suffix = 'A'

    # build the tex file
    f = open('certif.tex', 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
    f.write(week_monitor_body_text % (space_left[year], 'Large', monitor_name, suffix, roman_year[year], year, WEEK_DATE[year], hours))
    f.write(end_text)
    f.write(tail_text)
    f.close()
    
    # build pdf
    build_pdf('certif.tex')


def get_week_certif_monitor_chefe(monitor_name, genre, hours, year):
    write_log('get_week_certif_monitor=%s, year=%d' % (monitor_name,year))
    suffix = ''
    if genre=='F':
        suffix = 'A'

    # build the tex file
    f = open('certif.tex', 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
    f.write(week_monitor_chief_body_text % (space_left[year], 'Large', monitor_name, suffix, roman_year[year], year, WEEK_DATE[year], hours))
    f.write(end_text)
    f.write(tail_text)
    f.close()
    
    # build pdf
    build_pdf('certif.tex')

    
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

end_text_no_picture='''

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
de aulas teóricas e atividades práticas, num total de 35 horas.'''

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
de aulas teóricas e atividades práticas, num total de 35 horas.'''

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
de aulas teóricas e atividades práticas, num total de 35 horas.'''

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
de aulas teóricas e atividades práticas, num total de 35 horas.'''

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
de Informática (OBI%d). A Seletiva foi realizada durante a Semana Olímpica da OBI,  %s e consistiu
de aulas teóricas, atividades práticas e provas, num total de 35 horas.'''


week_monitor_body_text = '''
\\vspace*{3mm}
\\hspace*{%smm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\LARGE \\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI, 
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Semana Olímpica ocorreu de %s
no Instituto de Computação da Unicamp. Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos
em Programação de Computadores, Estrutura de Dados e Algoritmos. 
O trabalho dos monitores foi acompanhar os alunos em todas as atividades,
durante toda a semana, totalizando %s horas de monitoria'''

week_monitor_body_text = '''
\\vspace*{3mm}
\\hspace*{%smm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\LARGE \\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI, 
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Semana Olímpica ocorreu de %s
no Instituto de Computação da Unicamp. Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos
em Programação de Computadores, Estrutura de Dados e Algoritmos. 
O trabalho dos monitores foi acompanhar os alunos em todas as atividades,
durante toda a semana, totalizando %s horas de monitoria'''

week_monitor_chief_body_text = '''
\\vspace*{3mm}
\\hspace*{%smm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\LARGE \\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s-CHEFE durante a Semana Olímpica da OBI,
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira de
Informática (OBI%s). A Semana Olímpica ocorreu de %s no Instituto de
Computação da Unicamp. Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos em
Programação de Computadores, Estrutura de Dados e Algoritmos.  O
trabalho dos monitores foi acompanhar os alunos em todas as
atividades, durante toda a semana. O trabalho do monitor-chefe foi,
adicionalmente ao trabalho de monitor, organizar e
supervisionar o trabalho dos outros monitores, totalizando %s horas de
monitoria'''

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

trabalhou como PROFESSOR%s durante a Semana Olímpica,
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s), tendo ministrado aulas teóricas e práticas,
totalizando 40 horas de atividades. A Semana Olímpica da OBI2025 foi
realizada %s'''

week_setter_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como PROFESSOR%s durante a Semana Olímpica,
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s), tendo participado da elaboração e aplicação
das provas para a Seletiva para Competições Internacionais,
totalizando 40 horas de atividades. A Semana Olímpica da OBI%s foi
realizada %s'''

week_professor_body_text_old = '''
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

end_text='''.

\\end{minipage}
\\newpage
'''

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
    year = int(sys.argv[1])
    name = sys.argv[2]
    genre = 'M'
    hours = '40'
    course = 'Seletiva Competições Internacionais'
    #gen_certif_week_compets(year=year)
    #get_week_certif_monitor_chefe(monitor_name, genre, hours, year)
    get_week_certif_professor(name, genre, course, year)
