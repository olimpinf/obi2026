#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\begin{document}
'''

template = r'''
\begin{center}
  {\Large \bf OBI2023 -- Seletiva - Dia 1 }
\end{center}
\vspace{0.3cm}

\subsection*{Competidor}
{\large %s}

\subsection*{Computador}
\noindent \textbf{Nome de usuário}: \texttt{%s}

\noindent \textbf{Senha}: \texttt{%s}

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


if len(sys.argv) != 2:
    print("Usage: {} filename".format(sys.argv[0]))
    sys.exit(0)

filename = sys.argv[1]

with open(filename, "r") as f:

    count = 0
    with open("senhas.tex", "w") as tex:
        print(header, file=tex)
        for line in f:
            username_obi,password_obi,compet_id,name,password_cms = line.split(',')
            try:
                #obi01:Sewe5oon@ic,69235-I,Arthur Lobo Leite Lopes,nu-92-gu              
                username_obi,password_obi,compet_id,name,password_cms = line.split(',')
            except:
                continue
            print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            count += 1
        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")

