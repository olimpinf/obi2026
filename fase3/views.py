import csv
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
from django.contrib import messages

from principal.models import LANG_SUFFIXES_NAMES, LEVEL_NAME_FULL
from principal.models import (I1, I2, IJ, LANG_SUFFIXES_NAMES, LEVEL, LEVEL_ALL,
                             LEVEL_NAME, LEVEL_NAME_FULL, P1, P2, PJ, PS,
                              Compet, School, SchoolPhase3, ResIni)
from principal.forms import ConsultaCompetidoresForm
from principal.models import Colab, Compet, Deleg, ResWWW, School, SchoolPhase3, SubWWW
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
from .forms import (ConsultaResForm, ConsultaResIniForm, RecuperaSubmForm, SubmeteSolucoesForm, CorretorFolhasRespostasForm,
                    InserePontosIniLoteForm, TestForm, SchoolPrefIniForm, SchoolPrefProgForm)
from .models import SubFase3, ResFase3, SchoolPref
from exams.models import ExamFase3
from exams.views import show_results_all
from exams.settings import EXAMS

logger = logging.getLogger(__name__)
MAX_POINTS_INI = 40


from .forms import ConsultaSedesFase3Form, ConsultaSuaSedeFase3Form

#######
# sedes fase 3

def search_school_site_phase3(compet_id):
    try:
        compet = Compet.objects.get(compet_classif_fase2=True, pk=compet_id)
    except:
        return []
    school_compet = School.objects.get(pk=compet.compet_school_id)
    if compet.compet_school_id_fase3:
        schools = schools.filter(pk = compet.compet_school_id_fase3)
    elif compet.compet_type in (IJ, I1, I2): 
        schools = schools.filter(pk = school_compet.school_site_phase3_ini)
    else:
        schools = schools.filter(pk = school_compet.school_site_phase3_prog)
    return schools

def list_school_sites_phase3(f):
    schools = School.objects.filter(school_ok=True,school_is_site_phase3=True)
    if f['school_state']:
        schools = schools.filter(school_state = f['school_state'])
    if f['school_order'] == 'school_city':
        schools = schools.order_by('school_city','school_state')
    else: # order by school_state
        schools = schools.order_by('school_state','school_city')
    return schools

def consulta_sua_sede(request):
    if request.method == 'POST':
        form = ConsultaSuaSedeFase3Form(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            try:
                compet_id,compet_check = verify_compet_id(f['compet_id'])
                compet = Compet.objects.get(pk=compet_id)
            except:
                messages.error(request, 'Número de inscrição inválido')
                form = ConsultaSuaSedeFase3Form()
                return render(request, 'fase3/consulta_sua_sede.html', {'form': form})
            if not compet.compet_classif_fase2:
                messages.error(request, 'Competidor(a) não classificado para a Fase Nacional')
                form = ConsultaSuaSedeFase3Form()
                return render(request, 'fase3/consulta_sua_sede.html', {'form': form})
            school_compet = School.objects.get(pk=compet.compet_school_id)
            #print('school_compet',school_compet)
            #print(school_compet.school_site_phase3_ini)
            #print(school_compet.school_site_phase3_prog)
            if compet.compet_school_id_fase3:
                schools = School.objects.filter(pk = compet.compet_school_id_fase3)
                if compet.compet_type in (IJ, I1, I2):
                    mod = 'ini'
                else:
                    mod = 'prog'
            elif compet.compet_type in (IJ, I1, I2):
                schools = School.objects.filter(pk = school_compet.school_site_phase3_ini)
                mod = 'ini'
            else:
                schools = School.objects.filter(pk = school_compet.school_site_phase3_prog)
                mod = 'prog'
            #print('schools',schools)
            if len(schools) == 0:
                messages.error(request, 'Sede ainda não definida, por favor aguarde.')
                form = ConsultaSuaSedeFase3Form()
                return render(request, 'fase3/consulta_sua_sede.html', {'form': form})
            elif not schools[0].school_site_phase3_show:
                messages.error(request, 'Sede ainda não definida, por favor aguarde.')
                return render(request, 'fase3/consulta_sua_sede.html', {'form': form})
            return render(request, 'fase3/mostra_sede_fase3.html', { 'school': schools[0], 'mod': mod })
    else:
        form = ConsultaSuaSedeFase3Form()
    return render(request, 'fase3/consulta_sua_sede.html', {'form': form})

def mostra_sede_fase3(request,id):
    school = School.objects.get(school_id=id)
    return render(request, 'fase3/mostra_sede_fase3.html', {'school':school})



# def mapa_sedes(request, map_type):
#     return render(request, 'fase3/mapa_sedes.html', {'tipo': map_type})


def consulta_sedes(request):
    if request.method == 'POST':
        form = ConsultaSedesFase3Form(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            schools = list_school_sites_phase3(f)
            if f['modality'] == 'ini':
                schools = schools.filter(school_site_phase3_type__in=(1,3))
                return render(request, 'fase3/lista_sedes.html', { 'items': schools, 'mod': 'prog' })
            else:
                schools = schools.filter(school_site_phase3_type__in=(2,3))
                return render(request, 'fase3/lista_sedes.html', { 'items': schools, 'mod': 'prog' })
    else:
        form = ConsultaSedesFase3Form()
    return render(request, 'fase3/consulta_sedes.html', {'form': form})





#################
# results
#

def in_compet_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='compet').exists()

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

def consulta_resultado(request):
    pagetitle = 'Consulta Resultado - Fase 3'
    info_msg = 'Utilize este formulário para consultar o resultado da Fase 3'
    if request.method == 'POST':
        form = ConsultaResForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_id,check = verify_compet_id(f['compet_id'])
            try:
                c = Compet.objects.get(pk=compet_id)
                #return render(request, 'fase3/consulta_res_ini_resp.html', {'result': result})
            except:
                messages.error(request, "Número de inscrição não corresponde a competidor.")
                form = ConsultaResForm()
                return render(request, 'fase3/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
            if not c.compet_classif_fase1:
                messages.error(request, "Competidor não fez a prova, não estava classificado para a Fase3.")
                form = ConsultaResForm()
                return render(request, 'fase3/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
            return render(request, 'fase3/mostra_resultado.html', {'compet':c})
    else:
        form = ConsultaResForm()
    return render(request, 'fase3/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def mostra_resultado_compet_ini(request):
    try:
        c = request.user.compet
    except:
        c = None
    show_classif = EXAMS['provaf3']['exam_show_classif']
    show_correct = EXAMS['provaf3']['exam_show_results']['i']
    folha_resp = False
    try:
        res_ini = ResIni.objects.get(compet_id=c.compet_id)

        answers = eval(res_ini.answers_fase3)
        if c.compet_type == IJ:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3ij.txt')
        elif c.compet_type == I1:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i1.txt')
        elif c.compet_type == I2:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i2.txt')
        else:
            raise 'boom' # boom!
        errors,numquestions,gab = check_answers_file(gab_file_name)

        points, log = calc_log_and_points(gab, answers, show_correct=show_correct)
        #print(os.path.join(BASE_DIR,"media", "folhas_fase3", str(c.compet_id)+'.jpg'))
        if os.path.isfile(os.path.join(BASE_DIR,"media", "folhas_fase3", c.compet_id_full+'.pdf')):
            folha_resp = True
    except:
        # fez prova no sistema da escola?
        folha_resp = False
        log = ''
    return render(request, 'fase3/mostra_resultado.html', {'compet':c, 'show_classif': show_classif, 'log':log, 'folha_resp': folha_resp})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def mostra_resultado_coord_ini(request, compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id

    if school.school_site_phase3_ini == school_id:
        c = Compet.objects.get(pk=compet_id, compet_school_id=school_id, compet_classif_fase2=True) # will fail if not from school
    else:
        c = Compet.objects.get(pk=compet_id, compet_school_id=school_id, compet_classif_fase2=True) # will fail if not from school

    show_classif = EXAMS['provaf3']['exam_show_classif_coord']
    show_correct = EXAMS['provaf3']['exam_show_results_coord']['i']

    # check if exam taken online
    # exam taken in paper form
    exam = EXAMS['provaf3']['exam_object']
    compet_exam = exam.objects.get(compet_id=c.compet_id)
    #if compet_exam.time_finish:
    #    return redirect(f'/prova/provaf3/resultado/mostra_res/{c.compet_id}')

    folha_resp = False
    log = ''
    try:
        res_ini = ResIni.objects.get(compet_id=c.compet_id)

        answers = eval(res_ini.answers_fase3)
        if c.compet_type == IJ:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3ij.txt')
        elif c.compet_type == I1:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i1.txt')
        elif c.compet_type == I2:
            gab_file_name = os.path.join(BASE_DIR,'protected_files','gab_f3i2.txt')
        else:
            pass # boom!
        errors,numquestions,gab = check_answers_file(gab_file_name)

        points, log = calc_log_and_points(gab, answers, show_correct=show_correct)
        if os.path.isfile(os.path.join(BASE_DIR, "media", "folhas_fase3", c.compet_id_full+'.pdf')):
            folha_resp = True
    except:
        # fez prova no sistema da escola?
        pass
    return render(request, 'fase3/mostra_resultado.html', {'compet':c, 'show_classif': show_classif, 'log':log, 'folha_resp': folha_resp})

@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def serve_protected_document_zip(request, file):
    file=os.path.join(settings.BASE_DIR,'protected_files',file)
    # Split the elements of the path
    path, file_name = os.path.split(file)
    response = FileResponse(open(file,"rb"),content_type='application/zip')
    response["Content-Disposition"] = "attachment; filename={}".format(file_name)
    return response

# coords, colabs, compets
@login_required
def serve_folha_resp(request, compet_id):
    try:
        compet = request.user.compet
        c = Compet.objects.get(pk=compet.compet_id)
    except:
        print("not a compet")
        try:
            school = request.user.deleg.deleg_school
        except:
            try:
                school = request.user.colab.colab_school
            except:
                school = None # boom
        school_id = school.school_id
        #if school.school_is_site_phase3 and school.school_site_phase3_ini == school_id:
        #    compets = SchoolPhase3.objects.get(school_id=school.school_id).get_compets_ini_in_this_site()
        #    c = compets.get(pk=compet_id)
        #else:
        #    c = Compet.objects.get(pk=compet_id, compet_school_id=school_id, compet_classif_fase2=True) # will fail if not from school
        c = Compet.objects.get(pk=compet_id, compet_school_id=school_id, compet_classif_fase2=True) # will fail if not from school
        
    if compet_id==c.compet_id:
        file=os.path.join(settings.BASE_DIR, 'media', 'folhas_fase3', c.compet_id_full+'.pdf')
        response = FileResponse(open(file,"rb"),content_type='image/jpeg')
        response["Content-Disposition"] = f"attachment; filename=FolhaResposta{c.compet_id_full}.pdf"
        return response
    else:
        data = {'pagetitle':'Erro', 'msg':"Acesso inválido"}
        return render(request,'erro.html', data)

def consulta_res_ini(request):
    pagetitle = 'Consulta Pontuação Fase 3 - Iniciação'
    info_msg = 'Utilize este formulário para consultar a pontuação da Fase 3'
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_id,check = verify_compet_id(f['compet_id'])
            try:
                c = Compet.objects.get(pk=compet_id,compet_type__in=(I1,I2,IJ))
                #result = {'compet': c}
                #return render(request, 'fase3/consulta_res_ini_resp.html', {'result': result})
            except:
                messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Iniciação.")
                form = ConsultaResIniForm()
                return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
            exam_descriptor = "provaf3"
            return show_results_all(request,exam_descriptor,compet_id)
    else:
        form = ConsultaResIniForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})


def show_points_fase3(request,exam_descriptor,compet,pagetitle):
    # missing: check exam to only show if allowed
    return render(request, 'fase3/show_points.html', {'pagetitle': pagetitle, 'compet': compet})

    
def consulta_res_prog(request):
    pagetitle = 'Consulta Pontuação Fase Nacional - Programação'
    info_msg = 'Utilize este formulário para consultar a correção da Fase 3'
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_id,check = verify_compet_id(f['compet_id'])
            try:
                compet = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
            except:
                messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")
                form = ConsultaResIniForm()
                return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
            exam_descriptor = "provaf3"
            return show_points_fase3(request,exam_descriptor,compet,pagetitle)
    else:
        form = ConsultaResIniForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})


def consulta_res_prog_old(request):
    pagetitle = 'Consulta Correção Fase 3 - Programação'
    info_msg = 'Utilize este formulário para consultar a correção da Fase 3'
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            #result = grecaptcha_verify(request) #is_recaptcha_valid(request)
            result = True
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                res_log = ResFase3.objects.filter(compet_id=c.compet_id)
                result = {'compet': c, 'log': res_log}
                return render(request, 'fase3/consulta_res_prog_resp.html', {'result': result})
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(1,2,7))
                    result = {'compet': c}
                    #return render(request, 'fase3/consulta_res_ini_resp.html', {'result': result})
                    return show_results_all(request,"provaf1",compet_id)

                    compet_id,check = verify_compet_id(f['compet_id'])
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                    res_log = ResFase3.objects.filter(compet_id=c.compet_id)
                    result = {'compet': c, 'log': res_log}
                    return render(request, 'fase3/consulta_res_prog_resp.html', {'result': result})
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")
            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResIniForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

def consulta_subm_prog(request):
    pagetitle = 'Fase 3 - Programação, Consulta Submissões'
    info_msg = 'Utilize este formulário para consultar os arquivos de soluções submetidos e aceitos para correção.'
    msg = ''
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            #result = grecaptcha_verify(request)
            result = True
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                    result = {'compet':c}
                    submissions = SubFase3.objects.filter(compet_id=compet_id).order_by('problem_name')
                    if len(submissions) == 0:
                        msg = 'Não foram encontradas submissões aceitas'
                    elif len(submissions) == 1:
                        msg = 'Foi encontrada uma submissão.'
                    else:
                        msg = 'Foram encontradas {} submissões.'.format(len(submissions))
                    result['problems'] = []
                    for s in submissions:
                        filename = "{}.{}".format(s.problem_name,LANG_SUFFIXES_NAMES[s.sub_lang])
                        result['problems'].append(filename)
                    return render(request, 'fase3/consulta_subm_prog_resp.html', {'result': result})
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")

            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResIniForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

def consulta_classif(request):
    pagetitle = 'Fase 3 - Consulta Classificados'
    if request.method == 'POST':
        form = ConsultaCompetidoresForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            # set session data
            request.session['compet_name']=f['compet_name']
            request.session['compet_level']=f['compet_level']
            request.session['school_name']=f['school_name']
            request.session['school_city']=f['school_city']
            request.session['school_state']=f['school_state']
            request.session['list_order']=f['list_order']
            request.session['pagetitle']=pagetitle
            return HttpResponseRedirect('consulta_classif_resp')
    else:
        form = ConsultaCompetidoresForm()
    return render(request, 'principal/consulta_competidores.html', {'form': form, 'pagetitle':pagetitle})

def consulta_classif_resp(request):
    pagetitle = 'Fase 3 - Consulta Classificados'
    urlconsult = 'fase3:consulta_classif'
    urlresp='fase3:consulta_classif_resp'
    f = {}
    f['compet_name'] = request.session['compet_name']
    f['compet_level'] = request.session['compet_level']
    f['school_name'] = request.session['school_name']
    f['school_city'] = request.session['school_city']
    f['school_state'] = request.session['school_state']
    f['list_order'] = request.session['list_order']
    f['partic_year'] = 'default' # name of database current year
    pagetitle = request.session['pagetitle']
    compets = search_compets(f)
    compets = compets.filter(compet_classif_fase2=True)
    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    paginator = Paginator(compets, page_size)
    try:
        compets = paginator.page(page)
    except PageNotAnInteger:
        compets = paginator.page(1)
    except EmptyPage:
        compets = paginator.page(paginator.num_pages)
    return render(request, 'principal/consulta_competidores_resp.html', { 'items': compets, 'pagetitle': pagetitle, 'urlconsult':urlconsult, 'urlresp':urlresp })


def tarefa_iniciacao(request,year,phase,level,code,show_answers=False):
    descriptor = '{}f{}i{}_{}'.format(year,phase,level,code)
    if request.POST.get("show_answers"):
        show_answers = True
    else:
        show_answers = False
    return rendertask(request, descriptor, show_answers=show_answers, mod='i')

def tarefa_programacao(request,year,phase,level,code,show_answers=False):
    descriptor = '{}f{}p{}_{}'.format(year,phase,level,code)
    if request.POST.get("show_answers"):
        show_answers = True
    else:
        show_answers = False
    return rendertask(request, descriptor, show_answers=show_answers, mod='p')

def corrige_programacao(request,year,phase,level,code):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SubmeteSolucaoPratiqueForm(request.POST,request.FILES)
        # check whether it is valid:
        if form.is_valid():
            source_path = write_uploaded_file(request.FILES['data'],request.FILES['data'].name,'sub_www')
            try:
                with open(source_path,"rU") as fin:
                    source = fin.read()
                    #print('is utf8')
            except:
                try:
                    with open(source_path,"rU", encoding='latin1') as fin:
                        #print('is latin1')
                        source = fin.read()
                except:
                    # do not remove, to see its type
                    #os.remove(source_path)
                    return render(request, 'corrige_programacao_erro.html', {})
            os.remove(source_path)
            submission = SubWWW(sub_source=source,sub_lang=form.cleaned_data['sub_lang'],problem_name=form.cleaned_data['problem_name'],problem_name_full=form.cleaned_data['problem_name_full'],team_id=0)
            submission.save(using='corretor')
            # save the submission data in session
            request.session['submission_sub_id']=submission.sub_id
            request.session['submission_problem_name_full']=form.cleaned_data['problem_name_full'],
            request.session['problem_request_path']=form.cleaned_data['problem_request_path'],
            subm_ctx={
                'problem_request_path': form.cleaned_data['problem_request_path'],
                'problem_name_full': form.cleaned_data['problem_name_full'],
                'problem_level': request.path,
                'sub_id': submission.sub_id,
                }
            return render(request, 'corrige_programacao_resp.html', subm_ctx)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SubmeteSolucaoPratiqueForm()

    return render(request, 'submete_solucao.html', {'form': form})

def corrige_programacao_resultado(request,level,code,year,phase):
    try:
        sub_id = request.session['submission_sub_id']
        problem_name_full = request.session['submission_problem_name_full'][0]
    except:
        sub_id=0
        problem_name_full = ''
    try:
        problem_request_path = request.session['problem_request_path']
    except:
        problem_request_path = ''
    # clear session data
    request.session['submission_sub_id'] = 0
    request.session['submission_problem_name_full'] = None
    # do not erase, in case of user reloading
    #request.session['problem_request_path'] = None
    subm_ctx = {
        'problem_name_full': problem_name_full,
        'problem_request_path': problem_request_path,
        'msg': '',
        'log': "",}
    wait_tries = 20
    if sub_id == 0: # user is reloading page?
        subm_ctx['msg']='Por favor re-submeta sua solucão. Não atualize a página enquanto espera o resultado, pois isso impede que a resposta seja mostrada corretamente.'
    else:
        for i in range(1, wait_tries):
            sleep(3)
            try:
                new_result = ResWWW.objects.using('corretor').get(sub_id__exact=sub_id)
                subm_ctx['log'] = new_result.result_log
                break;
            except:
                pass
        if subm_ctx['log'] == '':
            subm_ctx['msg'] = 'Ocorreu um problema durante o processamento de sua solução. Se o problema persistir, por favor contate o administrador do site.'
        else:
            new_result.save(using='corretor')
    return render(request, 'corrige_programacao_resultado.html', subm_ctx)

def corrige_programacao_resp(request):
    template = loader.get_template('corrige_programacao_resp.html')
    context = {'problem_name_full':'Problem name'}
    return HttpResponse(template.render(context, request))


def recupera_subm_prog(request):
    pagetitle = 'Fase 3 - Programação, Recupera Submissões'
    info_msg = '''
Utilize este formulário para recuperar os arquivos de soluções
submetidos e aceitos para correção. As soluções serão enviadas para o
endereço de email cadastrado do competidor; note que o professor
coordenador da OBI em sua escola pode não ter cadastrado o email do
competidor. Nesse caso, entre em contato com seu professor para
acessar as soluções.'''
    msg = ''
    if request.method == 'POST':
        #form = ConsultaResFase3IniForm(request.POST)
        form = RecuperaSubmForm(request.POST)
        if form.is_valid():
            #result = grecaptcha_verify(request)
            result = True
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                compet_id=int(compet_id)
                c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                except:
                    c = None
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")
                    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
                if not c.compet_email:
                    messages.error(request, "Competidor não tem endereço de email cadastrado.")
                    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
                if not f['send_to_compet'] and not f['send_to_coord']:
                    messages.error(request, "Escolha ao menos um destinatário para o envio do arquivo de soluções (competidor ou coordenador local).")
                    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

                result = {'compet':c}
                submissions = SubFase3.objects.filter(compet_id=c.compet_id).order_by('problem_name')
                if len(submissions) == 0:
                    msg = 'Não foram encontradas submissões aceitas'
                    return render(request, 'fase3/recupera_subm_prog_resp.html', {'result': result,'msg': msg})
                zip_file = zip_submissions(submissions,'solucoes_fase3')
                subject = "OBI, Soluções Fase 3"
                if f['send_to_compet']:
                    msg_text = '''Caro {},

você está recebendo esta mensagem porque alguém solicitou
a recuperação de seus arquivos de soluções da Fase 3 da OBI,
modalidade Programação. Se não foi você quem fez a solicitação,
por favor desconsidere esta mensagem.

Atenciosamente,

---
Cordenação da OBI'''.format(c.compet_name)

                    to_addr = c.compet_email
                    from_addr = DEFAULT_FROM_EMAIL
                    #################### must update to attach file!!!!!!!!!
                    ############################# remove for production
                    if DEBUG:
                        to_addr = 'ranido@gmail.com'
                    #############################
                    send_mail(subject, msg_text, from_addr, [to_addr], file=zip_file, fname='solucoes_fase3.zip')
                    to_addr = c.compet_email
                    tmp = to_addr[:2]
                    for i in range(2,len(to_addr)-4):
                        if to_addr[i] != '@':
                            tmp += '*'
                        else:
                            tmp += '@'
                    tmp += to_addr[-4:]

                if f['send_to_coord']:
                    sch = School.objects.get(pk=c.compet_school_id)
                    msg_text = '''Caro(a) Prof(a). {},

você está recebendo esta mensagem porque alguém solicitou
a recuperação dos arquivos de soluções da Fase 3 da OBI,
modalidade Programação, de um(a) competidor(a) de sua escola:

     {} - {}

Se não foi você quem fez a solicitação, por favor
desconsidere esta mensagem.

Atenciosamente,

---
Cordenação da OBI'''.format(sch.school_deleg_name,format_compet_id(c.compet_id),c.compet_name)

                    to_addr = sch.school_deleg_email
                    from_addr = DEFAULT_FROM_EMAIL
                    if DEBUG:
                        to_addr = 'ranido@gmail.com'
                    send_mail(subject, msg_text, from_addr, [to_addr], file=zip_file, fname='solucoes_fase3.zip')
                    to_addr = sch.school_deleg_email
                    tmp_coord = to_addr[:2]
                    for i in range(2,len(to_addr)-4):
                        if to_addr[i] != '@':
                            tmp_coord += '*'
                        else:
                            tmp_coord += '@'
                    tmp_coord += to_addr[-4:]

                try:
                    zip_file.close()
                except:
                    print('failed to close zip_file')
                if f['send_to_compet']:
                    if f['send_to_coord']:
                        msg = 'Um arquivo contendo as submissões foi enviado para o email cadastrado para este competidor ({})  e para o email do Coordenador Local da OBI da escola do competidor ({}).'.format(tmp,tmp_coord)
                    else:
                        msg = 'Um arquivo contendo as submissões foi enviado para o email cadastrado para este competidor ({}).'.format(tmp)
                elif f['send_to_coord']:
                    msg = 'Um arquivo contendo as submissões foi enviado para o email cadastrado para o email do Coordenador Local da OBI da escola do competidor ({}).'.format(tmp_coord)
                else:
                    msg = 'Escolha ao menos um destinatário para o arquivo com as soluções.'
                return render(request, 'fase3/recupera_subm_prog_resp.html', {'result': result, 'msg': msg})

            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = RecuperaSubmForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})


####################
# Restrito
####################
from django.contrib.auth.decorators import user_passes_test
from restrito.views import in_coord_group
from corretor_ini.utils.build_answer_sheet import draw_page, draw_pages
from corretor_ini.utils.utils import pack_and_send
from reportlab.pdfgen import canvas

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def correcao_prog(request):
    return render(request, 'fase3/restrito/correcao_prog.html', {})

def school_has_compet_classif(school, mod):
    if mod == 'ini':
        compet_types = (IJ, I1, I2)
    else:
        compet_types = (PJ, P1, P2, PS)

    return Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase2=True, compet_type__in=compet_types).exists()


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def mostra_sede_fase3_coord(request,mod):
    
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school


    if mod == 'ini':
        site_id = school.school_site_phase3_ini
    else:
        site_id = school.school_site_phase3_prog

    try:
        site = School.objects.get(pk=site_id)
    except:
        if not school_has_compet_classif(school, mod):
            messages.error(request, 'Sede não tem classificados nesta modalidade.')
            return redirect('/restrito/')
        
        messages.error(request, 'Sede ainda não definida, por favor aguarde.')
        return redirect('/restrito/')
    if not site.school_site_phase3_show:
        if site.school_id == school.school_id:
            messages.error(request, 'Note que as sedes ainda não estão públicas, no momento são visíveis apenas para coordenadores de sede.')
            return render(request, 'fase3/mostra_sede_fase3.html', {'school':site, 'mod': mod})
        else:
            messages.error(request, 'Sede ainda não definida, por favor aguarde.')
            return redirect('/restrito/')

    return render(request, 'fase3/mostra_sede_fase3.html', {'school':site, 'mod': mod})

def mostra_sede_fase3(request,id):
    
    school = School.objects.get(school_id=id)
    if not school.school_site_phase3_show:
        messages.error(request, 'Sede ainda não definida, por favor aguarde.')
        return redirect('/restrito/')

    return render(request, 'fase3/mostra_sede_fase3.html', {'school':school, 'mod': mod})


#@user_passes_test(in_coord_group, login_url='/contas/login/')
@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def cadernos_tarefas_ini(request):
    #print(request.user.deleg)
    #try:
    #    school = request.user.deleg.deleg_school
    #except:
    #    school = request.user.deleg_colab.deleg_colab_school
    #if not school.school_is_site_phase3:
    #    messages.error(request, 'Esta escola não é sede da Fase Nacional.')
    #    return redirect('/restrito/')

    return render(request,'fase3/restrito/caderno_tarefas_ini.html', {})

#@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def cadernos_tarefas_prog(request):
    return render(request,'fase3/restrito/caderno_tarefas_prog.html', {})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def correcao_prog(request):
    if request.method == 'POST':
        ###############
        # not authorized, too late
        ###############
        messages.error(request, 'Período de submissão de soluções finalizado.')
        return redirect('/fase3/prog/restrito/correcao_prog')

        form = SubmeteSolucoesForm(request.POST, request.FILES)
        if form.is_valid():
            level = int(request.POST['compet_type'])
            level_name = LEVEL_NAME[int(request.POST['compet_type'])]
            # write file
            try:
                school_id = request.user.deleg.deleg_school.pk
            except:
                school_id = request.user.colab.colab_school.pk
            archive_path, resultfile = write_school_uploaded_file(school_id=school_id,
                                                   modality='prog',phase_name='fase-1',fwhy='sub_prog',
                                                   f=request.FILES['source_file'],fname=level_name)

            # and process it
            msg, result = check_solutions_file(archive_path, level, phase=1, school_id=school_id)
        else:
            msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
            <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
        return render(request,
                      'fase3/restrito/check_solutions_interm.html',
                      context={'msg':msg, 'result':result})
    else:
        form = SubmeteSolucoesForm()
    return render(request, 'fase3/restrito/correcao_prog.html', {'form': form, 'pagetitle': 'Submete Soluções'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def inserepontosini(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    ########
    # calculate classif for all levels in this school
    ########
    #for level in [IJ, I1, I2]:
    #    compute_classif_one_school(school.school_id,level)

    compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=(IJ,I1,I2))
    total = len(compets)
    if request.method == 'POST':
        form = CompetIniPontosFiltroForm(request.POST)
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
        form = CompetIniPontosFiltroForm(initial=instance)

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

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points_fase3').desc(nulls_last=True))
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
    compet_focus = None
    try:
        if request.session['compet_focus']:
            compet_focus = request.session['compet_focus']
            request.session['compet_focus'] = None
    except:
        pass
    return render(request, 'fase3/restrito/insere_pontos_ini.html', {'items': partics, 'total':total, 'pagetitle':'Insere/Modifica Pontuação', 'form': form, 'focus': compet_focus})

 
@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_classif_ini(request):
    return compet_lista_classif(request,mod='i')

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
        compets = Compet.objects.filter(compet_school_id=school_id, compet_classif_fase2=True,compet_type__in=(1,2,7))
    else:
        compets = Compet.objects.filter(compet_school_id=school_id, compet_classif_fase2=True,compet_type__in=(3,4,5,6))
    total = len(compets)
    if request.method == 'POST':
        # default
        compet_list_order = 'compet_points_fase2'

        if mod == 'i':
            form = CompetIniPontosFiltroForm(request.POST)
        else:
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
            form = CompetProgPontosFiltroForm(initial=instance)

    if compet_list_order == 'compet_points':
        compet_list_order = '-compet_points_fase3'

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
    return render(request, 'fase3/restrito/compet_lista_classif.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_ini(request):
    return compet_lista(request,mod='ini')

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_prog(request):
    return compet_lista(request,mod='prog')

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista(request,mod):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    if mod == 'ini':
        compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_school__school_site_phase3_ini=school_id,compet_classif_fase2=True)
        #compets = compets | Compet.objects.filter(compet_type__in=(1,2,7),compet_school_id_fase3=school_id,compet_classif_fase2=True)
        #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site()
    else:
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6),compet_school__school_site_phase3_prog=school_id,compet_classif_fase2=True)
        #compets = compets | Compet.objects.filter(compet_type__in=(3,4,5,6),compet_school_id_fase3=school_id,compet_classif_fase2=True)
        #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site()
    total = len(compets)
    if request.method == 'POST':
        # default
        compet_list_order = 'compet_name'

        if mod == 'ini':
            form = CompetIniPontosFiltroForm(request.POST)
        else:
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
            compet_list_order = 'compet_name'
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None

        if mod == 'ini' and compet_list_type in (3,4,5,6):
            compet_list_type = None
        elif mod == 'prog' and compet_list_type in (1,2,7):
            compet_list_type = None

        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        if mod == 'ini':
            form = CompetIniPontosFiltroForm(initial=instance)
        else:
            form = CompetProgPontosFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=(1,2,7))
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=(3,4,5,6))
        else:
            compet_list_type = int(compet_list_type)
            #print('***',compet_list_type)
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compet_list_order = 'compet_points_fase2'
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

    if mod == 'ini':
        pagetitle = 'Competidores da Sede, Modalidade Iniciação'
    else:
        pagetitle = 'Competidores da Sede, Modalidade Programação'

    return render(request, 'fase3/restrito/compet_lista.html', {'mod': mod, 'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form})



@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_show_status_ini(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    s = School.objects.get(school_id=school_id)
    compets = Compet.objects.filter(compet_school__school_site_phase3_ini=school_id, compet_type__in=(1,2,7), compet_classif_fase2=True)
    #if s.school_is_site_phase3_ini==s.school_id:
    #    #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site()
    #else: 
    #    compets = []
       
    total = len(compets)
    if request.method == 'POST':
        # default
        compet_list_order = 'compet_name'

        form = CompetIniFiltroForm(request.POST)

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

        form = CompetIniFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=(1,2,7))
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=(3,4,5,6))
        else:
            compet_list_type = int(compet_list_type)
            #print('***',compet_list_type)
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    #if compet_list_order == 'compet_points':
    #    compet_list_order = 'compet_points_fase3'
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

    pagetitle = 'Status Correção Modalidade Iniciação'

    return render(request, 'fase3/restrito/compet_status_ini.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_insere_pontos(request,compet_id,compet_points=None):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    try:
        c = Compet.objects.get(compet_id=compet_id,compet_school_id=school.school_id)
    except:
        messages.error(request, 'Atualização falhou, competidor não existe.')
        return redirect('/fase3/ini/restrito/inserepontosini')

    ###############
    # not authorized, too late
    ###############
    messages.error(request, 'Atualização falhou, período de alteração de notas finalizado.')
    return redirect('/fase3/ini/restrito/inserepontosini')

    # set session data for focus
    request.session['compet_focus']=compet_id
    if compet_points and (compet_points < 0 or compet_points > MAX_POINTS_INI):
        messages.error(request,'Atualização falhou, pontuação deve ser entre 0 e {}.'.format(MAX_POINTS_INI))
        return redirect('/fase3/ini/restrito/inserepontosini')

    c.compet_points_fase3 = compet_points
    c.save()
    if c.compet_sex == 'F':
        messages.success(request,'Pontuação da competidora "{}" foi atualizada.'.format(c))
    else:
        messages.success(request,'Pontuação do competidor "{}" foi atualizada.'.format(c))
    return redirect('/fase3/ini/restrito/inserepontosini')

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def inserepontosinilote(request):
    ###############
    # not authorized, too late
    ###############
    messages.error(request, 'Período de alteração de notas finalizado.')
    return redirect('/fase3/ini/restrito/inserepontosini')

    if request.method == 'POST':
        try:
            school = request.user.deleg.deleg_school
        except:
            school = request.user.colab.colab_school

        ###############
        # not authorized if online
        ###############
        compets = Compet.objects.filter(compet_school=school, compet_type__in=(IJ,I1,I2))
        exams = ExamFase3.objects.filter(time_start__isnull=False)
        ok = True
        for c in compets:
            if exams.filter(compet=c).exists():
                ok = False
                break
        if not ok:
            msg = 'Atualização falhou, alunos da escola fizeram a prova online, não é possível alterar a pontuação.'
            errors = {}
            valid = []
            return render(request,
                          'fase3/restrito/insere_pontos_ini_lote_resp.html',
                          context={'msg': msg, 'errors': errors, 'valid':valid,
                          })
        form = InserePontosIniLoteForm(request.POST, request.FILES)
        if form.is_valid():
            # write file
            archive_path, resultfile = write_school_uploaded_file(school_id=school.school_id,
                                                                  modality='ini',phase_name='fase-1',fwhy='pontos_ini',
                                                                  f=request.FILES['source_file'],fname='ini')

            # and process it
            phase = 1
            email = school.school_deleg_email
            f = request.FILES['source_file']
            file_name = get_valid_filename(f.name)
            msg,errors,validated_compet_points = check_compet_points_batch(archive_path,school.school_id,15,phase=1)
            valid = []
            if len(errors)==0 and len(msg)==0:
                for c,p in validated_compet_points:
                    c = Compet.objects.get(pk=c)
                    c.compet_points_fase3 = p
                    c.save()
                    valid.append({'id':format_compet_id(c.compet_id),'name':c.compet_name,'points':c.compet_points_fase3,'level':LEVEL_NAME[c.compet_type]})
                    # don't need this here, done in changelist_view
                    #compute_classif_one_school(school_id, IJ)
                    #compute_classif_one_school(school_id, I1)
                    #compute_classif_one_school(school_id, I2)
                    msg = '<p>O arquivo foi processado corretamente. Foram encontrados {} competidores no arquivo. As pontuações de todos os competidores foram inseridas no sistema e estão listadas abaixo. Você pode conferir/alterar as pontuações de seus competidores utilizando o formulário <a href="/fase3/ini/restrito/inserepontosini">Insere/Modifica Pontuação</a>.</p>'.format(len(validated_compet_points))

            else:
                msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. A pontuação não foi alterada para nenhum competidor.
<p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
            return render(request,
                          'fase3/restrito/insere_pontos_ini_lote_resp.html',
                          context={'msg': msg, 'errors': errors, 'valid':valid,
                          })

    else:
        form = InserePontosIniLoteForm()
    return render(request, 'fase3/restrito/insere_pontos_ini_lote.html', {'form': form, 'pagetitle': 'Insere Pontuação em Lote'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def resultado_prog(request):
    print("resultado_prog")
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    exam_descriptor = 'provaf3'
    show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']

    
    if school.school_site_phase3_prog and school.school_id:
        compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase2=True, compet_type__in=(PJ,P1,P2,PS))
        #compets = SchoolPhase3.objects.get(school_id=school.school_id).get_compets_prog_in_this_site()
    else:
        compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase2=True, compet_type__in=(PJ,P1,P2,PS))
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
        compets = compets.filter(compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points_fase3').desc(nulls_last=True))
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

    return render(request, 'fase3/restrito/resultado_prog.html', {'items': partics, 'total':total, 'pagetitle':'Resultado Fase 3', 'form': form, 'exam_descriptor': exam_descriptor})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def resultado_ini(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    exam_descriptor = 'provaf3'
    show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']
    # calculate classif for all levels in this school
    #for level in [IJ, I1, I2]:
    #    compute_classif_one_school(school.school_id,level)

    #if school.school_site_phase3_type and school.school_site_phase3_type in (1,3):
    #    compets = SchoolPhase3.objects.get(school_id=school.school_id).get_compets_ini_in_this_site()
    #else:
    #    compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=(IJ,I1,I2), compet_classif_fase2=True)
    compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=(IJ,I1,I2), compet_classif_fase2=True)    
    total = len(compets)
    if request.method == 'POST':
        form = CompetIniPontosFiltroForm(request.POST)
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
        form = CompetIniPontosFiltroForm(initial=instance)

    if compet_list_type:
        try:
            compet_list_type = int(compet_list_type)
            if compet_list_type in (PJ,P1,P2,PS):
                compet_list_type = None
            elif compet_list_type in (IJ,I1,I2):
                compets = compets.filter(compet_type=compet_list_type)
            else:
                compet_list_type = None
        except:
            compet_list_type = None
        request.session['compet_list_type'] = compet_list_type


    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points_fase3').desc(nulls_last=True))
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
    return render(request, 'fase3/restrito/resultado_ini.html', {'items': partics, 'total':total, 'pagetitle':'Resultado Fase 3', 'form': form, 'exam_descriptor': exam_descriptor, 'show_classif':show_classif})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def corretorfolhasrespostas(request):
    ###############
    # not authorized, 
    ###############
    messages.error(request, 'Período de submissão de folhas de respostas finalizado.')
    #messages.error(request, 'O sistema será disponibilizado após a prova, por favor aguarde.')
    return redirect('/fase3/ini/restrito/correcao_ini')

    if request.method == 'POST':
        form = CorretorFolhasRespostasForm(request.POST, request.FILES)
        if form.is_valid():
            level = int(request.POST['compet_type'])
            level_name = LEVEL_NAME[int(request.POST['compet_type'])]
            # write file
            try:
                school = request.user.deleg.deleg_school
            except:
                school = request.user.colab.colab_school
            school_id = school.school_id
            archive_path, resultfile = write_school_uploaded_file(school_id=school_id,
                                                   modality='ini',phase_name='fase-3',fwhy='sub_ini',
                                                   f=request.FILES['source_file'],fname=level_name)

            compets = Compet.objects.filter(compet_type=level,compet_school__school_site_phase3_ini=school_id,compet_classif_fase2=True)

            # for the report
            if level == IJ:
                levelstr = 'Nível Júnior'
                num_questions = 30
                num_alternatives = 5
            elif level == I1:
                levelstr = 'Nível 1'
                num_questions = 40
                num_alternatives = 5
            else:
                levelstr = 'Nível 2'
                num_questions = 50
                num_alternatives = 5
            label1 = f"OBI{YEAR}"
            label2 = f"Modalidade Iniciação • {levelstr}"
            label3 = school.school_name
            
            # and process it
            phase = 3
            email = school.school_deleg_email
            f = request.FILES['source_file']
            reference = request.POST['reference']
            file_name = get_valid_filename(f.name)
            if level == IJ:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3ij.txt')
            elif level == I1:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3i1.txt')
            else:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3i2.txt')

            participants = []
            for c in compets:
                participants.append((c.compet_id_full,c.compet_name))

            #source_file = os.path.join(settings.MEDIA_ROOT,file_name)
            #error_msg = pack_and_send(email,reference,archive_path,answer_file,obi=True,year=YEAR,phase=phase,level=level,school_id=school.school_id)
            error_msg = pack_and_send(email, reference, num_questions, num_alternatives, archive_path, answer_file, participants, label1=label1, label2=label2, label3=label3, obi=True, year=YEAR, school_id=school.school_id, phase=phase, level=level)

        else:
            error_msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
            <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
        return render(request,
                      'fase3/restrito/corretor_folhas_respostas_resp.html',
                      context={'msg':error_msg, 'pagetitle': 'Submete Folhas Respostas'})
    else:
        form = CorretorFolhasRespostasForm()
    return render(request, 'fase3/restrito/corretor_folhas_respostas.html', {'form': form, 'pagetitle': 'Submete Folhas Respostas'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def corretorfolhasrespostas_admin(request,school_id):
    ###############
    # not authorized, 
    ###############
    #messages.error(request, 'Período de submissão de folhas de respostas finalizado.')
    #messages.error(request, 'O sistema será disponibilizado após a prova.')
    #return redirect('/fase3/ini/restrito/correcao_ini')

    if request.method == 'POST':
        form = CorretorFolhasRespostasForm(request.POST, request.FILES)
        if form.is_valid():
            level = int(request.POST['compet_type'])
            level_name = LEVEL_NAME[int(request.POST['compet_type'])]
            # write file
            
            school = School.objects.get(school_id=school_id)
            archive_path, resultfile = write_school_uploaded_file(school_id=school_id,
                                                   modality='ini',phase_name='fase-3',fwhy='sub_ini',
                                                   f=request.FILES['source_file'],fname=level_name)

            compets = Compet.objects.filter(compet_type=level,compet_school__school_site_phase3_ini=school_id,compet_classif_fase2=True)

            # for the report
            if level == IJ:
                levelstr = 'Nível Júnior'
                num_questions = 30
                num_alternatives = 5
            elif level == I1:
                levelstr = 'Nível 1'
                num_questions = 40
                num_alternatives = 5
            else:
                levelstr = 'Nível 2'
                num_questions = 50
                num_alternatives = 5
            label1 = f"OBI{YEAR}"
            label2 = f"Modalidade Iniciação • {levelstr}"
            label3 = school.school_name
            
            # and process it
            phase = 3
            email = school.school_deleg_email
            f = request.FILES['source_file']
            reference = request.POST['reference']
            file_name = get_valid_filename(f.name)
            if level == IJ:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3ij.txt')
            elif level == I1:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3i1.txt')
            else:
                answer_file = os.path.join(settings.BASE_DIR,'protected_files','gab_f3i2.txt')

            participants = []
            for c in compets:
                participants.append((c.compet_id_full,c.compet_name))

            #source_file = os.path.join(settings.MEDIA_ROOT,file_name)
            #error_msg = pack_and_send(email,reference,archive_path,answer_file,obi=True,year=YEAR,phase=phase,level=level,school_id=school.school_id)
            error_msg = pack_and_send(email, reference, num_questions, num_alternatives, archive_path, answer_file, participants, label1=label1, label2=label2, label3=label3, obi=True, year=YEAR, school_id=school.school_id, phase=phase, level=level)

        else:
            error_msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
            <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
        return render(request,
                      'fase3/restrito/corretor_folhas_respostas_resp.html',
                      context={'msg':error_msg, 'pagetitle': 'Submete Folhas Respostas'})
    else:
        form = CorretorFolhasRespostasForm()
    return render(request, 'fase3/restrito/corretor_folhas_respostas.html', {'form': form, 'pagetitle': 'Submete Folhas Respostas'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def correcao_ini(request):
    if request.method == 'POST':
        form = SubmeteSolucoesForm(request.POST, request.FILES)
        if form.is_valid():
            level = int(request.POST['compet_type'])
            level_name = LEVEL_NAME[int(request.POST['compet_type'])]
            # write file
            try:
                school_id = request.user.deleg.deleg_school.pk
            except:
                school_id = request.user.colab.colab_school.pk
            archive_path, resultfile = write_school_uploaded_file(school_id=school_id,
                                                   modality='ini',phase_name='fase-3',fwhy='sub_ini',
                                                   f=request.FILES['source_file'],fname=level_name)

            # and process it
            msg, result = check_solutions_file(archive_path, level, phase=1, school_id=school_id)
        else:
            msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
            <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
        return render(request,
                      'fase3/restrito/check_solutions_interm.html',
                      context={'msg':msg, 'result':result})
    else:
        form = SubmeteSolucoesForm()
    return render(request, 'fase3/restrito/correcao_ini.html', {'form': form, 'pagetitle': 'Correção Iniciação'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def lista_presenca(request, level_name):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="ListaPresenca_{}.pdf"'.format(level_name)

    try:
        subtitle1 = 'Modalidade ' + LEVEL_NAME_FULL[level]
    except: # error!
        return

    title = 'OBI{} - Fase 3 (Fase Nacional)'.format(YEAR)
    if level in (IJ,I1,I2):
        subtitle2 = 'Lista de Presença {}'.format(get_obi_date('ini-fase-3-prova',"%d/%m/%Y"))
    else:
        subtitle2 = 'Lista de Presença {}'.format(get_obi_date('prog-fase-3-prova',"%d/%m/%Y"))
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    if level in (IJ,I1,I2):
        compets = Compet.objects.filter(compet_type=level,compet_school__school_site_phase3_ini=school_id,compet_classif_fase2=True)
        #compets = compets | Compet.objects.filter(compet_type__in=(1,2,7),compet_school_id_fase3=school_id,compet_classif_fase2=True)
        #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site().filter(compet_type=level)
    else:
        compets = Compet.objects.filter(compet_type=level,compet_school__school_site_phase3_prog=school_id,compet_classif_fase2=True)
        #compets = compets | Compet.objects.filter(compet_type__in=(3,4,5,6),compet_school_id_fase3=school_id,compet_classif_fase2=True)
        #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site().filter(compet_type=level)

    compets = compets.order_by('compet_name')
    data = [['Num. Inscr.', 'Nome', 'Assinatura'],]
    for c in compets:
        MAX = 43
        name = c.compet_name
        if len(name) > MAX:
            name = name[:MAX] + '...'
        data.append((format_compet_id(c.compet_id),name, " "))

    report = PrintPresenceList(subtitle1)
    pdf = report.print_list(data, title, subtitle1, subtitle2)

    response.write(pdf)
    return response

@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def folha_respostas(request, level_name):
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="FolhaRespostas{level_name}.pdf"'
    p = canvas.Canvas(response)
    label1 = 'Olimpíada Brasileira de Informática'
    label3 = 'Fase 3 - {}'.format(get_obi_date('ini-fase-3-prova',"%d/%m/%Y"))
    label4 = 'OBI{}'.format(YEAR)
    if level == IJ:
        numquestions = 30
        label2 = 'Modalidade Iniciação - Nível Júnior'
    elif level == I1:
        numquestions = 40
        label2 = 'Modalidade Iniciação - Nível 1'
    else:
        label2 = 'Modalidade Iniciação - Nível 2'
        numquestions = 50
    numdigits = 6
    numalternatives = 5
    idcheck=True

    draw_page(p, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type_arg=0, id='', name='', obi=True, filled=False)
    p.save()
    return response

@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def folhas_respostas(request, level_name, order_by = 'compet_name'):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk    
    level = LEVEL[level_name]
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="FolhasRespostas{level_name}.pdf"'
    p = canvas.Canvas(response)
    print("level",level)
    compets = Compet.objects.filter(compet_type=level,compet_school__school_site_phase3_ini=school_id,compet_classif_fase2=True)
    print(len(compets))
    #compets = compets | Compet.objects.filter(compet_type__in=(1,2,7),compet_school_id_fase3=school_id,compet_classif_fase2=True)
    label1 = 'Olimpíada Brasileira de Informática'
    label3 = 'Fase 3 - {}'.format(get_obi_date('ini-fase-3-prova',"%d/%m/%Y"))
    label4 = 'OBI{}'.format(YEAR)
    if level == IJ:
        numquestions = 30
    elif level == I1:
        numquestions = 40
    else:
        numquestions = 50
    numdigits = 6
    numalternatives = 5
    if level == IJ:
        if order_by == 'compet_class':
            tmp = compets.filter(compet_type=IJ).order_by('compet_class','compet_name')
        else:
            tmp = compets.filter(compet_type=IJ).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível Júnior'
    elif level == I1:
        if order_by == 'compet_class':
            tmp = compets.filter(compet_type=I1).order_by('compet_class','compet_name')
        else:
            tmp = compets.filter(compet_type=I1).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível 1'
    elif level == I2:
        if order_by == 'compet_class':
            tmp = compets.filter(compet_type=I2).order_by('compet_class','compet_name')
        else:
            tmp = compets.filter(compet_type=I2).order_by('compet_name')
        label2 = 'Modalidade Iniciação - Nível 2'

    #tmp = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site().filter(compet_type=level).order_by('compet_name')

    if not tmp:
        return erro(request,'Não há competidores inscritos nessa modalidade e nível.')
    data = []
    for c in tmp:
        data.append((c.compet_id,c.compet_name))
    draw_pages(p, data, label1, label2, label3, label4, numquestions, numalternatives, numdigits, sheet_type=0, obi=True, filled=False)
    p.save()
    return response

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def consulta_subm_aceitas(request):
    class Item():
        def __init__(self, level, compet, program):
            self.level = level
            self.compet = compet
            self.program = program

    school = request.user.deleg.deleg_school
    submissions = SubFase3.objects.filter(compet__compet_school=school).order_by('compet__compet_type','compet_id','problem_name')
    if len(submissions) == 0:
        data = {'pagetitle':'Erro', 'msg':'Não há submissões aceitas.'}
        return render(request,'restrito/erro.html', data)
    elif len(submissions) == 1:
        msg = 'Foi encontrada uma submissão aceita.'
    else:
        msg = 'Foram encontradas {} submissões.'.format(len(submissions))
    result = []
    for s in submissions:
        name = "{} - {}".format(format_compet_id(s.compet.compet_id),s.compet.compet_name)
        level = LEVEL_NAME_FULL[s.compet.compet_type]
        problem_name = "{}{}".format(s.problem_name,LANG_SUFFIXES_NAMES[s.sub_lang])
        c = Item(level, name, problem_name)
        result.append(c)

    context = {'msg': msg, 'result': result}
    return render(request, "fase3/restrito/subm_aceitas.html", context)


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def recupera_subm_aceitas(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    sch = School.objects.get(pk=school_id)
    #if sch.school_is_site_phase3:
    #    site_compets = Compet.objects.filter(compet_school__school_site_phase3_prog=school_id,compet_type__in=(PJ,P1,P2,PS))
    #else:
    # recupera apenas soluções da escola
    #    site_compets = Compet.objects.filter(compet_school_id=school_id,compet_type__in=(PJ,P1,P2,PS))
    site_compets = Compet.objects.filter(compet_school_id=school_id,compet_type__in=(PJ,P1,P2,PS))
    submissions = SubFase3.objects.filter(compet__in=site_compets).order_by('compet__compet_type','compet_id','problem_name')
    if not submissions:
        data = {'pagetitle':'Erro', 'msg':'Não há submissões aceitas.'}
        return render(request,'restrito/erro.html', data)

    zip_file = zip_submissions(submissions,'solucoes_fase3')
    response = HttpResponse(zip_file,content_type='application/zip')
    response['Content-Disposition'] = 'attachment; filename="solucoes_fase3.zip"'
    return response

def compute_classif_one_school(school_id,level):
    NUM_QUESTIONS = {1: 15, 2: 15, 3: 300, 4: 400, 5: 300, 6: 400, 7: 15}
    MINIMUM_POINTS = round(NUM_QUESTIONS[level]/3)
    all_compets = Compet.objects.filter(compet_school_id=school_id, compet_type=level)
    null_compets = all_compets.filter(compet_points_fase3__isnull=True)
    compets = all_compets.filter(compet_points_fase3__isnull=False).order_by('-compet_points_fase3')

    for c in null_compets:
        if c.compet_classif_fase3 != None:
            print("********** compet changed to none??",c.compet_id,c.compet_name)
        c.compet_classif_fase3 = None
        return 0,0,0
        #c.save()

    if len(compets) == 0:
        return 0,0,0

    num_classif=round(0.15*len(compets))
    # at least one is classified, unless zero points
    if num_classif==0:
        num_classif=1

    # reset all classif info
    #with connection.cursor() as cursor:
    #    cursor.execute("UPDATE compet SET compet_classif_fase3 = NULL \
    #                    WHERE compet_school_id = %s and compet_type = %s", [school_id,level])
    n=0
    min_points=100000
    for c in compets:
        if c.compet_points_fase3>=MINIMUM_POINTS and (n<num_classif or min_points==c.compet_points_fase3):
            min_points=c.compet_points_fase3
            if c.compet_classif_fase3 != True:
                print("compet changed to True",c.compet_id,c.compet_name," from ",c.compet_classif_fase3)
            c.compet_classif_fase3 = True
            n=n+1
        else:
            if c.compet_classif_fase3 != False:
                print("compet changed to False",c.compet_id,c.compet_name," from ",c.compet_classif_fase3)
            # do not change if already true
            if c.compet_classif_fase3 != True:
                c.compet_classif_fase3 = False
        c.save()
    return len(compets),n,min_points


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def consulta_pref_fase3_prog(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    count_pj = Compet.objects.filter(compet_type=PJ, compet_classif_fase2=True, compet_school__school_city=school.school_city).count()
    count_p1 = Compet.objects.filter(compet_type=P1, compet_classif_fase2=True, compet_school__school_city=school.school_city).count()
    count_p2 = Compet.objects.filter(compet_type=P2, compet_classif_fase2=True, compet_school__school_city=school.school_city).count()
    count_ps = Compet.objects.filter(compet_type=PS, compet_classif_fase2=True, compet_school__school_city=school.school_city).count()
    compets = [count_pj,count_p1,count_p2,count_ps]
    if request.method == 'POST':
        form = SchoolPrefProgForm(request.POST)
        if form.is_valid():
            own = form.cleaned_data["site_prog_own_compet"]
            all = form.cleaned_data["site_prog_all_compet"]
            try:
                school_pref = SchoolPref.objects.get(school=school)
            except:
                school_pref = SchoolPref(school=school)
                
            school_pref.site_prog_own_compet = own
            school_pref.site_prog_all_compet = all
            school_pref.save()
            messages.success(request, 'Sua preferência sobre sede da Fase 3 foi salva')
    else:
        form = SchoolPrefProgForm()
    return render(request, 'fase3/restrito/school_pref_fase3.html', {'pagetitle':'Preferência Sede Fase 3 - Modalidade Programação', 'form': form, 'compets': compets})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def consulta_pref_fase3_ini(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    print(school.school_id)
    if request.method == 'POST':
        form = SchoolPrefIniForm(request.POST)
        if form.is_valid():
            own = form.cleaned_data["site_ini_own_compet"]
            all = form.cleaned_data["site_ini_all_compet"]
            try:
                school_pref = SchoolPref.objects.get(school=school)
            except:
                school_pref = SchoolPref(school=school)
                
            school_pref.site_ini_own_compet = own
            school_pref.site_ini_all_compet = all
            school_pref.save()
            messages.success(request, 'Sua preferência sobre sede da Fase 3 foi salva')
    else:
        form = SchoolPrefIniForm()
    return render(request, 'fase3/restrito/school_pref_fase3.html', {'pagetitle':'Preferência Sede Fase 3 - Modalidade Iniciação', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_recupera_cadastro(request,mod):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="cadastro_competidores.csv"'},
    )
    writer = csv.writer(response)

    if mod == 'ini':
        levels = (1,2,7)
    else:
        levels = (3,4,5,6)
        
    writer.writerow(['Num. Inscr.', 'Nível', 'Nome', 'Escola'])
    for compet_type in levels:
        compets = Compet.objects.filter(compet_type=compet_type,compet_school__school_site_phase3_ini=school.pk,compet_classif_fase2=True)
        for c in compets:
            writer.writerow([c.compet_id_full, LEVEL_NAME[c.compet_type], c.compet_name, c.compet_school])
    return response

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def verifica_ini(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    pagetitle = 'Verificação da Correção - Fase 3'

    compets = Compet.objects.filter(compet_type__in=(1,2,7),compet_school__school_site_phase3_ini=school.school_id,compet_classif_fase2=True)
    total = len(compets)
    if request.method == 'POST':
        form = CompetIniPontosFiltroForm(request.POST)
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
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetIniPontosFiltroForm(initial=instance)

    
    if compet_list_type:
        try:
            compet_list_type = int(compet_list_type)
            if compet_list_type in (PJ,P1,P2,PS):
                compet_list_type = None
            elif compet_list_type in (IJ,I1,I2):
                compets = compets.filter(compet_type=compet_list_type)
            else:
                compet_list_type = None
        except:
            compet_list_type = None
        request.session['compet_list_type'] = compet_list_type


    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    # fix order
    if compet_list_order == 'compet_points': 
        compet_list_order = 'compet_name'
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
    return render(request, 'fase3/restrito/verifica_ini.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form})
