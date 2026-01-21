#!/usr/bin/env python3
import pandas as pd
from io import StringIO

df_escolas_ini = pd.read_csv('ini/planilha.csv', dtype={'school_city': str, 'school_state': str, 'school_id': int, 'school_name': str, 'motivo': int})
df_escolas_prog = pd.read_csv('prog/planilha.csv')


df_escolas_ini = df_escolas_ini[(df_escolas_ini['motivo'] > 1) & (df_escolas_ini['motivo'] != 4)]
df_escolas_prog = df_escolas_prog[(df_escolas_prog['motivo'] > 1) & (df_escolas_prog['motivo'] != 4)]

grouped_df_escolas_ini = df_escolas_ini.groupby(['school_id'])
grouped_df_escolas_prog = df_escolas_prog.groupby(['school_id'])

# ------- Iniciacao -------
print('----------------------- INICIACAO ----------------------- ')
print('{', end='')
for escola_ini in grouped_df_escolas_ini:
    print('                ', escola_ini[0], end=": [", sep='')
    print(",".join("['" + escola_ini[1]['school_city'] + "','" + escola_ini[1]['school_state'] + "']"), "],", sep='')
print('}')

# ------- Programacao -------
print('----------------------- PROGRAMACAO ----------------------- ')
print('{', end='')
for escola_prog in grouped_df_escolas_prog:
    print('                ', escola_prog[0], end=": [", sep='')
    print(",".join("['" + escola_prog[1]['school_city'] + "','" + escola_prog[1]['school_state'] + "']"), "],", sep='')
print('}')
