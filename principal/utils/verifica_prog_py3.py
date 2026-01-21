#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# OBI2004 - Script to verify the .zip/.tar.gz/.tar.bz2 archives
# Copyright (C) 2004 Ulisses Furquim
#

import base64
import os
import re
import string
import sys
import tarfile
import traceback
import zipfile

import psycopg2
from psycopg2 import psycopg1

from cadastro.utils.utils import format_compet_id

#from utils import format_compet_id


DB_NAME="obi2018"
DEBUG = 1  # debug output?

## HTML code to make the result file

HEADER = "<center>\n<table border=1>\n"
TAIL = "</table>\n</center>\n"
FORMAT_ERROR = "<tr><td class=\"form-error\">O arquivo n&atilde;o est&aacute; em um dos " \
               "formatos suportados (.zip/.tar.gz/.tar.bz2).</td></tr>\n"
SCHOOL_ERROR = "<tr><td class=\"form-error\">Nenhum registro encontrado. N&atilde;o h&aacute; alunos " \
               "cadastrados neste n&iacute;vel na escola.</td></tr>\n"
T_HEADER = "<tr><th>Aluno/Programa</th><th>Coment&aacute;rio</th></tr>\n"
T_FILE_NAME = "<tr><td class=\"form-text\">%s</td>"
T_NO_STD = "<td class=\"form-error\" align=\"center\">N&uacute;mero de inscri&ccedil;&atilde;o " \
           "n&atilde;o corresponde a aluno da escola nesta modalidade, verifique se formato est&aacute; correto</td></tr>\n"
T_EMPY_STD = "<td class=\"form-error\" align=\"center\">Nenhum programa encontrado, prov&aacute;vel erro no formato do arquivo</td></tr>\n"
T_NO_EXTENSION = "<td class=\"form-error\" align=\"center\">Nome do " \
                 "programa necessita extens&atilde;o</td></tr>\n"
T_NO_PROB_NAME = "<td class=\"form-error\" align=\"center\">Nome do " \
                 "programa inv&aacute;lido"
T_INI_TD = "<td class=\"form-error\" align=\"center\">"
T_BR = "<br>"
T_NO_VALID_EXT = "Extens&atilde;o inv&aacute;lida"
T_NO_VALID_TYPE = "Tipo de arquivo inv&aacute;lido (n&atilde;o &eacute; texto)"
T_REPEATED = "Nome de programa repetido para este aluno"
T_EMPTYFILE = "Arquivo fonte vazio"
T_BADFILE = "Arquivo aparentemente corrompido"
T_EMPTY_FILE = "Arquivo vazio"
T_TD_OK = "<td class=\"form-ok\" align=\"center\">OK"
T_TAIL = "</td></tr>\n"
T_STD_REPEATED = "Aluno repetido neste arquivo, submiss&atilde;o desconsiderada." 

## Helper functions

def is_binary(data):
    if '\0' in data: # found null byte
        return True
    return False

# prepara lista de cidades alocadas a esta sede
def busca_lista(s):
    query=' school_city in (0) '
    data=''
    with open('/usr/local/zope/obi/Extensions/sedes_fase2.txt','r') as fs:
        data=fs.readlines()
    for d in data:
        d=d.strip()
        if d=='' or d[0]=='#': continue
        tks=d.split(';')
        sede=int(tks[0])
        if sede!=s: continue
        tmp=tks[1].split('|')
        cidades=[]
        for t in tmp:
            lista=t.split(':')
            estado=lista[1]
            lista_cidades=lista[0].split(',')
            if (len(lista_cidades)==1 and lista_cidades[0]==''):
                cidades.append(" (school_state='"+estado+"') ")
            else:
                cidades.append(" (school_city in ('"+"','".join(lista_cidades)+"') and school_state='"+estado+"') ")
        lista_modalidades=tks[2].split(',')
        if len(lista_modalidades)>0 and len(lista_modalidades[0])>0:
            modalidades=" and compet_type in ("+",".join(lista_modalidades)+") "
        else:
            modalidades=''
        query="("+" or ".join(cidades)+")"+modalidades
        break
    return query


def dmsg(msg):
    """ Prints a debug message. """
    if DEBUG:
        sys.stderr.write(msg+"\n")

def write_res(txt):
    """ Writes a message to the result file. """
    resf.write(txt)
    resf.flush()

def bail_out():
    """ gives up """
    resf.write(TAIL)
    resf.flush()
    raise 'Give up'


def get_schs_stds(phase, school_id):
    """ Gets- schools/students from data base. """
    global conn
    school_id=int(school_id)
    #conn = psycopg2.connect(comm)
    curs = conn.cursor()
    if phase==1 or phase==2:
        curs.execute("select C.compet_id from compet as C, "
                 "school as S where C.compet_school_id = S.school_id and S.school_id = %s and compet_type=%d" % (school_id,compet_type))
    else:
        curs.execute("select C.compet_id from compet as C "
                 "where compet_type=%d and compet_classif_fase2=1" % (compet_type))
        # lista_escolas_sede=busca_lista(school_id)
        # curs.execute("select C.compet_id from compet as C, "
        #          "school as S where C.compet_school_id = S.school_id and %s and compet_type=%d and compet_classif_fase1=1" % (lista_escolas_sede,compet_type))
    data = curs.dictfetchall()
    conn.commit()
    return data


def insert_bd(school_id,phase,compet_id,sub_lang,sub_source,problem_name,problem_name_full):
    global conn
    curs = conn.cursor()
    comm = "delete from sub_fase%d where compet_id=%s and problem_name='%s';" % (phase, compet_id, problem_name)
    try:
        curs.execute(comm)
    except:
        print('delete failed')
        pass
    comm = "delete from res_fase%d where compet_id=%s and problem_name='%s';" % (phase, compet_id, problem_name)
    try:
        curs.execute(comm)
    except:
        pass

    curs.execute('insert into sub_fase1 (sub_school_id, sub_lang, compet_id, problem_name, problem_name_full, sub_source) values(%s, %s, %s, %s, %s, %s);', (school_id,sub_lang, compet_id, problem_name, problem_name_full, psycopg2.Binary(base64.b64encode(sub_source))))
    conn.commit()
    return 'OK'

def do_check(phase, sch_id, tfile, schs_stds, probs, sufs, is_zip):
    """ Checks the archive. """

    school_id=int(sch_id)
    print("do_check",file=sys.stderr)
    write_res(T_HEADER)

    try:
        tlist = tfile.namelist()
    except:
        try:
            tlist = tfile.getnames()
        except:
            dmsg(archive+" arquivo aparentemente corrompido")            
            write_res('Erro, arquivo aparentemente corrompido')
            return 0

    sch = {}
    for item in tlist:
        print(item,file=sys.stderr) 
        if item[-1]=='/':
            continue
        (prefix, src)=os.path.split(item)
        match=re.search('(^|/)(\d+-[A-Z])',prefix,re.IGNORECASE)
        if not match: continue
        std=match.group(2)
        print(prefix,src,std,file=sys.stderr)
        (snum,sconf)=std.split('-')
        snum=int(snum)
        std="%05d-%c" % (snum,sconf.upper())

        # for tk in os.walk(titem):
        #     print >> sys.stderr, 'tk=',tk[1]
        #     for item in tk[1]:
        #         print >> sys.stderr, 'item=',item
        #         if re.match('\d+-[A-Z]',item):
        #             print >> sys.stderr, "OK",std,tk
        if not std in sch:
            sch[std] = []
        if src:
            sch[std].append([item,src]) # string.lower(src))

    #print >> sys.stderr,"school list", sch
    #print >> sys.stderr,len(sch)
    # return value
    ret = 1
    if len(sch)==0:
        write_res(T_EMPY_STD)
        return 0

    # do the real checks
    for std in sch:
        # are the std's sources ok?
        submitted=[]  # stores the names of the programs submitted by the student
        for path,fname in sch[std]:
            dmsg("path=%s" % path)
            sanitized_path=path
            # windows is adding suffix .py to files with .py2 or .py3
            if (fname.find(".py2.py")!=-1) or (fname.find(".py3.py")!=-1):
                ind = path.rfind(".py")
                sanitized_path = path[:ind]
                ind = fname.rfind(".py")
                fname = fname[:ind]
            dmsg("fname=%s" % fname)

            if path.find("/")!=path.rfind("/"):
                ind = sanitized_path.find("/")
                sanitized_path = sanitized_path[ind+1:]
            dmsg("sanitized_path=%s" % sanitized_path)
            
            #print '--------- new fname', fname
            write_res(T_FILE_NAME % (sanitized_path))

            # is std in school nsch?
            if std not in schs_stds:
                dmsg("Competidor "+std+" nao cadastrado nesta escola")
                write_res(T_NO_STD)
                ret = 0
                continue

            ind = fname.find(".")
            if ind == -1:
                dmsg(fname+" do competidor "+std+" nao tem extensao")
                write_res(T_NO_EXTENSION)
                ret = 0
                continue

            pname = fname[:ind]
            psuf = fname[ind+1:]
            # windows is adding a .py extension!
            #ind = string.find(psuf,".")
            #if ind != -1:
            #    psuf = psuf[:ind]
            fok = True

            # is pname ok?
            if pname.lower() not in probs.keys():
                dmsg(fname+" do competidor "+std+" nao tem "
                     "nome de problema valido!")
                write_res(T_NO_PROB_NAME)
                fok = False

            # is psuf ok?
            if psuf.lower() not in sufs.keys():
                dmsg(fname+" do competidor "+std+" nao tem "
                     "extensao valida!")
                if fok:
                    write_res(T_INI_TD)
                else:
                    write_res(T_BR)
                write_res(T_NO_VALID_EXT)
                fok = False

            if fok:
                if submitted.count(pname.lower()) == 1:
                    write_res(T_INI_TD)
                    write_res(T_REPEATED)
                    fok = False
                else:
                    submitted.append(pname.lower())
                    
            if fok:
                if is_zip:
                    source=tfile.read(path)
                else:
                    fs=tfile.extractfile(path)                
                    source = fs.read()
                if len(source)==0:
                    dmsg(fname+" erro ao ler o arquivo, arquivo vazio")
                    source='';
                    write_res(T_INI_TD)
                    write_res(T_EMPTY_FILE)
                    #write_res(T_INI_TD)
                    #write_res(T_BADFILE)
                    fok = False
                if fok:
                    ######## apenas para a USP???
                    ######## source=source.replace('\302\250','"')
                    dmsg(pname.lower()+" "+std+" OK")
                    problem_name=pname.lower()
                    #if problem_name=='arco' and compet_type==6:
                    #    problem_name='arco_online'
                    insert_bd(school_id,phase, compet_id=int(std[:std.find('-')]),sub_lang=sufs[psuf.lower()],sub_source=source,problem_name=problem_name,problem_name_full=probs[pname.lower()])
                    write_res(T_TD_OK)
            else:
                ret = 0
            write_res(T_TAIL)

    return ret


## sanity check

def check_uploaded_file(school_id, archive, level, phase, RESULT_FILE):
    global resf
    global conn, compet_type
    
    print(RESULT_FILE,file=sys.stderr)

    ## open the result file and write the header
    resf = open(RESULT_FILE, "w+")
    write_res(HEADER)

    lang_suffixes = {"cc":2, "cpp":2, "c++":2, "c":1, "pas":3, "p":3, "py2":4, "java":5, "js":6, "py3":7}       ## hardcoded!!!

    if level=='pj':
        compet_type=5
        problems = {"zip":"Zip", "onibus":"Ônibus", "gomoku":"Gomoku"}  ## hardcoded!!!
    elif level=='p1':
        compet_type=3
        problems = {"zip":"Zip", "visita":"Visita entre cidades", "gomoku":"Gomoku", "bits":"bits"}  ## hardcoded!!!
    elif level=='p2':
        compet_type=4
        problems = {"taxa":"Taxa", "postes":"Postes", "imperio":"Dividindo o império", "arranhaceu":"Arranha-céu", "codigo":"Código"}  ## hardcoded!!!
    elif level=='pu':
        compet_type=6
        problems = {"carrinho":"Carrinho", "postes":"Postes", "imperio":"Dividindo o império", "arranhaceu":"Arranha-céu", "codigo":"Código"}  ## hardcoded!!!
    else:
        dmsg("Este nivel nao existe!")
        raise 'Give up'

    if not os.path.exists(archive):        # does the archive exist?
        dmsg(archive+" nao existe!")
        raise 'Give up'

    is_zip=True

    ## get the contents of the archive
    try:
        tfile = tarfile.open(archive, "r")
        file_list = tfile.getnames()
        print("tar", file_list,file=sys.stderr)
        is_zip=False
        #tfile.extractall()
        #tfile.close()
    except:
        try:
            tfile = zipfile.ZipFile(archive, "r")
            file_list = tfile.namelist()
            #tfile.extractall()
            #tfile.close()
        except:
            try:
                #print 'try bzip2'
                tfile = tarfile.open(archive, "r:bz2")
                file_list = tfile.getnames()
                is_zip=False
            except:
                dmsg(archive+" nao esta em nenhum dos formatos aceitos!")
                write_res(FORMAT_ERROR)
                write_res(TAIL)
                resf.close()
                raise 'Give up'


    ## get the schools/students, problem names and language suffixes
    ##   (note: all strings should be in lowercase)

    conn = psycopg1.connect("host=localhost dbname=%s user=obi password=guga.LC" % (DB_NAME))
    conn.set_client_encoding('utf-8')
    dtmp = get_schs_stds(phase,school_id)
    

    if len(dtmp)==0:
        write_res(SCHOOL_ERROR)
        write_res(TAIL)
        resf.close()
        raise 'Give up'

    print("OK",file=sys.stderr)

    schs_stds = []
    for item in dtmp:
        student = format_compet_id(item["compet_id"])
        if student in schs_stds:
            write_res(T_STD_REPEATED)
        else:
            schs_stds.append(student)


    ## now, check the contents of the archive!
    isok = do_check(phase, school_id, tfile, schs_stds, problems, lang_suffixes, is_zip)

    ## Finish the result file and close it
    write_res(TAIL)
    resf.close()

    if isok:
        print("isok",file=sys.stderr)

def usage():
    print("%s: school_id inputarchive level phase resultfile" % (sys.argv[0]))
    os._exit(1)

def main():
    try:
        school_id = sys.argv[1]
        archive = sys.argv[2]
        level =  sys.argv[3]
        phase =  int(sys.argv[4])
        RESULT_FILE = sys.argv[5]
        resf = open(RESULT_FILE, "w+")
    except:
        usage()
        dmsg("bad arguments, quitting.")
        os._exit(1)

    check_uploaded_file(school_id, archive, level, phase, RESULT_FILE)

if __name__ == "__main__":
    main()
