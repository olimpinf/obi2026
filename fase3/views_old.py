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
from django.core.mail import send_mail, EmailMessage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template import loader

from principal.models import LANG_SUFFIXES_NAMES, LEVEL_NAME_FULL, IJ, I1, I2, PJ, P1, P2, PS
from principal.forms import ConsultaCompetidoresForm
from principal.models import Colab, Compet, Deleg, ResWWW, School, SubWWW, ResIni
from principal.utils.get_certif import (get_certif_colab, get_certif_compet,
                                       get_certif_deleg)
from principal.utils.utils import (format_compet_id, format_phone_number, get_data_cep,
                                  make_password, obi_year,
                                  verify_compet_id, write_uploaded_file, zip_submissions)

from principal.views import search_compets
from principal.utils.utils import calculate_page_size
from tasks.models import Alternative, Question, Task
from tasks.views import rendertask
from obi.settings import DEBUG, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL
from .forms import ConsultaResIniForm, RecuperaSubmForm
from .models import SubFase3, ResFase3

logger = logging.getLogger(__name__)

from .forms import ConsultaSedesFase3Form, ConsultaSuaSedeFase3Form

def search_school_site_phase3(f):
    schools = School.objects.filter(school_ok=True,school_is_site_phase3=True)
    if f['compet_id']:
        compet_id,compet_check = verify_compet_id(f['compet_id'])
        try:
            compet = Compet.objects.get(compet_classif_fase2=True, pk=compet_id)
        except:
            return []
        if compet:
            school_compet = School.objects.get(pk=compet.compet_school_id)
            if compet.compet_type in (IJ, I1, I2): 
                schools = schools.filter(pk = school_compet.school_site_phase3_ini)
            else:
                schools = schools.filter(pk = school_compet.school_site_phase3_prog)
    else:
        schools = []
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
            schools = search_school_site_phase3(f)
            return render(request, 'fase3/mostra_sede.html', { 'items': schools })
    else:
        form = ConsultaSuaSedeFase3Form()
    return render(request, 'fase3/consulta_sua_sede.html', {'form': form})

def mapa_sedes(request, map_type):
    return render(request, 'fase3/mapa_sedes.html', {'tipo': map_type})


def consulta_sedes(request):
    if request.method == 'POST':
        form = ConsultaSedesFase3Form(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            schools = list_school_sites_phase3(f)
            return render(request, 'fase3/mostra_sede.html', { 'items': schools })
    else:
        form = ConsultaSedesFase3Form()
    return render(request, 'fase3/consulta_sedes.html', {'form': form})

def mostra_folha_respostas(request):
    compet_id = request.session['compet_id']
    response = HttpResponse(content_type='image/jpg')
    response['Content-Disposition'] = 'attachment; filename="FolhaResposta.jpg"'
    image_file = os.path.join(settings.MEDIA_ROOT,'folhas_respostas','fase-3','{0:05d}.jpg'.format(compet_id))
    with open(image_file, "rb") as f:
        data = f.read()
    response.write(data)
    #request.session['compet_id'] = 0
    return response

def corrige_iniciacao(request,year,phase,level,code,show_answers=False):
    correct_answers = 0
    if request.method == 'POST':
        try:
            descriptor = request.POST['descriptor']
        except:
            raise
        try:
            task = Task.objects.get(descriptor=descriptor)
        except:
            raise
        questions = Question.objects.filter(task=task)
        total_questions = len(questions)
        if not questions:
            raise
        for q in questions:
            if str(q.num) in request.POST.keys():
                try:
                    answer = Alternative.objects.filter(question=q).get(num=request.POST[str(q.num)],correct=True)
                    correct_answers += 1
                except:
                    pass
        # find level/modality from descriptor
        tmp = re.match('[0-9]{4}f(?P<phase>[123s])(?P<mod>[ip])(?P<level>[j12us])_',descriptor)
        tmp_mod = tmp.group('mod')
        tmp_level = tmp.group('level')
        context={'correct_answers':correct_answers,'total_questions':total_questions,'task':task}
        return render(request,'tasks/tarefa_iniciacao_resp.html', context)
    else:
        return render(request,'obi/error_500.html', {})

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
      
def consulta_res_ini(request):
    pagetitle = 'Consulta Pontuação Fase 3 - Iniciação'
    info_msg = 'Utilize este formulário para consultar a pontuação da Fase 3'
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            #result = grecaptcha_verify(request) #is_recaptcha_valid(request)
            result = True
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(1,2,7))
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Iniciação.")
                try:
                    a = ResIni.objects.get(compet_id=int(compet_id))
                    result = {'compet': c, 'answers': a}
                    request.session['compet_id'] = c.compet_id
                    return render(request, 'fase3/consulta_res_ini_resp.html', {'result': result})
                except:
                    messages.error(request, "Respostas não encontradas para esse competidor.")
            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResIniForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

      
def consulta_res_prog(request):
    pagetitle = 'Consulta Correção Fase 3 - Programação'
    info_msg = 'Utilize este formulário para consultar a correção da Fase 3'
    if request.method == 'POST':
        form = ConsultaResIniForm(request.POST)
        if form.is_valid():
            #result = grecaptcha_verify(request) #is_recaptcha_valid(request)
            result = True
            if result:
                f = form.cleaned_data
                #compet_id,check = verify_compet_id(f['compet_id'])
                #c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                #res_log = ResFase3.objects.filter(compet_id=c.compet_id)
                #result = {'compet': c, 'log': res_log}
                #return render(request, 'fase3/consulta_res_prog_resp.html', {'result': result})
                try:
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
    urlconsult = 'fase2:consulta_classif'
    urlresp='fase2:consulta_classif_resp'
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
                    print('is bad')
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
                    return render(request, 'fase2/recupera_subm_prog_resp.html', {'result': result,'msg': msg})
                zip_file = zip_submissions(submissions,'solucoes_fase2')
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
                    email = EmailMessage(subject, msg_text, from_addr, [to_addr], reply_to=[DEFAULT_REPLY_TO_EMAIL])
                    email.attach('solucoes_fase3.zip', zip_file.read(), 'application/zip')
                    email.send()
                    #send_mail(subject, msg_text, from_addr, [to_addr], file=zip_file, fname='solucoes_fase2.zip')
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
                    email = EmailMessage(subject, msg_text, from_addr, [to_addr], reply_to=[DEFAULT_REPLY_TO_EMAIL])
                    email.attach('solucoes_fase3.zip', zip_file.read(), 'application/zip')
                    email.send()
                    #send_mail(subject, msg_text, from_addr, [to_addr], file=zip_file, fname='solucoes_fase2.zip')
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
                return render(request, 'fase2/recupera_subm_prog_resp.html', {'result': result, 'msg': msg})

            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = RecuperaSubmForm()
    return render(request, 'principal/consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})
