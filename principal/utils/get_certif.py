#!/usr/bin/env python

# print certificates
import os
import platform
import shlex
import subprocess
import sys
import tempfile
import time
import qrcode
import re

import psycopg2
import psycopg2.extras

from obi.settings import BASE_DIR, YEAR

FIRST_YEAR_WITH_HASH=2021

from tempfile import TemporaryDirectory

from obi.settings import BASE_DIR
from principal.utils.medal_cuts import medal_cuts, medal_cuts_cf
#from principal.utils.medal_cuts_cf import medal_cuts_cf
from principal.utils.utils import slugfy, format_thousands

DB_HOST="localhost"

#print('\n'.join(sys.path))
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')

state_name = {
 'AC' : 'Acre',
 'AL' : 'Alagoas',
 'AM' : 'Amazonas',
 'AP' : 'Amapá',
 'BA' : 'Bahia',
 'CE' : 'Ceará',
 'DF' : 'Distrito Federal',
 'ES' : 'Espírito Santo',
 'GO' : 'Goiás',
 'MA' : 'Maranhão',
 'MG' : 'Minas Gerais',
 'MS' : 'Mato Grosso do Sul',
 'MT' : 'Mato Grosso',
 'PA' : 'Pará',
 'PB' : 'Paraíba',
 'PE' : 'Pernambuco',
 'PI' : 'Piauí',
 'PR' : 'Paraná',
 'RJ' : 'Rio de Janeiro',
 'RN' : 'Rio Grande do Norte',
 'RO' : 'Rondônia',
 'RR' : 'Roraima',
 'RS' : 'Rio Grande do Sul',
 'SC' : 'Santa Catarina',
 'SE' : 'Sergipe',
 'SP' : 'São Paulo',
 'TO' : 'Tocantins',
}

if platform.system() == 'Darwin':
    BASE_CERTIFS=os.path.join(BASE_DIR,"attic","certifs")
    PDFLATEX = "/Library/TeX/texbin/pdflatex"
    #PDFLATEX = "/opt/homebrew/bin/pdflatex"
else:
    BASE_CERTIFS=os.path.join(BASE_DIR,"attic","certifs")
    PDFLATEX = "/usr/bin/pdflatex"

def format_thousands(v):
    if not v:
        return 0
    thou = "."
    s = '{:.2f}'.format(float(v))
    integer, decimal = s.split(".")
    integer = re.sub(r"\B(?=(?:\d{3})+$)", thou, integer)
    return integer

roman_year={2005:'VII',2006:'VIII',2007:'IX',2008:'X',2009:'XI',2010:'XII',2011:'XIII',2012:'XIV',2013:'XV',2014:'XVI',2015:'XVII',2016:'XVIII',2017:'XIX',2018:'XX',2019:'XXI',2020:'XXII',2021:'XXIII',2022:'XXIV',2023:'XXV',2024:'XXVI',2025:'XXVII'}
space_left={2005:0,2006:0,2007:28,2008:28,2009:28,2010:28,2011:14,2012:14,2013:14,2014:14,2015:14,2016:14,2017:14,2018:14,2019:14,2020:14,2021:14,2022:14,2023:14,2024:14,2025:14}
text_size={2005:'huge',2006:'huge',2007:'huge',2008:'huge',2009:'huge',2010:'huge',2011:'Huge',2012:'Huge',2013:'Huge',2014:'Huge',2015:'Huge',2016:'Huge',2017:'Huge',2018:'Huge',2019:'Huge',2020:'Huge',2021:'Huge',2022:'Huge',2023:'Huge',2024:'Huge',2025:'Huge'}

WEEK_DATE = {2019: 'no Instituto de Computação da Unicamp de 1 a 7 de dezembro de 2019', 2020: 'online de 6 a 10 de dezembro de 2021', 2021: 'online de 6 a 10 de dezembro de 2021', 2023: 'no Instituto de Computação da Unicamp de 3 a 9 de dezembro de 2023', 2024: 'no Instituto de Computação da Unicamp de 1 a 7 de dezembro de 2024', 2025: 'no Instituto de Computação da Unicamp de 30 de novembro a 6 de dezembro de 2025'}


def get_qrcode(hash):
    qr = qrcode.QRCode(version = 1,
                       box_size = 10,
                       border = 2)    
    qr.add_data('http://olimpiada.ic.unicamp.br/certificados/verifica/'+hash)
    qr.make(fit = True)
    img = qr.make_image(fill_color = 'black',
                        back_color = 'white')
    img.save(f'{hash}.png')

# def get_certif_batch_compets(compets,year):
#     #write_log('get_certif_compet_batch_compets, year=%d' % (year))
#     # Consulta BD
#     global gold,silver,bronze,honor
#     db="obi%d" % year 
#     conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
#     conn.set_client_encoding('utf-8')
#     curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#     # build the tex file
#     f = open(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d.tex' % (year)), 'w')
#     f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

#     ###
#     # certifs compet
#     ###
#     comm = "select * from school,compet where compet_school_id=school_id and compet_points_fase1>=0 and compet_id in %s order by compet_type,compet_name" % str(tuple(compets))
#     curs.execute(comm)

#     #data = curs.fetchone()
#     #print("found", len(data), "participants")
#     #while data:
#     alldata = curs.fetchall()
#     for data in alldata:
#       school_id = data['school_id']
#       compet_id=data['compet_id']

#       if year >= 2022:
#           comm = f"select hash from certif_hash where compet_id={compet_id}"
#           curs.execute(comm)
#           hash = curs.fetchone()[0]
#           get_qrcode(hash)
#           f.write("\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}\n" % hash)
      
#       emit_certif_compet(compet_id,year,data,f,school_id)
#       #data = curs.fetchone()

#     f.write(tail_text)
#     f.close()
#     # build pdf
#     build_pdf(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d.tex' % (year)))
#     # return the certificate
#     imgf=open(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d.pdf' % (year)),"rb")
#     data=imgf.read()
#     imgf.close()
#     try:
#       os.unlink(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d_%d.pdf' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d_%d.tex' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d_%d.log' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifCompetBatch_%d_%d.aux' % (school_id,year)))
#     except:
#       pass
#     return(data)


def get_certif_school_compets(school_id,year,compets):
    write_log('get_certif_compet_school_compets, id=%d, year=%d' % (school_id,year))
    # Consulta BD
    # global gold,silver,bronze,honor
    # db="obi%d" % year 
    # conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    # conn.set_client_encoding('utf-8')
    # curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # comm = "select * from school where school_id = %d" % school_id
    # curs.execute(comm)
    # school = curs.fetchone()
    # school_name = school['school_name']
    # school_state = school['school_state']
    # print('school_name', school_name)
    
    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certifs compet
        ###
        for compet in compets:
            write_log(' school_id=%d' % school_id)
            compet_id=compet.compet_id

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash where compet_id={compet_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]

                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

            # kludge -- must fix it!!! Rewrite the whole thing...
            data = {}
            data['compet_id'] = compet.compet_id
            data['compet_type'] = compet.compet_type
            data['compet_name'] = compet.compet_name
            data['compet_school_id'] = compet.compet_school_id
            data['compet_points_fase1'] = compet.compet_points_fase1
            data['compet_rank_final'] = compet.compet_rank_final

            if compet.compet_type in (1,2,7) and year >= 2025:
                comm = "select * from compet as c, compet_extra as e, school as s where c.compet_school_id=school_id and c.compet_id=e.compet_id and c.compet_id=%d and compet_points_fase1 >=0" % compet.compet_id
                curs_year.execute(comm)
                data_extra = curs_year.fetchone()
            else:
                data_extra = None
            print(f"compet_id: {compet_id}, compet_name: {compet.compet_name},  data_extra:{data_extra}")
                
            emit_certif_compet(compet_id,year,data,f,data_extra=data_extra,school_id=school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)

def get_certif_school_compets_cf(school_id,year,compets):
    write_log('get_certif_compet_school_compets_cf, id=%d, year=%d' % (school_id,year))
    # Consulta BD
    # global gold,silver,bronze,honor
    # db="obi%d" % year 
    # conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    # conn.set_client_encoding('utf-8')
    # curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # comm = "select * from school where school_id = %d" % school_id
    # curs.execute(comm)
    # school = curs.fetchone()
    # school_name = school['school_name']
    # school_state = school['school_state']
    # print('school_name', school_name)
    
    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertifCf{year}.pdf"))

        ###
        # certifs compet
        ###
        for compet in compets:
            write_log(' school_id=%d' % school_id)
            compet_id=compet.compet_id

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash as h,compet_cfobi as c where h.compet_cf_id=c.id and c.compet_id={compet_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]

                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

            # kludge -- must fix it!!! Rewrite the whole thing...
            data = {}
            data['compet_id'] = compet.compet_id
            data['compet_type'] = compet.compet_type
            data['compet_name'] = compet.compet.compet_name
            data['compet_school_id'] = compet.compet.compet_school_id
            data['compet_points'] = compet.compet_points
            data['compet_rank'] = compet.compet_rank
            print(compet_id,year,data,f,school_id)
            emit_certif_compet_cf(compet_id,year,data,f,school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)

def get_certif_school_compets_old(school_id,year,compet_type=0):
    write_log('get_certif_compet_school_compets, id=%d, year=%d compet_type=%d' % (school_id,year,compet_type))
    # Consulta BD
    global gold,silver,bronze,honor
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certifs compet
        ###
        if compet_type==0:
            comm = "select * from school,compet where compet_school_id=school_id and compet_points_fase1>=0 and compet_school_id=%d order by compet_type,compet_name" % school_id
            #print(comm)
        else:
            comm = "select * from school,compet where compet_school_id=school_id and compet_points_fase1>=0 and compet_school_id=%d and compet_type=%d order by compet_type,compet_name" % (school_id,compet_type)
        curs.execute(comm)

        alldata = curs.fetchall()
        #print('len(alldata)',len(alldata))
        for data in alldata:
            write_log(' school_name=%s, school_state=%s' % (data['school_name'], data['school_state']))
            compet_id=data['compet_id']

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash where compet_id={compet_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]

                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)
      
            emit_certif_compet(compet_id,year,data,f,school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)

def get_certif_school_colabs(school_id,year):
    write_log('get_certif_compet_colabs id=%d, year=%d' % (school_id,year))
    # Consulta BD
    global gold,silver,bronze,honor
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        ###
        # certifs colabs
        ###
        comm = "select * from colab,school where school_id=%d and colab_school_id=%d order by colab_name" % (school_id,school_id)
        curs.execute(comm)
        alldata = curs.fetchall()
        if len(alldata) == 0:
            os.chdir(BASE_DIR)
            return(None)

        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        for data in alldata:
            colab_id=data['colab_id']

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash where colab_id={colab_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]
                
                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)
                
            emit_certif_colab(colab_id,year,data,f,school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        imgf=open('certif.pdf',"rb")
        data=imgf.read()
        imgf.close()

    os.chdir(BASE_DIR)
    return(data)

# def get_certif_school_all(school_id,year):
#     write_log('get_certif_school_all id=%d, year=%d' % (school_id,year))
#     # Consulta BD
#     global gold,silver,bronze,honor
#     db="obi%d" % year 
#     conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
#     conn.set_client_encoding('utf-8')
#     curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#     # build the tex file
#     f = open(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.tex' % (school_id,year)), 'w')
#     #f.write(head_text_no_picture)
#     f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))


#     ###
#     # certifs compet
#     ###
#     comm = "select * from school,compet where compet_school_id=school_id and compet_points_fase1>=0 and compet_school_id=%d order by compet_type,compet_name" % school_id
#     curs.execute(comm)

#     #data = curs.fetchone()
#     #while data:
#     alldata = curs.fetchall()
#     for data in alldata:
#       write_log(' school_name=%s, school_state=%s' % (data['school_name'], data['school_state']))
#       compet_id=data['compet_id']

#       if year >= FIRST_YEAR_WITH_HASH:
#           comm = f"select hash from certif_hash where compet_id={compet_id}"
#           curs.execute(comm)
#           hash = curs.fetchone()[0]
#           get_qrcode(hash)
#           f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)
      
#       emit_certif_compet(compet_id,year,data,f,school_id)
#       #data = curs.fetchone()

#     ###
#     # certif deleg
#     ###
#     comm = "select * from school where school_ok and school_id=%d" % school_id
#     curs.execute(comm)
#     data = curs.fetchone()
#     f.write(colab_body_text % (space_left[year], text_size[year], data['school_deleg_name'], roman_year[year], year))
#     if False: #data['school_fase2']==1:
#         f.write(deleg_text_fase2 % (data['school_city'],data['school_state']))
#         #f.write(deleg_text_fase2)
#     else:
#         f.write(deleg_text % (data['school_name']))
#     #f.write(end_text_no_picture % school_id)
#     f.write(end_text)

#     ###
#     # certifs colabs
#     ###
#     comm = "select * from colab,school where school_id=%d and colab_school_id=%d order by colab_name" % (school_id,school_id)
#     curs.execute(comm)

#     #data = curs.fetchone()
#     #while data:
#     alldata = curs.fetchall()
#     for data in alldata:
#       colab_id=data['colab_id']
#       emit_certif_colab(colab_id,year,data,f,school_id)
#       #data = curs.fetchone()

#     f.write(tail_text)
#     f.close()
#     # build pdf
#     build_pdf(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.tex' % (school_id,year)))
#     # return the certificate
#     imgf=open(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.pdf' % (school_id,year)),"rb")
#     data=imgf.read()
#     imgf.close()
#     try:
#       os.unlink(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.pdf' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.tex' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.log' % (school_id,year)))
#       os.remove(os.path.join(BASE_CERTIFS,'CertifEscola_%d_%d.aux' % (school_id,year)))
#     except:
#       pass
#     return(data)

def get_certif_list_compets(year,compets):
    write_log('get_certif_list_school_compets, year=%d' % (year))
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certifs compet
        ###
        for compet in compets:
            compet_id=compet.compet_id

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash where compet_id={compet_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]

                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

            # kludge -- must fix it!!! Rewrite the whole thing...
            data = {}
            data['compet_id'] = compet.compet_id
            data['compet_type'] = compet.compet_type
            data['compet_name'] = compet.compet_name
            data['compet_school_id'] = compet.compet_school_id
            data['compet_points_fase1'] = compet.compet_points_fase1
            data['compet_rank_final'] = compet.compet_rank_final
            school_id = compet.compet_school_id
            print(compet_id,year,data,f,school_id)
            emit_certif_compet(compet_id,year,data,f,school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)


def get_certif_cf_list_compets(year,compets):
    write_log('get_certif_cf_list_school_compets, year=%d' % (year))
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
    
        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certifs compet
        ###
        for compet in compets:
            compet_id=compet.compet_id

            if year >= FIRST_YEAR_WITH_HASH:

                db_name = f'obi{year}'
                conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
                conn_year.set_client_encoding('utf-8')
                curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
                comm = f"select hash from certif_hash where compet_id={compet_id}"
                curs_year.execute(comm)
                hash = curs_year.fetchone()[0]

                get_qrcode(hash)
                f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

            # kludge -- must fix it!!! Rewrite the whole thing...
            data = {}
            data['compet_id'] = compet.compet_id
            data['compet_type'] = compet.compet_type
            data['compet_name'] = compet.compet.compet_name
            data['compet_school_id'] = compet.compet.compet_school_id
            data['compet_points'] = compet.compet_points
            data['compet_rank'] = compet.compet_rank
            school_id = compet.compet.compet_school_id
            print(compet_id,year,data,f,school_id)
            emit_certif_compet_cf(compet_id,year,data,f,school_id)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)


def get_certif_colab(colab_id,year):
    write_log('get_certif_colab id=%d, year=%d' % (colab_id,year))
    # Consulta BD
    global gold,silver,bronze,honor
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)

        # build the tex file
        f = open('certif.tex','w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certif colab
        ###
        comm = "select * from colab,school where school_ok and school_id=colab_school_id and colab_id=%d order by colab_name" % (colab_id)
    
        curs.execute(comm)

        data = curs.fetchone()
        colab_id=data['colab_id']

        if year >= FIRST_YEAR_WITH_HASH:

            db_name = f'obi{year}'
            conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
            conn_year.set_client_encoding('utf-8')
            curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
            comm = f"select hash from certif_hash where colab_id={colab_id}"
            curs_year.execute(comm)
            hash = curs_year.fetchone()[0]
            
            get_qrcode(hash)
            f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

        emit_certif_colab(colab_id,year,data,f)

        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        imgf=open('certif.pdf',"rb")
        data=imgf.read()
        imgf.close()
    os.chdir(BASE_DIR)
    return(data)


def get_week_certif_monitor(monitor_name, genre, hours, year):
    write_log('get_week_certif_monitor=%s, year=%d' % (monitor_name,year))
    suffix = ''
    if genre=='F':
        suffix = 'A'

    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        
        # build the tex file
        f = open('certif.tex', 'w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
        f.write(week_monitor_body_text % (space_left[year], 'Large', monitor_name, suffix, roman_year[year], year, WEEK_DATE[year], hours))
        f.write(end_text)
        f.write(tail_text)
        f.close()

        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        imgf=open('certif.pdf',"rb")
        data=imgf.read()
        imgf.close()
        
    return(data)


def get_week_certif_monitor_lab(monitor_name, genre, hours, year):
    write_log('get_week_certif_monitor=%s, year=%d' % (monitor_name,year))
    suffix = ''
    if genre=='F':
        suffix = 'A'
    
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        
        # build the tex file
        f = open('certif.tex', 'w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
        f.write(week_monitor_lab_body_text % (space_left[year], 'Large', monitor_name, suffix, roman_year[year], year, WEEK_DATE[year], hours))
        f.write(end_text)
        f.write(tail_text)
        f.close()

        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        imgf=open('certif.pdf', "rb")
        data=imgf.read()
        imgf.close()

    return(data)


def get_week_certif_seletiva_monitor(monitor_name, genre, hours, year):
    write_log('get_week_certif_seletiva_monitor=%s, year=%d' % (monitor_name,year))
    suffix = ''
    if genre=='F':
        suffix = 'A'
    
    # build the tex file
    slug = slugfy(monitor_name)
    f = open(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.tex' % (slug,year)), 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
    f.write(week_monitor_seletiva_body_text % (space_left[year], 'LARGE', monitor_name, suffix, roman_year[year], year, hours))
    f.write(end_text)
    f.write(tail_text)
    f.close()

    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.tex' % (slug,year)))
    # return the certificate
    imgf=open(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.pdf' % (slug,year)),"rb")
    data=imgf.read()
    imgf.close()
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.pdf' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.tex' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.log' % (slug,year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifMonitor_%s_%d.aux' % (slug,year)))
    except:
      pass
    return(data)


def get_week_certif_professor(professor_name, genre, course, year):
    
    write_log('get_week_certif_professor=%s, year=%d' % (professor_name,year))
    print(f'get_week_certif_professor={professor_name}, course={course}, year={year}')
    suffix = ''
    if genre=='F':
        suffix = 'A'

    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        
        # build the tex file
        f = open('certif.tex', 'w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))
        if course == 'Seletiva Competições Internacionais':
            f.write(week_setter_body_text % (space_left[year], 'LARGE', professor_name, suffix, roman_year[year], year, WEEK_DATE[year]))
        else:
            f.write(week_professor_body_text % (space_left[year], 'LARGE', professor_name, suffix, roman_year[year], year, WEEK_DATE[year]))
        f.write(end_text)
        f.write(tail_text)        
        f.close()

        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = None
    os.chdir(BASE_DIR)
    return(data)

def get_certif_deleg(school_id,year):
    write_log('get_certif_deleg id=%d, year=%d' % (school_id,year))
    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        # build the tex file
        f = open('certif.tex', 'w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        ###
        # certif deleg
        ###
        comm = "select * from school where school_ok and school_id=%d" % school_id
        curs.execute(comm)
        data = curs.fetchone()
        
        if year >= FIRST_YEAR_WITH_HASH:

            db_name = f'obi{year}'
            conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
            conn_year.set_client_encoding('utf-8')
            curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
            comm = f"select hash from certif_hash where school_id={school_id}"
            curs_year.execute(comm)
            hash = curs_year.fetchone()[0]

            get_qrcode(hash)
            f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)
    
        f.write(colab_body_text % (space_left[year], text_size[year], data['school_deleg_name'], roman_year[year], year))
        if False: # 'school_fase2' in data.keys() and data['school_fase2']==1:
            f.write(deleg_text_fase2 % (data['school_city'],data['school_state']))
            #f.write(deleg_text_fase2)
        else:
            f.write(deleg_text % (data['school_name']))
        f.write(end_text)
        f.write(tail_text)
        f.close()

        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        imgf=open('certif.pdf',"rb")
        data=imgf.read()
        imgf.close()

    os.chdir(BASE_DIR)
    return(data)


def get_certif_compet(compet_id,year):
    print('get_certif_compet id=%d, year=%d' % (compet_id,year))
    write_log('get_certif_compet id=%d, year=%d' % (compet_id,year))
    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    #comm = "select * from compet as c, compet_extra as e, school as s where c.compet_school_id=school_id and c.compet_id=e.compet_id and c.compet_id=%d and compet_points_fase1 >=0" % compet_id
    #print('comm',comm)
    curs.execute(comm)
    data = curs.fetchone()
    if not data:
            return ''
    if data['compet_type'] in (1,2,7) and year >= 2025:
        comm = "select * from compet as c, compet_extra as e, school as s where c.compet_school_id=school_id and c.compet_id=e.compet_id and c.compet_id=%d and compet_points_fase1 >=0" % compet_id
        curs.execute(comm)
        data_extra = curs.fetchone()
    else:
        data_extra = None
        
    # build the tex file

    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)        
        f = open('certif.tex', 'w')
        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

        if year >= FIRST_YEAR_WITH_HASH:

            db_name = f'obi{year}'
            conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
            conn_year.set_client_encoding('utf-8')
            curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
            comm = f"select hash from certif_hash where compet_id={compet_id}"
            curs_year.execute(comm)
            hash = curs_year.fetchone()[0]

            get_qrcode(hash)
            f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

        emit_certif_compet(compet_id,year,data,f,data_extra)
        f.write(tail_text)
        f.close()

        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)
        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = ''

    os.chdir(BASE_DIR)    
    return(data)


def get_certif_compet_cf(compet_id,year):
    write_log('get_certif_compet_cf id=%d, year=%d' % (compet_id,year))

    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    comm = "select cf.compet_id, cf.compet_type, cf.compet_rank, cf.compet_points, c.compet_name, c.compet_school_id from compet_cfobi as cf,compet as c where c.compet_id=cf.compet_id and c.compet_id=%d" % compet_id
    #print('comm',comm)
    curs.execute(comm)
    # build the tex file
    data = curs.fetchone()

    #cur_dir = os.getcwd()
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)

        f = open('certif.tex', 'w')

        f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertifCf{year}.pdf"))

        if year >= FIRST_YEAR_WITH_HASH:

            db_name = f'obi{year}'
            conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
            conn_year.set_client_encoding('utf-8')
            curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
            comm = f"select hash from certif_hash as h,compet_cfobi as c where h.compet_cf_id=c.id and c.compet_id={compet_id}"
            curs_year.execute(comm)
            hash = curs_year.fetchone()[0]

            get_qrcode(hash)
            f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

        emit_certif_compet_cf(compet_id,year,data,f)
        f.write(tail_text)
        f.close()
        # build pdf
        build_pdf(tmpdirname,'certif.tex', year)

        result = subprocess.call([PDFLATEX, "-interaction=nonstopmode", "-halt-on-error", 'certif.tex'],timeout=15)


        # return the certificate
        try:
            imgf=open('certif.pdf',"rb")
            data=imgf.read()
            imgf.close()
        except:
            data = ''

    #os.chdir(cur_dir)
    os.chdir(BASE_DIR)
    return(data)

def get_week_certif_compet(compet_id,level,year):
    write_log('get_week_certif_compet id=%d, year=%d' % (compet_id,year))
    # Consulta BD
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    #comm = "select * from compet where compet_id=%d and compet_points_fase1 >= 0" % compet_id
    comm = "select * from compet where compet_id=%d" % compet_id
    curs.execute(comm)
    # build the tex file
    data = curs.fetchone()
    name = data[1]
    f = open(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.tex' % (compet_id,year)), 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

    if year >= FIRST_YEAR_WITH_HASH:

        db_name = f'obi{year}'
        conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
        conn_year.set_client_encoding('utf-8')
        curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
        comm = f"select hash from certif_hash where compet_id={compet_id}"
        curs_year.execute(comm)
        hash = curs_year.fetchone()[0]

        # do not use qr codes for this certificate
        # get_qrcode(hash)
        # f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)

    emit_week_certif_compet(compet_id,level,year,name,f)
    f.write(tail_text)
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.tex' % (compet_id,year)))
    # return the certificate
    try:
        imgf=open(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.pdf' % (compet_id,year)),"rb")
        data=imgf.read()
        imgf.close()
    except:
        data = ''
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.pdf' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.tex' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.log' % (compet_id,year)))
      os.remove(os.path.join(BASE_CERTIFS,'Certif_%06d_%d.aux' % (compet_id,year)))
    except:
      pass
    return(data)


def emit_certif_compet(compet_id,year,data,f,data_extra=None,school_id=None):

    write_log('in emit_certif_compet, id=%d' % (compet_id))
    global gold,silver,bronze,honor
    if not data:
        return

    print(f"compet_id={compet_id}, using data_extra={data_extra}")
    school_id=data['compet_school_id']
    level=data['compet_type']
    rank = data['compet_rank_final']
    if level in (1,2,7) and year >= 2025 and data_extra:
        state_rank = data_extra['compet_state_rank_fase2']
        state = state_name[data_extra['school_state']]
    else:
        state_rank = None
        state = ''
    compet_points_fase1=data['compet_points_fase1']
    #print level, 
    #print year
    gold,silver,bronze,honor,mod,level,total=medal_cuts(level,year)

    #print(gold,silver,bronze,honor,mod,level,total)
    medal=get_medal(rank)
    if rank==None:
        rank=1000000
    medal=get_medal(rank)
    try:
        name=data['compet_name']
    except:
        print('failed to get compet name', data['compet_id'], data['compet_name'],file=sys.stderr)
        exit(1)
    if mod=='Universitária':
      f.write(body_text_univ % (space_left[year], text_size[year], name, roman_year[year], year, mod))
    else:
      f.write(body_text % (space_left[year], text_size[year], name, roman_year[year], year, mod, level))

    if compet_points_fase1!=None and compet_points_fase1>=0:
        if rank!=None:
            if medal!='' or total/rank>4:
                formatted_total = format_thousands(total)
                formatted_rank = format_thousands(rank)
                f.write(text_rank % (formatted_rank,formatted_total))
            if medal!='':
                if state_rank!=None:
                    f.write(text_medal_and_state_hm % (medal, state))
                else:
                    f.write(text_medal % (medal))
            elif state_rank!=None:
                f.write(text_state_hm % state)
        elif state_rank!=None:
            f.write(text_state_hm % state)
        
    #if school_id!=None:
    #  f.write(end_text_no_picture % school_id)
    #else:
    f.write(end_text)
    write_log('returning from emit_certif_compet, get_certif_compet id=%d' % (compet_id))

    

def emit_certif_compet_cf(compet_id,year,data,f,school_id=None):
    global gold,silver,bronze,honor
    if not data:
        return

    school_id=data['compet_school_id']
    level=data['compet_type']
    rank = data['compet_rank']
    compet_points = data['compet_points']

    print('data', data)
    
    gold,silver,bronze,honor,mod,level,total=medal_cuts_cf(level,year)
    #print(gold,silver,bronze,honor,mod,level,total)
    medal=get_medal(rank)
    if rank==None:
        rank=1000000
    medal=get_medal(rank)
    try:
        name=data['compet_name']
    except:
        print('failed to get compet name', data['compet_id'], data['compet_name'],file=sys.stderr)
        exit(1)

    f.write(body_text_cf % (space_left[year], text_size[year], name, roman_year[year], year, mod, level))

    if compet_points!=None and compet_points>=0 and rank!=None:
        if medal!='' or total/rank>4:
            formatted_total = format_thousands(total)
            formatted_rank = format_thousands(rank)
            f.write(text_rank % (formatted_rank,formatted_total))
        if medal!='':
            f.write(text_medal % (medal))

    #if school_id!=None:
    #  f.write(end_text_no_picture % school_id)
    #else:
    f.write(end_text)

def emit_week_certif_compet(compet_id,level,year,name,f,school_id=None):
    if level == 1:
        f.write(week_body_text_i1 % (space_left[year], 'LARGE', name, roman_year[year], year, WEEK_DATE[year]))
    elif level == 2:
        f.write(week_body_text_i2 % (space_left[year], 'LARGE', name, roman_year[year], year, WEEK_DATE[year]))
    elif level == 3:
        f.write(week_body_text_p1 % (space_left[year], 'LARGE', name, roman_year[year], year, WEEK_DATE[year]))
    elif level == 4:
        f.write(week_body_text_p2 % (space_left[year], 'LARGE', name, roman_year[year], year, WEEK_DATE[year]))
    elif level == 5:
        f.write(week_body_text_pj % (space_left[year], 'LARGE', name, roman_year[year], year, WEEK_DATE[year]))
    else:
        print('wrong compet level', compet_level, compet_id, compet_name, file=sys.stderr)
        exit(1)
        
    f.write(end_text)

# delegados

def emit_certif_colab(colab_id,year,data,f,school_id=None):
    f.write(colab_body_text % (space_left[year], text_size[year], data['colab_name'], roman_year[year], year))
    if False: #'school_fase2' in data.keys() and data['school_fase2']==1:
        f.write(colab_text_fase2 % (data['school_city'],data['school_state']))
        #f.write(colab_text_fase2)
    else:
        f.write(colab_text % (data['school_name']))
    #if school_id!=None:
    #  f.write(end_text_no_picture % school_id)
    #else:
    f.write(end_text)
      
head_text = '''\\documentclass[landscape,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[portuges]{babel}
\\usepackage[landscape]{geometry}
\\usepackage{graphicx}
\\usepackage{eso-pic}
\\pagestyle{empty}

\\setlength{\\textwidth}{8in}           
\\setlength{\\topmargin}{0.4in}         
\\setlength{\\leftmargin}{0.0in}        
\\setlength{\\parskip}{1.2ex}
\\setlength{\\parindent}{0mm}

\\newcommand\\BackgroundPic{
  \\put(0,0){
    \\parbox[b][\\paperheight]{\\paperwidth}{
      \\vfill
      \\centering
      \\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio]{%s}
      \\vfill
    }
  }
}


\\newcommand{\\esimo}{\\mbox{\\raisebox{1ex}{\\rm\\b{\\small o}}}}

\\begin{document}
\\AddToShipoutPicture{\\BackgroundPic}
'''

head_text_no_picture = '''\\documentclass[landscape,a4paper]{article}
\\usepackage[utf8]{inputenc}
\\usepackage[portuges]{babel}
\\usepackage[landscape]{geometry}
\\pagestyle{empty}

\\setlength{\\textwidth}{8in}           
\\setlength{\\topmargin}{0.6in}         
\\setlength{\\leftmargin}{0.0in}        
\\setlength{\\parskip}{1.2ex}
\\setlength{\\parindent}{0mm}

\\newcommand{\\esimo}{\\mbox{\\raisebox{1ex}{\\rm\\b{\\small o}}}}

\\begin{document}

'''

body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou da %s Olimpíada Brasileira de Informática (OBI%d), 
Modalidade %s Nível %s'''

body_text_cf = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou da Competição Feminina da %s Olimpíada Brasileira de Informática (OBI%d), 
Modalidade %s Nível %s'''

body_text_univ = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou da %s Olimpíada Brasileira de Informática (OBI%d), 
Modalidade %s'''

text_rank= ", tendo obtido o %s\\hspace*{1mm}\\esimo\\ lugar entre %s participantes"
text_medal= " (%s)"
text_medal_and_state_hm= " (%s e Menção Honrosa Estadual - %s)"
text_state_hm= " (Menção Honrosa Estadual - %s)"

end_text='''.

\\end{minipage}
\\newpage
'''

end_text_no_picture='''.

\\end{minipage}
\\vfill
\\hspace{10mm}
{\\tiny e%d}
\\newpage
'''

tail_text = '''
\\end{document}
'''
#####
# colabs
#####
colab_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

colaborou com a %s Olimpíada Brasileira de Informática (OBI%d), '''


colab_text = 'trabalhando na organização da competição na escola \\emph{%s}'
#deleg_text = 'atuando como Delegado(a) da OBI na escola \\emph{%s}'
deleg_text = 'atuando como Coordenador(a) da OBI na escola \\emph{%s}'

#colab_text_fase2 = 'trabalhando na organização da competição na Sede Regional da Fase 2 da OBI em %s (%s)'
#deleg_text_fase2 = 'atuando como Delegado(a) da OBI na Sede Regional da Fase 2 em %s (%s)'



week_body_text_i1 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \\emph{Introdução à Programação de Computadores em C/C++} durante a  Semana Olímpica da OBI, 
para os melhores colocados da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, num total de 35 horas'''

week_body_text_i2 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \\emph{Introdução à Programação de Computadores em C/C++} durante a  Semana Olímpica da OBI, 
para os melhores colocados da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, num total de 35 horas'''

week_body_text_pj = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \\emph{Introdução a Técnicas de Programação, Estruturas de Dados e Algoritmos} durante a Semana Olímpica da OBI, 
para os melhores colocados da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, num total de 35 horas'''

week_body_text_p1 = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

participou do curso \\emph{Técnicas de Programação, Estruturas de Dados e Algoritmos} durante a Semana Olímpica da OBI, 
para os melhores colocados da %s Olimpíada Brasileira
de Informática (OBI%d). O Curso foi realizado %s e consistiu
de aulas teóricas e atividades práticas, num total de 35 horas'''

week_monitor_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\LARGE \\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI, 
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Semana Olímpica ocorreu %s. Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos
em Programação de Computadores, Estrutura de Dados e Algoritmos. 
O trabalho dos monitores foi acompanhar os alunos em todas as atividades,
durante toda a semana, além de auxiliar na organização da Semana Olímpica, totalizando %d horas de monitoria'''

week_monitor_lab_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\LARGE \\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s DE LABORATÓRIO durante a Semana Olímpica da OBI, 
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Semana Olímpica ocorreu %s. Durante a Semana Olímpica os alunos assistiram
a aulas teóricas e realizaram atividades práticas sobre tópicos
em Programação de Computadores, Estrutura de Dados e Algoritmos. 
O trabalho dos monitores foi auxiliar os alunos durante as 
atividades práticas, totalizando %d horas de monitoria'''

week_monitor_seletiva_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como MONITOR%s durante a Semana Olímpica da OBI -- Seletiva Competições Internacionais, 
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s). A Seletiva Competições Internacionais ocorreu
no Instituto de Computação da Unicamp, entre os dias 1 e 7 de maio de 2022. 
O trabalho dos monitores foi auxiliar os alunos durante as 
atividades práticas, totalizando %d horas de monitoria'''

week_professor_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como PROFESSOR%s durante a Semana Olímpica da OBI2025,
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s), tendo ministrado aulas teóricas e práticas,
totalizando 40 horas de atividades. A Semana Olímpica da OBI2025 foi
realizada %s'''

week_setter_body_text = '''
\\vspace*{3mm}
\\hspace*{%dmm}\\begin{minipage}[t]{1\\textwidth}
\\%s
Certificamos que

\\begin{center}
{\\bf \\emph{%s}}
\\end{center}

trabalhou como PROFESSOR%s durante a Semana Olímpica da OBI2025,
oferecida aos melho\\-res colocados da %s Olimpíada Brasileira
de Informática (OBI%s), tendo participado da elaboração e aplicação
das provas para a Seletiva para Competições Internacionais,
totalizando 40 horas de atividades. A Semana Olímpica da OBI2025 foi
realizada %s.'''

#---------------------------------------------------------------------------

def build_pdf(dirname, texfile, year):
    os.symlink(os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"), os.path.join(dirname,f"FundoCertif{year}.pdf"))
    
    #old = os.getcwd()
    #os.chdir(BASE_CERTIFS)

    result = subprocess.call([PDFLATEX, "-interaction=nonstopmode", "-halt-on-error", texfile],timeout=15)
    '''
    with open('/dev/null', 'w') as dev_null:
        result = subprocess.call(["pdflatex", "%s" % texfile],
                           stdin = dev_null,
                           stdout = dev_null,
                           stderr = dev_null)
    '''
    if result !=0:
      print("cannot build pdf:", result, file=sys.stderr)
    #os.chdir(old)

#---------------------------------------------------------------------------

def get_medal(rank):
    global gold,silver,bronze,honor
    if not rank:
      return ''
    if (rank<=gold):
        medal='Medalha de Ouro'
    elif (rank<=silver):
        medal='Medalha de Prata'
    elif (rank<=bronze):
        medal='Medalha de Bronze'
    elif (rank<=honor):
        medal='Honra ao Mérito'
    else:
        medal=''
    return medal

#---------------------------------------------------------------------------

def CurrentTime():
  return time.strftime('%Hh%Mm%Ss',time.localtime(time.time()))

#---------------------------------------------------------------------------

def CurrentDate():
  return time.strftime('%Y-%m-%d',time.localtime(time.time()))

#---------------------------------------------------------------------------

def write_log(msg):
    with open(os.path.join(BASE_CERTIFS,'LOG'), 'a') as f:
      f.write(CurrentDate()+" "+CurrentTime()+": %s\n" % msg)

#---------------------------------------------------------------------------

def print_all_certifs(year):
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    comm = "select school_id from school where school_ok order by school_id"
    curs.execute(comm)

    data = curs.fetchone()
    while data:
      get_certif_school_all(data['school_id'],year)
      data = curs.fetchone()


def get_certif_olimp_week(year):
    write_log('get_certif_olimp_week year=%d' % (year))
    # Consulta BD
    global gold,silver,bronze,honor
    db="obi%d" % year 
    conn = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db))
    conn.set_client_encoding('utf-8')
    curs = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # build the tex file
    f = open(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.tex' % (year)), 'w')
    f.write(head_text % os.path.join(BASE_CERTIFS,f"FundoCertif{year}.pdf"))

    ###
    # certifs compet
    ###
    for compet_type in (1,2,3,4,5):
      #comm = "select * from compet,school,week where compet_school_id=school_id and week.compet_id=compet.compet_id and compet_type=%d;" % (compet_type)
      comm = "select * from compet,school,week where compet_school_id=school.school_id and week.compet_id=compet.compet_id and compet.compet_id=week.compet_id and compet.compet_type=%d" % (compet_type)
      curs.execute(comm)
      data = curs.dictfetchall()
      #print >> sys.stderr, "found", len(data), "participants in level",compet_type
      for d in data:
        compet_id=d['compet_id']
        school_id=d['school_id']
        #print >> sys.stderr, compet_id,school_id

        if year >= FIRST_YEAR_WITH_HASH:

            db_name = f'obi{year}'
            conn_year = psycopg2.connect("host=%s dbname=%s user=obi password=guga.LC" % (DB_HOST,db_name))
            conn_year.set_client_encoding('utf-8')
            curs_year = conn_year.cursor(cursor_factory=psycopg2.extras.DictCursor)
            comm = f"select hash from certif_hash where compet_id={compet_id}"
            curs_year.execute(comm)
            hash = curs_year.fetchone()[0]

            get_qrcode(hash)
            f.write(r"\includegraphics[scale=0.3, trim=11cm 0 0 12cm]{%s.png}" % hash)
        
        emit_certif_compet(compet_id,year,d,f,school_id)

    f.write(tail_text)
    f.close()
    # build pdf
    build_pdf(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.tex' % (year)))
    # return the certificate
    imgf=open(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.pdf' % (year)),"rb")
    data=imgf.read()
    imgf.close()
    try:
      os.unlink(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.pdf' % (year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.tex' % (year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.log' % (year)))
      os.remove(os.path.join(BASE_CERTIFS,'CertifCompetWeek_%d.aux' % (year)))
    except:
      pass
    return(data)


if __name__=="__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'obi.settings')
    #get_certif_colab(colab_id=123,year=2005)
    #get_certif_colab(colab_id=992,year=2013)
    #get_certif_colab(colab_id=596,year=2012)
    #get_certif_compet(
  
    #print_all_certifs(2014)
    #get_certif_school_compets(compet_type=0,school_id=384,year=2014)
    #get_certif_school_colabs(school_id=2,year=2014)
    #get_certif_compet(compet_id=3339,year=2014)
    #get_certif_compet(compet_id=26227,year=2015)
    #get_certif_compet(compet_id=26227,year=2016)
    #get_certif_compet(compet_id=43455,year=2016)
    #get_certif_school_colabs(school_id=1,year=2016)
    #get_certif_olimp_week(year=2016)
    #get_certif_compet(compet_id=23486,year=2017)
    #get_certif_colab(colab_id=490,year=2017)
    #get_certif_compet(compet_id=1402,year=2013)
    
    #get_certif_compet(compet_id=28707,year=2018)
    #get_certif_school_all(school_id=1,year=2018)
    
    #get_certif_colab(colab_id=35,year=2018)
    #get_certif_compet(compet_id=8753,year=2020)
    #get_certif_olimp_week(year=2018)
    #get_week_certif_compet(compet_id=28446,level=3,year=2021)
    #print("OK",file=sys.stderr)
    #get_week_certif_seletiva_monitor(monitor_name="Luã",genre="M",hours=35,year=2021)
