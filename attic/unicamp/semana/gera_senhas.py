#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\begin{document}
'''

template = r'''
\thispagestyle{empty}

\begin{center}
  {\huge \bf OBI2025 -- Semana Olímpica }\\[15pt]
{\large \bf {%s}}
\end{center}
\vspace{0.2cm}

\subsection*{Competidor}
{\large %s}

\subsection*{Computador}
\noindent \textbf{Nome de usuário}: \texttt{%s}\\
\noindent \textbf{Senha}: \texttt{%s}

\subsection*{Prova - CMS}
\noindent \textbf{Nome de usuário}: \texttt{%s}\\
\noindent \textbf{Senha}: \texttt{%s}

\subsection*{Endereços}

%%\noindent MOJ: \texttt{https://moj.naquadah.com.br/new/treino/?searchtag=obi}\\
%%\noindent Programação Nível Júnior: \texttt{https://pj.provas.ic.unicamp.br}\\
%%\noindent Programação Nível 1: \texttt{https://p1.provas.ic.unicamp.br}\\
\noindent Programação Nível 2: \texttt{https://p2.provas.ic.unicamp.br}\\
%%\noindent Programação Nível Sênior: \texttt{https://ps.provas.ic.unicamp.br}\\
'''

tail = r'''
\end{document}
'''


if len(sys.argv) != 2:
    print("Usage: {} filename".format(sys.argv[0]))
    sys.exit(0)

filename = sys.argv[1]

LEVEL_NAME = {
    'PJ': 'Programação Nível Júnior',
    'P1': 'Programação Nível 1',
    'P2': 'Programação Nível 2',
    'I1': 'Iniciação Nível 1',
    'I2': 'Iniciação Nível 2',
}
with open(filename, "r") as f:

    count,i = 0,0
    with open("senhas.tex", "w") as tex:
        print(header, file=tex)
        lines = f.readlines()
        for i in range(len(lines)):
            
            if i >= len(lines):
                break
            line = lines[i].strip().split(',')
            if len(line) < 5:
                break

            username_obi,password_obi,name,compet_id,password_cms,level = line

            if name =='':
                continue
            if level not in ('P2'):
                continue

            print(lines[i])
            
            #level_name = LEVEL_NAME[int(level)]
            level_name = LEVEL_NAME[level]
            print(template % (level_name,name,username_obi,password_obi,compet_id,password_cms), file=tex)
            count += 1


            # if i >= len(lines):
            #     break
            # line = lines[i].split(',')
            # try:
            #     username_obi,password_obi,compet_id,name,password_cms = line
            # except:
            #     break
            
            # print(r'\vspace*{0.5cm}', file=tex)
            # print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
            # count += 1
            # i += 1

            print(r"\pagebreak", file=tex)

        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")
        
