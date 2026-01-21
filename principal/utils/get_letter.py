#!/usr/bin/env python

# print letters
import os
import platform
import shlex
import subprocess
import sys
import tempfile
import time

import psycopg2
import psycopg2.extras

from obi.settings import BASE_DIR, YEAR

#print('\n'.join(sys.path))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')

DB_HOST="localhost"

BASE_CERTIFS=os.path.join(BASE_DIR,"attic","certifs")

if platform.system() == 'Darwin':
    PDFLATEX = "/opt/homebrew/bin/pdflatex"
else:
    PDFLATEX = "/usr/bin/pdflatex"

    
def get_letter_teacher(name,sex,year):
    #write_log('get_letter_compet id=%d, year=%d' % (compet_id,year))
    # Consulta BD
    slug = name.replace(' ', '-')
    first_name = name.split()[0]
    f = open(os.path.join(BASE_CERTIFS,'Letter_%s_%d.tex' % (slug,year)), 'w')

    if sex == 'F':
        flex = 'a'
    else:
        flex = 'o'
    f.write(letter_teacher_text % (name, flex, first_name, first_name))
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'Letter_%s_%d.tex' % (slug,year)))
    # return the certificate
    try:
        imgf=open(os.path.join(BASE_CERTIFS,'Letter_%s_%d.pdf' % (slug,year)),"rb")
        data=imgf.read()
        imgf.close()
    except:
        data = ''
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'Letter_%s_%d.pdf' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%s_%d.tex' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%s_%d.log' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%s_%d.aux' % (slug,year)))
    except:
      pass
    return(data)

def get_letter_compet(compet_id,year,num_compets):
    #write_log('get_letter_compet id=%d, year=%d' % (compet_id,year))

    compet_level = {1:"Modalidade Iniciação Nível 1",
                    2:"Modalidade Iniciação Nível 2",
                    3:"Modalidade Programação Nível 1",
                    4:"Modalidade Programação Nível 2",
                    5:"Modalidade Programação Nível Júnior",
                    6:"Modalidade Programação Nível Sênior",
                    7:"Modalidade Iniciação Nível Júnior",
                    }

    
    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    comm = "select * from compet,week where compet.compet_id=week.compet_id and compet.compet_id=%d" % compet_id
    #print('comm',comm)
    curs.execute(comm)
    # build the tex file
    data = curs.fetchone()
    f = open(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)), 'w')
    name = data['compet_name']
    level_num = data['compet_type']
    level = compet_level[level_num]
    if data['compet_sex'] == 'F':
        flex = 'a'
    else:
        flex = 'o'
    f.write(letter_text % (name, flex, flex, flex, num_compets, level))
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)))
    # return the certificate
    try:
        imgf=open(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.pdf' % (compet_id,year)),"rb")
        data=imgf.read()
        imgf.close()
    except:
        data = ''
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.pdf' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.log' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.aux' % (compet_id,year)))
    except:
      pass
    return(data)

def get_letter_compet_camp(compet_id,year):
    #write_log('get_letter_compet id=%d, year=%d' % (compet_id,year))
    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    comm = "select * from compet where compet.compet_id=%d" % compet_id
    #print('comm',comm)
    curs.execute(comm)
    # build the tex file
    data = curs.fetchone()
    f = open(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)), 'w')
    name = data['compet_name']
    if data['compet_sex'] == 'F':
        flex = 'a'
    else:
        flex = 'o'
    f.write(letter_text_camp % (name, flex, flex, flex))
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)))
    # return the certificate
    try:
        imgf=open(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.pdf' % (compet_id,year)),"rb")
        data=imgf.read()
        imgf.close()
    except:
        data = ''
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.pdf' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.tex' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.log' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Letter_%06d_%d.aux' % (compet_id,year)))
    except:
      pass
    return(data)

def build_pdf(texfile):
    old = os.getcwd()
    os.chdir(BASE_CERTIFS)
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
    os.chdir(old)

      
letter_text = r'''
\documentclass[11pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}

\newcommand\BackgroundPic{
  \put(0,0){
    \parbox[b][\paperheight]{\paperwidth}{
      \vfill
      \centering
      \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{letterhead.pdf}
      \vfill
    }
  }
}


\begin{document}
\AddToShipoutPicture{\BackgroundPic}


\thispagestyle{plain}
\pagenumbering{gobble}

\vspace*{2cm}

\hfill Campinas, 30 de outubro de 2025

\vspace*{1cm}

\noindent
Caros colegas professores,
\vspace*{0.5cm}

\noindent
em nome da Olimpíada Brasileira de Informática -- OBI, venho por meio desta
informar que

\vfill
\begin{center}
\emph{%s}
\end{center}
\vfill

\noindent
foi convidad%s para participar da Semana Olímpica da OBI, que ocorrerá no Instituto de
Computação da UNICAMP, com os melhores alunos classificados na
OBI, entre os dias 30 de novembro e 6 de dezembro de
2025.

Gostaríamos de solicitar a sua colaboração, se possível, para permitir
que %s alun%s possa adiar (ou adiantar) a realização de provas e
outras atividades de sua disciplina, bem como abonar suas faltas naquela semana. Esses alunos convidados para a
Semana Olímpica demonstraram comprometimento e dedicação excepcionais
no estudo e preparação para as provas da OBI, tendo obtido excelentes
resultados, entre mais de %d mil participantes na \emph{%s}
da OBI.  Tenho certeza de que, com o mesmo comprometimento e
dedicação, poderão recuperar o conhecimento e atividades não vistos
durante o período em que participarem da Semana Olímpica da OBI.

A OBI é uma promoção da SBC -- Sociedade Brasileira de Computação, com
coordenação do Instituto de Computação da Unicamp, e reúne anualmente
mais de 110 mil competidores de todo o país. Para mais informações, por
favor consulte\\
 \texttt{http://olimpiada.ic.unicamp.br}.

\vspace*{3mm}

Atenciosamente,

\vfill

\begin{center}
\includegraphics[width=5cm]{signature_blue.jpg}\\
Prof. Dr. Ricardo Anido\\
Instituto de Computação - UNICAMP\\
Coordenador da OBI2025
\end{center}

\vfill

\end{document}
'''

letter_text_camp = r'''
\documentclass[11pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}

\newcommand\BackgroundPic{
  \put(0,0){
    \parbox[b][\paperheight]{\paperwidth}{
      \vfill
      \centering
      \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{letterhead.pdf}
      \vfill
    }
  }
}


\begin{document}
\AddToShipoutPicture{\BackgroundPic}


\thispagestyle{plain}
\pagenumbering{gobble}

\vspace*{2cm}

\hfill Campinas, 1 de junho de 2023

\vspace*{1cm}

\noindent
Caros colegas professores,
\vspace*{0.5cm}

\noindent
em nome da Coordenação da Olimpíada Brasileira de Informática -- OBI, venho por meio desta
informar que

\vfill
\begin{center}
\emph{%s}
\end{center}
\vfill

\noindent
foi convidad%s para participar da Semana de Treinamento para
Competições Internacionais, que ocorrerá no Instituto de
Computação da UNICAMP, com os alunos selecionados para
representar o Brasil 
na IOI - \emph{International Olympiad in Informatics} e
na EGOI - \emph{European Girls Olympiad in Informatics}. A Semana
de Treinamento ocorrerá
 entre os dias 4 e 11 de junho de
2023.

Gostaríamos de solicitar a sua colaboração, se possível, para permitir
que %s alun%s possa adiar a realização de provas e
outras atividades de sua disciplina, bem como abonar suas faltas naquela semana. Esses alunos convidados para a
Semana de Treinamento
demonstraram comprometimento e dedicação excepcionais
no estudo e preparação para serem selecionados para as equipes
que disputarão as competições internacionais.  
Tenho certeza de que, com o mesmo comprometimento e
dedicação, poderão recuperar o conhecimento e atividades não vistos
durante o período em que participarem do Treinamento para Competições Internacionais.

A OBI é uma promoção da SBC -- Sociedade Brasileira de Computação, com
coordenação do Instituto de Computação da Unicamp, e reúne anualmente
mais de 100 mil competidores de todo o país. Para mais informações, por
favor consulte\\
 \texttt{https://olimpiada.ic.unicamp.br}.

\vspace*{3mm}

Atenciosamente,

\vfill

\begin{center}
\includegraphics[width=5cm]{signature_blue.jpg}\\
Prof. Dr. Ricardo Anido\\
Instituto de Computação - UNICAMP\\
\end{center}

\vfill

\end{document}
'''

letter_teacher_text = r'''
\documentclass[10pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}

\newcommand\BackgroundPic{
  \put(0,0){
    \parbox[b][\paperheight]{\paperwidth}{
      \vfill
      \centering
      \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{letterhead.pdf}
      \vfill
    }
  }
}


\begin{document}
\AddToShipoutPicture{\BackgroundPic}


\thispagestyle{plain}
\pagenumbering{gobble}

\vspace*{2cm}

\hfill Campinas, 9 de dezembro de 2023

\vspace*{1cm}

\noindent
Caros colegas professores,
\vspace*{0.5cm}

\noindent
em nome da Olimpíada Brasileira de Informática -- OBI, venho por meio desta
informar que

\begin{center}
\emph{%s}
\end{center}

\noindent foi convidad%s para participar como \emph{professor} da
Semana Olímpica da OBI -- Seletiva para Competições Internacionais,
que ocorreu no Instituto de Computação da UNICAMP, com os melhores
alunos classificados na \emph{Modalidade Programação} da OBI, entre os
dias 3 e 9 de dezembro de 2023. Participaram da OBI2023 mais de 100 mil
competidores de todo o país, dos quais 25 foram convidados para
participar da Seletiva para Competições Internacionais.

A Seletiva para Competições Internacionais da OBI seleciona os alunos
que representarão o Brasil na Olimpíada Internacional de Informática
(IOI), na Competição Iberoamericana de Informática e Computação (CIIC) e na
Olimpíada Européia de Informática para Meninas (EGOI, na qual o Brasil
participa como país convidado).

Os professores da Semana Olímpica são todos ex-competidores
medalhistas da OBI, muitos deles também medalhistas da IOI e da
Maratona de Programação da SBC. Essa experiência é fundamental para o
sucesso da Seletiva para Competições Internacionais. Os professores
ficam alojados no mesmo hotel que os alunos e além das aulas também
preparam as provas (diárias), de forma que a dedicação deles é em
tempo integral durante a Semana Olímpica.

Gostaríamos de solicitar a sua colaboração, se possível, para permitir
que {%s} possa realizar, num futuro próximo, as atividades
eventualmente perdidas de sua disciplina.  Também seria muito
importante que as faltas nessa semana pudessem ser abonadas.

Tenho certeza de que, com o mesmo comprometimento e dedicação que
demonstra para com a OBI, {%s} poderá recuperar o conhecimento e
atividades não vistos durante o período em que contribuiu com a
Semana Olímpica da OBI.

A OBI é uma promoção da SBC -- Sociedade Brasileira de Computação, com
coordenação do Instituto de Computação da Unicamp. A Semana Olímpica
da OBI teve o apoio do CNPq -- Conselho Nacional de Desenvolvimento Científico e Tecnológico
e da AluraStart. Para mais informações, por
favor consulte \texttt{http://olimpiada.ic.unicamp.br}.

Atenciosamente,

\vfill

\begin{center}
\includegraphics[width=5cm]{signature_blue.jpg}\\
Prof. Dr. Ricardo Anido\\
Instituto de Computação - UNICAMP\\
Coordenador da OBI2023
\end{center}

\vfill

\end{document}
'''

letter_teacher_ini_text = r'''
\documentclass[10pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}

\newcommand\BackgroundPic{
  \put(0,0){
    \parbox[b][\paperheight]{\paperwidth}{
      \vfill
      \centering
      \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{letterhead.pdf}
      \vfill
    }
  }
}


\begin{document}
\AddToShipoutPicture{\BackgroundPic}


\thispagestyle{plain}
\pagenumbering{gobble}

\vspace*{2cm}

\hfill Campinas, 9 de dezembro de 2023

\vspace*{1cm}

\noindent
Caros colegas professores,
\vspace*{0.5cm}

\noindent
em nome da Olimpíada Brasileira de Informática -- OBI, venho por meio desta
informar que

\begin{center}
\emph{%s}
\end{center}

\noindent foi convidad%s para participar como \emph{professor} da
Semana Olímpica da OBI -- Seletiva para Competições Internacionais,
que ocorreu no Instituto de Computação da UNICAMP, com os melhores
alunos classificados na \emph{Modalidade Programação} da OBI, entre os
dias 3 e 9 de dezembro de 2023. Participaram da OBI2023 mais de 100 mil
competidores de todo o país, dos quais 82 foram convidados para
participar da Seletiva para Competições Internacionais.

A Seletiva para Competições Internacionais da OBI seleciona os alunos
que representarão o Brasil na Olimpíada Internacional de Informática
(IOI), na Competição Iberoamericana de Informática e Computação (CIIC) e na
Olimpíada Européia de Informática para Meninas (EGOI, na qual o Brasil
participa como país convidado).

Os professores da Semana Olímpica são todos ex-competidores
medalhistas da OBI, muitos deles também medalhistas da IOI e da
Maratona de Programação da SBC. Essa experiência é fundamental para o
sucesso da Seletiva para Competições Internacionais. Os professores
ficam alojados no mesmo hotel que os alunos e além das aulas também
preparam as provas (diárias), de forma que a dedicação deles é em
tempo integral durante a Semana Olímpica.

Gostaríamos de solicitar a sua colaboração, se possível, para permitir
que {%s} possa realizar, num futuro próximo, as atividades
eventualmente perdidas de sua disciplina.  Também seria muito
importante que as faltas nessa semana pudessem ser abonadas.

Tenho certeza de que, com o mesmo comprometimento e dedicação que
demonstra para com a OBI, {%s} poderá recuperar o conhecimento e
atividades não vistos durante o período em que contribuiu com a
Semana Olímpica da OBI.

A OBI é uma promoção da SBC -- Sociedade Brasileira de Computação, com
coordenação do Instituto de Computação da Unicamp. A Semana Olímpica
da OBI teve o apoio do CNPq - Conselho Nacional de Desenvolvimento Científico e Tecnológico. Para mais informações, por
favor consulte \texttt{http://olimpiada.ic.unicamp.br}.

Atenciosamente,

\vfill

\begin{center}
\includegraphics[width=5cm]{signature_blue.jpg}\\
Prof. Dr. Ricardo Anido\\
Instituto de Computação - UNICAMP\\
Coordenador da OBI2023
\end{center}

\vfill

\end{document}
'''

if __name__=="__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')
    #get_certif_colab(colab_id=123,year=2005)
    #get_certif_colab(colab_id=992,year=2013)
    #get_certif_colab(colab_id=596,year=2012)
    #get_certif_compet(compet_id=1636,year=2014)
    #get_certif_compet(compet_id=1902,year=2014)
    #get_certif_deleg(school_id=673,year=2014)
    #get_certif_deleg(school_id=532,year=2012)
    #get_certif_compet(compet_id=14404,year=2006)
    #get_certif_compet(compet_id=04565,year=2008)
    #get_certif_compet(compet_id=9380,year=2010)
    #get_certif_compet(compet_id=6086,year=2011)
    #get_certif_compet(compet_id=9452,year=2012)
    #get_certif_compet(compet_id=1402,year=2013)
    #get_certif_compet_school(school_id=384,year=2014)
    #get_certif_school_all(school_id=384,year=2014)
  
    #print_all_certifs(2014)
    #get_certif_school_compets(compet_type=0,school_id=384,year=2014)
    #get_certif_school_colabs(school_id=2,year=2014)
    #get_certif_compet(compet_id=3339,year=2014)
    #get_certif_compet(compet_id=26227,year=2015)
    #get_certif_compet(compet_id=26227,year=2016)
    #get_certif_compet(compet_id=43455,year=2016)
    #get_certif_school_colabs(school_id=1,year=2016)
    #get_certif_olimp_week(year=2016)
    #get_certif_compet(compet_id=23486,year=2017)
    #get_certif_colab(colab_id=490,year=2017)
    #get_certif_compet(compet_id=1402,year=2013)
    
    #get_certif_compet(compet_id=28707,year=2018)
    #get_certif_school_all(school_id=1,year=2018)
    
    #get_certif_colab(colab_id=35,year=2018)
    #get_certif_compet(compet_id=8753,year=2020)
    #get_certif_olimp_week(year=2018)
    #get_week_certif_compet(compet_id=28446,level=3,year=2021)
    #get_letter_compet(compet_id=250,year=2023)
    #get_letter_teacher(name='Ricardo Anido',sex='M',year=2023)
