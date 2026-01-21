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

from principal.models import CompetCfObi

from principal.models import LANG_SUFFIXES_NAMES, LEVEL_NAME_FULL
from principal.models import (I1, I2, IJ, LANG_SUFFIXES_NAMES, LEVEL,
                              LEVEL_NAME, LEVEL_NAME_FULL, P1, P2, PJ, PS,
                              SEX_CHOICES_CFOBI, LEVEL_CFOBI,
                              Compet, School, ResIni)
from principal.forms import ConsultaCompetidoresForm
from principal.models import Colab, Compet, CompetDesclassif, Deleg, ResWWW, School, SubWWW
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
from restrito.forms import CompetFiltroForm, CompetIniFiltroForm, CompetIniPontosFiltroForm, CompetProgPontosFiltroForm, CompetFemininaFiltroForm, CompetFemininaPontosFiltroForm
from principal.views import search_compets
from tasks.models import Alternative, Question, Task
from tasks.views import rendertask
from obi.settings import BASE_DIR, DEBUG, DEFAULT_FROM_EMAIL, MEDIA_ROOT, YEAR

#from .models import PointsFase2,SubFase2, ResFase2
from exams.models import ExamFase2
from exams.views import show_results_all
from exams.settings import EXAMS

from restrito.views import (in_coord_group, in_coord_colab_group, in_coord_colab_full_group)

logger = logging.getLogger(__name__)
MAX_POINTS_INI = 20

def in_compet_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='compet').exists()


#################
# results
#

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def grecaptcha_verify(request):
  return True
  if DEBUG:
      return True
  try:
    if request.method == 'POST':
        response = {}
        data = request.POST
        captcha_rs = data.get('g-recaptcha-response')
        url = "https://www.google.com/recaptcha/api/siteverify"
        params = {
            'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
            'response': captcha_rs,
            'remoteip': get_client_ip(request)
        }
        verify_rs = requests.get(url, params=params, verify=True)
        verify_rs = verify_rs.json()
        #print('will return',verify_rs['success'])
        return verify_rs['success']
    else:
        return False
  except:
      return False

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def passo_a_passo_prog(request):
    return render(request,'cfobi/restrito/passo_a_passo_prog.html', {})

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
    return render(request,'cfobi/restrito/caderno_tarefas_ini.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def cadernos_tarefas_prog(request):
    return render(request,'cfobi/restrito/caderno_tarefas_prog.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_classif_prog(request):
    return compet_lista_classif(request,mod='p')




@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_classif(request,mod):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    if mod == 'i':
        compets = Compet.objects.filter(compet_school_id=school_id, compet_classif_cfobi=True,compet_type__in=(1,2,7))
    else:
        compets = Compet.objects.filter(compet_school_id=school_id, compet_classif_cfobi=True,compet_type__in=(3,4,5,6))
    total = len(compets)
    if request.method == 'POST':
        # default
        compet_list_order = 'compet_points'
        
        if mod == 'i':
            form = CompetIniPontosFiltroForm(request.POST)
        else:
            #form = CompetProgPontosFiltroForm(request.POST)
            form = CompetFemininaPontosFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_list_order = f['compet_order']
            compet_list_name = f['compet_name']
            compet_list_type = f['compet_type']
            request.session['compet_list_name'] = compet_list_name
            request.session['compet_list_order'] = compet_list_order
            request.session['compet_list_type'] = compet_list_type
    else:
        try:
            compet_list_order = request.session['compet_list_order']
        except:
            compet_list_order = 'compet_name'
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        if mod == 'i':
            form = CompetIniPontosFiltroForm(request.POST)
        else:
            form = CompetFemininaPontosFiltroForm(initial=instance)

    if compet_list_order == 'compet_points':
        compet_list_order = '-compet_points_cfobi'

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=(1,2,7))
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=(3,4,5,6))
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)
    compets = compets.order_by(compet_list_order)
    #################################################################
    # it is nor ordering! check why
    #print(compet_list_order)
    
    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    try:
        paginator = Paginator(compets, page_size)
        try:
            partics = paginator.page(page)
        except PageNotAnInteger:
            partics = paginator.page(1)
        except EmptyPage:
            partics = paginator.page(paginator.num_pages)
    except:
        partics = []

    if mod == 'i':
        pagetitle = 'Classificados para a Fase 3, Modalidade Iniciação'
    elif mod == 'p':
        pagetitle = 'Classificados para a Fase 3, Modalidade Programação'
    else:
        pagetitle = 'Classificados para a Fase 3'
    return render(request, 'cfobi/restrito/compet_lista_classif.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form})


def compet_lista_desclassif(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    pagetitle = 'Competidores desclassificados'
    compets = CompetDesclassif.objects.filter(compet_school_id=school.school_id)
    total = len(compets)
    if request.method == 'POST':
        form = CompetProgPontosFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_list_order = f['compet_order']
            compet_list_name = f['compet_name']
            compet_list_type = f['compet_type']
            request.session['compet_list_name'] = compet_list_name
            request.session['compet_list_order'] = compet_list_order
            request.session['compet_list_type'] = compet_list_type
    else:
        try:
            compet_list_order = request.session['compet_list_order']
        except:
            compet_list_order = 'compet_points'
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetProgPontosFiltroForm(initial=instance)

    if compet_list_type:
        try:
            compet_list_type = int(compet_list_type)
            if compet_list_type in (PJ,P1,P2,PS,CF):
                compets = compets.filter(compet_type=compet_list_type)
            elif compet_list_type in (IJ,I1,I2):
                compet_list_type = None
            else:
                compet_list_type = None
        except:
            compet_list_type = None
        request.session['compet_list_type'] = compet_list_type

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points_fase2').desc(nulls_last=True))
    else:
        compets = compets.order_by(compet_list_order)

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    try:
        paginator = Paginator(compets, page_size)
        try:
            partics = paginator.page(page)
        except PageNotAnInteger:
            partics = paginator.page(1)
        except EmptyPage:
            partics = paginator.page(paginator.num_pages)
    except:
        partics = []

    return render(request, 'cfobi/restrito/compet_lista_desclassif.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form, 'mod': 'prog'})
    


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def correcao_prog(request):
    form = {}
    return render(request, 'cfobi/restrito/correcao_prog.html', {'form': form, 'pagetitle': 'Correção Modalidade Programação CF-OBI'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def resultado_prog(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    exam_descriptor = 'cfobif1'
    show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']
    show_results_coord = EXAMS['provaf2']['exam_show_results_coord']['p']
        
    if not show_results_coord:
        messages.error(request, 'Ainda não disponível.')
        return redirect('/restrito')
        
    exam_descriptor = 'cfobif1'
    show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']
    #points_fase2 = PointsFase2
    pagetitle = 'Resultado Competição Feminina'
    #compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase1=True, compet_type__in=(PJ,P1,P2,PS))
    compets = CompetCfObi.objects.filter(compet__compet_school_id=school.school_id, compet_type__in=(PJ,P1,P2))
    total = len(compets)
    if request.method == 'POST':
        form = CompetFemininaPontosFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_list_order = f['compet_order']
            compet_list_name = f['compet_name']
            compet_list_type = f['compet_type']
            request.session['compet_list_name'] = compet_list_name
            request.session['compet_list_order'] = compet_list_order
            request.session['compet_list_type'] = compet_list_type
            print("compet_list")
    else:
        try:
            compet_list_order = request.session['compet_list_order']
        except:
            compet_list_order = 'compet_points'
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetFemininaPontosFiltroForm(initial=instance)

    if compet_list_type:
        try:
            compet_list_type = int(compet_list_type)
            if compet_list_type in (PJ,P1,P2,PS):
                compets = compets.filter(compet_type=compet_list_type)
            elif compet_list_type in (IJ,I1,I2):
                compet_list_type = None
            else:
                compet_list_type = None
        except:
            compet_list_type = None
        request.session['compet_list_type'] = compet_list_type

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet__compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points').desc(nulls_last=True))
    elif compet_list_order == 'compet_name':
        compets = compets.order_by('compet__compet_name')
    else:
        compets = compets.order_by('compet__compet_id')

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    try:
        paginator = Paginator(compets, page_size)
        try:
            partics = paginator.page(page)
        except PageNotAnInteger:
            partics = paginator.page(1)
        except EmptyPage:
            partics = paginator.page(paginator.num_pages)
    except:
        partics = []

    return render(request, 'cfobi/restrito/resultado_prog.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form, 'show_classif': show_classif, 'exam_descriptor': exam_descriptor})


    return render(request, 'cfobi/restrito/correcao_ini.html', {'form': form, 'pagetitle': 'Correção Iniciação'})



@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def lista_presenca(request, level_name):
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ListaPresenca_{}.pdf"'.format(level_name)

    if level == PJ:
        subtitle1 = 'Competição Feminina Nível Júnior'
    elif level == P1:
        subtitle1 = 'Competição Feminina Nível 1'
    elif level == P2:
        subtitle1 = 'Competição Feminina Nível 2'
    else:
        # error!
        return

    title = 'CF-OBI{}'.format(YEAR)
    subtitle2 = 'Lista de Presença {}'.format(get_obi_date('cfobi-fase-1-prova',"%d/%m/%Y"))

    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    compets = Compet.objects.filter(compet_sex__in=(x[0] for x in SEX_CHOICES_CFOBI), competcfobi__compet_type=level, compet_school_id=school_id, competcfobi__isnull=False)

    compets = compets.order_by('compet_name')
    data = [['Num. Inscr.', 'Nome', 'Turma', 'Assinatura'],]

    for c in compets:
        MAX = 43
        name = c.compet_name
        if len(name) > MAX:
            name = name[:MAX] + '...'
        data.append((format_compet_id(c.compet_id),name, c.compet_class, " "))

    report = PrintPresenceList(subtitle1)
    pdf = report.print_list(data, title, subtitle1, subtitle2)

    response.write(pdf)
    return response

