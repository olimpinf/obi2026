#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from importlib import reload

kIntrod = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{color}
\usepackage[a4paper, total={7in, 9in}]{geometry}
\begin{document}
\setlength{\parindent}{0pt}

\begin{center}
    \textbf{
        UNIVERSIDADE ESTADUAL DE CAMPINAS\\
        CERIMONIAL\\
        \bigskip
         PREMIAÇÃO DA OLIMPÍADA BRASILEIRA DE INFORMÁTICA\\
        INSTITUTO DE COMPUTAÇÃO\\
        DIA – 05 DE DEZEMBRO DE 2025\\
        HORÁRIO: 19H00 ÀS 20H30\\
        IC - Unicamp – CAMPINAS/SP 
    }
\end{center}

\textbf{Mestre de Cerimônia:}\
Boa noite a todos!\
\textbf{Sejam bem vindos à Cerimônia de Premiação da Vigésima Quinta Olimpíada Brasileira de Informática.}\\
\color{blue}Este evento é promovido pela Sociedade Brasileira de Computação. Em sua 27ª edição, a OBI foi organizada pelo Instituto de Computação da Unicamp (IC) sob a Coordenação do Prof. Dr. Ricardo de Oliveira Anido.\\
\color{black}
Convidamos para compor a mesa de honra desta Cerimônia as seguintes autoridades:
\begin{itemize}
%\item \textbf{Prof. Dr. Munir Skaf}\\\\
%Pró-reitor de Pesquisa da Unicamp\\\\
%Professor Titular do Instituto de Química da Unicamp

%\item \textbf{Prof. Dr. Marcelo Duduchi}\\\\
%Diretor da Sociedade Brasileira de Computação (SBC)

\item \textbf{Prof. Dr. Rodolfo Jardim de Azevedo}\\
Ex-Diretor do Instituto de Computação da Unicamp e co-coordenador da Olimpíada Brasileira de Informática 2025.
\item \textbf{Prof. Dr. Ricardo de Oliveira Anido}\\
Professor do Instituto de Computação da Unicamp e \\
Coordenador da Olimpíada Brasileira de Informática 2025
\end{itemize}


Com a palavra o Prof. Dr. Ricardo de Oliveira Anido, professor do Instituto de Computação da Unicamp e Coordenador da OBI 2025.\\
\color{red}\textbf{(Breve discurso de abertura)}\color{black}\\

Faremos neste momento a chamada para a premiação dos alunos, que deverão apresentar-se à frente do palco, para receberem suas medalhas e certificados a serem entregues pelos componentes da mesa.\\
\color{red}\textbf{(Cada slide representa um conjunto de alunos que será chamado simultaneamente ao palco)}\color{black}\\
"""

kPresSentences = {      'i1': u'Iniciaremos a premiação com a Modalidade Iniciação Nível 1, para alunos até o sétimo ano do Ensino Fundamental',
                                        'i2': u'Passamos agora à Modalidade Iniciação Nível 2, para alunos até o nono ano do Ensino Fundamental',
                                        'pj': u'Passamos agora à premiação da Modalidade Programação Nível Júnior, para alunos até o nono ano do Ensino Fundamental',
                                        'p1': u'Passamos agora à premiação da Modalidade Programação Nível 1, para alunos até o segundo ano do ensino médio',
                                        'p2': u'Passamos agora à premiação da Modalidade Programação Nível 2, para alunos até o terceiro ano do ensino médio'}

kCats = [('Iniciação Nível 1', 'i1'), ('Iniciação Nível 2', 'i2'), ('Programação Nível Júnior', 'pj'), ('Programação Nível 1', 'p1'), ('Programação Nível 2', 'p2')]

kMedals = [u'Medalhas de Ouro', u'Medalhas de Prata', u'Medalhas de Bronze', u'Honra ao Mérito']

kAssistProfsMessage = r"""
Finalmente faremos um agradecimento especial aos professores e monitores que se dedicaram aos cursos e aos cuidados dos alunos.\\
Nós os chamaremos agora para entrega dos certificados de monitoria e para que recebam os merecidos aplausos:\\

Os Professores:
"""

kIOIResult = r"""
Estes alunos participaram também da Seletiva para a Olimpíada Internacional de Informática de 2025, que acontecerá em agosto do ano que vem, no Uzbequistão. Os alunos realizaram provas diárias e a última delas terminou há alguns minutos. Os alunos selecionados são, em ordem alfabética:\\\\
\color{blue}\textbf{Selecionados para Olimpiada Internacional de Informática}\color{black}
"""

kFinalSpeeches = r"""
Neste momento convidamos para fazer uso da palavra:\\
\color{red}\textbf{(Tempo para discurso: até 3 minutos cada)}\color{black}\\
\begin{itemize}
%\\item Prof. Dr. Munir Skaf, Pró-reitor de Pesquisa da Unicamp
%\\item Prof. Dr. Marcelo Duduchi, Diretor da Sociedade Brasileira de Computação (SBC)
\item Prof. Dr. Rodolfo Jardim de Azevedo, Ex-Diretor do Instituto de Computação da Unicamp e co-coordenador da OBI2025
%%\\item Profa. Dra. Flavia Pisani, Coordenadora Acadêmica do TFC2022
\item Prof. Dr. Ricardo de Oliveira Anido, Coordenador da OBI2025
\end{itemize}
"""

kFinalMessage = """
Encerramos esta cerimônia, agradecendo a presença dos componentes da mesa de honra e da audiência.\\\\
\textbf{Parabenizamos mais uma vez a todos os participantes e premiados.}
"""

def parseList(fileName):
        print("********** in parseList",fileName,file=sys.stderr)
        medalsIdx = 0
        ans = []
        with open("raw/%s.txt" % fileName, encoding='utf-8', mode='r') as f:
                for line in f:
                        print(line,file=sys.stderr)
                        tokens = line.split(',')
                        if 'HM' in tokens:
                                tokens.remove('HM')
                        if len(tokens) == 1:
                                print("=========== len(tokens)==1",file=sys.stderr)
                                medalsIdx = (medalsIdx + 1)%4
                        else:
                                entry = {'medal': kMedals[medalsIdx], 'group': tokens[0], 'rank': tokens[1], 'name': tokens[3], 'school': tokens[4], 'city': tokens[5], 'state': tokens[6]}
                                ans.append(entry)
                                print("========== appending", entry,file=sys.stderr)
        return ans[::-1]

def parseRegList(fileName):
        ans = []
        with open("raw/%s.txt" % fileName, encoding='utf-8', mode='r') as f:
                for line in f:
                        ans.append(line.rstrip())
        print(ans,file=sys.stderr)
        return ans

def genCatTex(cat, catId):
        ans = r"""
\color{blue}
\textbf{%s}\\\\\\""" % kPresSentences[catId]

        l = parseList(catId)
        curMedal = ""
        shouldEnd = False
        idx = 0
        while idx < len(l):
                entry = l[idx]
                print(entry,file=sys.stderr)
                medal = entry['medal']
                if medal != curMedal:
                        curMedal = medal
                        if shouldEnd:
                                ans += r'''
                                \end{itemize}'''
                                shouldEnd = False
                        ans += r"""
\textbf{\color{blue}Ganhadores de %s, \color{black}Modalidade %s}
\color{black}
""" % (medal, cat)
                        ans += r'''
                        \begin{itemize}'''
                        shouldEnd = True

                cgroup = entry['group']
                while idx < len(l) and l[idx]['group'] == cgroup:
                        entry = l[idx]
                        ans += "\\item \\textbf{%sº lugar} - \\textbf{%s} – %s – %s/%s\n\n" % (entry['rank'], entry['name'], entry['school'], entry['city'], entry['state'])
                        idx += 1
                ans += '\n'

        if shouldEnd:
                ans += '\\end{itemize}\n'

        return ans
        
def genListTex(fileName):
        ans = r'''
        \begin{itemize}
        '''
        l = parseRegList(fileName)
        for entry in l:
                ans += " \\item %s\n" % entry
        ans += r'''\end{itemize}'''
        return ans

def main():
        ans = kIntrod
        for cat, catId in kCats:
                print(cat,catId,file=sys.stderr)
                tex = genCatTex(cat, catId)
                ans += tex
        ans += "\\bigskip\n"
        ans += kIOIResult
        ans += genListTex('ioi')
        ans += "\\bigskip\n"
        ans += kFinalSpeeches
        ans += "\\bigskip\n"
        ans += kAssistProfsMessage
        ans += genListTex('professors')
        ans += "\nOs Monitores:\n"
        ans += genListTex('assistants')
        ans += "\\bigskip\n"
        ans += kFinalMessage
        ans += r'\end{document}'
        print(ans)

if __name__ == '__main__':
        reload(sys)  
        main()
