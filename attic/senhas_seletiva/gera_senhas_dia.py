#!/usr/bin/env python3

import os, sys, random, string

def escape(s):
    return s.replace("_","\_")

header =  r'''\documentclass{article}
\begin{document}
'''

template = r'''
\begin{center}
  {\Large \bf OBI2024 -- Seletiva - Dia {%s} }
\end{center}
\vspace{0.3cm}

\subsection*{Competidor}
{\large %s}

\subsection*{Ambiente de prova}
\noindent \textbf{Nome de usuário}: \texttt{%s}

\noindent \textbf{Senha}: \texttt{%s}

\subsection*{Endereço}

\noindent Programação Nível 2: \texttt{https://p2.provas.ic.unicamp.br}\\

\pagebreak
'''

tail = r'''
\end{document}
'''


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} day filename")
    sys.exit(0)

day = sys.argv[1]
filename = sys.argv[2]

with open(filename, "r") as f:

    count = 0
    with open("senhas.tex", "w") as tex:
        print(header, file=tex)
        for line in f:
            username,password,name = line.split(',')
            username = escape(username)
            print(template % (day,name,username,password), file=tex)
            count += 1
        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")

