#!/usr/bin/env python3

import csv
import pandas as pd
import os
import re
import sys
from io import StringIO

SHORT = ['emefei','eefmepja','emeief','emefi','emef','emebi','emei','em','ciep','etec de','etec','ctig']
LONG = ['col tec industrial','colegio tecnico de','colegio tecnico','colegio',
        'escola tecnica estadual','escola tecnica','escola de educacao infantil','escola',
        'educandario','instituto','centro educacional']
ROMAN = ['i','ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xx', 'xxi']

def capitalize(name):
    new_name = ''
    for token in name.split():
        token = token.strip()
        if not token:
            continue
        if token in ['de','da','do','das','dos','e']:
            new_name += ' ' + token
        elif token in SHORT + ROMAN:
            new_name += ' ' + token.upper()
        else:
            if token == 'colegio':
                token = 'colégio'
            elif token == 'coracao':
                token = 'coração'
            elif token == 'crianca':
                token = 'criança'
            elif token == 'dr':
                token = 'dr.'                
            elif token == 'dra':
                token = 'dra.'                
            elif token == 'educacao':
                token = 'educação'                
            elif token == 'educacandario':
                token = 'educandário'          
            elif token == 'escolastica':
                token = 'escolástica'
            elif token == 'joao':
                token = 'joão'
            elif token == 'jose':
                token = 'josé'
            elif token == 'medio':
                token = 'médio'
            elif token == 'prof':
                token = 'prof.'
            elif token == 'profa':
                token = 'profa.'
            elif token == 'sao':
                token = 'são'
            elif token == 'tecnica':
                token = 'técnica'
            elif token == 'tecnico':
                token = 'técnico'
            elif token == 'tupa':
                token = 'tupã'
                
            new_name += ' ' + token.capitalize()
    return new_name

def clean_institution(name):
    for institution in LONG + SHORT:
        pat = "(.*)(\s+|^)("+ institution +")(\s+|$)(.*)"
        match = re.search(pat, name)
        if match:
            return (institution, f"{match.groups()[0].strip()} {match.groups()[4].strip()}")
    return ("", name)

def clean_religious(name):
    for institution in ['adventista de', 'adventista']:
        pat = "(.*)(\s+|^)("+ institution +")(\s+|$)(.*)"
        match = re.search(pat, name)
        if match:
            return (institution, f"{match.groups()[0].strip()} {match.groups()[4].strip()}")
    return ("", name)


def clean_prefix(name):
    for prefix in ['dra','dr','madre','padre','profa','prof','vereador','vereadora','prefeito','prefeita','papa','professor','professora']:
        pat = "(.*)(\s+|^)("+ prefix +")(\s+|$)(.*)"
        match = re.search(pat, name)
        if match:
            return f"{prefix} {match.groups()[0].strip()} {match.groups()[4].strip()}"
    return name

def clean(name):
    institution,other_name = clean_institution(name.lower())
    other_name = clean_prefix(other_name)
    new_name = f"{institution} {other_name}"
    new_name = capitalize(new_name)
    return new_name


#name = "EMEIEF PROF IRANI PAES DE OLIVEIRA"
# name = "FUNDACAO BRADESCO ESCOLA DE EDUCACAO BASICA E PROFISSIONAL"
# name = clean(name).strip()
# print(name)
# sys.exit(0)

df = pd.read_excel(sys.argv[1])

use_type = True
if sys.argv[1] == 'FEDERAL.xlsx' or sys.argv[1] == 'MUNICIPAL.xlsx':
    use_type = False
    
linenum = 0
for r in df.iterrows():
    linenum += 1
    if len(r[1])==0 or pd.isnull(r[1][0]):
        continue
    try:
        tipo_escola = int(r[1][4])
    except:
        tipo_escola = 0
    # comment out for municipal
    if use_type and (tipo_escola not in [8,11,12,13,14,26,27,28,40,51]):
        continue

    if pd.isnull(r[1][20]):
        continue

    name = r[1][7]
    email = r[1][20]
    if r[1][27]!=0 or r[1][28]!=0 or r[1][29]!=0 or r[1][30]!=0 or r[1][31]!=0 or r[1][32]!=0 or \
       r[1][33]!=0 or r[1][34]!=0 or r[1][35]!=0 or r[1][36]!=0:
        name = clean(name).strip()
        print(f"{name},{email.lower()},")

        
