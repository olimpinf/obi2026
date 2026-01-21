#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

kIntrod = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\usepackage{color}
\usepackage[a4paper, total={7in, 9in}]{geometry}
\\begin{document}
\setlength{\parindent}{0pt}

"""

kPresSentences = {	'i1': u'Iniciaremos a premiação com a Modalidade Iniciação Nível 1, para alunos até o sétimo ano (sexta série) do Ensino Fundamental',
				  	'i2': u'Passamos agora à Modalidade Iniciação Nível 2, para alunos até o nono ano (oitava série) do Ensino Fundamental',
				  	'pj': u'Passamos agora à premiação da Modalidade Programação Nível Júnior, para alunos até o nono ano (oitava série) do Ensino Fundamental',
				  	'p1': u'Passamos agora à premiação da Modalidade Programação Nível 1, para alunos até o segundo ano do ensino médio',
				  	'p2': u'Passamos agora à premiação da Modalidade Programação Nível 2, para alunos até o terceiro ano do ensino médio'}

kCats = [('Iniciação Nível 1', 'i1'), ('Iniciação Nível 2', 'i2'), ('Programação Nível Júnior', 'pj'), ('Programação Nível 1', 'p1'), ('Programação Nível 2', 'p2')]

kMedals = [u'Medalhas de Ouro', u'Medalhas de Prata', u'Medalhas de Bronze', u'Honra ao Mérito']

kAssistProfsMessage = """
Finalmente faremos um agradecimento especial aos professores e monitores que se dedicaram aos cursos e aos cuidados dos alunos.\\\\
Nós os chamaremos agora para entrega dos certificados de monitoria e para que recebam os merecidos aplausos:\\\\

Os Professores:
"""

kIOIResult = """
Estes alunos participaram também da Seletiva para a Olimpíada Internacional de Informática de 2023, que acontecerá em julho do ano que vem, em Cingapura. Os alunos realizaram provas diárias e a última delas terminou há alguns minutos. Os alunos selecionados são, em ordem alfabética:\\\\
\color{blue}\\textbf{Selecionados para Olimpiada Internacional de Informática}\color{black}
"""

kFinalSpeeches = """
Neste momento convidamos para fazer uso da palavra:\\\\
\color{red}\\textbf{(Tempo para discurso: até 3 minutos cada)}\color{black}\\
\\begin{itemize}
%\\item Prof. Dr. Munir Skaf, Pró-reitor de Pesquisa da Unicamp
%\\item Prof. Dr. Marcelo Duduchi, Diretor da Sociedade Brasileira de Computação (SBC)
\\item Prof. Dr. Rodolfo Jardim de Azevedo, Ex-Diretor do Instituto de Computação da Unicamp e Presidente da Univesp - Universidade Virtual do Estado de São Paulo
\\item Profa. Dra. Flavia Pisani, Coordenadora Acadêmica do TFC2022
\\item Prof. Dr. Ricardo de Oliveira Anido, Coordenador da OBI2022
\\end{itemize}
"""

kFinalMessage = """
Encerramos esta cerimônia, agradecendo a presença dos componentes da mesa de honra e da audiência.\\\\
\\textbf{Parabenizamos mais uma vez a todos os participantes e premiados.}
"""

def parseList(fileName):
	medalsIdx = 0
	ans = []
	with open("raw/%s.txt" % fileName, encoding='utf-8', mode='r') as f:
		for line in f:
			tokens = line.split('\t')
			if 'HM' in tokens:
				tokens.remove('HM')
			if len(tokens) == 1:
				medalsIdx = (medalsIdx + 1)%4
			else:
				entry = {'medal': kMedals[medalsIdx], 'group': tokens[0], 'rank': tokens[1], 'name': tokens[3], 'school': tokens[4], 'city': tokens[5], 'state': tokens[6]}
				ans.append(entry)
	return ans[::-1]

def parseRegList(fileName):
	ans = []
	with open("raw/%s.txt" % fileName, encoding='utf-8', mode='r') as f:
		for line in f:
			ans.append(line.rstrip())
	return ans

def genCatTex(cat, catId):
	ans = u"""
\color{blue}
\\textbf{%s}\\\\\\\\""" % kPresSentences[catId]

	l = parseList(catId)
	curMedal = u""
	shouldEnd = False
	idx = 0
	while idx < len(l):
		entry = l[idx]
		medal = entry['medal']
		if medal != curMedal:
			curMedal = medal
			if shouldEnd:
				ans += '\\end{itemize}\n'
				shouldEnd = False
			ans += u"""
\\textbf{\color{blue}Ganhadores de %s, \color{black}Modalidade %s}
\color{black}
""" % (medal, cat)
			ans += '\n\\begin{itemize}\n'
			shouldEnd = True

		cgroup = entry['group']
		ans += "\item\n"
		while idx < len(l) and l[idx]['group'] == cgroup:
			entry = l[idx]
			ans += "\\textbf{%sº lugar} - \\textbf{%s} – %s – %s/%s\n\n" % (entry['rank'], entry['name'], entry['school'], entry['city'], entry['state'])
			idx += 1
		ans += '\n'

	if shouldEnd:
		ans += '\\end{itemize}\n'

	return ans
	
def genListTex(fileName):
	ans = '\n\\begin{itemize}\n'
	l = parseRegList(fileName)
	for entry in l:
		ans += "\item %s\n" % entry
	ans += '\\end{itemize}\n'
	return ans

def main():
	ans = kIntrod
	for cat, catId in kCats:
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
	ans += '\end{document}'
	print(ans)

if __name__ == '__main__':
	#reload(sys)  
	#sys.setdefaultencoding('utf8')	
	main()
