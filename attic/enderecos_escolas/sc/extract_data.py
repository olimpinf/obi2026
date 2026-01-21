#!/usr/bin/env python3

import csv
import pandas as pd
import os
import re
import sys
from io import StringIO

SHORT = ['emefei','eefmepja','emeief','emefi','emef','emebi','emei','em','ciep','etec de','etec','ctig','eieb','eief','eeb','eef','eem','ee','ud', 'cedup']
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
        if token in SHORT + ROMAN:
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
            elif token == 'publica':
                token = 'pública'
            elif token == 'sao':
                token = 'são'
            elif token == 'tecnica':
                token = 'técnica'
            elif token == 'tecnico':
                token = 'técnico'
            elif token == 'saude':
                token = 'saúde'
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

linenum = 0
for r in df.iterrows():
    linenum += 1
    if len(r[1])==0 or pd.isnull(r[1][1]):
        continue
    # comment out for municipal
    #if use_type and (tipo_escola not in [8,11,12,13,14,26,27,28,40,51]):
    #    continue


    name = r[1][1]
    email = r[1][9]
    try:
        email = email.lower()
    except:
        continue

    try:
        name = name.strip()
    except:
        name = ""
        
    try:
        email = email.strip()
    except:
        email = ""

    if not name or not email:
        continue

    if name.lower().find('penitenciaria') > 0:
        continue
    
    if name.lower().find('penitenciária') > 0:
        continue
    
    if name.lower().find('presidio') > 0:
        continue

    if name.lower().find('presídio') > 0:
        continue

    if name.lower().find('prisional') > 0:
        continue

    #try:
    #    name,type = name.split(',')
    #except:
    #    continue

    # tmp = []
    # prof = ""
    # de = ""
    # pres = type.split('-')
    # for pre in pres:
    #     prefixes = pre.split()
    #     for prefix in prefixes:
    #         if prefix in ['Prof', 'Profa', 'Dr', 'Dra']:
    #             prof = prefix + '.'
    #             continue
    #         if prefix == 'Dq':
    #             prof = 'Duque'
    #             continue
    #         if prefix == 'Ver':
    #             prof = 'Vereador'
    #             continue
    #         if prefix == 'Pref':
    #             prof = 'Prefeito'
    #             continue
    #         if prefix == 'Pres':
    #             prof = 'Presidente'
    #             continue
    #         if prefix == 'Pres':
    #             prof = 'Presidente'
    #             continue
    #         if prefix == 'Frei':
    #             prof = 'Frei'
    #             continue
    #         if prefix == 'Frei':
    #             prof = 'Frei'
    #             continue
    #         if prefix == 'Barao':
    #             prof = 'Barão'
    #             continue
    #         if prefix == 'Padre' or prefix == 'Pe':
    #             prof = 'Padre'
    #             continue
    #         if prefix == 'Madre':
    #             prof = 'Madre'
    #             continue
    #         if prefix == 'Dona':
    #             prof = 'Dona'
    #             continue
    #         if prefix == 'Dom':
    #             prof = 'Dom'
    #             continue
    #         if prefix == 'Dep':
    #             prof = 'Deputado'
    #             continue
    #         if prefix == 'Des':
    #             prof = 'Des.'
    #             continue
    #         if prefix == 'Mal':
    #             prof = 'Marechal'
    #             continue
    #         if prefix == 'Maj':
    #             prof = 'Major'
    #             continue
    #         if prefix == 'Mons':
    #             prof = 'Mons.'
    #             continue
    #         if prefix == 'Princ':
    #             prof = 'Princesa'
    #             continue
    #         if prefix == 'Marqes':
    #             prof = 'Marquês'
    #             continue
    #         if prefix == 'Jorn':
    #             prof = 'Jorn.'
    #             continue
    #         if prefix == 'Irma' or prefix == 'Ir':
    #             prof = 'Irmã'
    #             continue
    #         if prefix == 'Vovo':
    #             prof = 'Vovo'
    #             continue
    #         if prefix == 'Tia':
    #             prof = 'Tia'
    #             continue
    #         if prefix == 'Pastor':
    #             prof = 'Pastor'
    #             continue
    #         if prefix.lower() == 'de':
    #             de = 'de'
    #             continue
    #         if prefix.lower() == 'da':
    #             de = 'da'
    #             continue
    #         if prefix.lower() == 'do':
    #             de = 'do'
    #             continue
    #         if prefix in ['Papa', 'Vereador', 'Prefeito', 'Governador', 'Presidente']:
    #             prof = prefix
    #             continue
    #         if prefix == 'c':
    #             prefix = 'C'
    #         if prefix == 'Profis':
    #             prefix = ' Profiss.'
            
    #         tmp.append(prefix)
        
    # prefix = "".join(tmp)
    # prefix = prefix.strip()
    

    # if prefix.lower().find('pion') > 0:
    #     continue
    # if prefix.lower().find('caic') > 0:
    #     continue

    prefix = name.split()[0]
    
    if prefix.lower().find('creche') > 0:
        continue
    if prefix.lower() in ['cmei', 'cei', 'eei','cmeip', 'cmeid', 'pemei', 'crmei', 'preescei', 'ceja']:
        continue

    
    final = capitalize(name).strip()
    print(f"{final.strip()},{email},")
    
        
