#!/usr/bin/env python3

header = '''title: Quadro de Medalhas - CIIC2020
template:flatpages_competicoes.html
<h1>Quadro de Medalhas <br/> Competição Iberoamericana de Informática e Computação - CIIC2020</h1>

<p><center>
<img src="/static/img/medalhinha_ouro.gif">=Medalha de Ouro,
<img src="/static/img/medalhinha_prata.gif">=Medalha de Prata,<br>
<img src="/static/img/medalhinha_bronze.gif">=Medalha de Bronze

<table class="simple"> 
<tr class="row-header">
<td align="center" colspan="2">Classif.</td>
<td align="center">Pontos</td>
<td>Nome</td>
<td>País</td>
</tr>
'''

entry = '''
<tr class="row-{}">
<td><img src="/static/img/medalhinha_xxx.gif"></td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
<td>{}</td>
</tr>
'''

with open("ciic2020.csv","r") as f:
    data = f.readlines()

print(header)

color = 'dark'
for line in data:
    if color == 'dark':
        color = 'light'
    else:
        color = 'dark'
    tks = line.split(',')
    print(entry.format(color,tks[0],tks[2],tks[1],tks[3].strip()))
