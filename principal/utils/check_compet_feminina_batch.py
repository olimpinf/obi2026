import csv
import pandas as pd
import os
import re
from datetime import date
from io import StringIO
import math

from principal.models import (LEVEL, LEVEL_CFOBI, SCHOOL_YEARS, SCHOOL_YEARS_CFOBI, SEX_F, SEX_O, CF,
                              Compet, validate_compet_level, validate_username, validate_username_compet)
from principal.models import (CompetCfObi)
from principal.utils.utils import (caps, csv_sniffer, format_compet_id, capitalize_name)
from obi.settings import YEAR

# Column IDs
COL_COMPET_ID = 0
COL_COMPET_TYPE_OBI = 1
COL_COMPET_TYPE_CFOBI = 2
COL_COMPET_NAME = 3
COL_COMPET_BIRTH_DATE = 4
COL_COMPET_SEX = 5
COL_COMPET_YEAR = 6
COL_COMPET_CLASS = 7
COL_COMPET_EMAIL = 8

NUM_COLS = 9

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line


def format_line(row, delimiter):
    tokens = []
    for i in range(len(row)):
        if pd.isnull(row.iloc[i]) or pd.isna(row.iloc[i]) or pd.isna(row.iloc[i] == ''):
            tokens.append('')
        elif type(row.iloc[i]) == float:
            tokens.append(int(row.iloc[i]))
        elif type(row.iloc[i]) == pd._libs.tslibs.timestamps.Timestamp:
            tokens.append(row.iloc[i].strftime('%d/%m/%Y'))
        else:
            tokens.append(str(row.iloc[i]))
    return '{}'.format(delimiter).join(tokens)


def check_compet_feminina_batch(f, school):
        tmp = Compet.objects.filter(compet_school_id=school.school_id)
        existing_compets = []

        for c in tmp:
            existing_compets.append(c.compet_name.lower())

        msg = ''
        errors = []
        validated_compets=[]
        validated_compets_cfobi=[]

        if f.multiple_chunks(): # default is 2.5 MB
            msg = 'Arquivo muito grande (deve ser no máximo de 2.5MB).'
            return msg, errors, validated_compets, validated_compets_cfobi

        # f.read() does not work...
        for chunk in f.chunks():
            decoded_file = chunk

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

        ext = os.path.splitext(f.name)[1].lower()[1:]
        if ext == 'csv':
            try:
                the_file = StringIO(decoded_file.decode(),newline=None)
            except:
                try:
                    the_file = StringIO(decoded_file.decode('latin1'),newline=None)
                except:
                    try:
                        the_file = StringIO(decoded_file.decode('macroman'),newline=None)
                    except:
                        msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                        return msg,errors,validated_compets, validated_compets_cfobi

            try:
                df = pd.read_csv(the_file)
            except:
                msg = 'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras.'
                return msg, errors, validated_compets, validated_compets_cfobi
        elif ext == 'xls':
            try:
                df = pd.read_excel(decoded_file)
            except:
                msg = 'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras.'
                return msg, errors, validated_compets, validated_compets_cfobi
        elif ext == 'xlsx':
            try:
                df = pd.read_excel(decoded_file, engine='openpyxl')
            except:
                msg = 'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras.'
                return msg, errors, validated_compets, validated_compets_cfobi
        else:
            msg = 'Arquivo deve estar no formato xls, xlsx ou csv.'
            return msg, errors, validated_compets, validated_compets_cfobi

        linenum = 0
        delimiter = ','
        new_compets=[]

        for idx, row in df.iterrows():

            formatted_line = format_line(row, delimiter)
            linenum += 1

            if row.isnull().all()  or row.replace("", pd.NA).isna().all():
                # all columns are empty
                continue

            if pd.isna(row.iloc[COL_COMPET_ID]) or row.iloc[COL_COMPET_ID] == "":
                is_new_compet = True
            else:
                is_new_compet = False
                compet_id_full = row.iloc[COL_COMPET_ID].strip()
                try:
                    compet = Compet.objects.get(compet_id_full=compet_id_full)
                except:
                    compet = None
                    errors.append(Error(linenum,'Número de inscrição incorreto', formatted_line))
                    continue
            #elif len(r) < NUM_COLS:
            #    errors.append(Error(linenum,'Formato incorreto, coluna faltando', formatted_line))
            #    continue

            # Read mandatory fields
            try:
                compet_type_cfobi=row.iloc[COL_COMPET_TYPE_CFOBI].strip().upper()
            except:
                errors.append(Error(linenum,'Formato incorreto na coluna Nível CF-OBI', formatted_line))
                continue


            if pd.isna(row.iloc[COL_COMPET_NAME]) or row.iloc[COL_COMPET_NAME] == "":
                if is_new_compet:
                    compet_name = ''
                    errors.append(Error(linenum,'Falta nome de competidora', formatted_line))
                else:
                    compet_name = capitalize_name(compet.compet_name)
            else:
                try:
                    tmp_name=capitalize_name(row.iloc[COL_COMPET_NAME].strip())
                except:
                    errors.append(Error(linenum,'Formato incorreto na coluna Nome', formatted_line))
                    tmp_name = ''
                if is_new_compet:
                    compet_name = tmp_name
                else:
                    if tmp_name != capitalize_name(compet.compet_name):
                        errors.append(Error(linenum,'Nome é diferente de competidora com esse número de inscrição', formatted_line))
                    compet_name = tmp_name

            if pd.isna(row.iloc[COL_COMPET_BIRTH_DATE]) or row.iloc[COL_COMPET_BIRTH_DATE] == "":
                if is_new_compet:
                    errors.append(Error(linenum,'Formato incorreto na coluna Data de Nascimento', formatted_line))
                    continue

            compet_birth_date = ''
            try:
                if type(row.iloc[COL_COMPET_BIRTH_DATE]) == pd._libs.tslibs.timestamps.Timestamp:
                    compet_birth_date = row.iloc[COL_COMPET_BIRTH_DATE].strftime('%d/%m/%Y')
                else:
                    print("row.iloc[COL_COMPET_BIRTH_DATE]",row.iloc[COL_COMPET_BIRTH_DATE])
                    compet_birth_date = row.iloc[COL_COMPET_BIRTH_DATE].strip()
            except:
                if is_new_compet:
                    errors.append(Error(linenum,'Formato incorreto na coluna Data de Nascimento', formatted_line))
                    continue
                else:
                    compet_birth_date = compet.compet_birth_date.strftime('%d/%m/%Y')

            try:
                compet_sex=row.iloc[COL_COMPET_SEX].strip().upper()
            except:
                if is_new_compet:
                    errors.append(Error(linenum,'Formato incorreto na coluna Gênero', formatted_line))
                    continue
                else:
                    compet_sex = compet.compet_sex

            try:
                compet_year=row.iloc[COL_COMPET_YEAR].strip()
            except:
                if is_new_compet:
                    errors.append(Error(linenum,'Formato incorreto na coluna Ano Escola', formatted_line))
                    continue
                else:
                    compet_year = compet.compet_year

            try:
                compet_class=str(row.iloc[COL_COMPET_CLASS]).strip()
                compet_class = compet_class[:8] # 8 is the character limit
            except:
                if is_new_compet:
                    errors.append(Error(linenum,'Formato incorreto na coluna Turma Escola', formatted_line))
                continue

            try:
                compet_email=row.iloc[COL_COMPET_EMAIL].strip()
            except:
                compet_email=None

            if compet_email:
                if not EMAIL_REGEX.match(compet_email):
                    errors.append(Error(linenum,'Formato incorreto na coluna Email', formatted_line))
                    continue

            # Validate mandatory fields
            try:
                compet_type_cfobi = LEVEL[compet_type_cfobi]
            except:
                errors.append(Error(linenum,'Nível CF-OBI inválido', formatted_line))
                continue

            if compet_type_cfobi not in LEVEL_CFOBI:
                errors.append(Error(linenum,'Nível CF-OBI inválido para participação na CF-OBI', formatted_line))
                continue

            if compet_year not in SCHOOL_YEARS_CFOBI:
                errors.append(Error(linenum,'Ano Escola inválido para participação na CF-OBI', formatted_line))
                continue

            res_validate_type_cfobi = validate_compet_level(compet_type_cfobi, compet_year, school.school_type)

            if res_validate_type_cfobi:
                errors.append(Error(linenum, res_validate_type_cfobi, formatted_line))
                continue

            if len(compet_name) == 0:
                errors.append(Error(linenum,'Falta nome de competidora', formatted_line))
                continue
            elif compet_name.lower() in new_compets:
                errors.append(Error(linenum,'Nome de competidora repetido neste arquivo', formatted_line))
                continue
            else:
                new_compets.append(compet_name.lower())

            try:
                day, month, year=[int(x) for x in compet_birth_date.split('/')]
                year_limit = YEAR - 8
                if day < 1 or day > 31 or month < 1 or month > 12 or year < 1900 or year > year_limit: #TODO: add year range to settings and use it here and on forms.
                    errors.append(Error(linenum,'Data de nascimento inválida (usar formato: dia/mes/ano)', formatted_line))
                    continue
                compet_birth_date = date(year, month, day)
            except:
                errors.append(Error(linenum,'Data de nascimento inválida (usar formato: dia/mes/ano)', formatted_line))
                continue

            if compet_sex not in [SEX_F, SEX_O]:
                errors.append(Error(linenum,'Gênero inválido para participação na CF-OBI', formatted_line))
                continue

            if len(compet_year)==0:
                errors.append(Error(linenum,'Coluna Ano Escolar não pode ser vazia', formatted_line))
                continue

            if len(compet_class)==0:
                errors.append(Error(linenum,'Coluna Turma Escolar não pode ser vazia', formatted_line))
                continue

            # Read optional fields
            try:
                compet_id_full=str(row.iloc[COL_COMPET_ID]).strip().upper()
            except:
                errors.append(Error(linenum,'Formato incorreto na coluna Num. Inscr.', formatted_line))
                continue

            try:
                compet_type_obi=str(row.iloc[COL_COMPET_TYPE_OBI]).strip().upper()
            except:
                errors.append(Error(linenum,'Formato incorreto na coluna Nível OBI', formatted_line))
                continue

            # Validate optional fields
            if compet_id_full != 'NAN' and compet_type_obi != 'NAN':
                try:
                    compet_type_obi = LEVEL[compet_type_obi]
                except:
                    errors.append(Error(linenum,'Nível OBI inválido', formatted_line))
                    continue

                if compet_type_obi in LEVEL_CFOBI and compet_type_obi != compet_type_cfobi:
                    errors.append(Error(linenum, 'Competidora já inscrita na Modalidade Programação deve participar do mesmo nível na CF-OBI', formatted_line))
                    continue

                try:
                    compet_id = int(compet_id_full.split('-')[0])
                    c = Compet.objects.get(compet_id=compet_id, compet_type=compet_type_obi, compet_year=compet_year)
                except:
                    errors.append(Error(linenum, 'Competidora ' + compet_id_full + ' não encontrada, verificar se todos os dados da linha estão corretos', formatted_line))
                    continue

                if getattr(c, 'competcfobi', None) is not None: # Already registered for CF-OBI.
                    errors.append(Error(linenum, 'Competidora ' + compet_id_full + ' já está inscrita na CF-OBI', formatted_line))
                    continue
            else:
                if compet_name.lower() in existing_compets:
                    errors.append(Error(linenum,'Competidora já foi inscrita anteriormente, informar Num. Inscr. e Nível OBI', formatted_line))
                    continue

                c = Compet(compet_type=CF, compet_name=compet_name, compet_birth_date=compet_birth_date,
                           compet_sex=compet_sex, compet_year=compet_year, compet_class=compet_class,
                           compet_email=compet_email, compet_school_id=school.school_id)

                validated_compets.append(c)

            c_cfobi = CompetCfObi(compet=c, compet_type=compet_type_cfobi)

            validated_compets_cfobi.append(c_cfobi)

        return msg, errors, validated_compets, validated_compets_cfobi


def check_compet_feminina_batch_password(f,school):
        tmp = Compet.objects.filter(compet_school_id=school.school_id)
        existing_compets = []
        for c in tmp:
            existing_compets.append(c.compet_name.lower())
        msg = ''
        errors = []
        validated_compets=[]
        school_passwords=[]

        if f.multiple_chunks(): # default is 2.5 MB
            msg = 'Arquivo muito grande (deve ser no máximo de 2.5MB).'
            return msg,errors,validated_compets
        # f.read() does not work...
        for chunk in f.chunks():
            decoded_file = chunk

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        ext = os.path.splitext(f.name)[1].lower()[1:]
        if ext == 'csv':
            try:
                the_file = StringIO(decoded_file.decode(),newline=None)
            except:
                try:
                    the_file = StringIO(decoded_file.decode('latin1'),newline=None)
                except:
                    try:
                        the_file = StringIO(decoded_file.decode('macroman'),newline=None)
                    except:
                        msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                        return msg,errors,validated_compets
            df = pd.read_csv(the_file)
        elif ext == 'xls':
            df = pd.read_excel(decoded_file)
        elif ext == 'xlsx':
            df = pd.read_excel(decoded_file, engine='openpyxl')
        else:
            msg = 'Arquivo deve estar no formato xls, xlsx ou csv.'
            return msg,errors,validated_compets

        linenum = 0
        delimiter = ','
        new_compets=[]
        for r in df.iterrows():
            linenum += 1
            if len(r[1])==0:
                continue
            elif len(r[1]) != 8:
                errors.append(Error(linenum,'número de colunas incorreto',format_line(r, delimiter)))
                continue
            if r[1][1].strip().lower()=='nome':
                continue
            ok_row=True
            msg_row=''
            try:
                compet_type=r[1][0].strip().upper()
                compet_name=caps(r[1][1].strip())
                compet_birth_date=r[1][2].strip()
                compet_sex=r[1][3].strip()
                compet_year=r[1][4].strip()
                compet_class=r[1][5].strip()
                password=r[1][7].strip()
            except:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            try:
                compet_email=r[1][6].strip()
            except:
                compet_email=None
            if compet_email:
                if not EMAIL_REGEX.match(compet_email):
                    errors.append(Error(linenum,'Email com formato incorreto',format_line(r, delimiter)))
                    continue
            elif compet_type in ('PJ','P1','P2','PS'):
                errors.append(Error(linenum,'Email é obrigatório para competidoras da CF-OBI',format_line(r, delimiter)))
                continue
            try:
                compet_type = LEVEL[compet_type]
            except:
                errors.append(Error(linenum,'Nível de competidora com formato incorreto',format_line(r, delimiter)))
                continue
            if compet_year not in SCHOOL_YEARS:
                errors.append(Error(linenum,'Ano na escola com formato incorreto',format_line(r, delimiter)))
                continue
            res_validate_type = validate_compet_level(compet_type,compet_year,school.school_type)
            if res_validate_type:
                errors.append(Error(linenum,res_validate_type,format_line(r, delimiter)))
                continue
            if len(compet_name) == 0:
                errors.append(Error(linenum,'Falta nome de competidora',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in new_compets:
                errors.append(Error(linenum,'Nome de competidora repetido neste arquivo',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in existing_compets:
                errors.append(Error(linenum,'Competidora já foi inscrita anteriormente',format_line(r, delimiter)))
                continue
            else:
                new_compets.append(compet_name.lower())
            try:
                day,month,year=[int(x) for x in compet_birth_date.split('/')]
                if day < 1 or day > 31 or month < 1 or month > 12 or year < 1900 or year > 2015:
                    errors.append(Error(linenum,'Data de nascimento inválida',format_line(r, delimiter)))
                    continue
                compet_birth_date = date(year,month,day)
            except:
                errors.append(Error(linenum,'Data de nascimento inválida',format_line(r, delimiter)))
                continue
            try:
                compet_sex=compet_sex.upper()
                if compet_sex!='F' and compet_sex!='O':
                    errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                    continue
            except:
                errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                continue
            if len(compet_year)==0:
                errors.append(Error(linenum,'Coluna Ano Escolar não pode ser vazia',format_line(r, delimiter)))
                continue
            c = Compet(compet_type=compet_type, compet_name=compet_name, compet_birth_date=compet_birth_date, compet_sex=compet_sex, compet_year=compet_year, compet_email=compet_email,compet_school_id=school.school_id)
            validated_compets.append(c)
            school_passwords.append(password)
        return msg,errors,validated_compets,school_passwords


def check_compet_feminina_batch_update_password(f,school):
        msg = ''
        errors = []
        validated_compets=[]
        compets_seen=set()

        if f.multiple_chunks(): # default is 2.5 MB
            msg = 'Arquivo muito grande (deve ser no máximo de 2.5MB).'
            return msg,errors,validated_compets
        # f.read() does not work...
        for chunk in f.chunks():
            decoded_file = chunk

        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        ext = os.path.splitext(f.name)[1].lower()[1:]
        if ext == 'csv':
            try:
                the_file = StringIO(decoded_file.decode(),newline=None)
            except:
                try:
                    the_file = StringIO(decoded_file.decode('latin1'),newline=None)
                except:
                    try:
                        the_file = StringIO(decoded_file.decode('macroman'),newline=None)
                    except:
                        msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                        return msg,errors,validated_compets
            df = pd.read_csv(the_file)
        elif ext == 'xls':
            df = pd.read_excel(decoded_file)
        elif ext == 'xlsx':
            df = pd.read_excel(decoded_file, engine='openpyxl')
        else:
            msg = 'Arquivo deve estar no formato xls, xlsx ou csv.'
            return msg,errors,validated_compets

        linenum = 0
        delimiter = ','
        new_compets=[]
        for r in df.iterrows():
            linenum += 1
            if len(r[1])==0:
                continue
            elif len(r[1]) != 2:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            if r[1][1].strip().lower()=='num. inscr.':
                continue
            ok_row=True
            msg_row=''
            try:
                compet_id_full=r[1][0].strip()
                password=r[1][1].strip()
            except:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            try:
                compet_id = int(compet_id_full.split('-')[0])
            except:
                errors.append(Error(linenum,'número de inscrição em formato errado',format_line(r, delimiter)))
                continue

            if compet_id in compets_seen:
                errors.append(Error(linenum,'competidora repetida no arquivo',format_line(r, delimiter)))
                continue
            compets_seen.add(compet_id)

            if format_compet_id(compet_id) != compet_id_full:
                errors.append(Error(linenum,'número de inscrição em formato errado',format_line(r, delimiter)))
                continue

            try:
                compet = Compet.objects.get(compet_id=compet_id, compet_school_id=school.school_id)
            except:
                errors.append(Error(linenum,'número de inscrição não corresponde a competidora da escola',format_line(r, delimiter)))
                continue

            if len(password) < 5:
                errors.append(Error(linenum,'senha deve ter no mínimo cinco caracteres',format_line(r, delimiter)))
                continue

            validated_compets.append((compet, password))

        return msg,errors,validated_compets

if __name__=="__main__":
    try:
        school_id=int(sys.argv[1])
        f=open(sys.argv[2])
    except:
        print("usage: {} school_id file.csv".format(sys.argv[0]))
        sys.exit(0)

    msg,errors,validated_compets = check_compet_feminina_batch(school_id, f)
    print('msg:', msg)
    print('errors:', errors)
    print('validated_compets:', validated_compets)
