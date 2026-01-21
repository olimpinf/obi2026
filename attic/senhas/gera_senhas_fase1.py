#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\pagestyle{empty}
\begin{document}
'''

template = r'''
\begin{center}
  {\Large \bf OBI2024 -- Fase 1 }
\end{center}
\vspace{0.3cm}

\subsection*{%s}

\noindent \textbf{Nome de usuário}: \texttt{%s}
\noindent \textbf{Senha}: \texttt{%s}
\noindent \textbf{Endereço}: \texttt{http://ps.provas.ic.unicamp.br}

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
            try:
                username_obi,password_obi,name,level = line.split(',')
            except:
                continue
            print(template % (name,level,username_obi,password_obi), file=tex)
            count += 1
            if count % 3 == 0:
                print(r"\pagebreak",file=tex)
            else:
                print(r"\vspace*{5cm}",file=tex)
                
        print(tail, file=tex)
            
    print('generated',count)
    if count > 0:
        os.system("pdflatex senhas")
        
