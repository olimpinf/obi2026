#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import getopt

head_text = r'''
\documentclass[a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}
\usepackage[papersize={20cm, 15cm}]{geometry}
\usepackage{rotating}
\usepackage{fontspec}
\usepackage{graphicx}
\usepackage{eso-pic}
\usepackage[
  % set width and height
  width=29.7truecm, height=21.0truecm,
  % use any combination of these options to add different cut markings
  %cam, axes, frame, cross,
  cam, axes,
  % set the type of TeX renderer you use
  pdftex,
  % center the contents
  center
]{crop}


\makeatletter 
\newcommand\HUGE{\@setfontsize\Huge{33}{37}}
\makeatother

%\setmainfont{Asana-Math}
\setmainfont{Helvetica}

\setlength\fboxrule{0.00pt}
\newcommand{\cracha}[5] {
  \fbox{\hspace{-3.7cm}
    \begin{minipage}[c][150mm]{100mm}
      \begin{center}

        \vspace*{-10mm}
        {\HUGE \bf #1}\\[6pt]
        
        {\LARGE #1 #2} \\[8pt]
        
        {\Large #3}
        
        \vspace{1mm}  
        \includegraphics[width=20mm]{qrcodes/#5.pdf}
        \vspace{-1mm}  
        
        {\LARGE \textbf{Semana Olímpica da OBI2025}\\[3pt]
          \normalsize Sociedade Brasileira de Computação\\[3pt]
                      {\bf Instituto de Computação -- UNICAMP}\\[8pt]}

      \end{center}
    \end{minipage}
  }
%
  \fbox{\hspace{-0.4cm}
    \begin{minipage}[c][150mm]{100mm}\setlength{\parindent}{10mm}
     \Large
     \vspace{-1cm}
      {\bf Alergias}
      
      #4
      
      \vspace*{0.5cm}
              {\bf Telefones em caso de emergência}
              \begin{itemize}
              \item Coordenador da OBI2025:\\
                Prof. Ricardo Anido\\(19) 99915-5515 
              \item Coordenador de Monitores:\\
                Wladimir Carrillo \\(19) 98198‑1665
%%              \item Secretária OBI:\\
%%                Lívia\\(11) 95808-5787 
              \item Vigilância do Campus:\\
                (19) 3521-6000
              \end{itemize}
    \end{minipage}
  }

}
'''

# string cannot be raw if string has arguments? Using not raw then
head_color = '''
\\newcommand\\BackgroundPic{
  \\put(-3,0){
    \\parbox[b][150mm]{100mm}{
      \\vfill
      \\centering
      \\includegraphics[width=100mm,keepaspectratio]{%s}
      \\vfill
    }
  }
}
\\begin{document}
\\AddToShipoutPicture{\\BackgroundPic}
\\pagestyle{empty}
'''

body_text = r'''
\cracha{%s}{%s}{%s}{%s}{%s}
'''

tail_text = '''
\\end{document}
'''

nome=""
modalidade="I1"

def usage():
    print("%s: file.csv logo_color\nfile must have columns first_name, last_name, partic_type, id, allergies\n" % sys.argv[0], file = sys.stderr)
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

background = "FundoCracha%s2025.pdf" % args[1].capitalize()
print(head_text)
print(head_color % background)

f=open(args[0],"r")    
data=f.readlines()

line = 0
for i in range(len(data)):
    line += 1
    print(line,end=",",file=sys.stderr)
    tmp = data[i].strip()
    if not tmp:
        continue
    tmp = tmp.split(',')
    firstname,lastname,modalidade,id,alergias=tmp[0].strip(),tmp[1].strip(),tmp[2].strip(),tmp[3].strip(),tmp[4].strip()
    
    if alergias=='' or alergias=='""':
        alergias = 'Nenhuma'
    else:
        alergias = alergias.replace('"', '')
        
    print(body_text % (firstname,lastname,modalidade,alergias,id))

print(tail_text)
print(file=sys.stderr)

