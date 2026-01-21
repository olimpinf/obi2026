#!/usr/bin/env python

# print letters
import os
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import date

import psycopg2
import psycopg2.extras

UNIT_VALUE = 2000.0
VALUES = {1: 'Dois Mil e Trezentos Reais',
          2: 'Quatro Mil e Seicentos Reais',
          3: 'Seis Mil e Novecentos Reais',
          4: 'Nove Mil e Duzentos Reais',
          5: 'Onze Mil e Quinhentos Reais',
          6: 'Treze Mil e Oitocentos Reais',
          7: 'Dezesseis Mil e Cem Reais',
          8: 'Dezoito Mil e Quatrocentos Reais',
          9: 'Vinte Mil e Setecentos Reais',
          10: 'Vinte e Três Mil Reais',
          11: 'Vinte e Cinco Mil e Trezentos Reais',
          12: 'Vinte e Sete Mil e Seiscentos Reais',
          }

UNITS = {1: '01 (uma) inscrição',
         2: '02 (duas) inscrições',
         3: '03 (três) inscrições',
         4: '04 (quatro) inscrições',
         5: '05 (cinco) inscrições',
         6: '06 (seis) inscrições',
         7: '07 (sete) inscrições',
         8: '08 (oito) inscrições',
         9: '09 (nove) inscrições',
         10:'10 (dez) inscrições',
         11:'11 (onze) inscrições',
         12:'12 (doze) inscrições',
         }


MAC=False
#print('\n'.join(sys.path))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')

DB_HOST="localhost"
if not MAC:
    BASE_DIR = '/home/olimpinf/django3.2/obi2022/'
    #from obi2021.settings import BASE_DIR
    #DB_HOST="10.0.0.16"
    BASE_CERTIFS=os.path.join(BASE_DIR,"attic","certifs")
    PDFLATEX = "/usr/bin/pdflatex"

else:
    print("executing in a MAC")
    BASE_CERTIFS="/Users/ranido/Documents/SBC/OBI/django3.2.nosync/obi2022/attic/certifs/"
    #BASE_CERTIFS="/Users/ranido/Documents/OBI/django3.2/obi2022/attic/certifs/"
    PDFLATEX = "/Library/TeX/texbin/pdflatex"

def format_value(v):
    s = f'%.2f' % v
    s = s.replace('.',',')
    s = s.replace('000','.000')
    return s
    
def get_receipt(year,id):
    #write_log('get_letter_compet id=%d, year=%d' % (compet_id,year))
    # Consulta BD
    
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    comm = "select * from payment where id=%d" % id
    #print('comm',comm)
    curs.execute(comm)
    # build the tex file
    data = curs.fetchone()
    f = open(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.tex' % (id,year)), 'w')
    name = data['doc_name']
    number = data['doc_number']
    compets = data['data']
    value = data['value']
    #receipt_date = date.today().strftime("%d-%m-%Y")
    receipt_date = data['time_confirmed'].strftime("%d-%m-%Y")
    tmp = value / UNIT_VALUE
    num_inscricoes = UNITS[int(tmp)]
    value_str = VALUES[int(tmp)]
    compets = data['data']
    
    f.write(receipt_text % (id, year, format_value(value), name, number, format_value(value), value_str, num_inscricoes, compets, receipt_date))
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.tex' % (id,year)))
    # return the certificate
    try:
        imgf=open(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.pdf' % (id,year)),"rb")
        data=imgf.read()
        imgf.close()
    except:
        data = ''
    try:
      #os.unlink(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.pdf' % (id,year)))
      #os.remove(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.tex' % (id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.log' % (id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Receipt_%06d_%d.aux' % (id,year)))
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
      
receipt_text = r'''
\documentclass[12pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage{geometry}
\usepackage{eso-pic}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}

%%\newcommand\BackgroundPic{
%%  \put(0,0){
%%    \parbox[b][\paperheight]{\paperwidth}{
%%      \vfill
%%      \centering
%%      \includegraphics[width=\paperwidth,height=\paperheight,keepaspectratio]{receipt.pdf}
%%      \vfill
%%    }
%%  }
%%}


\begin{document}
%%\AddToShipoutPicture{\BackgroundPic}


\thispagestyle{plain}
\pagenumbering{gobble}


\vspace*{-1cm}
\begin{center}
{\Large \bf Recibo de Pagamento}
\end{center}

\null\hfill Recibo $N^{\underline{o}}$ OBI-%03d-%s\\
\null\hfill Valor: R\$ %s

\vspace*{1cm}
\noindent
Recebemos de 

\emph{%s}, \\
\indent
CPF/CNPJ %s,

\noindent
o valor de R\$ %s (%s), referente a %s no evento 
Semana Olímpica da OBI.

{\footnotesize
\begin{verbatim}
%s
\end{verbatim}
}

\noindent
{\footnotesize 
\null\hfill Emitido por Ricardo de Oliveira Anido em %s
}

\noindent
\centering
\includegraphics[width=0.7\paperwidth,keepaspectratio]{receipt.jpg}

\end{document}
'''

if __name__=="__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')
    get_receipt(id=28,year=2022)
