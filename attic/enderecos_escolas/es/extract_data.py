#!/usr/bin/env python3

import csv
import pandas as pd
import os
import re
import sys
from io import StringIO

SHORT = [
    'CEEFMTI',
    'CEEJA',
    'CEEMTI',
    'CEET',
    'CEIER',
    'EE',
    'EE',
    'NAAHS',
    'EEE',
    'EEEF',
    'EEEFM',
    'EEEM',
    'EEPEF',
    'EEUEF',
    'PRÉ',
    'EEIEFM',
    'EEEFMTI',
    'PRÉ-ENEM',
    'PRE-ENEM',
    'PRE',
    'PRÉ',
    'ENEM'
    ]
LONG = ['col tec industrial','colegio tecnico de','colegio tecnico','colegio',
        'escola tecnica estadual','escola tecnica','escola de educacao infantil','escola',
        'educandario','instituto','centro educacional']
ROMAN = ['i','ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x', 'xi', 'xii', 'xiii', 'xx', 'xxi', 'xxiii', 'xxiv', 'xxv', 'xxx']

def capitalize(name):
    name = name.lower()
    new_name = ''
    for token in name.split():        
        token = token.strip()
        if not token:
            continue
        if token.upper() in SHORT:
            new_name += ' ' + token.upper()
        elif token in ROMAN:
            new_name += ' ' + token.upper()
        elif token in ['de','da','do','das','dos','e']:
            new_name += ' ' + token
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

df = pd.read_csv(sys.argv[1],delimiter=';')

linenum = 0
for r in df.iterrows():
    linenum += 1
    if len(r[1])==0 or pd.isnull(r[1][0]):
        continue

    # comment out for municipal
    #if use_type and (tipo_escola not in [8,11,12,13,14,26,27,28,40,51]):
    #    continue


    name = r[1][3]
    email = r[1][12]
    try:
        email = email.lower()
    except:
        continue

    if name.lower().find('ed esp') > 0:
        continue

    name = name.strip()

    final = capitalize(name).strip()
    print(f"{final.strip()},{email},")
    
        
