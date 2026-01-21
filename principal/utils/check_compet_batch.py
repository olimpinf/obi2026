import csv
import pandas as pd
import os
import re
import tempfile
from datetime import date
from io import StringIO, BytesIO

from principal.models import (LEVEL, LEVEL_NAME, SCHOOL_YEARS, Compet, validate_compet_level,
                              validate_username, validate_username_compet)
from principal.utils.utils import caps, csv_sniffer, format_compet_id, capitalize_name

from obi.settings import YEAR

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line


def format_line(row, delimiter):
    tokens = []
    for i in range(len(row[1])):
        if pd.isnull(row[1].iloc[i]) or pd.isna(row[1].iloc[i]) or pd.isna(row[1].iloc[i] == ''):
            tokens.append('')
        elif type(row[1].iloc[i]) == float:
            tokens.append(int(row[1].iloc[i]))
        elif type(row[1].iloc[i]) == pd._libs.tslibs.timestamps.Timestamp:
            tokens.append(row[1].iloc[i].strftime('%d/%m/%Y'))
        else:
            tokens.append(str(row[1].iloc[i]))
    return '{}'.format(delimiter).join(tokens)

def format_line_old(l, delimiter):
    tokens = []
    for i in l[1][:]:
        if type(i) == "<class 'float'>":
            tokens.append(int(i))
        elif type(i) == "<class 'pandas._libs.tslibs.timestamps.Timestamp'>":
            tokens.append(str(i))
        elif i == 'nan':
            tokens.append('')
        else:
            tokens.append(str(i))
    #tokens = [str(i) for i in l[1][:]]
    return '{}'.format(delimiter).join(tokens)

def check_compet_batch(f,school):
        tmp = Compet.objects.filter(compet_school_id=school.school_id)
        existing_compets = []
        for c in tmp:
            existing_compets.append(c.compet_name.lower())
        msg = ''
        errors = []
        validated_compets=[]

        #print(f.content_type)

        temp_file = tempfile.NamedTemporaryFile()

        for chunk in f.chunks():
            temp_file.write(chunk)
        temp_file.flush()   
        with open(temp_file.name, "rb") as tmpf:
            decoded_file = tmpf.read()

        
        EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
        ext = os.path.splitext(f.name)[1].lower()[1:]

        if ext == 'csv':
            try:
                df = pd.read_csv(temp_file.name, engine='python', sep=",|;")
            except Exception as e:
                try:
                    df = pd.read_csv(temp_file.name, engine='python', sep=",|;", encoding="latin_1")
                except Exception as e:
                    msg = f'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras. ({e})'
                    temp_file.close()
                    return msg,errors,validated_compets
        elif ext == 'xls':
            try:
                df = pd.read_excel(BytesIO(decoded_file))
            except Exception as e:
                msg = f'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras. ({e})'
                temp_file.close()
                return msg,errors,validated_compets
        elif ext == 'xlsx':
            try:
                df = pd.read_excel(BytesIO(decoded_file), engine='openpyxl')
            except Exception as e:
                msg = f'Problema na leitura do arquivo; por favor verifique que não haja linhas com colunas extras. ({e})'
                temp_file.close()
                return msg,errors,validated_compets
        else:
            msg = 'Arquivo deve estar no formato xls, xlsx ou csv.'
            temp_file.close()
            return msg,errors,validated_compets

        temp_file.close()
        
        linenum = 0
        delimiter = ','
        new_compets=[]
        for r in df.iterrows():
            linenum += 1
            if len(r[1])==0 or pd.isnull(r[1].iloc[0]):
                continue
            elif len(r[1]) < 5: # or np.any(pd.isnull(r[1])):
                errors.append(Error(linenum,'formato incorreto, coluna faltando',format_line(r, delimiter)))
                continue

            try:
                tmp = r[1].iloc[1].strip().lower()
            except:
                continue    
            if r[1].iloc[1].strip().lower()=='nome':
                continue
            ok_row=True
            msg_row=''

            try:
                compet_type=r[1].iloc[0].strip().upper()
            except:
                errors.append(Error(linenum,'formato incorreto na coluna nível de competidor',format_line(r, delimiter)))
                continue

            try:
                compet_name=capitalize_name(r[1].iloc[1].strip())
            except:
                errors.append(Error(linenum,'formato incorreto na coluna nome de competidor',format_line(r, delimiter)))
                continue

            try:
                #print('date:', r[1].iloc[2])
                #print('type:', type( r[1].iloc[2]))
                if str(type(r[1].iloc[2])) == "<class 'datetime.datetime'>":
                    compet_birth_date = r[1].iloc[2].strftime('%d/%m/%Y')
                elif type(r[1].iloc[2]) == pd._libs.tslibs.timestamps.Timestamp:
                    compet_birth_date = r[1].iloc[2].strftime('%d/%m/%Y')
                else:
                    # type is string?? type(row[1][2]) == str:
                    compet_birth_date = r[1].iloc[2].strip()
            except:
                errors.append(Error(linenum,'formato incorreto na coluna data de nascimento',format_line(r, delimiter)))
                continue

            try:
                compet_sex=r[1].iloc[3].strip()
            except:
                errors.append(Error(linenum,'formato incorreto na coluna gênero de competidor',format_line(r, delimiter)))
                continue

            try:
                #print('compet_year:', r[1].iloc[4])
                compet_year=r[1].iloc[4].strip()
            except:
                errors.append(Error(linenum,'formato incorreto na coluna ano escolar',format_line(r, delimiter)))
                continue

            try:
                compet_class=str(r[1].iloc[5]).strip()
            except:
                errors.append(Error(linenum,'formato incorreto na coluna turma escolar',format_line(r, delimiter)))
                continue
            compet_class = compet_class[:8]
            try:
                compet_email=r[1].iloc[6].strip()
                #compet_email=r[1].iloc[6].strip()
            except:
                compet_email=None
            if compet_email:
                if not EMAIL_REGEX.match(compet_email):
                    errors.append(Error(linenum,'Email com formato incorreto',format_line(r, delimiter)))
                    continue
            # Não precisa mais (?)
            # elif compet_type in ('PJ','P1','P2','PS'):
            #     errors.append(Error(linenum,'Email é obrigatório para competidores da Modalidade Programação',format_line(r, delimiter)))
            #     continue

            try:
                compet_type = LEVEL[compet_type]
            except:
                errors.append(Error(linenum,'Nível de competidor com formato incorreto',format_line(r, delimiter)))
                continue
            if compet_year not in SCHOOL_YEARS:
                errors.append(Error(linenum,'Ano na escola com formato incorreto',format_line(r, delimiter)))
                continue                
            res_validate_type = validate_compet_level(compet_type,compet_year,school.school_type)
            if res_validate_type:
                errors.append(Error(linenum,res_validate_type,format_line(r, delimiter)))
                continue
            if len(compet_name) == 0:
                errors.append(Error(linenum,'Falta nome de competidor',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in new_compets:
                errors.append(Error(linenum,'Nome de competidor repetido neste arquivo',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in existing_compets:
                errors.append(Error(linenum,'Competidor já foi inscrito anteriormente',format_line(r, delimiter)))
                continue
            else:
                new_compets.append(compet_name.lower())

            try:
                day,month,year=[int(x) for x in compet_birth_date.split('/')]
                year_limit = YEAR - 8
                if day < 1 or day > 31 or month < 1 or month > 12 or year < 1900 or year > year_limit:
                    #print(day,month,year)
                    errors.append(Error(linenum,'Data de nascimento inválida (usar formato: dia/mes/ano)',format_line(r, delimiter)))
                    continue
                compet_birth_date = date(year,month,day)
            except:
                errors.append(Error(linenum,'Data de nascimento inválida (usar formato: dia/mes/ano)',format_line(r, delimiter)))
                continue
            try:
                compet_sex=compet_sex.upper()
                if compet_sex!='M' and compet_sex!='F' and compet_sex !='O':
                    errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                    continue
            except:
                errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                continue
            if len(compet_year)==0:
                errors.append(Error(linenum,'Coluna Ano Escolar não pode ser vazia',format_line(r, delimiter)))
                continue
            if len(compet_class)==0:
                errors.append(Error(linenum,'Coluna Turma Escolar não pode ser vazia',format_line(r, delimiter)))
                continue
            c = Compet(compet_type=compet_type, compet_name=compet_name, compet_birth_date=compet_birth_date, compet_sex=compet_sex, compet_year=compet_year, compet_class=compet_class, compet_email=compet_email,compet_school_id=school.school_id)
            validated_compets.append(c)
        return msg,errors,validated_compets

def check_compet_batch_password(f,school):
        tmp = Compet.objects.filter(compet_school_id=school.school_id)
        existing_compets = []
        for c in tmp:
            existing_compets.append(c.compet_name.lower())
        msg = ''
        errors = []
        validated_compets=[]
        school_passwords=[]
        #print(f.content_type)
        #if f.content_type != 'text/csv' and f.content_type != 'text/plain': 
        #    msg = 'Tipo de arquivo incorreto. Arquivo deve estar no formato CSV.'
        #    errors.append(Error(0,msg,''))
        #    return msg,errors,validated_compets
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
                #csvf = StringIO(decoded_file.decode())
                #print('utf-8')
            except:
                try:
                    the_file = StringIO(decoded_file.decode('latin1'),newline=None)
                    #print('latin1')
                    #csvf = StringIO(decoded_file.decode('latin1'))
                except:
                    try:
                        the_file = StringIO(decoded_file.decode('macroman'),newline=None)
                        #print('macroman')
                        #csvf = StringIO(decoded_file.decode('macroman'))
                    except:
                        msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                        return msg,errors,validated_compets
            df = pd.read_csv(the_file, sep=",|;")
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
            if r[1].iloc[1].strip().lower()=='nome':
                continue
            ok_row=True
            msg_row=''
            try:
                compet_type=r[1].iloc[0].strip().upper()
                compet_name=caps(r[1].iloc[1].strip())
                compet_birth_date=r[1].iloc[2].strip()
                compet_sex=r[1].iloc[3].strip()
                compet_year=r[1].iloc[4].strip()
                compet_class=r[1].iloc[5].strip()
                password=r[1].iloc[7].strip()
            except:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            try:
                compet_email=r[1].iloc[6].strip()
            except:
                compet_email=None
            if compet_email:
                if not EMAIL_REGEX.match(compet_email):
                    errors.append(Error(linenum,'Email com formato incorreto',format_line(r, delimiter)))
                    continue
            elif compet_type in ('PJ','P1','P2','PS'):
                errors.append(Error(linenum,'Email é obrigatório para competidores da Modalidade Programação',format_line(r, delimiter)))
                continue
            try:
                compet_type = LEVEL[compet_type]
            except:
                errors.append(Error(linenum,'Nível de competidor com formato incorreto',format_line(r, delimiter)))
                continue
            if compet_year not in SCHOOL_YEARS:
                errors.append(Error(linenum,'Ano na escola com formato incorreto',format_line(r, delimiter)))
                continue                
            res_validate_type = validate_compet_level(compet_type,compet_year,school.school_type)
            if res_validate_type:
                errors.append(Error(linenum,res_validate_type,format_line(r, delimiter)))
                continue
            if len(compet_name) == 0:
                errors.append(Error(linenum,'Falta nome de competidor',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in new_compets:
                errors.append(Error(linenum,'Nome de competidor repetido neste arquivo',format_line(r, delimiter)))
                continue
            elif compet_name.lower() in existing_compets:
                errors.append(Error(linenum,'Competidor já foi inscrito anteriormente',format_line(r, delimiter)))
                continue
            else:
                new_compets.append(compet_name.lower())
            try:
                day,month,year=[int(x) for x in compet_birth_date.split('/')]
                if day < 1 or day > 31 or month < 1 or month > 12 or year < 1900 or year > 2016:
                    errors.append(Error(linenum,'Data de nascimento inválida',format_line(r, delimiter)))
                    continue
                compet_birth_date = date(year,month,day)
            except:
                errors.append(Error(linenum,'Data de nascimento inválida',format_line(r, delimiter)))
                continue
            try:
                compet_sex=compet_sex.upper()
                if compet_sex!='M' and compet_sex!='F' and compet_sex!='O':
                    errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                    continue
            except:
                errors.append(Error(linenum,'Gênero inválido',format_line(r, delimiter)))
                continue
            if len(compet_year)==0:
                errors.append(Error(linenum,'Coluna Escolaridade não pode ser vazia',format_line(r, delimiter)))
                continue
            c = Compet(compet_type=compet_type, compet_name=compet_name, compet_birth_date=compet_birth_date, compet_sex=compet_sex, compet_year=compet_year, compet_email=compet_email,compet_school_id=school.school_id)
            validated_compets.append(c)
            school_passwords.append(password)
        return msg,errors,validated_compets,school_passwords

def check_compet_batch_update_password(f,school):
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
                #csvf = StringIO(decoded_file.decode())
                #print('utf-8')
            except:
                try:
                    the_file = StringIO(decoded_file.decode('latin1'),newline=None)
                    #print('latin1')
                    #csvf = StringIO(decoded_file.decode('latin1'))
                except:
                    try:
                        the_file = StringIO(decoded_file.decode('macroman'),newline=None)
                        #print('macroman')
                        #csvf = StringIO(decoded_file.decode('macroman'))
                    except:
                        msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                        return msg,errors,validated_compets
            df = pd.read_csv(the_file, sep=",|;")
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
            if r[1].iloc[1].strip().lower()=='num. inscr.':
                continue
            ok_row=True
            msg_row=''
            try:
                compet_id_full=r[1].iloc[0].strip()
                password=r[1].iloc[1].strip()
            except:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            try:
                compet_id = int(compet_id_full.split('-')[0])
            except:
                errors.append(Error(linenum,'número de inscrição em formato errado',format_line(r, delimiter)))
                continue

            if compet_id in compets_seen:
                errors.append(Error(linenum,'competidor repetido no arquivo',format_line(r, delimiter)))
                continue
            compets_seen.add(compet_id)

            if format_compet_id(compet_id) != compet_id_full:
                errors.append(Error(linenum,'número de inscrição em formato errado',format_line(r, delimiter)))
                continue

            try:
                compet = Compet.objects.get(compet_id=compet_id, compet_school_id=school.school_id)
            except:
                errors.append(Error(linenum,'número de inscrição não corresponde a competidor da escola',format_line(r, delimiter)))
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

    msg,errors,validated_compets = check_compet_batch(school_id,f) 
    print('msg:',msg)
    print('errors:',errors)
    print('validated_compets:',validated_compets)
