#!/usr/bin/env python3

import os, sys, random, string

header =  r'''\documentclass{article}
\begin{document}
'''

template = r'''
\begin{center}
  {\Large \bf OBI2023 -- Seletiva - %s }
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

def make_password(syllables=2, add_number=True, separator='-'):
    """Alternate random consonants & vowels creating decent memorable passwords                                                                                                         
    """
    FORBIDDEN = ['cu','ku','pu','fu','fo','bo']
    rnd = random.SystemRandom()
    s = string.ascii_lowercase
    vowels = 'aeiu'
    spec = 'hloqwy' # avoid these
    consonants = ''.join([x for x in s if x not in vowels+spec])
    tmp = ''
    while len(tmp)//2 < syllables//2:
        s = ''.join([rnd.choice(consonants)+rnd.choice(vowels)])
        if s not in FORBIDDEN:
            tmp += s

    pwd = tmp #tmp.title()
    pwd += separator # just for readability

    if add_number:
        pwd += str(rnd.choice(range(2,10)))+str(rnd.choice(range(2,10))) # avoid digits 0,1
    tmp = ''
    while len(tmp)//2 < syllables - syllables//2:
        s = ''.join([rnd.choice(consonants)+rnd.choice(vowels)])
        if s not in FORBIDDEN:
            tmp += s

    pwd += separator # just for readability
    pwd += tmp # tmp.title()

    return pwd



if len(sys.argv) != 2:
    print("Uso: {} rotulo\n\tsenhas_ic deve ter duas colunas: usuário e senha.\n\talunos.csv deve ter três colunas: ID e nome".format(sys.argv[0]))
    sys.exit(0)

label = sys.argv[1]

with open('senhas_ic.csv') as f:
    lines_passwords = f.readlines()

with open("alunos.csv", "r") as f:
    lines_names = f.readlines()

lines = []
for i in range(len(lines_names)):
    password = make_password()
    line_name = lines_names[i].strip()
    password_ic = lines_passwords[i].strip()
    password = make_password()
    line = f"{password_ic},{line_name},{password}"
    lines.append(line)

# write cms password file
with open("senhas_cms.csv","w") as f:
    for line in lines:
        columns = line.split(',')
        print(",".join(columns[2:]), file=f)

# write tex file

count = 0
with open("senhas.tex", "w") as tex:
    print(header, file=tex)
    for line in lines:
        columns = line.split(',')
        #print(template % (name,username_obi,password_obi,compet_id,password_cms), file=tex)
        
        print(template % (label,columns[3],columns[0],columns[1],columns[2],columns[4]), file=tex)
        count += 1
        print(tail, file=tex)
        
print('generated',count)
if count > 0:
    os.system("pdflatex senhas")

os.system("rm -rf *aux *log")
    
