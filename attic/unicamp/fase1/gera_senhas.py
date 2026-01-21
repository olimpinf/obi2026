#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\begin{document}
'''

template = r'''
\thispagestyle{empty}

\begin{center}
  {\Large \bf OBI2025 -- Fase 1 }
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

%%\noindent \textbf{Endereço}: \texttt{https://ps.provas.ic.unicamp.br}

\subsection*{Endereços}
%%\noindent Programação Nível Júnior: \texttt{https://pj.provas.ic.unicamp.br}\\
%%\noindent Programação Nível 1: \texttt{https://p1.provas.ic.unicamp.br}\\
\noindent Programação Nível 2: \texttt{https://oii.obi.org.bo}\\

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
        for i in range(10):
            print(lines[i])
            if i >= len(lines):
                break
            line = lines[i].split(',')
            if len(line) < 5:
                break

            username_obi,password_obi,compet_id,name,password_cms = line
            print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            count += 1
            i += 1

            # if i >= len(lines):
            #     break
            # line = lines[i].split(',')
            # try:
            #     username_obi,password_obi,compet_id,name,password_cms = line
            # except:
            #     break
            
            # print(r'\vspace*{5cm}', file=tex)
            # print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            # count += 1
            # i += 1

            print("\pagebreak", file=tex)

        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")
        
