import csv
import os
import paramiko
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from time import sleep
import uuid
from io import StringIO

from obi.settings import DEBUG, SSH_SISCA_HOSTNAME, SSH_SISCA_USERNAME

def run(cmd, timeout):
    try:
        #print('cmd:',cmd)
        result=subprocess.run(cmd, shell=True, timeout=timeout)
    except:
        return 'Erro no processamento de comando interno (timeout)'
    if result.returncode!=0:
        return 'Erro no processamento de comando interno' # +str(result)
    return ''

def compute_points(gab, answer):
    points = 0
    log=''
    if len(answer)!=len(gab):
        log='ERRO: número de respostas é diferente do número de questões'
        print("number of answers does not match number of questions",file=sys.stderr)
        return points, log
    for i in range(len(gab)):
        log=log+"%d. " % (i+1)
        if i<9 and len(gab)>=10: log+=' '
        accept=gab[i]
        if accept[0]=='-':
            log=log+"Questão anulada"
        elif accept[0]=='=':
            log=log+"Questão não usada"
        elif answer[i]=='X':
            log=log+"Resposta inválida"
        else:
            log=log+"%s" % (answer[i])
        if len(accept)==1: # only one answer possible
            if ((accept[0]=='*') or (answer[i]==accept[0])):
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                # se quiser mostrar os errados...
                #log=log+" (errada)"
                #all_answers[i]['X'] += 1
                log=log+"\n"
        else: # list of correct answers
            if answer[i] in accept:
                log=log+" +"
                points = points + 1
                log=log+"\n"
            else:
                log=log+"\n"
    return points,log

def pack_and_send(email, reference, source_file, answer_file, obi=False, year=None, school_id=None, phase=None, level=None):
    cur_dir=os.getcwd()

    with TemporaryDirectory() as tmp_dir:
        os.chdir(tmp_dir)
        shutil.copy(source_file, "source.pdf")
        shutil.copy(answer_file, "gab.txt")

        tmpf=open('email.txt','w')
        tmpf.write(email)
        tmpf.close()

        tmpf=open('ref.txt','w')
        tmpf.write(reference)
        tmpf.close()

        if obi:
            tmpf=open('obi.txt','w')
            tmpf.write("{}\n{}\n{}\n{}\n".format(year,phase,level,school_id))
            tmpf.close()

        unique_filename = 'CORRETOR_{}_{}'.format(email, uuid.uuid4())
        result=run('zip %s.zip source.pdf *.txt' % unique_filename, timeout=120)
        if result != '':
            os.chdir(cur_dir)
            return result

        ssh = paramiko.SSHClient()
        username='exec_corretor'
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ok = False
        tries = 4
        for t in range(tries):
            ssh.connect(hostname=SSH_SISCA_HOSTNAME, username=SSH_SISCA_USERNAME)
            try:
                ok = True
                break
            except:
                #print('connect failed, sleeping')
                sleep(0.5)
        if not ok:
            result = 'Erro de conexão com o corretor'
            os.chdir(cur_dir)
            return result
        
        source_path = f'{unique_filename}.zip'
        if obi:
            #print('is obi')
            remote_path = os.path.join('answer_sheet', 'files_obi', f'{unique_filename}.zip')
        else:
            #print('is not obi')
            remote_path = os.path.join('answer_sheet', 'files', f'{unique_filename}.zip')

        try:
            ftp_ssh=ssh.open_sftp()
            ftp_ssh.put(source_path, remote_path)
            ftp_ssh.close()
        except:
            result = 'Erro de conexão com o corretor'
            os.chdir(cur_dir)
            return result

        tmpf=open('%s.lock' % unique_filename,'w')
        tmpf.write('1')
        tmpf.close()
        if obi:
            remote_path = os.path.join('answer_sheet', 'files_obi', f'{unique_filename}.lock')
        else:
            remote_path = os.path.join('answer_sheet', 'files', f'{unique_filename}.lock')

        try:
            ftp_ssh=ssh.open_sftp()
            ftp_ssh.put(source_path, remote_path)
            ftp_ssh.close()
        except:
            result = 'Erro de conexão com o corretor'
            os.chdir(cur_dir)
            return result

    os.chdir(cur_dir)
    return ''

def check_answers_file(f, num_questions, num_alternatives):

    if f.multiple_chunks(): # default is 2.5 MB
        msg = 'Arquivo muito grande.'
        errors.append(Error(0,msg,''))
        return msg,errors,validated
    # f.read() does not work...
    for chunk in f.chunks():
        decoded_file = chunk
        try:
            fin = StringIO(decoded_file.decode())
        except:
            try:
                fin = StringIO(decoded_file.decode('latin-1'))
            except:
                msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                return msg,errors,validated
  
    data = fin.readlines()
    #with open(f,"rU") as fin:
    #    data = fin.readlines()
    pattern_comment = re.compile('\s*#.*')
    pattern_alternative = re.compile('\s*(?P<num>[0-9]+)\.\s*(?P<alt>.*)')
    valid_alternatives = ['A','B','C','D','E'][:num_alternatives]
    all_alternatives = valid_alternatives + ['*','-']
    i = 0
    msg = ''
    errors = []
    answers = {}
    line_num = 0
    for line in data:
        line = line.strip()
        line_num += 1
        if line == '': continue
        if re.match(pattern_comment,line): continue
        m = re.match(pattern_alternative,line)
        if not m: 
           errors.append(Error(line_num,'Erro de formatação',line))
        try:
            num = int(m.group('num'))
            if num != i+1:
                errors.append(Error(line_num,'Número fora de sequência',line))
                continue
        except:
            errors.append(Error(line_num,'Número fora de sequência',line))
            continue
        alternative = m.group('alt').strip()
        if len(alternative) == 1:
            if alternative not in all_alternatives:
                errors.append(Error(line_num,f'Caractere de alternativa fora do esperado {str(all_alternatives)}',line))
        else:
            multiple_alt = [a.strip() for a in alternative.split(',')]
            if len(multiple_alt) == 1:
                errors.append(Error(line_num,'Alternativa deve ser um caractere ou lista de caracteres separados por vírgula',line))
            else:
                for a in multiple_alt:
                    if a not in valid_alternatives:
                        errors.append(Error(line_num,f'Caractere de alternativa múltipla fora do esperado {str(valid_alternatives)}',line))
                alternative = ','.join(multiple_alt)
        answers[i] = alternative
        i += 1
    if num_questions != len(answers):
        msg = "O número de questões informado é diferente do número de respostas no arquivo de gabarito."
    if errors:
        msg = "Foram detectados erros no arquivo de gabarito. Por favor corrija e submeta novamente."
    return msg,errors,answers

class Error():
    def __init__(self, linenum, msg, line):
        self.linenum = linenum
        self.msg = msg
        self.line = line

def format_line(l, delimiter):
    return '{}'.format(delimiter).join(l)

def check_partic_batch(f, num_dig):
        msg = ''
        errors = []
        validated = []
        if f.multiple_chunks(): # default is 2.5 MB
            msg = 'Arquivo muito grande.'
            errors.append(Error(0,msg,''))
            return msg,errors,validated
        # f.read() does not work...
        for chunk in f.chunks():
            decoded_file = chunk
        try:
            csvf = StringIO(decoded_file.decode())
        except:
            try:
                csvf = StringIO(decoded_file.decode('latin-1'))
            except:
                msg = 'Problema na decodificação do arquivo. Arquivo deve estar codificado no padrão UTF-8 ou LATIN-1.'
                return msg,errors,validated
            
        try:
            dialect = csv.Sniffer().sniff(csvf.read(1024))
        except:
            msg = 'Problema no formato do arquivo. Não foi possível determinar qual o caractere separador utilizado. Normalmente o caractere separador do formato CVS é a vírgula, mas também são aceitos ponto-e-vírgula e TAB. Esse erro pode ocorrer quando as linhas do arquivo têm número diferentes de colunas (indicadas pelo caractere separador). Por favor verifique seu arquivo.'
            return msg,errors,validated
                
        delimiter = dialect.delimiter
        csvf.seek(0)
        reader = csv.reader(csvf, dialect)
        linenum=0
        for r in reader:
            linenum += 1
            if len(r)<2:
                errors.append(Error(linenum,'formato incorreto, deve haver duas colunas',format_line(r, delimiter)))
                continue
            if r[0].strip().lower()=='id' or r[1].strip().lower()=='nome':
                continue
            if len(r)==0:
                continue
            ok_row=True
            msg_row=''
            partic_id=r[0].strip()
            partic_name=r[1].strip()
            if len(partic_name)==0:
                errors.append(Error(linenum,'falta nome de participante',format_line(r, delimiter)))
                continue
            if len(partic_id)==0:
                errors.append(Error(linenum,'falta o número de identificação',format_line(r, delimiter)))
                continue
            if num_dig != -1 and num_dig <= 6:
                try:
                    partic_id = int(partic_id)
                except:
                    errors.append(Error(linenum,'número de identificação deve ser um inteiro se o número de dígitos é menor ou igual a 6',format_line(r, delimiter)))
                    continue
                if len(str(partic_id)) > num_dig:
                    errors.append(Error(linenum,'número de identificação tem mais dígitos do que o número de dígitos especificado',format_line(r, delimiter)))
                    continue

            validated.append((partic_id,partic_name))
        return msg,errors,validated

if __name__=="__main__":
    import sys


    # for check_answers_file
    try:
        fname=sys.argv[1]
    except:
        print("usage: {} gabarito.txt".format(sys.argv[0]))
        sys.exit(0)
    msg,errors,answers = check_answers_file(fname)

    for e in errors:
        print(e.linenum, e.msg, e.line)
    print('answers',answers)

    sys.exit(0)

    try:
        f=open(sys.argv[1])
    except:
        print("usage: {} file.csv".format(sys.argv[0]))
        sys.exit(0)

    msg,errors,validated = check_partic_batch(f) 
    print('msg:',msg)
    print('errors:',errors)
    print('validated_partic:',validated)
    

    #resultado=pack_and_send("ranido@gmail.com", "a reference", "file.pdf", "answer")
    #print resultado
