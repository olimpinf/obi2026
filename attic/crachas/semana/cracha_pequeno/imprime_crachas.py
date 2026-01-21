#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import getopt

head_text = r'''
\documentclass[a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}
\usepackage{geometry}
\usepackage{rotating}
\pagestyle{empty}
\geometry{
  paperwidth=8in,paperheight=10in,
  top=10mm,
  bottom=10mm,
  %bindingoffset=25mm,
  left=-80mm,right=0mm
}
\usepackage[a4]{crop}

\setlength\fboxrule{0.05pt}
\newcommand{\cracha}[5] {
  \fbox{
    \begin{minipage}[b][115mm]{75mm}
      \begin{center}
        \vspace{3mm}
        \includegraphics[width=28mm]{#4}

        \vspace*{6mm}

        {\Huge \textbf{#1}}\\[10pt]
            
        {\normalsize \textbf{#1 #2}} \\[10pt]

        {\Large #3}
            
        \vspace{3mm}        
            
        {\normalsize \textbf{Semana Olímpica da OBI2022}\\[3pt]
          \footnotesize Sociedade Brasileira de Computação\\[3pt]
          {\bf Instituto de Computação -- UNICAMP}\\[8pt]
       \vfill
          \includegraphics[width=75mm]{logos_patrocinadores.pdf}\\
        }
        \vspace*{2mm}
      \end{center}
    \end{minipage}
  }
  
  \rotatebox[origin=c]{180}{ 
    \fbox{
      \begin{minipage}[c][110mm]{75mm}\setlength{\parindent}{5mm}
        
        {\bf Alergias}

         #5
        
        \vspace*{0.5cm}
                {\bf Telefones em caso de emergência}
                \begin{itemize}
                \item Coordenador da OBI2022:\\
                  Prof. Ricardo Anido\\(19) 99915-5515 
                \item Monitor-chefe:\\
                  Luan\\(65) 98146-5848 
                \item Secretaria OBI:\\
                  (19) 3199-7399
                \item Vigilância do Campus:\\
                  (19) 3521-6000
                \end{itemize}
      \end{minipage}
    }
  }
}

\begin{document}
'''

body_text = r'''

\begin{center}
\cracha{%s}{%s}{%s}{%s}{%s}
\end{center}
\newpage

'''

tail_text = '''
\end{document}
'''

nome=""
modalidade="I1"

def usage():
    print("%s: file.csv logo_color\nfile must have columns first_name, last_name, partic_type, allergies\n" % sys.argv[0], file = sys.stderr)
    sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], "h", ["back", "help"])
except getopt.GetoptError as err:
    print(str(err), file = sys.stderr)  # will print something like "option -a not recognized"
    usage()

back = False
for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        else:
            assert False, "unhandled option"

if len(args) != 2:
    usage()

print(head_text)
    
f=open(args[0],"r")    
data=f.readlines()
logo_obi = "logo_obi_%s.pdf" % args[1]


for i in range(0,len(data),2):
    tmp = data[i].strip()
    if not tmp:
        continue
    tmp = tmp.split(',')
    firstname1,lastname1,modalidade1=tmp[0].strip(),tmp[1].strip(),tmp[2].strip()
    try:
        alergias1 = tmp[3].strip()
    except:
        alergias1 = 'Nenhuma'
    try:
        tmp = data[i+1].split(',')
        firstname2,lastname2,modalidade2=tmp[0].strip(),tmp[1].strip(),tmp[2].strip()
        try:
            alergias2 = tmp[3].strip()
        except:
            alergias2 = 'Nenhuma'
    except:
        firstname2,lastname2,modalidade2,alergias2='Nome','Sobrenome','Modalidade','Nenhuma'

    alergias1 = 'Nenhuma' if alergias1=='' or alergias1=='""' else alergias1.replace('"', '')
    alergias2 = 'Nenhuma' if alergias2=='' or alergias2=='""' else alergias2.replace('"', '')

    print(body_text % (firstname1,lastname1,modalidade1,logo_obi,alergias1))
    print(body_text % (firstname2,lastname2,modalidade2,logo_obi,alergias2))
    
print(tail_text)

