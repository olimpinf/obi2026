import csv
import re
from datetime import date
from io import StringIO

from principal.models import I1, I2, IJ, LEVEL, LEVEL_NAME, Compet
from principal.utils.utils import caps, csv_sniffer, format_compet_id
from exams.models import ExamFase1, ExamFase2, ExamFase3

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line

def format_line(l, delimiter):
    return '{}'.format(delimiter).join(l)

def check_compet_points_batch(f,school_id,maxpoints,phase,is_superuser=False):
        msg = ''
        errors = []
        seen_compets=set()
        validated_compets=[]

        if phase == 1:
            exams = ExamFase1.objects.filter(time_start__isnull=False)
        elif phase == 2:
            exams = ExamFase2.objects.filter(time_start__isnull=False)
        elif phase == 3:
            exams = ExamFase3.objects.filter(time_start__isnull=False)
        else:
            msg = 'Problema na configuração, fase incorreta'
            return msg,errors,validated_compets
        
        try:
            csvf = open(f,"r", encoding='utf-8')
            print('utf-8')
        except:
            try:
                csvf = open(f,"r", encoding='iso8859-1')
                #print('iso8859-1')
            except:
                try:
                    csvf = open(f,"r", encoding='macroman')
                    #print('mac os roman')
                except:
                    msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                    return msg,errors,validated_compets

        Email_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

        delimiter = None
        try:
            sample = csvf.read()
        except:
            msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1 (também conhecido como ISO-8859).'
            return msg,errors,validated_compets

        delimiter = csv_sniffer(sample,[3,4,5,6])
        print("delimiter", delimiter)
        try:
            delimiter = csv_sniffer(sample,[3,4,5,6])
        except:
            msg = 'Problema no formato ou decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1 (também conhecido como ISO-8859).'
            return msg,errors,validated_compets

        #delimiter = dialect.delimiter
        #print('delimiter',delimiter)
        if not delimiter:
            #######
            # maybe implement a warning msg variable
            #msg = 'Problema no formato do arquivo. Não foi possível determinar qual o caractere separador utilizado. Normalmente o caractere separador do formato CVS é a vírgula, mas também são aceitos ponto-e-vírgula e TAB. Esse erro pode ocorrer quando as linhas do arquivo têm número diferentes de colunas (indicadas pelo caractere separador). Por favor verifique seu arquivo. Estamo usando vírgula como separador, pode não ser o correto e nesse caso outros erros ocorrerão'
            print('could not find delimiter, using ;')
            delimiter = ';'

        csvf.seek(0)
        reader = csv.reader(csvf, delimiter=delimiter)

        linenum=0
        new_compets=[]
        for r in reader:
            linenum += 1
            if len(r)==0:
                continue
            elif len(r)<3 :
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            if r[0].strip().lower()=='num. inscr.' or r[1].strip().lower()=='nivel' or r[1].strip().lower()=='nível':
                continue
            ok_row=True
            msg_row=''
            try:
                compet_id_full=r[0].strip()
                compet_type=r[1].strip().upper()
                compet_points=r[2].strip()
            except:
                errors.append(Error(linenum,'formato incorreto',format_line(r, delimiter)))
                continue
            try:
                compet_points = int(compet_points)
            except:
                errors.append(Error(linenum,'pontos devem ser inteiros',format_line(r, delimiter)))
                continue
            if compet_points < 0 or compet_points > maxpoints:
                errors.append(Error(linenum,'pontos fora do intervalo',format_line(r, delimiter)))
                continue
            if compet_points < 0 or compet_points > maxpoints:
                errors.append(Error(linenum,'pontos fora do intervalo',format_line(r, delimiter)))
                continue
            
            try:
                compet_type=LEVEL[compet_type]
                if compet_type not in (IJ, I1, I2):
                    errors.append(Error(linenum,'nível incorreto',format_line(r, delimiter)))
                    continue
            except:
                errors.append(Error(linenum,'nível incorreto',format_line(r, delimiter)))
                continue

            try:
                # formato incorreto mas utilizavel: 012345A
                compet_id = compet_id_full[:-1]
                compet_id = int(compet_id)
                #print('OK1, compet_points',compet_points,'compet_id_full',compet_id_full, ' compet_id', compet_id)
                
            except:
                try:
                    # formato correto: 012345-A
                    compet_id = compet_id_full[:-2]
                    compet_id = int(compet_id)
                    #print('OK2, compet_points',compet_points,'compet_id_full',compet_id_full, ' compet_id', compet_id)
                except:
                    #print('ERRO, compet_points',compet_points,'compet_id_full',compet_id_full, ' compet_id', compet_id)
                    errors.append(Error(linenum,'número de inscrição no formato errado',format_line(r, delimiter)))
                    continue
            #if format_compet_id(compet_id) != compet_id_full:
            #    errors.append(Error(linenum,'número de inscrição errado',format_line(r, delimiter)))
            #    continue

            try:
                c = Compet.objects.get(pk=compet_id)
                if c.compet_school_id != school_id:
                    errors.append(Error(linenum,'número de inscrição não corresponde a competidor da escola',format_line(r, delimiter)))
                    continue
                if c.compet_type != compet_type:
                    errors.append(Error(linenum,'competidor não é do nível informado',format_line(r, delimiter)))
                    continue
                if phase==2 and c.compet_classif_fase1 != True:
                    errors.append(Error(linenum,'competidor não está classificado para esta fase',format_line(r, delimiter)))
                    continue
            except:
                errors.append(Error(linenum,'número de inscrição não corresponde a competidor da escola',format_line(r, delimiter)))
                continue

            try:
                tmp = exams.get(compet=c)
                ok = False
            except:
                ok = True

            if (not ok) and (not is_superuser):
                errors.append(Error(linenum,'competidor fez a prova online, não é possível alterar a pontuação.',format_line(r, delimiter)))
                continue
            
            if compet_id in seen_compets:
                errors.append(Error(linenum,'número de inscrição repetido neste arquivo',format_line(r, delimiter)))
            else:
                seen_compets.add(compet_id)
                validated_compets.append((compet_id,compet_points))

        csvf.close()
        return msg,errors,validated_compets

if __name__=="__main__":

    try:
        school_id=int(sys.argv[1])
        f=sys.argv[2]
    except:
        print("usage: {} school_id file.csv".format(sys.argv[0]))
        sys.exit(0)

    msg,errors,validated_compets = check_compet_points_batch(f,school_id,maxpoints,phase=2) 
    print('msg:',msg)
    print('errors:',errors)
    print('validated_compets:',validated_compets)
