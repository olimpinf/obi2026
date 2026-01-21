# -*- coding: utf-8 -*-
import json
import os
import random
import re
import smtplib
import string
import subprocess
import sys
import tempfile
import urllib.request
import unicodedata
import uuid
from time import strftime
from django.utils.text import get_valid_filename
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from obi.settings import MEDIA_ROOT, YEAR

from cal.models import CalendarNationalEvent

def format_thousands(v):
    if not v:
        return 0
    thou = "."
    s = '{:.2f}'.format(float(v))
    integer, decimal = s.split(".")
    integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
    return integer

def format_currency(v):
    if not v:
        return 0
    thou = "."
    dec = ","
    s = '{:.2f}'.format(float(v))
    integer, decimal = s.split(".")
    integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
    return integer + dec + decimal

def slugfy(s):
    slug = ''
    for c in s:
        if c == ' ':
            slug += '-'
        elif c in string.ascii_letters:
            slug += c.lower()
    if slug == '':
        slug = 'slug'
    return slug
    
def check_answers_file(filename):
    '''
    checks if answers file is consistent 
    '''
    if not os.path.isfile(filename):
        return 'arquivo não encontrado',0,{}
    try:
        with open(filename) as f:
            data = f.readlines()
    except:
        try:
            with open(filename,encoding='iso-8859-1') as f:
                data = f.readlines()
        except:
            return 'erro na codificação do arquivo (deve ser UTF-8 ou ISO-8859-1)',0,{}
    pattern_comment = re.compile('\s*#.*')
    pattern_alternative = re.compile('\s*(?P<num>[0-9]+)\.\s*(?P<alt>.*)')
    i = 0
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
            return 'Linha %d: erro de formatação' % line_num,0,{}
        num = int(m.group('num'))
        if num != i+1:
            return 'Linha %d: número fora de sequência' % line_num,0,{}
        alternative = m.group('alt').strip()
        if len(alternative) == 1:
            if alternative not in ['A','B','C','C','D','E','*','-']:
                return 'Linha %d: Caractere de alternativa fora do esperado (A,B,C,D,E,* ou -)' % line_num,0,{}
        else:
            multiple_alt = [a.strip() for a in alternative.split(',')]
            if len(multiple_alt) == 1:
                return 'Linha %d: Alternativa deve ser um caractere ou lista de caracteres separados por vírgula' % line_num,0,{}
            else:
                for a in multiple_alt:
                    if a not in ['A','B','C','C','D','E','*','-']:
                        return 'Linha %d: Caractere de alternativa múltipla fora do esperado (A,B,C,D,E,* ou -)' % line_num,0,{}
                alternative = ','.join(multiple_alt)
        answers[i] = alternative
        i += 1
    return '',i,answers

def calc_log_and_points(gab, answer, show_correct):
    points = 0
    log=''
    if len(answer)!=len(gab):
        log='ERRO: número de respostas é diferente do número de questões (folha em branco?)'
        #print >> sys.stderr,"number of answers does not match number of questions"
        return points, log
    for i in range(len(gab)):
        log=log+"%d. " % (i+1)
        if i<9 and len(gab)>=10: log+=' '
        accept=gab[i]
        if accept[0]=='-':
            log=log+"Questão anulada"
        elif answer[i]=='X':
            log=log+"Resposta inválida"
        else:
            log=log+"%s" % (answer[i])
        if len(accept)==1: # only one answer possible
            #all_answers[i][answer[i]] += 1
            #if accept[0]=='*':
            #    print >> sys.stderr, '============================= i=',i
            if (accept[0]=='*' or answer[i]==accept[0]):
                if show_correct:
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
                if show_correct:
                    log=log+" +"
                    points = points + 1
                log=log+"\n"
            else:
                log=log+"\n"
    if show_correct:
        log += "\nO sinal '+' indica resposta correta."
    return points,log

def get_obi_date(slug,format="%d/%m/%Y"):
    event = CalendarNationalEvent.objects.get(slug=slug)
    date = event.start
    return date.strftime(format)

def get_obi_date_finish(slug,format="%d/%m/%Y"):
    event = CalendarNationalEvent.objects.get(slug=slug)
    date = event.finish
    return date.strftime(format)

def calculate_page_size(n, page, maxsize=50):
    '''for Paginator'''
    if page == 'all' and n > 0: 
        page_size = n
    elif n == 0:
        page_size = 1
    elif n > 5:
        page_size = maxsize
    else:
        page_size =  n
    return page_size

def remove_accents(input_str):
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii

#from .models import LANG_SUFFIXES_NAMES
# import does not work, don't know how to import
LANG_SUFFIXES_NAMES = {2:".cpp", 1:".c", 3:".pas", 4:"_py2.py", 5:".java", 6:".js", 7:"_py3.py"}

def csv_sniffer(sample, columns):
    '''Try to guess the delimiter in a csv file '''
    lines = sample.split('\n')
    if len(lines) == 0:
        # not right
        return None
    # try comma
    for delimiter in  [',', ';', '\t']:
        sizes = {c:0 for c in columns}
        for l in lines:
            tmp = len(l.split(delimiter))
            if tmp in sizes.keys():
                sizes[tmp] += 1
            else:
                sizes[tmp] = 1
        tot = 0
        for c in columns:
            tot += sizes[c]
        if tot > len(lines)/2:
            return delimiter
    return None

def caps(s):
    tks = s.split()
    newtks = []
    for t in tks:
        #if nt.upper() in ['ITA','ICMC/USP','ICMC','USP', 'UFPE' 'IFBA', 'UFRN', 'IFCE', 'IME-USP', 'UFRRJ', 'UFRJ', 'IFPB']:
      t = t.lower()
      if t in ['de','da','do','e','das','dos']:
        newtks.append(t)
      else:
        newtks.append(t.capitalize())
    return ' '.join(newtks)

def unslugfy(s):
    pat = re.compile("obi[1-2][0-9]*")
    tks = s.split("-")
    newtks = []
    for t in tks:
      t = t.lower()
      if t in ['de','da','do','e','das','dos']:
        newtks.append(t)
      elif re.match(pat,t):
        newtks.append(t.upper())
      elif t == 'olimpica':
        newtks.append('Olímpica')
      else:
        newtks.append(t.capitalize())
    return ' '.join(newtks)

def verify_compet_id(id):
    pattern = re.compile("([0-9]+)-([A-K])")
    m = re.match(pattern,id)
    if m:
        return m.group(1),m.group(2)
    else:
        return 0,'*'

# def format_phone_number(ddd,phone):
#     if ddd:
#         m = re.search('(?P<ddd>(0\d\d)|(\d\d))',ddd)
#         tmp = int(m.group('ddd'))
#         formatted_phone = '({}) '.format(tmp)
#     else:
#         formatted_phone = '?? '
#     for d in phone:
#         if d in string.digits:
#             formatted_phone += d
#     formatted_phone = formatted_phone[0:-4] + '-' + formatted_phone[-4:]
#     return formatted_phone

def format_phone_number(n):
    digits = re.sub("\D","",n)
    if digits == "":
        return ''
    if digits[0] == '0':
        digits = digits[1:]
    if len(digits) < 10:
        return ''
    #if len(digits) > 12:
    #    return ''
    l = len(digits)
    return f'({digits[:2]}) {digits[2:l-4]}-{digits[l-4:]}'

def format_compet_id(id):
    try:
        id=int(id)
    except:
        return u"ainda não definido"
    d1 = id % 10
    d2 = id % 100 // 10
    d3 = id % 1000 // 100
    d4 = id % 10000 // 1000
    d5 = id // 10000
    digit = (3 * d1 + 2 * d2 + 1 * d3 + 2 * d4 + 3 * d5) % 10
    if digit == 0:
        digit = 10
    return "%05d-%c" % (id, digit + 64)

def get_data_cep(cep):
    clean = ''
    for c in cep:
        if c in string.digits:
            clean += c
    url_api = 'http://www.viacep.com.br/ws/{}/json'.format(cep)
    try:
        with urllib.request.urlopen(url_api) as response:
            html = response.read()
        data = json.loads(html.decode('utf-8'))
    except:
        data = {}
    return data

def make_password(syllables=2, add_number=True, separator='-'):
    """Alternate random consonants & vowels creating decent memorable passwords                                                                                                         
    """
    FORBIDDEN = ['cu','ku','pu','fu','fo','bo']
    rnd = random.SystemRandom()
    s = string.ascii_lowercase
    vowels = 'aeiu'
    spec = 'hloqwy' # avoid these
    consonants = ''.join([x for x in s if x not in vowels+spec])
    tmp = ''
    while len(tmp)//2 < syllables//2:
        s = ''.join([rnd.choice(consonants)+rnd.choice(vowels)])
        if s not in FORBIDDEN:
            tmp += s

    pwd = tmp #tmp.title()
    pwd += separator # just for readability

    if add_number:
        pwd += str(rnd.choice(range(2,10)))+str(rnd.choice(range(2,10))) # avoid digits 0,1
    tmp = ''
    while len(tmp)//2 < syllables - syllables//2:
        s = ''.join([rnd.choice(consonants)+rnd.choice(vowels)])
        if s not in FORBIDDEN:
            tmp += s

    pwd += separator # just for readability
    pwd += tmp # tmp.title()

    return pwd

def obi_year(as_int=False):
    year = YEAR
    if as_int:
        return year
    else:
        return 'OBI{}'.format(year)

def write_uploaded_file(f,fname,move_dir):
    ''' Write file to move_dir with unique name and return the new file name
    '''
    file_name = get_valid_filename(fname)
    unique_filename = '{}_{}'.format(uuid.uuid4(),file_name)
    #orig_path = os.path.join(MEDIA_ROOT,file_name)
    new_path = os.path.join(MEDIA_ROOT,move_dir,unique_filename)
    with open(new_path, "wb") as destf:
        for chunk in f.chunks():
            destf.write(chunk)
    return new_path

def write_school_uploaded_file(school_id,modality,phase_name,fwhy,f,fname):
    ''' Write file to appropriate directory with unique name and return the new file name
    '''
    file_name = get_valid_filename(fname)
    school_number = "{:04d}".format(school_id)
    sch_dir = ''
    path_parts = [MEDIA_ROOT, 'escolas', modality, phase_name, fwhy, school_number]

    # pre-create these path:
    sch_dir = os.path.join(MEDIA_ROOT, 'escolas', modality, phase_name)
    # create dynamicaly these:
    for p in [fwhy, school_number]:
        sch_dir = os.path.join(sch_dir, p)
        if not os.path.exists(sch_dir):
            os.mkdir(sch_dir, 0o755)

    file_path = os.path.join(sch_dir,fname)
    result_path = os.path.join(sch_dir,"%s_log" % (fname))

    if os.path.exists(file_path):
        # if there is already a file with with this name, there may be other versions, find the newest
        for i in range(1,1000):
            if not os.path.exists('%s_%03d' % (file_path,i)):
                break
        os.rename(file_path,'%s_%03d' % (file_path,i))
        if os.path.exists(result_path):
            os.rename(result_path,'%s_%03d' % (result_path,i))

    # now get the contents of the file
    with open(file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # and return it
    return file_path, result_path

def zip_submissions(submissions,dirname):
    cur_dir=os.getcwd()
    tmp_dir=tempfile.mkdtemp()
    os.chdir(tmp_dir)
    os.mkdir(dirname)
    full_compet_id = ''
    for s in submissions:
        if full_compet_id != s.compet_id:
            full_compet_id = format_compet_id(s.compet_id)
            if not os.path.isdir(os.path.join(dirname,full_compet_id)):
                os.mkdir(os.path.join(dirname,full_compet_id))
        fname = s.problem_name
        ext = LANG_SUFFIXES_NAMES[s.sub_lang]
        with open(os.path.join(dirname,full_compet_id,'{}{}'.format(fname,ext)), 'w') as f:
            f.write(s.sub_source)

    result=subprocess.run('zip -q -r {}.zip {}'.format(dirname,dirname), shell=True, timeout=100)
    if result.returncode!=0:
        data={'msg':"erro ao processar arquivo zip"}
        return render(request,'obi/error.html', data)
    zip_file = open('{}.zip'.format(dirname),'rb')
    os.chdir(cur_dir)
    return zip_file

def my_send_mail(subject, msg_text, to_addr, file=None, fname=None):
    SMTP_SERVER = "taquaral.ic.unicamp.br" 
    SMTP_PORT = 587
    SMTP_USERNAME = "olimpinf"
    SMTP_PASSWORD = "pric23weg"
    EMAIL_FROM = '"Coordenação da {}" <olimpinf@ic.unicamp.br>'.format(obi_year())
    EMAIL_FROM_MULTIPART = 'olimpinf@ic.unicamp.br'
    
    if file:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM_MULTIPART
        msg['To'] = to_addr
        msg.attach(MIMEText(msg_text))
        part = MIMEApplication(
                file.read(),
                Name=fname
                )
        #file.close()
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % (fname)
        msg.attach(part)
    else:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_addr
        msg.set_content(msg_text)

    s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    s.starttls()
    s.login(SMTP_USERNAME, SMTP_PASSWORD)
    res = s.sendmail(msg['From'], msg['To'], msg.as_string())
    #s.send_message(msg) # checks utf8 capability and does not work
    s.quit()

def capitalize_name(s):
    s = s.strip()
    if s.find("'") > 0:
        s = s.replace(" '","'")
        s = s.replace("' ","'")
    tks = s.split()
    newtks = []
    for t in tks:
        t = t.strip().lower()
        if t in ['de','da','do','e','das','dos']:
            newtks.append(t)
        elif t in ['ee','eee','eemti','eep','eeep','eeefm','usp','ime','ii']:
            newtks.append(t.upper())
        elif t.find("'") > 0:
            composed = t.split("'")
            if composed[0].lower() == 'd':
                c0 = 'd'
            else:
                c0 = composed[0].title()
            if composed[1].lower() == 's':
                c1 = 's'
            else:
                c1 = composed[1].title()
            newtks.append(c0+"’"+c1)
        else:
            newtks.append(t.title())
    capitalized = ' '.join(newtks)
    return capitalized


def pack_and_send_compet_solutions(compet_id,phase):
    full_compet_id = format_compet_id(compet_id)
    if phase == 1:
        from fase1.models import SubFase1
        submissions = SubFase1.objects.filter(compet_id=compet_id)
    elif phase == 2:
        from fase2.models import SubFase2
        submissions = SubFase2.objects.filter(compet_id=compet_id)
    elif phase == 3:
        from fase3.models import SubFase3
        submissions = SubFase3.objects.filter(compet_id=compet_id)
    else:
        return ''
    cur_dir=os.getcwd()
    tmp_dir=tempfile.mkdtemp()
    os.chdir(tmp_dir)
    os.mkdir(full_compet_id)
    for s in submissions:
        fname = s.problem_name
        ext = LANG_SUFFIXES_NAMES[s.sub_lang]
        with open(os.path.join(full_compet_id,'{}{}'.format(fname,ext)), 'w') as f:
            f.write(s.sub_source)

    result=subprocess.run('zip -q -r {}.zip {}'.format(full_compet_id,full_compet_id), shell=True, timeout=100)
    if result.returncode!=0:
        return 'Erro no processamento'
    with open('{}.zip'.format(full_compet_id), 'rb') as f:
        file_data = f.read()
    os.chdir(cur_dir)
    return file_data

if __name__=='__main__':
    pass
  # send_mail
  #send_mail("Não é um teste", "Um teste com acentuação.", ["ranido@gmail.com","ranido@ic.unicamp.br"])

  # make_password
  #print(make_password())

  # caps
  #print(caps(sys.argv[1]))

#  with open(sys.argv[1],"r") as fin:
#    names = fin.readlines()
#    for name in names:
#      print(caps(name))
