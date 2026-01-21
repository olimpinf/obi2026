#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os
import getopt

head_text = r'''
\documentclass[a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage{epsfig}
\usepackage[landscape]{geometry}
\usepackage{rotating}
\usepackage{fontspec}
\usepackage{graphicx}
\usepackage{eso-pic}

\pagestyle{empty}
\geometry{
  top=00mm,
  %bindingoffset=25mm,
  left=00mm,right=0mm
}

\makeatletter 
\newcommand\HUGE{\@setfontsize\Huge{33}{37}}
\makeatother

%\setmainfont{Asana-Math}
\setmainfont{Helvetica}

\setlength\fboxrule{0.05pt}
\newcommand{\cracha}[5] {
  \fbox{
    \begin{minipage}[c][165mm]{105mm}
      \begin{center}

        \vspace*{37mm}
        {\HUGE \bf #1}\\[12pt]
        
        {\LARGE #2} \\[10pt]

        {\large #4} \\[10pt]
        
        \vspace{1mm}  
        \includegraphics[width=20mm]{qrcodes/#3.pdf}

        \vspace{1mm}  
        
        {\LARGE \textbf{Treinamento OII2025}\\[3pt]
          \normalsize Sociedade Brasileira de Computação\\[3pt]
                      {\bf Instituto de Computação -- UNICAMP}\\[8pt]}

      \end{center}
    \end{minipage}
  }
%
  \fbox{
    \begin{minipage}[c][165mm]{105mm}\setlength{\parindent}{5mm}
     \Large      
      {\bf Alergias}
      
      #5
      
      \vspace*{0.5cm}
              {\bf Telefones em caso de emergência}
              \begin{itemize}
              \item Coordenador da OBI:\\
                Prof. Ricardo Anido\\(19) 99915-5515 
%%              \item Monitor-chefe:\\
%%                Luan\\(65) 98146-5848 
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
  \\put(12,110){
    \\parbox[b][165mm]{105mm}{
      \\vfill
      \\centering
      \\includegraphics[width=109mm,keepaspectratio]{%s}
      \\vfill
    }
  }
}
\\begin{document}
\\AddToShipoutPicture{\\BackgroundPic}
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

background = "FundoCracha%s.pdf" % args[1].capitalize()
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
    firstname,lastname,id,role,alergias=tmp[0].strip(),tmp[1].strip(),tmp[2].strip(),tmp[3].strip(),tmp[4].strip()
    
    if alergias=='' or alergias=='""':
        alergias = 'Nenhuma'
    else:
        alergias = alergias.replace('"', '')
        
    print(body_text % (firstname,lastname,id,role,alergias))

print(tail_text)
print(file=sys.stderr)

