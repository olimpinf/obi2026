#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\begin{document}
'''

template_small = r'''
\thispagestyle{empty}

\begin{center}
  {\Large \bf Treinamento OII  }
\end{center}
\vspace{0.3cm}

\section*{Competidor}
{\large %s}

\section*{Senhas}
\subsection*{Computador}
\noindent \textbf{Nome de usuário}: \texttt{%s}
\noindent \textbf{Senha}: \texttt{%s}


'''

tail = r'''
\end{document}
'''


if len(sys.argv) != 2:
    print("Usage: {} filename".format(sys.argv[0]))
    sys.exit(0)

filename = sys.argv[1]

with open(filename, "r") as f:

    count,i = 0,0
    with open("senhas.tex", "w") as tex:
        print(header, file=tex)
        lines = f.readlines()
        while True:
            print(lines[i])
            
            if i >= len(lines):
                break
            line = lines[i].strip().split(',')
            print(line)
            #username_obi,password_obi,compet_id,name,password_cms = line
            #print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            try:
                username_obi,password_obi,name = line
            except Exception as e:
                break
            #print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            print(template_small % (name,username_obi,password_obi), file=tex)
            count += 1

            i += 1

            if i >= len(lines):
                break
            line = lines[i].strip().split(',')

            print(line)
            try:
                username_obi,password_obi,name = line
            except:
                break
            
            print(r'\vspace*{5cm}', file=tex)
            print(template_small % (name,username_obi,password_obi), file=tex)
            count += 1
            i += 1

            print("\pagebreak", file=tex)

        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")
        
