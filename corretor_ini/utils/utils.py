# -*- coding: utf-8 -*-
import json
import os
import random
import re
import shutil
import smtplib
import string
import subprocess
import sys
import urllib.request
import unicodedata
import uuid
from time import sleep
import logging

from tempfile import TemporaryDirectory
from time import strftime
from django.utils.text import get_valid_filename
from email.message import EmailMessage
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from obi.settings import MEDIA_ROOT, YEAR
from corretor_ini.settings import SSH_CORRETOR_INI_HOSTNAME, SSH_CORRETOR_INI_USERNAME

from cal.models import CalendarEvent

logger = logging.getLogger('restrito')


def run(cmd, timeout):
    try:
        #print('cmd:',cmd)
        result=subprocess.run(cmd, shell=True, timeout=timeout)
    except:
        return 'Erro no processamento de comando interno (timeout)'
    if result.returncode!=0:
        return 'Erro no processamento de comando interno' # +str(result)
    return ''

def pack_and_send(email, reference, num_questions, num_alternatives, source_file, answer_file, participants, label1=None, label2=None, label3=None, obi=True, year=None, school_id=None, phase=None, level=None):

    print("in pack and send")
    logger.info(f"corretor.utils in pack_and_send {email} {reference}") 
    #cur_dir=os.getcwd()
    
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


        user_id = 1028 # olimpinf@gmail.com user_id
        reference_id = uuid.uuid4()
        lang = 'pt'
        with open('info.txt','w') as tmpf:
            print(f'num_questions = {num_questions}', file=tmpf)
            print(f'num_alternatives = {num_alternatives}', file=tmpf)
            print(f'lang = "{lang}"', file=tmpf)
            print(f'user_id = "{user_id}"', file=tmpf)
            print(f'email = "{email}"', file=tmpf)
            print(f'reference = "{reference}"', file=tmpf)
            print(f'label1 = "{label1}"', file=tmpf)
            print(f'label2 = "{label2}"', file=tmpf)
            print(f'label3 = "{label3}"', file=tmpf)
            print(f'reference_id = "{reference_id}"', file=tmpf)
        
        tmpf=open('obi.txt','w')
        tmpf.write("{}\n{}\n{}\n{}\n".format(year,phase,level,school_id))
        tmpf.close()

        with open('participants.csv', 'w') as tmpf:
            for id,name in participants:
                print(f'{id},"{name}"', file=tmpf)

        unique_filename = 'CORRETOR_{}_{}'.format(email, uuid.uuid4())
        result=run('zip %s.zip source.pdf *.txt participants.csv' % unique_filename, timeout=120)
        if result != '':
            #os.chdir(cur_dir)
            return result


        source_path = f'{unique_filename}.zip'
        remote_path = os.path.join(MEDIA_ROOT,'files_to_send_to_grader', f'{unique_filename}.zip')
        shutil.copy(source_path, remote_path)

    return ''

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
