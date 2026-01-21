import json
import logging
import os
import re
import urllib
import urllib.parse
import urllib.request
from time import sleep
from urllib.request import urlopen

import requests
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import F
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.text import get_valid_filename

from principal.models import LANG_SUFFIXES_NAMES, LEVEL_NAME_FULL
from principal.models import (I1, I2, IJ, LANG_SUFFIXES_NAMES, LEVEL,
                              LEVEL_NAME, LEVEL_NAME_FULL, P1, P2, PJ, PS,
                              Compet, School, ResIni)
from principal.models import Colab, Compet, Deleg, ResWWW, School, SubWWW
from principal.utils.check_compet_points_batch import check_compet_points_batch
from principal.utils.check_solutions_file import check_solutions_file
from principal.utils.get_certif import (get_certif_colab, get_certif_compet,
                                       get_certif_deleg)
from principal.utils.utils import (calculate_page_size, format_compet_id, format_phone_number, get_data_cep,
                                   get_obi_date, get_obi_date_finish, make_password, obi_year, 
                                   calc_log_and_points, check_answers_file,
                                   verify_compet_id, write_uploaded_file, zip_submissions, write_school_uploaded_file)
from principal.utils.presence_lists import PrintPresenceList
from django.contrib.auth.decorators import user_passes_test, login_required

from restrito.views import erro, in_coord_group, in_coord_colab_group, in_coord_colab_full_group
from restrito.forms import CompetFiltroForm, CompetIniFiltroForm, CompetIniPontosFiltroForm, CompetProgPontosFiltroForm
from principal.views import search_compets
from tasks.models import Alternative, Question, Task
from tasks.views import rendertask
from obi.settings import BASE_DIR, DEBUG, DEFAULT_FROM_EMAIL, MEDIA_ROOT, YEAR
from exams.models import ExamFase1, ExamFase1b
from exams.views import show_results_all
from exams.views import check_exam_status
from exams.settings import EXAMS

logger = logging.getLogger(__name__)
MAX_POINTS_INI = 15

def in_compet_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='compet').exists()

#################
# results
#


####################
# Restrito
####################
from django.contrib.auth.decorators import user_passes_test
from restrito.views import in_coord_group
from sisca.utils.build_answer_sheet import draw_page, draw_pages
from sisca.utils.utils import pack_and_send
from reportlab.pdfgen import canvas

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def cadernos_tarefas_ini(request):
    return render(request,'fase0/restrito/caderno_tarefas_ini.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def cadernos_tarefas_prog(request):
    return render(request,'fase0/restrito/caderno_tarefas_prog.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def passo_a_passo_prog(request):
    return render(request,'fase0/restrito/passo_a_passo_prog.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def passo_a_passo_ini(request):
    return render(request,'fase0/restrito/passo_a_passo_ini.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def lista_presenca(request, level_name):
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ListaPresenca_{}.pdf"'.format(level_name)
    
    if level == IJ:
        subtitle1 = 'Modalidade Iniciação Nível Júnior'
    elif level == I1:
        subtitle1 = 'Modalidade Iniciação Nível 1'
    elif level == I2:
        subtitle1 = 'Modalidade Iniciação Nível 2'
    elif level == PJ:
        subtitle1 = 'Modalidade Programação Nível Júnior'
    elif level == P1:
        subtitle1 = 'Modalidade Programação Nível 1'
    elif level == P2:
        subtitle1 = 'Modalidade Programação Nível 2'
    elif level == PS:
        subtitle1 = 'Modalidade Programação Nível Sênior'
    else:
        # error!
        return
    
    title = f'OBI{YEAR} - Prova Teste'
    if level in (IJ,I1,I2):
        subtitle2 = 'Lista de Presença'
    else:
        subtitle2 = 'Lista de Presença'

    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    #compets = Compet.objects.filter(compet_classif_fase2=True)
    compets = Compet.objects.filter(compet_type=level)
    compets = compets.filter(compet_school_id=school_id)
    compets = compets.order_by('compet_name')
    data = [['Num. Inscr.','Nome', 'Assinatura'],]
    for c in compets:
        data.append((format_compet_id(c.compet_id),c.compet_name," "))
        
    report = PrintPresenceList(subtitle1)
    pdf = report.print_list(data, title, subtitle1, subtitle2)
    
    response.write(pdf)
    return response

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def folha_respostas(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="FolhaRespostas.pdf"'
    p = canvas.Canvas(response)
    label1 = 'Olimpíada Brasileira de Informática'
    label2 = 'Modalidade Iniciação'
    label3 = 'Prova Teste' # • {} a {}'.format(get_obi_date('ini-fase-1-prova',"%d/%m"),get_obi_date_finish('ini-fase-1-prova'))
    label4 = 'OBI{}'.format(YEAR)
    numquestions = 5
    numdigits = 5
    numalternatives = 5
    idcheck=True
    draw_page(p, label1, label2, label3, label4, numquestions, numdigits, idcheck, numalternatives, obi=True)
    p.save()
    return response 

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def folhas_respostas(request, level_name):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk    
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="FolhasRespostas.pdf"'
    p = canvas.Canvas(response)
    compets = Compet.objects.filter(compet_school_id=school_id)
    label1 = 'Olimpíada Brasileira de Informática'
    label3 = 'Prova Teste' # • {} a {}'.format(get_obi_date('ini-fase-1-prova',"%d/%m"),get_obi_date_finish('ini-fase-1-prova'))
    label4 = 'OBI{}'.format(YEAR)
    numquestions = 5
    numdigits = 5
    numalternatives = 5
    if level == IJ:
        tmp = compets.filter(compet_type=IJ).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível Júnior'
    elif level == I1:
        tmp = compets.filter(compet_type=I1).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível 1'
    elif level == I2:
        tmp = compets.filter(compet_type=I2).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível 2'

    if not tmp:
        return erro(request,'Não há competidores inscritos nessa modalidade e nível.')
    data = []
    for c in tmp:
        data.append((c.compet_id,c.compet_name))
    draw_pages(p, data, label1, label2, label3, label4, numquestions, numdigits, True, numalternatives, obi=True)
    p.save()
    return response 

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def lista_presenca(request, level_name):
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ListaPresenca_{}.pdf"'.format(level_name)
    
    if level == IJ:
        subtitle1 = 'Modalidade Iniciação Nível Júnior'
    elif level == I1:
        subtitle1 = 'Modalidade Iniciação Nível 1'
    elif level == I2:
        subtitle1 = 'Modalidade Iniciação Nível 2'
    elif level == PJ:
        subtitle1 = 'Modalidade Programação Nível Júnior'
    elif level == P1:
        subtitle1 = 'Modalidade Programação Nível 1'
    elif level == P2:
        subtitle1 = 'Modalidade Programação Nível 2'
    elif level == PS:
        subtitle1 = 'Modalidade Programação Nível Sênior'
    else:
        # error!
        return
    
    title = 'OBI{} - Prova Teste'.format(YEAR)
    if level in (IJ,I1,I2):
        subtitle2 = 'Lista de Presença' # • {} a {}'.format(get_obi_date('ini-fase-1-prova',"%d/%m"),get_obi_date_finish('ini-fase-1-prova'))
    else:
        subtitle2 = 'Lista de Presença' # • {} a {}'.format(get_obi_date('prog-fase-1-prova',"%d/%m"),get_obi_date_finish('prog-fase-1-prova'))

    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    
    #compets = Compet.objects.filter(compet_classif_fase2=True)
    compets = Compet.objects.filter(compet_type=level)
    compets = compets.filter(compet_school_id=school_id)
    compets = compets.order_by('compet_name')
    if not compets:
        return erro(request,'Não há competidores inscritos nessa modalidade e nível.')
    data = [['Num. Inscr.','Nome', 'Assinatura'],]
    for c in compets:
        data.append((format_compet_id(c.compet_id),c.compet_name," "))
        
    report = PrintPresenceList(subtitle1)
    pdf = report.print_list(data, title, subtitle1, subtitle2)
    
    response.write(pdf)
    return response

