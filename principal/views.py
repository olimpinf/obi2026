import secrets
import json
import logging
import os
import re
import sys
import urllib
import urllib.parse
import urllib.request
import time
from time import sleep
from datetime import datetime, timedelta
from urllib.request import urlopen
from random import randint

import hmac
import hashlib
import base64


import requests
from django.contrib.auth.models import User, Group
from django.conf import settings
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Q,F
from django.http import HttpResponseRedirect
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.http import JsonResponse, HttpResponseBadRequest

from django.shortcuts import redirect, render
from django.template import loader
from django.core.mail import send_mail, EmailMessage
from django.utils.timezone import make_aware
from django.utils import timezone
from django.views.decorators.http import require_GET

from .models import (LANG_SUFFIXES_NAMES, LEVEL_NAME, LEVEL_NAME_FULL, CompetAutoRegister, School, SchoolExtra, CompetCfObi,
                     PasswordRequest, Password, PasswordCms, PJ, P1, P2, PS, CertifHash, EmailRequest)
from .utils.get_certif import (get_certif_colab, get_certif_compet, get_certif_compet_cf,
                                       get_certif_deleg)
from .utils.get_letter import (get_letter_compet, get_letter_teacher)

from cms.utils import (cms_update_password)
from .utils.utils import (get_data_cep, calculate_page_size,
                          make_password, obi_year, remove_accents,
                          verify_compet_id, write_uploaded_file)
from tasks.models import Alternative, Question, Task
from tasks.views import rendertask
from obi.settings import YEAR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL, UA_SECRET

from restrito.views import queue_email

from .forms import (ConsultaCompetidoresForm, ConsultaEscolasForm, RegisterEmailForm,
                    ConsultaParticipantesForm, ConsultaResFase1IniForm,
                    AutoCadastroCompetForm, RecuperaCadastroForm,
                    RelataErroForm,
                    RegisterSchoolForm, SubmeteSolucaoPratiqueForm,
                    PasswordResetForm, PasswordResetCompetForm, PasswordResetCoordForm)
from .models import Colab, Compet, Deleg, ResWWW, School, SubWWW
from .admin import authorize_a_school

logger = logging.getLogger('obi')

EMAIL_MSG_COMPET_PRE = '''{greeting} competidor{sex_suffix},

você está recebendo esta mensagem porque informou este endereço de
email ao se pré-registrar na OBI (Olimpíada Brasileira de Informática),
com os seguinte dados

Nome: {name}
Modalidade: {modal}
Escola: {school}
Cidade: {city}
Estado: {state}
Coordenador Local: {coord}

Quando o professor Coordenador Local da OBI na sua escola validar sua
inscrição você receberá uma mensagem informando seu número de inscrição
e a senha para acessar sua página pessoal da OBI2025.

Boa OBI2025!

Esta é uma mensagem enviada automaticamente, por favor não responda.

---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

MESSAGE_REGISTERED = """
Caro(a) Prof(a). {contact_name},

obrigado por cadastrar a escola

      {school_name}

na Olimpíada Brasileira de Informática (https://olimpiada.ic.unicamp.br).

Caso o(a) Sr(a). não tenha preenchido o cadastro da OBI, alguém de sua escola deve ter preenchido o cadastro e colocado o seu nome como responsável. Se o(a) Sr(a). não é o responsável pela OBI em sua escola, solicitamos que entre em contato o mais breve possivel com a Coordenação da OBI, respondendo a esta mensagem, para evitar que o cadastro seja utilizado indevidamente em seu nome.

As informações fornecidas para cadastro serão verificadas com a escola, o que pode demorar um ou dois dias. Assim que o cadastro for confirmado enviaremos uma outra mensagem, informando a senha para acesso ao sistema da OBI.

Esta é uma mensagem enviada automaticamente, por favor não responda.

Atenciosamente,

Coordenação da OBI2025
olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399
"""


INTERJECTIONS = ['Ahh... ', 'Ihh... ', 'Xiii... ', 'Ops... ', 'Vixe... ']
def interjection():
    return INTERJECTIONS[randint(0,len(INTERJECTIONS)-1)]

def sucesso(request, title, msg):
    msg = '<em>' + msg + "</em>"
    data = {'pagetitle':title, 'msg': msg}
    return render(request,'principal/sucesso.html', data)

def testa_correcao(request):
    data = {'pagetitle':'Erro', 'msg': ""}
    return render(request,'principal/testa_correcao.html', data)

def ambiente_prova(request):
    context = {'pagetitle':'Ambiente de Prova'}
    return render(request,'principal/ambiente_prova.html', context)


def in_sbc_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name__in=['sbc']).exists()


@user_passes_test(in_sbc_group, login_url='/contas/login/')
def sbc_index(request):
    return redirect('/semana/sbc_lista_pagamento')


def pix_qrcode(request):
    return render(request,'principal/pix_qrcode.html')


def handler400(request, exception):
    msg = interjection() + 'ocorreu um erro durante o processamento da sua solicitação: '
    msg = msg + '<em>solicitação inválida.</em>'
    data = {'pagetitle':'Erro', 'msg': msg}
    return render(request,'principal/erro.html', data)


def handler403(request, exception):
    msg = interjection() + 'ocorreu um erro durante o processamento da sua solicitação: '
    msg = msg + '<em>você não tem permissão para acessar a página solicitada.</em>'
    data = {'pagetitle':'Erro', 'msg': msg}
    return render(request,'principal/erro.html', data)


def handler404(request, exception):
    msg = interjection() + 'ocorreu um erro durante o processamento da sua solicitação: '
    msg = msg + '<em>a página solicitada não existe.</em>'
    data = {'pagetitle':'Erro', 'msg': msg}
    return render(request,'principal/erro.html', data)


def handler500(request):
    msg = interjection() + 'ocorreu um erro durante o processamento da sua solicitação.'
    data = {'pagetitle':'Erro', 'msg': msg}
    return render(request,'principal/erro.html', data)


def erro(request, msg):
    msg = interjection() + 'ocorreu um erro durante o processamento da sua solicitação: <em>' + msg + "</em>"
    data = {'pagetitle':'Erro', 'msg': msg}
    return render(request,'principal/erro.html', data)


def aviso(request, msg):
    data = {'pagetitle':'Aviso', 'msg': msg}
    return render(request,'principal/aviso.html', data)


def aplicativos(request):
    return render(request, 'flatpages:info/aplicativos', {})


def perfil(request):
    if request.user.is_superuser:
        return HttpResponseRedirect('/admin/')
    if request.user.is_authenticated and request.user.groups.filter(name='local_coord').exists():
        return HttpResponseRedirect('/restrito/')
    return render(request, 'principal/index.html', {})


def relata_erro(request,page):
    try:
        sender = request.user
        sender_email = sender.email
        sender_name = sender.last_name
    except:
        sender_email = ''
        sender_name = 'anônimo'
    if request.method == 'POST':
        form = RelataErroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            report = f['description']
            subject = 'Site: Relato de erro'
            body = "{}\n\nPágina:{}\nRelator: {} {}".format(report,page,sender_name, sender_email)
            to_addr = DEFAULT_FROM_EMAIL
            queue_email(
                subject,
                body,
                DEFAULT_FROM_EMAIL,
                to_addr
            )
            logger.info("relato de erro: {}".format(report))

            # send_mail(
            #     'Site: Relato de erro',
            #     "{}\n\nPágina:{}\nRelator: {} {}".format(report,page,sender_name, sender_email),
            #     DEFAULT_FROM_EMAIL,
            #     [DEFAULT_FROM_EMAIL]
            # )
            return render(request, 'principal/relata_erro_resp.html', {})
    else:
        form = RelataErroForm()
    return render(request, 'principal/relata_erro.html', {'form': form, 'offending_page':page})


def pre_inscricao_compet(request, id):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    return aviso(request, msg)

    school = School.objects.get(school_id=int(id))
    #print(school.school_name, school.school_id)

    # error message is wrong. Must check forms
    if request.method == 'POST':
        form = AutoCadastroCompetForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            c = CompetAutoRegister(compet_name=f['compet_name'],
                                   compet_type=f['compet_type'],
                                   compet_year=f['compet_year'],
                                   compet_class=f['compet_class'],
                                   compet_email=f['compet_email'],
                                   compet_birth_date=f['compet_birth_date'],
                                   compet_sex=f['compet_sex'],
                                   compet_school=school)
            c.save()
            compet_send_email(request,c,school,queue=True)
            logger.info("pre_inscricao_compet succeeded: {}".format(c))
            return render(request, 'principal/pre_inscricao_compet_resp.html', {'compet': c})
    else:
        data = {'school_id': school.school_id}
        form = AutoCadastroCompetForm(initial=data)

    return render(request, 'principal/pre_inscricao_compet.html', {'form': form, 'school':school})


def compet_send_email(request,c,school,queue=False):
    mod = LEVEL_NAME_FULL[int(c.compet_type)]
    current_year = obi_year(as_int=True)

    if c.compet_sex == 'F':
        greeting = 'Prezada'
        sex_suffix = 'a'
    else:
        greeting = 'Prezado'
        sex_suffix = ''
    msg = EMAIL_MSG_COMPET_PRE
    body = msg.format(greeting=greeting,
                      sex_suffix=sex_suffix,
                      name=c.compet_name,
                      school=school.school_name,
                      modal=mod,
                      city=school.school_city,
                      state=school.school_state,
                      coord=school.school_deleg_name)

    if queue:
        queue_email(
            f'OBI{current_year}, pré-inscrição',
            body,
            DEFAULT_FROM_EMAIL,
            c.compet_email
        )
        logger.info("queued email to compet, user={}, compet={}, reason=pre-compet".format(request.user,c))

    else:
        try:
            send_mail(
                f'OBI{current_year}, pré-inscrição',
                body,
                DEFAULT_FROM_EMAIL,
                [c.compet_email]
            )
            logger.info("sent email to pre-compet, user={}, compet={} ".format(request.user,c))
        except:
            messages.error(request, 'Envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
            logger.warning("send email to pre-compet failed, user={}, compet={}".format(request.user,c))


def consulta_escolas_pre_inscricao(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    #msg = 'Período de inscrições terminou.'
    #return aviso(request, msg)

    if request.method == 'POST':
        form = ConsultaEscolasForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            schools = search_schools(f)
            # set session data
            request.session['school_name']=f['school_name']
            request.session['school_city']=f['school_city']
            request.session['school_state']=f['school_state']
            request.session['school_order']=f['school_order']
            return HttpResponseRedirect('consulta_escolas_pre_inscricao_resp')
    else:
        form = ConsultaEscolasForm()
    return render(request, 'principal/consulta_escolas_pre_inscricao.html', {'form': form})


def consulta_escolas_pre_inscricao_resp(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    #msg = 'Período de inscrições terminou.'
    #return aviso(request, msg)

    f = {}
    f['school_name'] = request.session['school_name']
    f['school_city'] = request.session['school_city']
    f['school_state'] = request.session['school_state']
    f['school_order'] = request.session['school_order']
    schools = search_schools(f)
    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(schools), page)
    paginator = Paginator(schools, page_size)
    try:
        schools = paginator.page(page)
    except PageNotAnInteger:
        schools = paginator.page(1)
    except EmptyPage:
        schools = paginator.page(paginator.num_pages)
    return render(request, 'principal/consulta_escolas_pre_inscricao_resp.html', { 'items': schools })


def mostra_escola_pre_inscricao(request,id):
    #msg = 'Sistema em manutenção, por favor aguarde'
    #msg = 'Período de inscrições terminou.'
    #return aviso(request, msg)

    template = loader.get_template('principal/mostra_escola_pre_inscricao.html')
    school = School.objects.get(school_id=id)
    context = {'school':school}
    return HttpResponse(template.render(context, request))


def acesso_escolas(request):
    template = loader.get_template('principal/acesso_escolas.html')
    context = {}
    return HttpResponse(template.render(context, request))


def school_name_repeated(name,city):
    "Returns True if school name appears already in the DB"
    is_repeated = False
    try:
        query = School.objects.filter(school_city__iexact=city)
        query = query.only('school_name')
        school_names = []
        for s in query:
            school_names.append(remove_accents(s.school_name))
        if remove_accents(name.strip()) in school_names:
            is_repeated = True
    except:
        is_repeated = False
    return is_repeated

def exec_cadastra_escola(f, is_auto=False):
    logger.info('in exec_cadastra_escola')
    print('in exec_cadastra_escola',f)
    #if school_name_repeated(f['school_name'],f['school_city']):
        #logger.info('escola com esse nome já cadastrada nessa cidade.')
        #messages.error(request, 'Aviso: escola com esse nome já cadastrada nessa cidade, cadastro efetuado mas entraremos em contato para esclarecer a situação. ')
        #return False, "Erro: Escola com esse nome já cadastrada nessa cidade.", None
    subject = obi_year() + ' - Cadastro em processamento'

    try:
        new_school = School(school_name=f['school_name'],
                            school_type=f['school_type'],
                            school_inep_code=f['school_inep_code'],
                            school_zip=f['school_zip'],
                            school_address=f['school_address'],
                            school_address_number=f['school_address_number'],
                            school_address_complement=f['school_address_complement'],
                            school_address_district=f['school_address_district'],
                            school_phone=f['school_phone'],
                            school_city=f['school_city'],
                            school_state=f['school_state'],
                            school_deleg_name=f['school_deleg_name'],
                            school_deleg_phone=f['school_deleg_phone'],
                            school_deleg_cpf=f['school_deleg_cpf'],
                            school_deleg_email=f['school_deleg_email'],
                            school_deleg_username=f['school_deleg_email'],
                            school_is_known=f['school_is_known'],
                            school_change_coord=f['school_change_coord'],
                            )
    except Exception as e:
        return False, "Erro: {}".format(str(e)), None
    if f['school_is_known']:
        # remember last year's id
        new_school.school_prev = f['school_prev']
    else:
        new_school.school_prev = 0
    try:
        new_school.save()
    except Exception as e:
        return False, "Erro: {}".format(str(e)), None
    if not is_auto:
        body = MESSAGE_REGISTERED.format(contact_name=f['school_deleg_name'], school_name=f['school_name'])
        from_addr = settings.DEFAULT_FROM_EMAIL
        to_addr = f['school_deleg_email']

        queue_email(
            subject,
            body,
            DEFAULT_FROM_EMAIL,
            to_addr
        )
        logger.info("queued email to school_deleg, user=anonymous, reason=register")

        # send a duplicate 
        to_addr = "ranido@unicamp.br"
        queue_email(
            subject,
            body,
            DEFAULT_FROM_EMAIL,
            to_addr
        )

        
        # try:
        #     send_mail(
        #         subject,
        #         body,
        #         settings.DEFAULT_FROM_EMAIL,
        #         (f['school_deleg_email'],)
        #     )
        # except Exception as e:
        #     logger.warning(f"error sending email in cadastra_escola, school={new_school}, email={f['school_deleg_email']}")
        #     return False, "Erro ao enviar mensagem: {}".format(str(e)), None
    return True,"",new_school

def cadastra_escola_auto(request,hash):
    current_year = obi_year(as_int=True)
    # get hash from previous year DB
    try:
        old_school = School.objects.using('obi{}'.format(current_year-1)).get(school_hash=hash)
    except:
        msg = 'Erro: solicitação inválida.'
        logger.info(f'cadastra_escola_auto failed, wrong hash: {hash}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Confirma Cadastro de Escola'})

    # check if school already in this year's DB

    if School.objects.filter(school_prev=old_school.school_id).exists():
        msg = f'Erro: solicitação inválida, cadastro da escola <p>{old_school.school_name} <p>já foi confirmado.'
        logger.info(f'cadastra_escola_auto failed, already registered: {old_school.school_name}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Confirma Cadastro de Escola'})

    # do the work

    return cadastra_escola_auto_exec(request, old_school)

def cadastra_escola_auto_exec(request, school):
    s = school
    data = {'school_name':s.school_name}
    data['school_id'] = s.school_id
    data['school_type'] = s.school_type
    data['school_inep_code'] = s.school_inep_code
    data['school_phone'] = s.school_phone
    data['school_zip'] = s.school_zip
    data['school_address'] = s.school_address
    data['school_address_number'] = s.school_address_number
    data['school_address_district'] = s.school_address_district
    data['school_city'] = s.school_city
    data['school_state'] = s.school_state
    data['school_address_complement'] = s.school_address_complement
    data['school_deleg_name'] = s.school_deleg_name
    data['school_deleg_phone'] = s.school_deleg_phone
    data['school_deleg_username'] = s.school_deleg_username
    data['school_deleg_email'] = s.school_deleg_email
    data['school_deleg_email_conf'] = s.school_deleg_email
    data['school_code'] = s.school_code
    data['school_prev'] = s.school_id
    data['school_is_known'] = True
    data['school_ok'] = True

    ok,msg,new_school = exec_cadastra_escola(data, is_auto=True)
    if not ok:
        template = loader.get_template('principal/cadastra_escola_erro.html')
        context = {'school': data, 'erro': msg}
        return HttpResponse(template.render(context, request))

    # now authorize the school
    try:
        password = make_password()
        authorize_a_school(request,new_school,password)
        msg = f'<p>Obrigado por confirmar o cadastro da escola <p>{data["school_name"]}. <p>Uma mensagem com a senha para acesso foi enviada para o endereço de email cadastrado para o Coordenador Local.'
        'A mensagem pode demorar alguns minutos. '
        'Verifique sua lixeira eletrônica para ter certeza de que a mensagem não foi marcada erroneamente como lixo.'
        pagetitle = "Cadastro confirmado"
    except:
         msg = f'Ocorreu um erro ao confirmar o cadastro da escola {data["school_name"]}. Você pode efetuar um novo cadastro para a escola <a href="/cadastra_escola">clicando aqui</a>. Se a escola tem o mesmo nome, na mesma cidade, ou o mesmo código INEP, o novo cadastro será consolidado com o cadastro antigo para fins de história na OBI (como o número de medalhas).'
         pagetitle = "Erro"
    return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle': pagetitle})

def cadastra_escola_auto_envio(request):
    ''' envia hash da escola para email do coordenador do ano passado, para
        recadastramento da escola.
    '''
    class AUser:
        pass
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            current_year = obi_year(as_int=True)
            f = form.cleaned_data
            username = f['username'].strip()
            # can be a username or an email
            try:
                # try first username
                #print("trying username")
                user = User.objects.using('obi{}'.format(current_year-1)).get(username=username)
                user_type, full_name, greeting = get_user_type(user)
                if user_type == 'coord':
                    hash = user.deleg.deleg_school.school_hash
                    school_name = user.deleg.deleg_school.school_name
                    # send link for school
                    template = loader.get_template('principal/mensagem_cadastra_escola_auto_hash.html')
                    subject = 'OBI - Confirmação de cadastro de escola'
                    body = template.render({'hash': hash, 'greeting': greeting, 'full_name': full_name, 'school_name': school_name}, request)
                    from_addr = settings.DEFAULT_FROM_EMAIL
                    to_addr = (user.email,)

                    #msg = EmailMessage(subject, body, from_addr, to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL])
                    #msg.send()

                    queue_email(
                        subject,
                        body,
                        DEFAULT_FROM_EMAIL,
                        user.email
                    )

                    logger.info(f'cadastra_escola_auto_envio sent hash successfull for email={user.email}, username={user.username}')
                else:
                    logger.info(f'cadastra_escola_auto_envio sent hash failed, not coordinator,  for email={user.email}, username={user.username}')
            except:
                #print("username failed, trying email")
                email = username
                users = User.objects.using('obi{}'.format(current_year-1)).filter(email=email)
                if len(users) == 0:
                    # do nothing, wrong email
                    logger.info('cadastra_escola non existent username or email = {}'.format(username))
                elif len(users) == 1:
                    # send link for school
                    user_type, full_name, greeting = get_user_type(users[0])
                    if user_type == 'coord':
                        s = users[0].deleg.deleg_school
                        # send link for school
                        hash = s.school_hash
                        subject = 'OBI - Confirmação de cadastro de escola'
                        template = loader.get_template('principal/mensagem_cadastra_escola_auto_hash.html')
                        body = template.render({'hash': hash, 'greeting': greeting, 'full_name': full_name, 'school_name': s.school_name}, request)
                        from_addr = settings.DEFAULT_FROM_EMAIL
                        to_addr = (users[0].email,)

                        #msg = EmailMessage(subject, body, from_addr, to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL])
                        #msg.send()

                        queue_email(
                            subject,
                            body,
                            DEFAULT_FROM_EMAIL,
                            users[0].email
                        )

                        #msg = EmailMessage(subject, body, from_addr, ('olimpinf@ic.unicamp.br',), reply_to=[DEFAULT_REPLY_TO_EMAIL])
                        #msg.send()
                        logger.info(f'cadastra_escola_send_hash send hash successfull for email={email}, username={users[0].username}')
                    else:
                        logger.info(f'cadastra escola_send_hash failed for email={email}, username={users[0].username}')
                else:
                    # user manages more than one school, send usernames
                    # deal only with coordinators
                    #print("user manages more than one school, send usernames")
                    #print(users)
                    user_schools=[]
                    for u in users:
                        user_type, full_name, greeting = get_user_type(u)
                        if user_type == 'coord':
                            auser = AUser()
                            auser.username = u.username
                            s = u.deleg.deleg_school
                            auser.school_name = s.school_name
                            # send link for school
                            hash = s.school_hash
                            auser.hash = hash
                            user_schools.append(auser)
                        else:
                            logger.info('email is not a coord, may be a compet with the coord email={}'.format(email))
                            #print('email is not a coord, may be a compet with the coord email={}'.format(email))

                    #print('user_schools',user_schools)

                    if len(user_schools) > 0:
                        template = loader.get_template('principal/mensagem_cadastra_escola_auto_multiple_hash.html')
                        subject = 'OBI - confirmação de cadastro de escola'
                        body = template.render({'hash': hash, 'greeting': greeting, 'full_name': full_name, 'user_schools': user_schools, 'user': users[0]}, request)
                        from_addr = settings.DEFAULT_FROM_EMAIL
                        to_addr = (email,)


                        #msg = EmailMessage(subject, body, from_addr, to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL])
                        #msg.send()

                        queue_email(
                            subject,
                            body,
                            DEFAULT_FROM_EMAIL,
                            email
                        )

                        logger.info('cadastra_escola_auto_envio sent hash multiple schools successfull for email={}'.format(email))
                    else:
                        logger.info(f'cadastra escola_send_hash failed for email={email}, username={users[0].username}')
        msg = 'Uma mensagem com instruções para a confirmação do cadastro da escola foi enviada para o endereço de email do professor Coordenador Local da escola. <p>A mensagem pode demorar alguns minutos. ' +\
                    'Verifique sua lixeira eletrônica para ter certeza de que a mensagem não foi marcada erroneamente como lixo.'
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Confirmação de Cadastro de Escola'})

    else:
        form = PasswordResetForm()
    return render(request, 'principal/school_confirm_form.html', {'form': form, 'pagetitle':'Confirmação de Cadastro de Escola'})


def cadastra_escola_1(request):
    logger.info("in cadastra_escola_1")
    return render(request, 'principal/cadastra_escola_1.html', {})

def cadastra_escola_2(request, hash):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    logger.info("in cadastra_escola_2")
    return render(request, 'principal/cadastra_escola_2.html', {})

def cadastra_escola_3(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    logger.info("in cadastra_escola_3")
    return render(request, 'principal/cadastra_escola_3.html', {})

def cadastra_escola_4(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    return render(request, 'principal/cadastra_escola_4.html', {})

def cadastra_escola_5(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    return render(request, 'principal/cadastra_escola_5.html', {})

def cadastra_escola_6(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    return render(request, 'principal/cadastra_escola_6.html', {})

def cadastra_escola_7(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    return render(request, 'principal/cadastra_escola_7.html', {})

def confirma_email(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)

    MESSAGE_REGISTER_EMAIL = """
Caro(a) Prof(a).,

obrigado pelo interesse na OBI2025.

Para cadastrar sua escola, utilize o seguinte link:

https://olimpiada.ic.unicamp.br/cadastra/{hash}

Esta é uma mensagem enviada automaticamente, por favor não responda.

Atenciosamente,

Coordenação da OBI2025
olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399
"""

    
    if request.method == 'POST':
        form = RegisterEmailForm(request.POST)
        logger.info(f'email = {form["deleg_email"]}')
        
        if form.is_valid():
            f = form.cleaned_data
            try:
                email_req = EmailRequest.objects.get(email=f['deleg_email'])
            except:
                hash = secrets.token_urlsafe(32)
                email_req = EmailRequest(email=f['deleg_email'],hash=hash)
                email_req.save()

            body = MESSAGE_REGISTER_EMAIL.format(hash=email_req.hash)
            from_addr = settings.DEFAULT_FROM_EMAIL
            to_addr = f['deleg_email']
            subject = f'OBI{YEAR}, cadastro de escola'

            queue_email(
                subject,
                body,
                DEFAULT_FROM_EMAIL,
                to_addr
            )
            logger.info("queued email to school_deleg, user=anonymous, reason=confirmação de email")

            # send a duplicate 
            to_addr = "ranido@unicamp.br"
            queue_email(
                subject,
                body,
                DEFAULT_FROM_EMAIL,
                to_addr
            )
            template = loader.get_template('principal/confirma_email_resp.html')
            context = {'email': email_req.email}
            return render(request, 'principal/confirma_email_resp.html', context)
        else:
            logger.info("get confirma_email failed validation")
            return render(request, 'principal/confirma_email.html', {'form': form, 'title': 'Cadastra Escola'})
    else:
        logger.info("get confirma_email")
        form = RegisterEmailForm()
        return render(request, 'principal/confirma_email.html', {'form': form, 'title': 'Cadastra Escola'})

def cadastra_escola(request, hash):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)
    try:
        email_req = EmailRequest.objects.get(hash=hash)
    except:
        logger.info("get cadastra_escola fail validation")
        return render(request, 'principal/erro.html', {'msg': 'Erro na solicitação.'})

    first_school = not School.objects.filter(school_deleg_username=email_req.email).exists()
    print('first_school', first_school)
    if request.method == 'POST':
        form = RegisterSchoolForm(request.POST)
        print(form)
        # logger.info('RegisterSchoolForm --  school_type={}; school_zip={}; school_address={}; school_address_number={}; school_address_complement={}; school_address_district={}; school_phone={}; school_city={}; school_state={};school_deleg_name={}; school_deleg_phone={}; school_deleg_email={}; school_deleg_cpf={},school_is_known={}'.format(form['school_type'],
        #                                                 form['school_zip'],
        #                                                 form['school_address'],
        #                                                 form['school_address_number'],
        #                                                 form['school_address_complement'],
        #                                                 form['school_address_district'],
        #                                                 form['school_phone'],
        #                                                 form['school_city'],
        #                                                 form['school_state'],
        #                                                 form['school_deleg_name'],
        #                                                 form['school_deleg_phone'],
        #                                                 form['school_deleg_email'],
        #                                                 form['school_deleg_cpf'],
        #                                                 form['school_is_known'])
        #         )
          
        if form.is_valid():
            f = form.cleaned_data
            ok,msg,new_school = exec_cadastra_escola(f)
            if ok:
                template = loader.get_template('principal/cadastra_escola_resp.html')
                context = {'school':f}
                return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('principal/cadastra_escola_erro.html')
                context = {'school':f, 'erro': msg}
                return HttpResponse(template.render(context, request))
        # else:
        #     logger.info("get cadastra_escola fail validation")
        #     print("Form errors:", form.errors)
        #     print("Form errors as dict:", form.errors.as_data())
        #     return render(request, 'principal/erro.html', {'msg': 'Erro na solicitação, dados inválidos.'})
    else:
        logger.info("get cadastra_escola")

        if first_school:
            #data = {'email': email_req.email}
            initial = {'school_deleg_email': email_req.email,'first_school':True}
            form = RegisterSchoolForm(initial=initial)
        else:
            school = School.objects.filter(school_deleg_username=email_req.email)[0]
            #data = {'email': email_req.email, 'school_deleg_name': school.school_deleg_name}
            initial = {'school_deleg_email': email_req.email,
                       'school_deleg_name': school.school_deleg_name,
                       'school_deleg_phone': school.school_deleg_phone,
                       'school_deleg_cpf': school.school_deleg_cpf,
                       'first_school':False}
            form = RegisterSchoolForm(initial=initial)
            
    return render(request, 'principal/cadastra_escola.html', {'form': form, 'title': 'Cadastra Escola', 'school_is_known':False})
    
def cadastra_escola_fase3(request):
    #msg = 'Período de cadastro de escolas terminou.'
    #return aviso(request, msg)

    if request.method == 'POST':
        form = RegisterSchoolForm(request.POST)
        logger.info('school_site_fase3, school_type={}; school_zip={}; school_address={}; school_address_number={}; school_address_complement={}; school_address_district={}; school_phone={}; school_city={}; school_state={};school_deleg_name={}; school_deleg_phone={}; school_deleg_email={}; school_deleg_username={}; school_is_known={}'.format(form['school_type'],
                                                        form['school_zip'],
                                                        form['school_address'],
                                                        form['school_address_number'],
                                                        form['school_address_complement'],
                                                        form['school_address_district'],
                                                        form['school_phone'],
                                                        form['school_city'],
                                                        form['school_state'],
                                                        form['school_deleg_name'],
                                                        form['school_deleg_phone'],
                                                        form['school_deleg_email'],
                                                        form['school_deleg_username'],
                                                        form['school_is_known'])
                )
          
        if form.is_valid():
            f = form.cleaned_data
            ok,msg,new_school = exec_cadastra_escola(f)
            if ok:
                new_school.school_is_site_phase3 = True
                new_school.save()
                template = loader.get_template('principal/cadastra_escola_fase3_resp.html')
                context = {'school':f}
                return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('principal/cadastra_escola_erro.html')
                context = {'school':f, 'erro': msg}
                return HttpResponse(template.render(context, request))
        else:
            logger.info("get cadastra_escola fail validation")
            return render(request, 'principal/cadastra_escola.html', {'form': form, 'title': 'Cadastra Sede Fase Nacional', 'school_is_known':False})
    else:
        logger.info("get cadastra_escola")
        form = RegisterSchoolForm()
        return render(request, 'principal/cadastra_escola.html', {'form': form, 'title': 'Cadastra Sede Fase Nacional', 'school_is_known':False})

def cadastra_escola_recuperada(request):
    if request.method == 'POST':
        form = RegisterSchoolForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            ok,msg,new_school = exec_cadastra_escola(f)
            if ok:
                template = loader.get_template('principal/cadastra_escola_resp.html')
                context = {'school':f}
                return HttpResponse(template.render(context, request))
            else:
                template = loader.get_template('principal/cadastra_escola_erro.html')
                context = {'school':f, 'erro': msg}
                return HttpResponse(template.render(context, request))
    else:
        try:
            form = RegisterSchoolForm(initial=request.session['form_data'])
            request.session['form_data'] = None
            is_known = True
        except:
            form = RegisterSchoolForm()
    return render(request, 'principal/cadastra_escola.html', {'form': form,'school_is_known':True})

def cadastra_escola_resp(request):
    template = loader.get_template('principal/cadastra_escola_resp.html')
    context = {}
    return HttpResponse(template.render(context, request))

def consultas(request):
    #logger.debug("this is a debug message!")
    return render(request, 'principal/consultas.html', {})
    # template = loader.get_template('principal/consultas.html')
    # context = {}
    # return HttpResponse(template.render(context, request))

def consultas_resp(request):
    template = loader.get_template('principal/consultas.html')
    context = {}
    return HttpResponse(template.render(context, request))

def contato(request):
    return render(request, 'principal/contatos.html', {})

def consulta_participantes(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ConsultaParticipantesForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            f = form.cleaned_data
            # set session data
            request.session['partic_year']=f['partic_year']
            request.session['competition']=f['competition']
            request.session['partic_type']=f['partic_type']
            request.session['partic_name']=f['partic_name']
            request.session['partic_year']=f['partic_year']
            request.session['compet_level']=f['compet_level']
            request.session['school_name']=f['school_name']
            request.session['school_city']=f['school_city']
            request.session['school_state']=f['school_state']
            request.session['list_order']=f['list_order']
            return HttpResponseRedirect('consulta_participantes_resp')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ConsultaParticipantesForm()
    return render(request, 'principal/consulta_participantes.html', {'form': form})

def consulta_participantes_resp(request):
    f = {}
    f['partic_year'] = request.session['partic_year']
    f['competition'] = request.session['competition']
    f['partic_name'] = request.session['partic_name']
    f['partic_type'] = request.session['partic_type']
    f['partic_year'] = request.session['partic_year']
    f['compet_level'] = request.session['compet_level']
    f['school_name'] = request.session['school_name']
    f['school_city'] = request.session['school_city']
    f['school_state'] = request.session['school_state']
    f['list_order'] = request.session['list_order']

    if f['partic_type']=='compet' and f['competition'].upper() == 'OBI':
        f['compet_name'] = f['partic_name']
        partic = search_compets(f)
        # used in certificates, search only if compet_points_fase1 >= 0
        partic = partic.filter(compet_points_fase1__gte=0)
        partic = partic.exclude(compet_name__icontains='teste') | partic.filter(compet_name='Rafael Xavier Teste')
    elif f['partic_type']=='compet' and f['competition'].upper() == 'CF':
        f['compet_name'] = f['partic_name']
        partic = search_compets_cf(f)
        # used in certificates, search only if compet_points >= 0
        partic = partic.filter(compet_points__gte=0)
        partic = partic.exclude(compet__compet_name__icontains='teste')
    elif f['partic_type']=='colab':
        f['colab_name'] = f['partic_name']
        partic = search_colabs(f)
    else:
        f['deleg_name'] = f['partic_name']
        partic = search_school_delegs(f)

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(partic), page)
    paginator = Paginator(partic, page_size)
    try:
        partics = paginator.page(page)
    except PageNotAnInteger:
        partics = paginator.page(1)
    except EmptyPage:
        partics = paginator.page(paginator.num_pages)

    return render(request, 'principal/consulta_participantes_resp.html', { 'competition': f['competition'], 'partic_year':f['partic_year'], 'partic_type':f['partic_type'],'items': partics })

# def corrige_iniciacao(request,year,phase,level,code,show_answers=False):
#     correct_answers = 0
#     if request.method == 'POST':
#         try:
#             descriptor = request.POST['descriptor']
#         except:
#             raise
#         try:
#             task = Task.objects.get(descriptor=descriptor)
#         except:
#             raise
#         questions = Question.objects.filter(task=task)
#         total_questions = len(questions)
#         if not questions:
#             raise
#         for q in questions:
#             if str(q.num) in request.POST.keys():
#                 try:
#                     answer = Alternative.objects.filter(question=q).get(num=request.POST[str(q.num)],correct=True)
#                     correct_answers += 1
#                 except:
#                     pass
#         # find level/modality from descriptor
#         tmp = re.match('[0-9]{4}f(?P<phase>[123s])(?P<mod>[ip])(?P<level>[j12us])_',descriptor)
#         tmp_mod = tmp.group('mod')
#         tmp_level = tmp.group('level')
#         context={'correct_answers':correct_answers,'total_questions':total_questions,'task':task}
#         return render(request,'tasks/tarefa_iniciacao_resp.html', context)
#     else:
#         return render(request,'500.html', {})

# def redefine_senha(request):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = RedefineSenhaForm(request.POST)
#         # check whether it's valid:
#         if form.is_valid():
#             subject = obi_year() + ' - Cadastro em processamento'
#             MESSAGE_REGISTERED = """
# Caro(a) Prof(a). {contact_name},

# obrigado por cadastrar a escola

#       {school_name}

# na Olimpíada Brasileira de Informática.

# Se o(a) Sr(a). não preencheu o cadastro da OBI, solicitamos que entre em contato o mais breve possivel com a Coordenação da OBI, respondendo a esta mensagem, para garantir que não haja acesso indevido ao sistema da OBI.

# As informações fornecidas para cadastro serão verificaas com a escola, o que pode demorar um ou dois dias. Assim que o cadastro for confirmado enviaremos uma outra mensagem, informando a senha para acesso ao sistema da OBI.

# Atenciosamente,


# Coordenação da OBI2025
# olimpinf@ic.unicamp.br
# WhatsApp e Telegram: (19) 3199-7399
# """
#             f = form.cleaned_data
#             send_mail(
#                 subject,
#                 MESSAGE_REGISTERED.format(contact_name=f['school_deleg_name'],
#                                           school_name=f['school_name']
#                                           ),
#                 f['school_deleg_email']
#             )
#             return render(request, 'senha_enviada.html', {})

#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = RedefineSenhaForm()
#     return render(request, 'redefine_senha.html', {'form': form})

def search_compets(f):
    
    compets = Compet.objects.using("obi" + f['partic_year']).select_related('compet_school')
    compets = compets.only('compet_name', 'compet_type', 'compet_school__school_name', 'compet_school__school_city', 'compet_school__school_state')
    if f['compet_name']:
        tks = f['compet_name'].split()
        for tk in tks:
            compets = compets.filter(compet_name__icontains = tk)
    if f['compet_level']:
        compets = compets.filter(compet_type = f['compet_level'])
    if f['school_state']:
        compets = compets.filter(compet_school__school_state = f['school_state'])
    if f['school_name']:
        tks = f['school_name'].split()
        for tk in tks:
            compets = compets.filter(compet_school__school_name__icontains = tk)
    if f['school_city']:
        tks = f['school_city'].split()
        for tk in tks:
            compets = compets.filter(compet_school__school_city__icontains = tk)
    if f['list_order'] == 'compet_name':
        compets = compets.order_by('compet_name')
    elif f['list_order'] == 'compet_type':
        compets = compets.order_by('compet_type','compet_name')
    elif f['list_order'] == 'school_name':
        compets = compets.order_by('compet_school__school_name','compet_name')
    elif f['list_order'] == 'school_city':
        compets = compets.order_by('compet_school__school_city','compet_school__school_state','compet_school__school_name','compet_name')
    elif f['list_order'] == 'school_state':
        compets = compets.order_by('compet_school__school_state','compet_school__school_city','compet_school__school_name','compet_name')
    else: # order by compet_name
        compets = compets.order_by('compet_name')
    return compets

def search_compets_cf(f):
    compets = CompetCfObi.objects.using('obi' + f['partic_year']).filter(compet_points__gte=0).select_related('compet__compet_school')
    compets = compets.only('compet__compet_name', 'compet_type', 'compet__compet_school__school_name', 'compet__compet_school__school_city', 'compet__compet_school__school_state')
    if f['compet_name']:
        tks = f['compet_name'].split()
        for tk in tks:
            compets = compets.filter(compet__compet_name__icontains = tk)
    if f['compet_level']:
        compets = compets.filter(compet_type = f['compet_level'])
    if f['school_state']:
        compets = compets.filter(compet__compet_school__school_state = f['school_state'])
    if f['school_name']:
        tks = f['school_name'].split()
        for tk in tks:
            compets = compets.filter(compet__compet_school__school_name__icontains = tk)
    if f['school_city']:
        tks = f['school_city'].split()
        for tk in tks:
            compets = compets.filter(compet__compet_school__school_city__icontains = tk)
    if f['list_order'] == 'compet__compet_name':
        compets = compets.order_by('compet__compet_name')
    elif f['list_order'] == 'compet_type':
        compets = compets.order_by('compet_type','compet__compet_name')
    elif f['list_order'] == 'school_name':
        compets = compets.order_by('compet__compet_school__school_name','compet__compet_name')
    elif f['list_order'] == 'school_city':
        compets = compets.order_by('compet__compet_school__school_city','compet__compet_school__school_state','compet__compet_school__school_name','compet__compet_name')
    elif f['list_order'] == 'school_state':
        compets = compets.order_by('compet__compet_school__school_state','compet__compet_school__school_city','compet__compet_school__school_name','compet__compet_name')
    else: # order by compet_name
        compets = compets.order_by('compet__compet_name')
    return compets

def search_colabs(f):
    year = int(f['partic_year'][3:])
    colabs = Colab.objects.using('obi'+f['partic_year']).filter(colab_school__school_ok=True).select_related('colab_school')
    if f['partic_name']:
        tks = f['partic_name'].split()
        for tk in tks:
            colabs = colabs.filter(colab_name__icontains = tk)
    if f['school_state']:
        colabs = colabs.filter(colab_school__school_state = f['school_state'])
    if f['school_name']:
        tks = f['school_name'].split()
        for tk in tks:
            colabs = colabs.filter(colab_school__school_name__icontains = tk)
    if f['school_city']:
        tks = f['school_city'].split()
        for tk in tks:
            colabs = colabs.filter(colab_school__school_city__icontains = tk)
    if f['list_order'] == 'partic_name':
        colabs = colabs.order_by('colab_name')
    elif f['list_order'] == 'school_name':
        colabs = colabs.order_by('colab_school__school_name','colab_name')
    elif f['list_order'] == 'school_city':
        colabs = colabs.order_by('colab_school__school_city','colab_school__school_state','colab_school__school_name','colab_name')
    else: # order by school_state
        colabs = colabs.order_by('colab_school__school_state','colab_school__school_city','colab_school__school_name','colab_name')
    return colabs

def search_school_delegs(f):
    # upto 2017 school included deleg
    year = int(f['partic_year'][3:])
    delegs = School.objects.using('obi'+f['partic_year']).filter(school_ok=True)
    if f['partic_name']:
        tks = f['partic_name'].split()
        for tk in tks:
            delegs = delegs.filter(school_deleg_name__icontains = tk)
    if f['school_state']:
        delegs = delegs.filter(school_state = f['school_state'])
    if f['school_name']:
        tks = f['school_name'].split()
        for tk in tks:
            delegs = delegs.filter(school_name__icontains = tk)
    if f['school_city']:
        tks = f['school_city'].split()
        for tk in tks:
            delegs = delegs.filter(school_city__icontains = tk)
    if f['list_order'] == 'partic_name':
        delegs = delegs.order_by('school_deleg_name')
    elif f['list_order'] == 'school_name':
        delegs = delegs.order_by('school_name','school_deleg_name')
    elif f['list_order'] == 'school_city':
        delegs = delegs.order_by('school_city','school_state','school_name','school_deleg_name')
    else: # order by school_state
        delegs = delegs.order_by('school_state','school_city','school_name','school_deleg_name')
    return delegs

def consulta_competidores(request):
    pagetitle='Consulta Competidores'
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
            return HttpResponseRedirect('consulta_competidores_resp')
    else:
        form = ConsultaCompetidoresForm()
    return render(request, 'principal/consulta_competidores.html', {'form': form, 'pagetitle':pagetitle})

def consulta_competidores_resp(request):
    pagetitle='Consulta Competidores'
    urlconsult='principal:consulta_competidores'
    urlresp='principal:consulta_competidores_resp'
    f = {}
    f['compet_name'] = request.session['compet_name']
    f['compet_level'] = request.session['compet_level']
    f['school_name'] = request.session['school_name']
    f['school_city'] = request.session['school_city']
    f['school_state'] = request.session['school_state']
    f['list_order'] = request.session['list_order']
    f['partic_year'] = str(YEAR)
    pagetitle = request.session['pagetitle']
    compets = search_compets(f)
    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    paginator = Paginator(compets, page_size, allow_empty_first_page=True)
    try:
        compets = paginator.page(page)
    except PageNotAnInteger:
        compets = paginator.page(1)
    except EmptyPage:
        compets = paginator.page(paginator.num_pages)
    return render(request, 'principal/consulta_competidores_resp.html', { 'items': compets, 'pagetitle': pagetitle, 'urlconsult':urlconsult, 'urlresp':urlresp })

def search_schools(f):
    schools = School.objects.filter(school_ok=True)
    if f['school_state']:
        schools = schools.filter(school_state = f['school_state'])
    if f['school_name']:
        tks = f['school_name'].split()
        for tk in tks:
            schools = schools.filter(school_name__icontains = tk)
    if f['school_city']:
        tks = f['school_city'].split()
        for tk in tks:
            schools = schools.filter(school_city__icontains = tk)
    if f['school_order'] == 'school_name':
        schools = schools.order_by('school_name','school_state','school_city')
    elif f['school_order'] == 'school_city':
        schools = schools.order_by('school_city','school_state','school_name')
    else: # order by school_state
        schools = schools.order_by('school_state','school_city','school_name')
    return schools

def consulta_escolas(request):
    if request.method == 'POST':
        form = ConsultaEscolasForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            schools = search_schools(f)
            # set session data
            request.session['school_name']=f['school_name']
            request.session['school_city']=f['school_city']
            request.session['school_state']=f['school_state']
            request.session['school_order']=f['school_order']
            return HttpResponseRedirect('consulta_escolas_resp')
    else:
        form = ConsultaEscolasForm()
    return render(request, 'principal/consulta_escolas.html', {'form': form})

def consulta_escolas_resp(request):
    f = {}
    f['school_name'] = request.session['school_name']
    f['school_city'] = request.session['school_city']
    f['school_state'] = request.session['school_state']
    f['school_order'] = request.session['school_order']
    schools = search_schools(f)
    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(schools), page)
    paginator = Paginator(schools, page_size)
    try:
        schools = paginator.page(page)
    except PageNotAnInteger:
        schools = paginator.page(1)
    except EmptyPage:
        schools = paginator.page(paginator.num_pages)
    return render(request, 'principal/consulta_escolas_resp.html', { 'items': schools })

def profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('/')
    elif user.is_authenticated and user.groups.filter(name__in=['local_coord', 'colab', 'colab_full']).exists():
        return redirect('/restrito/')
    else:
        return redirect('/compet/')


def index(request):
    # to test error page
    # raise PermissionDenied
    #raise 'boom'  # will cause system error
    return render(request,'principal/index.html',{})

def datas(request):
    template = loader.get_template('principal/datas.html')
    context = {}
    return HttpResponse(template.render(context, request))

def emite_carta_professor(request,year,id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carta.pdf"'
    file_data = get_letter_teacher(name,id)
    response.write(file_data)
    return response

def emite_carta(request,year,id):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carta.pdf"'
    file_data = get_letter_compet(id,year)
    response.write(file_data)
    return response
    
def emite_certificado(request,year,competition,type,id):
    #if year == 2025:
    #    return erro(request,'Não há certificado para o participante selecionado.')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
    if not year or year=='':
        year = YEAR
    if type=='compet' and competition.upper() == 'OBI':
        file_data = get_certif_compet(id,year)
    elif type=='compet' and competition.upper() == 'CF':
        file_data = get_certif_compet_cf(id,year)
    elif type=='colab':
        file_data = get_certif_colab(id,year)
    elif type=='deleg':
        file_data = get_certif_deleg(id,year)
    if file_data == None:
        return erro(request,'Não há certificado para o participante selecionado.')
    response.write(file_data)
    return response

def verifica_certificado(request,hash):
    year = hash[:4]
    dbname= f'obi{year}'
    show_classif = False
    num_compets = 0
    compet = None
    colab = None
    school = None
    is_cf = False
    #print('year',year)
    #print(hash[5:])
    
    try:
        certif = CertifHash.objects.using(dbname).get(hash=hash)
    except:
        data = {'pagetitle':'Verifica Certificado', 'msg': "O certificado consultado não é válido."}
        return render(request,'principal/pagina_com_mensagem.html', data)

    award = ''
    if certif.compet:
        compet = certif.compet
        if compet.compet_medal:
            if compet.compet_medal == 'o':
                award = 'Medalha de Ouro'
            elif compet.compet_medal == 'p':
                award = 'Medalha de Prata'
            elif compet.compet_medal == 'b':
                award = 'Medalha de Bronze'
            elif compet.compet_medal == 'h':
                award = 'Honra ao Mérito'
        num_compets = Compet.objects.using(dbname).filter(compet_type=compet.compet_type,compet_points_fase1__gte=0).count()
        #num_compets = Compet.objects.using(dbname).filter(compet_type=compet.compet_type).count()
        show_classif = num_compets/compet.compet_rank_final > 4
    elif certif.compet_cf:
        compet = certif.compet_cf
        if compet.compet_medal:
            if compet.compet_medal == 'o':
                award = 'Medalha de Ouro'
            elif compet.compet_medal == 'p':
                award = 'Medalha de Prata'
            elif compet.compet_medal == 'b':
                award = 'Medalha de Bronze'
            elif compet.compet_medal == 'h':
                award = 'Honra ao Mérito'
        num_compets = CompetCfObi.objects.using(dbname).filter(compet_type=compet.compet_type,compet_points__gte=0).count()
        show_classif = num_compets/compet.compet_rank > 4
        is_cf = True
    elif certif.colab:
        pass
    elif certif.school:
        pass
    return render(request, 'principal/verifica_certificado.html', {'year': year, 'compet': compet, 'colab': certif.colab, 'school': certif.school, 'show_classif': show_classif, 'num_compets': num_compets, 'is_cf': is_cf, 'award': award})

def news(request):
    template = loader.get_template('principal/news.html')
    context = {}
    return HttpResponse(template.render(context, request))

def code(request):
    template = loader.get_template('principal/code.html')
    context = {}
    return HttpResponse(template.render(context, request))

def community(request):
    template = loader.get_template('principal/community.html')
    context = {}
    return HttpResponse(template.render(context, request))

def donate(request):
    template = loader.get_template('principal/donate.html')
    context = {}
    return HttpResponse(template.render(context, request))

def documentation(request):
    template = loader.get_template('principal/documentation.html')
    context = {}
    return HttpResponse(template.render(context, request))

def mostra_escola(request,id):
    template = loader.get_template('principal/mostra_escola.html')
    school = School.objects.get(school_id=id)
    context = {'school':school}
    return HttpResponse(template.render(context, request))

def mostra_sede_fase3(request,id):
    template = loader.get_template('principal/mostra_sede_.html')
    school = School.objects.get(school_id=id)
    context = {'school':school}
    return HttpResponse(template.render(context, request))


def reenvia_conf_cadastro(request,hash):
    try:
        q = School.objects.get(school_hash=hash,school_ok=True)
    except:
        msg = 'Erro no link. Por favor entre em contato com a Coordenação.'
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Reenvia Confirmação de Cadastro'})
    u = User.objects.get(username=q.school_deleg_username)

    password = make_password()
    u.set_password(password)
    u.save()

    subject = obi_year() + ' - Cadastro finalizado'
#    message_authorized = \"\"\"
#Caro(a) Prof(a). {contact_name},
#
#mais uma vez, obrigado por cadastrar a escola
#
#      {school_name}
#
#na Olimpíada Brasileira de Informática.
#
#O processo de cadastramento da escola foi finalizado e o acesso ao sistema de inscrição de competidores está habilitado. A inscrição de competidores deve ser feita na página da OBI:
#
#https://olimpiada.ic.unicamp.br
#
#seguindo o link "Acesso Escolas" no alto da página inicial, usando o nome de usuário e a senha a seguir:
#
#nome de usuário: {username}
#senha: {password}
#
#---
#Coordenação da OBI2025
#Email: olimpinf@ic.unicamp.br
#WhatsApp e Telegram: (19) 3199-7399
#
#Organização:  Instituto de  Computação -  UNICAMP
#Promoção:  Sociedade Brasileira de Computação
#\"\"\"

# Mensagem inscricao CF-OBI
    message_authorized = """
Caro(a) Prof(a). {contact_name},

mais uma vez, obrigado por cadastrar a escola

      {school_name}

na Olimpíada Brasileira de Informática.

O processo de cadastramento da escola foi finalizado e o acesso ao sistema de inscrição de competidores está habilitado.

Note que no momento estamos aceitando apenas a inscrição de *** alunas *** para participação na Competição Feminina da OBI. Outras inscrições não terão validade, dado que as provas das Fases 1 e 2 da OBI já aconteceram.

A inscrição das competidoras para a Competição Feminina da OBI deve ser feita na página da OBI:

https://olimpiada.ic.unicamp.br

seguindo o link "Acesso Escolas" no alto da página inicial, usando o nome de usuário e a senha a seguir:

nome de usuário: {username}
senha: {password}

---
Coordenação da OBI2025
Email: olimpinf@ic.unicamp.br
WhatsApp e Telegram: (19) 3199-7399

Organização:  Instituto de  Computação -  UNICAMP
Promoção:  Sociedade Brasileira de Computação
"""

    queue_email(
        subject,
        message_authorized.format(contact_name=q.school_deleg_name,
                                  school_name=q.school_name,
                                  username=q.school_deleg_username,
                                  password=password
        ),
        DEFAULT_FROM_EMAIL,
        q.school_deleg_email
    )
    
    # send email to new coordinator
    # send_mail(
    #     subject,
    #     message_authorized.format(contact_name=q.school_deleg_name,
    #                               school_name=q.school_name,
    #                               username=q.school_deleg_username,
    #                               password=password
    #                               ),
    #     DEFAULT_FROM_EMAIL,
    #     [q.school_deleg_email]
    # )
    # # send email to obi
    # send_mail(
    #     subject,
    #     message_authorized.format(contact_name=q.school_deleg_name,
    #                               school_name=q.school_name,
    #                               username=q.school_deleg_username,
    #                               password=password
    #                               ),
    #     DEFAULT_FROM_EMAIL,
    #     [DEFAULT_FROM_EMAIL]
    # )

    msg = f'<p>Uma mensagem com a senha para acesso foi enviada para o endereço de email cadastrado para o Coordenador Local.'
    'A mensagem pode demorar alguns minutos. '
    'Verifique sua lixeira eletrônica para ter certeza de que a mensagem não foi marcada erroneamente como lixo.'
    logger.info('reenvio cadastro, school {}  username={}'.format(q.school_name, q.school_deleg_username))
    return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Reenvia Confirmação de Cadastro'})


def recupera_cadastro_auto(request,hash):
    current_year = obi_year(as_int=True)
    try:
        s = School.objects.using('obi{}'.format(current_year-1)).get(school_hash=hash,school_ok=True)
        data = {'school_name':s.school_name}
        data['school_id'] = s.school_id
        data['school_type'] = s.school_type
        data['school_inep_code'] = s.school_inep_code
        data['school_phone'] = s.school_phone
        data['school_zip'] = s.school_zip
        data['school_address'] = s.school_address
        data['school_address_number'] = s.school_address_number
        data['school_address_district'] = s.school_address_district
        data['school_city'] = s.school_city
        data['school_state'] = s.school_state
        data['school_address_complement'] = s.school_address_complement
        data['school_deleg_name'] = s.school_deleg_name
        data['school_deleg_phone'] = s.school_deleg_phone
        data['school_deleg_username'] = s.school_deleg_username
        data['school_deleg_email'] = s.school_deleg_email
        data['school_deleg_email_conf'] = 'Confirme o email'
        data['school_code'] = s.school_code
        data['school_is_known'] = True
        data['school_prev'] = s.school_id
        data['school_ok'] = True
    except:
        msg = 'Erro no link. Por favor entre em contato com a Coordenação.'
        template = loader.get_template('principal/cadastra_escola_erro_recupera.html')
        context = {'school':{}, 'erro': msg}
        return HttpResponse(template.render(context, request))
    request.session['form_data']=data
    return redirect(to='principal:cadastra_escola_recuperada')

def recupera_cadastro(request):
    if request.method != 'POST':
        form = RecuperaCadastroForm()
        return render(request, 'principal/recupera_cadastro.html', {'form': form})

    # check password from last year
    form = RecuperaCadastroForm(request.POST)

    current_year = obi_year(as_int=True)
    msg = 'Combinação de usuário e senha não registrados na OBI{}. Por favor, verifique as informações ou cadastre uma nova escola na OBI{}.'.format(current_year-1, current_year)
    template = loader.get_template('principal/cadastra_escola_erro_recupera.html')
    context = {'school':{}, 'erro': msg}

    # check whether it's valid:
    if form.is_valid():
        f = form.cleaned_data
        try:
            s = School.objects.using('obi{}'.format(current_year-1)).get(school_deleg_username=f['old_username'])
        except:
            return HttpResponse(template.render(context, request))

        return cadastra_escola_auto_exec(request, s)

    return HttpResponse(template.render(context, request))

#################
# results
#
# def resultados(request):
#     return render(request, 'resultados.html', {})

# def resultados_f1ini(request):
#     return render(request, 'resultados_f1ini.html', {})

# def resultados_f1prog(request):
#    return render(request, 'resultados_f1prog.html', {})


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def grecaptcha_verify(request):
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
      
def consulta_res_fase1_ini(request):
    pagetitle = 'Consulta Pontuação Fase 1 - Iniciação'
    info_msg = 'Utilize este formulário para consultar a pontuação da Fase 1'
    if request.method == 'POST':
        form = ConsultaResFase1IniForm(request.POST)
        if form.is_valid():
            result = grecaptcha_verify(request) #is_recaptcha_valid(request)
            #print('result', result)
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(1,2,7))
                    result = {'compet': c}
                    return render(request, 'consulta_res_fase1_ini_resp.html', {'result': result})
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Iniciação.")
            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResFase1IniForm()
    return render(request, 'consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

      
def consulta_res_fase1_prog(request):
    pagetitle = 'Consulta Correção Fase 1 - Programação'
    info_msg = 'Utilize este formulário para consultar a correção da Fase 1'
    if request.method == 'POST':
        form = ConsultaResFase1IniForm(request.POST)
        if form.is_valid():
            result = grecaptcha_verify(request) #is_recaptcha_valid(request)
            #print('result', result)
            if result:
                f = form.cleaned_data
                try:
                    compet_id,check = verify_compet_id(f['compet_id'])
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                    res_log = ResFase1.objects.filter(compet_id=c.compet_id)
                    result = {'compet': c, 'log': res_log}
                    return render(request, 'consulta_res_fase1_prog_resp.html', {'result': result})
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")
            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResFase1IniForm()
    return render(request, 'consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

def consulta_subm_fase1_prog(request):
    pagetitle = 'Fase 1 - Programação, Consulta Submissões'
    info_msg = 'Utilize este formulário para consultar os arquivos de soluções submetidos e aceitos para correção.'
    msg = ''
    if request.method == 'POST':
        form = ConsultaResFase1IniForm(request.POST)
        if form.is_valid():
            result = grecaptcha_verify(request)
            #result = True
            if result:
                f = form.cleaned_data
                compet_id,check = verify_compet_id(f['compet_id'])
                try:
                    c = Compet.objects.get(pk=compet_id,compet_type__in=(3,4,5,6))
                    result = {'compet':c}
                    submissions = SubFase1.objects.filter(compet_id=compet_id).order_by('problem_name')
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
                    return render(request, 'consulta_subm_fase1_prog_resp.html', {'result': result})
                except:
                    messages.error(request, "Número de inscrição não corresponde a competidor da Modalidade Programação.")

            else:
                messages.error(request, "Captcha inválido.")
    else:
        form = ConsultaResFase1IniForm()
    return render(request, 'consulta_compet_id.html', {'form': form, 'pagetitle':pagetitle, 'info_msg':info_msg})

def consulta_classif_fase1(request):
    pagetitle = 'Fase 1 - Consulta Classificados'
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
            return HttpResponseRedirect('consulta_classif_fase1_resp')
    else:
        form = ConsultaCompetidoresForm()
    return render(request, 'principal/consulta_competidores.html', {'form': form, 'pagetitle':pagetitle})

def consulta_classif_fase1_resp(request):
    pagetitle = 'Fase 1 - Consulta Classificados'
    urlconsult = 'consulta_classif_fase1'
    urlresp='consulta_classif_fase1_resp'
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
    compets = compets.filter(compet_classif_fase1=True)
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
    descriptor = '{}f{}p{}_{}'.format(year,phase,level,code)
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
                    return render(request, 'tasks/corrige_programacao_erro.html', {})
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
            return render(request, 'tasks/corrige_programacao_resp.html', subm_ctx)

    # if a GET (or any other method) we'll create a blank form
    #else:
    #    form = SubmeteSolucaoPratiqueForm()

    return rendertask(request, descriptor, show_answers=False, mod='p')
    #return render(request, 'submete_solucao.html', {'form': form})

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
    return render(request, 'tasks/corrige_programacao_resultado.html', subm_ctx)

def corrige_programacao_resp(request):
    template = loader.get_template('tasks/corrige_programacao_resp.html')
    context = {'problem_name_full':'Problem name'}
    return HttpResponse(template.render(context, request))


def get_user_type(user):
    #print(f'in get_user_type user.id={user.id}, user.username={user.username}')

    user_type = user.groups.all().first().name
    #print('user_type', user_type)
    
    if user_type == 'local_coord':
        deleg = Deleg.objects.get(user_id=user.id)
        return 'coord', deleg.deleg_school.school_deleg_name, 'Caro(a) Prof(a).'

    if user_type == 'colab' or user_type == 'colab_full':
        colab = Colab.objects.get(user_id=user.id)
        return 'colab', colab.colab_name, 'Caro(a) Prof(a).'

    if user_type == 'compet':
        compet = Compet.objects.get(user_id=user.id)
        return 'compet', compet.compet_name, 'Caro(a)'

    return '', '', ''

def password_reset(request):
    return render(request, 'principal/password_reset.html', {'pagetitle':'Redefine Senha'})

def password_reset_compet(request):
    if request.method == 'POST':
        form = PasswordResetCompetForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            username = f['username'].strip()
            compet_id,check = verify_compet_id(username)
            if compet_id == 0:
                messages.error(request, "Entre com um número de inscrição válido.")
            else:
                try:
                    u = User.objects.get(username=username)
                    compet_id = u.compet.compet_id # just to cause exception if not compet
                    result,result_msg = password_reset_exec(request, username, 'compet')
                    return render(request, 'principal/pagina_com_mensagem.html', {'msg': result_msg, 'pagetitle':'Redefine Senha de Competidor'})
                except:
                    logger.info('password_reset failed, username does not exist username={}'.format(username))
                    messages.error(request, "Número de inscrição não corresponde a competidor inscrito.")
    else:
        form = PasswordResetCompetForm()
    return render(request, 'principal/password_reset_compet.html', {'form': form, 'pagetitle':'Redefine Senha de Competidor'})

def password_reset_coord(request):
    if request.method == 'POST':
        form = PasswordResetCoordForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            username = f['username'].strip() # can be username or email, password_reset_exec will try both
            if True:
                result,result_msg = password_reset_exec(request, username, 'coord')
                logger.info('password_reset succeeded, username={}'.format(username))
                #print('password_reset succeeded, username={}'.format(username))
                return render(request, 'principal/pagina_com_mensagem.html', {'msg': result_msg, 'pagetitle':'Redefine Senha de Coordenador ou Colaborador'})
            else:
                logger.info('password_reset failed, username does not exist username={}'.format(username))
                messages.error(request, "Usuário ou email não cadastrado na {}.".format(obi_year()))
    else:
        form = PasswordResetCoordForm()
    return render(request, 'principal/password_reset_coord.html', {'form': form, 'pagetitle':'Redefine Senha de Coordenador ou Colaborador'})


def password_reset_other(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            username = f['username'].strip()
            try:
                result,result_msg = password_reset_exec(request, username, 'other')
                return render(request, 'principal/pagina_com_mensagem.html', {'msg': result_msg, 'pagetitle':'Redefine Senha'})
            except:
                logger.info('password_reset failed, username does not exist username={}'.format(username))
                messages.error(request, "Usuário ou email não cadastrado.")
    else:
        form = PasswordResetForm()
    return render(request, 'principal/password_reset_other.html', {'form': form, 'pagetitle':'Redefine Senha'})

def password_reset_exec(request, username, user_type):
    class AUser:
        pass

    result_msg = '''Uma mensagem com instruções para redefinição da sua senha foi enviada para o endereço 
    de email cadastrado. <p>A mensagem pode demorar alguns minutos. Verifique sua lixeira eletrônica
    para ter certeza de que a mensagem não foi marcada erroneamente como lixo.'''
    result_fail_msg = '''Não foi possível indentificar um usuário cadastrado com os dados informados.'''

    # can be a username or an email
    hash = secrets.token_urlsafe(32)
    try:
        # try first username
        logger.info(f'password_reset_exec try username={username}')
        user = User.objects.get(username=username)
    except:
        email = username
        logger.info(f'password_reset_exec try email={email}')
        users = User.objects.filter(email=email)
        logger.info(f'password_reset_exec users={users}')
        if len(users) == 0:
            # do nothing, wrong email
            logger.info('password_reset non existent username or email = {}'.format(username))
            return False, result_fail_msg
        elif len(users) == 1:
            user = users[0]
        elif user_type=='coord':
            # special case
            logger.info('password_reset repeating coord email = {}'.format(email))
            # user manages more than one school, or used his email for students, send usernames coord
            # deal only with coordinators
            user_schools=[]
            the_user = users[0] # may be not the correct user, see below
            for u in users:
                try:
                    auser = AUser()
                    auser.username = u.username
                    auser.first_name = u.first_name
                    auser.last_name = u.last_name
                    auser.school = u.deleg.deleg_school.school_name
                    hash = secrets.token_urlsafe(32)
                    pwd_req = PasswordRequest(user_id=u.id, request_hash=hash)
                    pwd_req.save()
                    auser.hash = hash
                    user_schools.append(auser)
                    the_user = auser
                except:
                    # email of coord is also used for another role?
                    pass

            template = loader.get_template('principal/mensagem_password_reset_coord_multiple_hash.html')
            subject = 'Redefinição de senha'
            body = template.render({'user_schools':user_schools, 'user': the_user},request)
            from_addr = settings.DEFAULT_FROM_EMAIL
            to_addr = (email,)
            queue_email(
                subject,
                body,
                DEFAULT_FROM_EMAIL,
                email
            )

            logger.info('password_reset send hash multiple schools successfull for email={}'.format(email))
            return True, result_msg
        else:
            logger.info('password_reset fail, repeating email, but not coord = {}'.format(username))
            return False, result_fail_msg

    # send link for new password
    hash = secrets.token_urlsafe(32)
    pwd_req = PasswordRequest(user_id=user.id, request_hash=hash)
    pwd_req.save()
    user_type, full_name, greeting = get_user_type(user)
    template = loader.get_template('principal/mensagem_password_reset_hash.html')
    subject = 'Redefinição de senha'
    body = template.render({'hash': hash, 'greeting': greeting, 'full_name': full_name}, request)
    from_addr = settings.DEFAULT_FROM_EMAIL
    to_addr = (user.email,)

    #msg = EmailMessage(subject, body, from_addr, to_addr, reply_to=[DEFAULT_REPLY_TO_EMAIL])
    #msg.send()

    queue_email(
        subject,
        body,
        DEFAULT_FROM_EMAIL,
        user.email
    )
    logger.info(f'password_reset_exec send to_addr={to_addr}')
    
    #msg = EmailMessage(subject, body, from_addr, ('olimpinf@ic.unicamp.br',), reply_to=[DEFAULT_REPLY_TO_EMAIL])
    #msg.send()
    logger.info(f'password_reset send hash successfull for email={user.email}, username={user.username}')
    
    return True,result_msg

def redefine_senha(request,hash):
    logger.info(f'redefine_senha, hash: {hash}')
    logger.info(f'redefine_senha, path: {request.path}')
    # logger.info(f'redefine_senha, path_info: {request.path_info}')
    # logger.info(f'redefine_senha, method: {request.method}')
    # logger.info(f'redefine_senha, GET: {request.GET}')
    # logger.info(f'redefine_senha, POST: {request.POST}')
    # logger.info(f'redefine_senha, META: {request.META}')

    EXPIRE_MINUTES = 30
    #print("hash", hash)
    try:
        pwd_req = PasswordRequest.objects.get(request_hash=hash)
        #print("pwd_req",pwd_req)
    except:
        msg = '<p><b>Erro:</b>solicitação inválida.</p>'
        logger.info(f'redefine_senha failed, wrong hash: {hash}')
        #print(f'password apply failed, wrong hash: {hash}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Redefine Senha'})

    first = pwd_req.first
    if first:
        pwd_req.first = False
        pwd_req.save()
        logger.info(f'redefine_senha first,  hash: {hash}')
        #return HttpResponse(status=444)
    else:
        logger.info(f'redefine_senha second,  hash: {hash}')


    if timezone.now() > pwd_req.request_time + timedelta(seconds=60*EXPIRE_MINUTES):
        logger.info(f'password apply failed, expired hash: {hash}')
        msg = '<p><b>Erro:</b> solicitação de redefinição de senha expirada.</p>'
        print("render expirada",file=sys.stderr)
        #return redirect(to='principal:erro',msg=msg)
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Redefine Senha'})

    # if used:
    #     msg = '<p><b>Erro:</b> solicitação inválida (já utilizada).</p>'
    #     logger.info(f'password apply failed, already used hash: {hash}')
    #     #print("render já utilizada", file=sys.stderr)
    #     #return redirect(to='principal:erro',msg=msg)
    #     return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Redefine Senha'})


    logger.info(f'generate new password')
    u = User.objects.get(id=pwd_req.user_id)
    password = make_password()
    u.set_password(password)
    u.save()
    # store only contestants passwords
    try:
        c = u.compet
        pw = Password(user_id=u.id,password=password)
        pw.save()
        c.compet_conf = password
        c.save()
        logger.info(f'redefine_senha, competidor')
        # update password in CMS db
        # if c.compet_type in (PJ, P1, P2, PS):
        #     try:
        #         p = PasswordCms.objects.get(compet=compet)
        #     except:
        #         p = PasswordCms()
        #         p.password = make_password(separator='.')
        #         p.compet = c
        #         p.save()

        #     logger.info(f'redefine_senha, atualiza senha cms')
        #     cms_update_password(u.username, c.compet_type, p.password)
    except:
        logger.info(f'redefine_senha, não é competidor')
        #print('not a compet?')
        pass

    template = loader.get_template('principal/password_reset_msg.html')
    subject = 'Redefinição de senha'
    body = template.render({'new_password':password, 'user': u},request)
    from_addr = settings.DEFAULT_FROM_EMAIL
    to_addr = (u.email,)

    queue_email(
        subject,
        body,
        DEFAULT_FROM_EMAIL,
        u.email
    )

    pwd_req.used = True
    pwd_req.save()

    msg = '<p>Uma mensagem com a nova senha foi enviada para o endereço de email cadastrado.</p>'
    logger.info(f'redefine_senha, redirecionando para sucesso')
    return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Redefine Senha'})


def consulta_cidades_fase3(request):
    compets = Compet.objects.filter(
        compet_classif_fase2=True
    ).select_related("compet_school")

    DISREGARD_CITIES = [] # ['Campina Grande']
    city_counts = {}
    for c in compets:
        school = c.compet_school
        if school.school_city in DISREGARD_CITIES:
            continue
        key = (school.school_city, school.school_state)
        city_counts.setdefault(key, {"ini": 0, "prog": 0, "has_unassigned": False})

        # Count competitors
        if c.compet_type in (1, 2, 7):
            city_counts[key]["ini"] += 1
        else:
            city_counts[key]["prog"] += 1

        # Check if this school has no site assigned
        if (school.school_site_phase3_ini == 0 and
            school.school_site_phase3_prog == 0):
            city_counts[key]["has_unassigned"] = True

    sorted_city_counts = sorted(
        city_counts.items(), key=lambda x: (x[0][1], x[0][0])
    )

    # Build a set of (city, state) that have *any* site assigned
    DISREGARD = 'Campina Grande'
    site_assigned_cities = set(
        School.objects.filter(
            Q(school_site_phase3_ini__gte=1) | Q(school_site_phase3_prog__gte=1)
        ).values_list("school_city", "school_state")
    )

    # ---- Future refinement (per-modality check) ----
    # site_cities_ini = set(
    #     School.objects.filter(school_site_phase3_ini__isnull=False)
    #     .values_list("school_city", "school_state")
    # )
    # site_cities_prog = set(
    #     School.objects.filter(school_site_phase3_prog__isnull=False)
    #     .values_list("school_city", "school_state")
    # )
    #
    # Then in the template, you can check separately:
    # - (city.0, city.1) in site_cities_ini
    # - (city.0, city.1) in site_cities_prog

    
    return render(request, "principal/consulta_cidades_fase3.html", {
        "city_counts": sorted_city_counts, "site_assigned_cities": site_assigned_cities
    })


def info_exam(request):
    return render(request, "principal/info_exam.html", {})
    
