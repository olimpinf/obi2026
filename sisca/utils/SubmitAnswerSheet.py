# define a function to build answer sheets
# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile
import uuid


def process(source_data, answer_data, email, reference):
    cur_dir=tempfile.mkdtemp()
    os.chdir(cur_dir)
    tmpf=open('source.pdf','w')
    tmpf.write(source_data)
    tmpf.close()

    tmpf=open('gab.txt','w')
    tmpf.write(answer_data)
    tmpf.close()

    tmpf=open('email.txt','w')
    tmpf.write(email)
    tmpf.close()

    tmpf=open('ref.txt','w')
    tmpf.write(reference)
    tmpf.close()

    unique_filename = 'CORRETOR_%s' % uuid.uuid4()
    result=subprocess.call('zip %s.zip source.pdf gab.txt email.txt ref.txt' % unique_filename, shell=True)
    result=subprocess.call('scp %s.zip exec_corretor@10.0.0.23:www_answer_sheet/files' % unique_filename, shell=True)
    tmpf=open('%s.lock' % unique_filename,'w')
    tmpf.write('1')
    tmpf.close()
    result=subprocess.call('scp %s.lock exec_corretor@10.0.0.23:www_answer_sheet/files' % unique_filename, shell=True)

    return 'OK'
    

if __name__=="__main__":
    f=open('joined_test.pdf','r')
    g=open('gab10.txt','r')
    resultado=process(f.read(), g.read().strip(), "ranido@gmail.com")
    print resultado
