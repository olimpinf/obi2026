#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

import psycopg2
import psycopg2.extras

HOST = 'localhost' #'10.0.0.16'
YEAR = 2024
DB = f'obi{YEAR}'

head_text = r'''\documentclass[landscape,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[portuges]{babel}
\usepackage[portrait]{geometry}
\usepackage{graphicx}
\usepackage{eso-pic}
\pagestyle{empty}

\setlength{\textwidth}{6.2in}
\setlength{\topmargin}{0.5in}
\setlength{\leftmargin}{0.0in}
\setlength{\parskip}{1.2ex}
\setlength{\parindent}{0mm}

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



\newcommand{\esimo}{\mbox{\raisebox{1ex}{\rm\b{\small o}}}}

\begin{document}
'''
body_text = r'''
\AddToShipoutPicture{\BackgroundPic}

Caro(a) Prof(a). %s,

\vspace{0.3cm} inicialmente, parabéns pelos resultados de seus alunos
da escola \emph{%s} na OBI%d.

Para auxiliar nos custos de envio de medalhas, solicitamos a
contribuição voluntária de R\$ 30,00 para escolas públicas e R\$ 60,00
para escolas privadas. A contribuição é única por escola, independente
do número de medalhas. A contribuição deve ser realizada na conta da
OBI na Sociedade Brasileira de Computação.

\subsubsection*{Pagamento através de transferência bancária}

\noindent
\textbf{Conta para depósito}: Banco do Brasil (001)\\
\textbf{Agência}: 1899-6\\
\textbf{Conta}: 23943-7\\
\textbf{CNPJ}: 29.532.264/0001-78\\
\textbf{Titular}: Sociedade OBI (esse é o nome da conta da OBI, cujo titular
é a Sociedade Brasileira de Computação; o CNPJ acima é o da SBC)

\subsubsection*{Pagamento com PIX}

\textbf{Chave aleatória}: a927a030-460a-4478-8722-10a70a3c72cb

Ou escaneie o código QR abaixo:

\begin{center}
\includegraphics[width=5cm]{pix_qrcode.png}\\[15pt]
\end{center}

Atenciosamente,

Coordenação da OBI%d\\
olimpinf@ic.unicamp.br


\hspace*{\fill}{\tiny %d}

\pagebreak
'''

tail_text='''
\end{document}
'''


# Consulta BD

conn = psycopg2.connect("host={} dbname={} user=obi password=guga.LC".format(HOST,DB))
conn.set_client_encoding('utf-8')
curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def usage():
    print(sys.argv[0])

def clean(s):
    return s

def write_letter(school_id, school_name, deleg_name, f):

    f.write(body_text % (deleg_name,school_name,YEAR,YEAR,school_id))


comm = '''select 
    school_id,
    school_name,
    school_deleg_name,
    compet_name,
    f.compet_type, 
    f.compet_medal 
    from school,compet as c, compet_cfobi as f
    where f.compet_id=c.compet_id and compet_school_id=school_id and f.compet_medal in ('o','p','b') 
    order by compet_school_id,f.compet_type,f.compet_rank,f.compet_medal,compet_name'''

curs.execute(comm)
data = curs.fetchall()
# DictCursor not working

print('compets found:', len(data),file=sys.stderr)

cur_school_id = 0
f = open(f'cartas_medalhas_cf.tex','w')
f.write(head_text)

for d in data:
    
    if d[0] != cur_school_id:
        print(cur_school_id)
        write_letter(d[0], d[1], d[2], f)
        cur_school_id = d[0]
f.write(tail_text)

f.close()

os.system("pdflatex cartas_medalhas_cf")

