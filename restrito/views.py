import os
import csv
import logging
from urllib.parse import urlparse

from tempfile import TemporaryDirectory

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.db.models import F
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import FileResponse, HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, User, UserManager

from reportlab.graphics import shapes

from obi import settings
from principal.models import (Compet, CompetExtra, CompetAutoRegister, School, SchoolPhase3, Deleg, Password, QueuedMail, SchoolExtra,
                              Colab, PasswordCms, REGULAR_PUBLIC, REGULAR_PRIVATE,
                              SEX_CHOICES_CFOBI, LEVEL_CHOICES_FILTER_CFOBI, LEVEL_CHOICES_FILTER_INI,
                              LEVEL_NAME_FULL, LEVEL, LEVEL_NAME, LEVEL_ALL, LEVEL_INI, LEVEL_PROG, LEVEL_CFOBI,
                              IJ, I1, I2, PJ, P1, P2, PS, CF,
                              LastAccess, CompetDesclassif)

from principal.models import (CompetCfObi)

from .forms import (CompetInscreveForm, CompetFemininaInscreveForm, CompetInscreveLoteForm,
                    CompetEditaForm, CompetFemininaEditaForm,
                    CompetFiltroForm, CompetFemininaFiltroForm, CompetPreRegFiltroForm,
                    CompetSenhasFiltroForm, CompetFemininaSenhasFiltroForm, CompetSenhasCmsFiltroForm,
                    EscolaEditaForm, EscolaEditaInepForm, CoordEditaForm,
                    ColabInscreveForm, ColabEditaForm,
                    CompetValidaForm, CompetAutorizaProvaOnlineForm)

from week.forms import ParticSemanaFiltroForm

from cms.utils import (cms_add_user, cms_remove_user, DEFAULT_CONTEST_ID)
from principal.utils.check_compet_batch import check_compet_batch, check_compet_batch_password, check_compet_batch_update_password
from principal.utils.check_compet_feminina_batch import check_compet_feminina_batch, check_compet_feminina_batch_password, check_compet_feminina_batch_update_password
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,
                                   write_school_uploaded_file,
                                   calculate_page_size)
from principal.utils.get_certif import (get_certif_school_compets, get_certif_school_compets_cf, get_certif_school_colabs, get_certif_deleg)

from obi.settings import DEFAULT_FROM_EMAIL, YEAR
from exams.models import ExamFase2, ExamFase1, TesteFase1, ExamCfObi
from exams.views import check_exam_status
from exams.settings import EXAMS, DEFAULT_CONTEST_ID, DEFAULT_CONTEST_ID_CFOBI
from week.models import STATUS, Week

logger = logging.getLogger(__name__)


def in_coord_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='local_coord').exists()


def in_coord_colab_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name__in=['local_coord', 'colab', 'colab_full']).exists()


def in_coord_colab_full_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name__in=['local_coord', 'colab_full']).exists()


def in_compet_coord_colab_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name__in=['local_coord', 'colab', 'colab_full','compet']).exists()


def in_sbc_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='sbc').exists()


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def password_reset(request):
    return render(request, 'restrito/index.html', {})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def index(request):
    # check if there are compets to validate
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    school = School.objects.get(pk=school_id)

    try:
        last_access = LastAccess.objects.get(user=request.user)
    except:
        last_access = LastAccess(user=request.user)
    last_access.save()
    
    num_pre_compets = CompetAutoRegister.objects.filter(compet_school_id=school_id, compet_status='new').count()
    num_compets = Compet.objects.filter(compet_school_id=school_id).exclude(compet_type=CF).count()
    num_compets_feminina = Compet.objects.filter(compet_school_id=school_id, competcfobi__isnull=False).count()
    num_colabs = Colab.objects.filter(colab_school_id=school_id).count()

    num_compets_ini = Compet.objects.filter(compet_school_id=school_id,compet_type__in=(1,2,7)).count()
    num_compets_prog = Compet.objects.filter(compet_school_id=school_id,compet_type__in=(3,4,5,6)).count()
    
    has_week = Week.objects.filter(school_id=school_id).exclude(status=STATUS['no_reply']).exists()
    week_receipts = []
    if has_week:
        participants = Week.objects.filter(school_id=school_id)
        for partic in participants:
            if partic.payment and partic.payment not in week_receipts:
                week_receipts.append(partic.payment)

    has_desclassif =  CompetDesclassif.objects.filter(compet_school_id=school_id).exists()

    return render(request, 'restrito/index.html',
                 {'school': school, 'num_colabs': num_colabs,
                  'num_pre_compets': num_pre_compets, 'num_compets': num_compets, 'num_compets_feminina': num_compets_feminina,
                  'user': request.user, 'has_week': has_week, 'week_receipts': week_receipts, 'current_year': YEAR, 'has_desclassif': has_desclassif, 'num_compets_ini': num_compets_ini, 'num_compets_prog': num_compets_prog})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def aviso(request, msg):
    data = {'pagetitle':'Aviso', 'msg':msg}
    return render(request,'restrito/aviso.html', data)


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def erro(request, msg):
    data = {'pagetitle':'Erro', 'msg':msg}
    return render(request,'restrito/aviso.html', data)


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_desclassif(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    pagetitle = 'Competidores desclassificados'
    compets = CompetDesclassif.objects.filter(compet_school_id=school.school_id)
    total = len(compets)
    if request.method == 'POST':
        form = CompetFiltroForm(request.POST)
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
        form = CompetFiltroForm(initial=instance)

    if compet_list_type:
        try:
            compet_list_type = int(compet_list_type)
            if compet_list_type in (PJ,P1,P2,PS):
                compets = compets.filter(compet_type=compet_list_type)
            elif compet_list_type in (IJ,I1,I2):
                compets = compets.filter(compet_type=compet_list_type)
            else:
                compet_list_type = None
        except:
            compet_list_type = None
        request.session['compet_list_type'] = compet_list_type
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    if compet_list_order == 'compet_points':
        compets = compets.order_by(F('compet_points_fase1').desc(nulls_last=True))
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

    return render(request, 'restrito/compet_lista_desclassif.html', {'items': partics, 'total':total, 'pagetitle': pagetitle, 'form': form, 'mod': 'prog'})
    
@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_relatorio_desclassif(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    filepath = os.path.join(settings.BASE_DIR,"static","dupl-fase1","duplicates.csv")
    with open(filepath, 'r') as f:
        lines = f.readlines()
    items = []
    cluster = 0
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        # cluster;task; compet_type; compet_id; compet_name; school; score; link
        try:
            junk, task,compet_type,compet_id, compet_name, school_name, score, link = line.split(';')
        except:
            cluster += 1
            continue
        if school_name == school.school_name:
            items.append([cluster, task, compet_type, compet_id, compet_name])

    pagetitle = 'Relatório resumido'
    return render(request, 'restrito/compet_relatorio_desclassif.html', {'items': items, 'pagetitle': pagetitle })
        

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_classif_final(request,level):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compet_type = LEVEL[level.upper()]
    compets = Compet.objects.filter(compet_school_id=school_id, compet_type=compet_type, compet_points_fase1__gte=0).order_by('compet_rank_final')
    compets = compets.exclude(compet_name__icontains='teste') | compets.filter(compet_name='Rafael Xavier Teste')
    
    total = Compet.objects.filter(compet_type=compet_type, compet_points_fase1__gte=0).count()


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

    return render(request, 'restrito/compet_lista_classif_final.html', {'level':level, 'items': partics, 'total':total, 'pagetitle':'Classificação Final'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_classif_final_cf(request,level):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compet_type = LEVEL[level.upper()]
    compets = CompetCfObi.objects.filter(compet__compet_school_id=school_id, compet_type=compet_type, compet_points__gte=0).order_by('compet_rank')
    compets = compets.exclude(compet__compet_name__icontains='teste')
    total = CompetCfObi.objects.filter(compet_type=compet_type, compet_points__gte=0).count()


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

    return render(request, 'restrito/compet_lista_classif_final.html', {'level':level, 'items': partics, 'total':total, 'pagetitle':'Classificação Final - Competição Feminina'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def emite_certificados_escola(request,ctype):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    ctype = ctype.upper()
    if ctype in ('IJ','I1','I2','PJ','P1','P2','PS'):
        #print(f"get_certif_school_compets(school_id={school_id},int(YEAR={YEAR}),compet_type={LEVEL[ctype]}")
        compets = Compet.objects.filter(compet_school_id=school_id,compet_type=LEVEL[ctype],compet_points_fase1__gte=0).order_by('compet_name')
        compets = compets.exclude(compet_name__icontains='teste')
        file_data = get_certif_school_compets(school_id,int(YEAR),compets)
    elif ctype=='COLABS':
        file_data = get_certif_school_colabs(school_id,year=int(YEAR))
    elif ctype=='DELEG':
        file_data = get_certif_deleg(school_id,year=int(YEAR))
    if file_data == None:
        return erro(request,'Não há certificados para os participantes selecionados.')
    ctype = ctype.lower()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificados_{ctype}.pdf"'
    response.write(file_data)
    return response

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def emite_certificados_escola_cf(request,ctype):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    ctype = ctype.upper()
    if ctype in ('PJ','P1','P2'):
        #print(f"get_certif_school_compets(school_id={school_id},int(YEAR={YEAR}),compet_type={LEVEL[ctype]}")
        compets = CompetCfObi.objects.filter(compet__compet_school_id=school_id,compet_type=LEVEL[ctype],compet_points__gte=0).order_by('compet__compet_name')
        print("len(compets)",len(compets))
        compets = compets.exclude(compet__compet_name__icontains='teste')
        file_data = get_certif_school_compets_cf(school_id,int(YEAR),compets)
    else:
        file_data = None

    if file_data == None:
        return erro(request,'Não há certificados para os participantes selecionados.')
    ctype = ctype.lower()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificados_{ctype}.pdf"'
    response.write(file_data)
    return response


@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def serve_protected_document_pdf(request, file, return_url='/restrito'):
    try:
        file=os.path.join(settings.BASE_DIR,'protected_files',file)
        # Split the elements of the path
        path, file_name = os.path.split(file)
        response = FileResponse(open(file,"rb"),content_type='application/pdf')
        response["Content-Disposition"] = "attachment; filename={}".format(file_name)
        return response
    except:
        url_from = request.META.get('HTTP_REFERER')
        messages.error(request, 'Ainda não disponível. Consulte o calendário para ver a data em que estará disponível.')
        url_return = urlparse(url_from).path
        return redirect(url_return)


@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def serve_protected_document_txt(request, file):
    file=os.path.join(settings.BASE_DIR,'protected_files',file)
    # Split the elements of the path
    path, file_name = os.path.split(file)
    response = FileResponse(open(file,"rb"),content_type='text/plain')
    response["Content-Disposition"] = "attachment; filename={}".format(file_name)
    return response


@user_passes_test(in_coord_colab_full_group, login_url='/contas/login/')
def serve_protected_document_zip(request, file):
    file=os.path.join(settings.BASE_DIR,'protected_files',file)
    # Split the elements of the path
    path, file_name = os.path.split(file)
    response = FileResponse(open(file,"rb"),content_type='application/zip')
    response["Content-Disposition"] = "attachment; filename={}".format(file_name)
    return response


def compet_cms_add_user(request, c, compet_type, contest_id=DEFAULT_CONTEST_ID):
    # print("in compet_cms_add_user")
    try:
        cms_add_user(c, compet_type, contest_id)
    except:
        logger.info("compet_cms_add_user falhou, user={} compet={}".format(request.user,c))


def compet_cms_remove_user(request, compet_id_full, compet_type, contest_id=DEFAULT_CONTEST_ID):
    try:
        cms_remove_user(compet_id_full, compet_type, contest_id)
    except:
        logger.info("compet_cms_remove_user falhou, user={} compet={}".format(request.user,compet_id_full))


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_create_user(request, c, compet_type, school, school_password=None, contest_id=DEFAULT_CONTEST_ID):
    logger.info("compet_create_user, user={} compet={}".format(request.user, c))

    if school_password:
        password = school_password
    else:
        password = make_password()

    c.save() # to get compet_id
    c.compet_id_full = format_compet_id(c.compet_id)
    logger.info("compet_create_user, compet_id_full={}".format(c.compet_id_full))

    username = c.compet_id_full
    email = c.compet_email
    user = User.objects.create_user(username, email, password)
    user.last_name = c.compet_name
    user.is_staff = False
    g = Group.objects.get(name='compet')
    g.user_set.add(user)
    user.save()

    c.user = user
    c.compet_conf = password
    c.save()
    #print("in compet_create_user")

    # add user to CMS db
    #if compet_type in LEVEL_PROG:
    #    compet_cms_add_user(request, c, compet_type, contest_id)
    if compet_type in LEVEL_PROG:
        compet_cms_add_user(request, c, compet_type, contest_id)


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_recupera_cadastro(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="cadastro_competidores.csv"'},
    )
    writer = csv.writer(response)

    writer.writerow(['Num. Inscr.', 'Nível', 'Nome', 'Nascimento', 'Gênero', 'Ano Escola', 'Turma Escolar', 'Email','Senha'])
    for compet_type in LEVEL_ALL:
        compets=Compet.objects.filter(compet_school_id=school.school_id,compet_type=compet_type).order_by('compet_name')
        for c in compets:
            birthdate = c.compet_birth_date.strftime("%d/%m/%Y")
            writer.writerow([c.compet_id_full, LEVEL_NAME[c.compet_type], c.compet_name, birthdate, c.compet_sex, c.compet_year, c.compet_class, c.compet_email, c.compet_conf])
    return response


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_recupera_cadastro(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="cadastro_competidoras_cfobi.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Num. Inscr.', 'Nível CF-OBI', 'Nome', 'Nascimento', 'Gênero', 'Ano Escola', 'Turma Escolar', 'Email','Senha'])

    for compet_type in LEVEL_CFOBI:
        compets=Compet.objects.filter(compet_school_id=school.school_id, competcfobi__compet_type=compet_type).order_by('compet_name')
        for c in compets:
            birthdate = c.compet_birth_date.strftime("%d/%m/%Y")
            writer.writerow([c.compet_id_full, LEVEL_NAME[c.competcfobi.compet_type], c.compet_name, birthdate, c.compet_sex, c.compet_year, c.compet_class, c.compet_email, c.compet_conf])

    return response


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_authorize_default_exams(request,c,school):
    '''authorize TestFase1 for all contestants
       authorize ExamFase1 for programacao
    '''
    # authorize only for programacao
    if c.compet_type not in LEVEL_PROG:
        return

    try:
        ex = TesteFase1(compet=c,school=school)
        ex.save()
    except:
        logger.info("compet_authorize_default_exams falhou ao autorizar TesteFase1, user={} compet={}".format(request.user,c))
    if c.compet_type in LEVEL_PROG:
        try:
            ex = ExamFase1(compet=c,school=school)
            ex.save()
        except:
            logger.info("compet_authorize_default_exams falhou ao autorizar ExamFase1, user={} compet={}".format(request.user,c))
    logger.info("compet_authorized_default_exams finished, user={} compet={}".format(request.user,c))


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_authorize_default_exams(request, c_cfobi, school):
    '''authorize TestFase1 for all contestants
       authorize ExamCfObi for programacao
    '''

    # TODO Test competition for CF-OBI?
    #try:
    #    ex = TesteFase1(compet=c,school=school)
    #    ex.save()
    #except:
    #    logger.info("compet_feminina_authorize_default_exams falhou ao autorizar TesteFase1, user={} competcfobi={}".format(request.user,c_cfobi))

    try:
        ex = ExamCfObi(compet=c_cfobi, school=school)
        ex.save()
    except:
        logger.info("compet_feminina_authorize_default_exams falhou ao autorizar ExamCfObi, user={} competcfobi={}".format(request.user, c_cfobi))

    logger.info("compet_feminina_authorized_default_exams finished, user={} competcfobi={}".format(request.user, c_cfobi))


def queue_email(subject, body, from_addr, to_addr, priority=0):
    m = QueuedMail(subject=subject, body=body, from_addr=from_addr, to_addr=to_addr, priority=priority)
    m.save()


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_send_email(request,c,school,reason,queue=False):
    if not c.compet_email:
        logger.warning("compet send email returned without sending, compet has no email, user={}, compet={}, reason={}".format(request.user,c,reason))
        return
    if c.compet_email.strip() == '':
        logger.warning("compet send email returned without sending, compet has no email, user={}, compet={}, reason={}".format(request.user,c,reason))
        return

    mod = LEVEL_NAME_FULL[int(c.compet_type)]
    if c.compet_sex == 'F':
        greeting = 'Prezada'
        sex_suffix = 'a'
    else:
        greeting = 'Prezado'
        sex_suffix = ''
    msg = EMAIL_MSG_COMPET_PASSWD
    body = msg.format(greeting=greeting,
                      year=YEAR,
                      sex_suffix=sex_suffix,
                      reason=reason,
                      name=c.compet_name,
                      compet_id=c.compet_id_full,
                      school=school.school_name,
                      modal=mod,
                      city=school.school_city,
                      state=school.school_state,
                      user=c.compet_id_full,
                      password=c.compet_conf)
    if queue:
        queue_email(
            f'OBI{YEAR}, inscrição',
            body,
            DEFAULT_FROM_EMAIL,
            c.compet_email
        )
        logger.info("queued email to compet, user={}, compet={}, reason={}".format(request.user,c,reason))
    else:
        try:
            send_mail(
                f'OBI{YEAR}, inscrição',
                body,
                DEFAULT_FROM_EMAIL,
                [c.compet_email]
            )
            logger.info("sent email to compet, user={}, compet={}, reason={}".format(request.user,c,reason))
        except:
            messages.error(request, 'Envio de email com a senha para o competidor falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
            logger.warning("send email to compet failed, user={}, compet={}, reason={}".format(request.user,c,reason))


def compet_send_email_admin(c,school,reason,queue=True):
    if not c.compet_email:
        logger.warning("compet send email returned without sending, compet has no email, compet={}, reason={}".format(c,reason))
        return
    if c.compet_email.strip() == '':
        logger.warning("compet send email returned without sending, compet has no email, compet={}, reason={}".format(c,reason))
        return

    mod = LEVEL_NAME_FULL[int(c.compet_type)]
    if c.compet_sex == 'F':
        greeting = 'Prezada'
        sex_suffix = 'a'
    else:
        greeting = 'Prezado'
        sex_suffix = ''
    msg = EMAIL_MSG_COMPET_PASSWD
    body = msg.format(greeting=greeting,
                      year=YEAR,
                      sex_suffix=sex_suffix,
                      reason=reason,
                      name=c.compet_name,
                      compet_id=c.compet_id_full,
                      school=school.school_name,
                      modal=mod,
                      city=school.school_city,
                      state=school.school_state,
                      user=c.compet_id_full,
                      password=c.compet_conf)

    queue_email(
        f'OBI{YEAR}, inscrição',
        body,
        DEFAULT_FROM_EMAIL,
        c.compet_email
    )
    logger.info("queued email to compet, compet={}, reason={}".format(c,reason))

            
@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_inscreve_lote(request):

    msg = 'Período de inscrições terminou.'
    return aviso(request, msg)

    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id

    #msg = 'Sistema em manutenção, por favor aguarde'

    #if school_id not in (1,):
    #    msg = 'Período de inscrições terminou.'
    #    return aviso(request, msg)
    
    if request.method == 'POST':
        form = CompetInscreveLoteForm(request.POST, request.FILES)
        if form.is_valid():
            file_path, disregard = write_school_uploaded_file(school_id=school_id,
                                                   modality='',phase_name='',fwhy='inscricao',
                                                   f=request.FILES['data'],fname=request.FILES['data'].name)
            msg,errors,validated_compets = check_compet_batch(request.FILES['data'],school)
            if len(errors)==0 and len(msg)==0:
                res_msg = Compet.objects.bulk_create(validated_compets)
                for c in validated_compets:
                    # create user for compet and send email
                    c.compet_id_full = format_compet_id(c.compet_id)
                    compet_create_user(request,c,c.compet_type,school)
                    compet_send_email(request,c,school,reason="fazer sua inscrição",queue=True)
                    compet_authorize_default_exams(request,c,school)
                msg = '<p>O arquivo foi processado corretamente. Foram encontrados {} competidores no arquivo. Todos os competidores foram inseridos no sistema.</p>'.format(len(validated_compets))
            else:
                msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
                <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
            return render(request,
                      'restrito/compet_inscreve_lote_resp.html',
                      context={'msg': msg, 'errors': errors,
                      })
    else:
        form = CompetInscreveLoteForm()
    return render(request, 'restrito/compet_inscreve_lote.html', {'form': form, 'pagetitle': 'Inscreve Competidores por Lote', 'pagetype': 'batch'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_lote(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    #msg = 'Período de inscrições ainda não iniciou.'
    return aviso(request, msg)

    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    school_id = school.school_id

    if request.method == 'POST':
        form = CompetInscreveLoteForm(request.POST, request.FILES)
        if form.is_valid():
            file_path, disregard = write_school_uploaded_file(school_id=school_id,
                                                   modality='',phase_name='',fwhy='inscricao',
                                                   f=request.FILES['data'],fname=request.FILES['data'].name)
            msg, errors, validated_compets, validated_compets_cfobi = check_compet_feminina_batch(request.FILES['data'],school)

            if len(errors) == 0 and len(msg) == 0:
                if len(validated_compets) > 0:
                    res_msg_compet = Compet.objects.bulk_create(validated_compets)
                res_msg_compet_cfobi = CompetCfObi.objects.bulk_create(validated_compets_cfobi)

                for c in validated_compets:
                    # create user for compet and send email
                    compet_create_user(request, c, c.competcfobi.compet_type, school, contest_id=DEFAULT_CONTEST_ID_CFOBI)
                    compet_send_email(request, c, school,reason="fazer sua inscrição", queue=True)
                    compet_feminina_authorize_default_exams(request, c, school)

                msg = '<p>O arquivo foi processado corretamente. Foram encontradas {} competidoras no arquivo. Todas as competidoras foram inscritas na CF-OBI.</p>'.format(len(validated_compets_cfobi))
            else:
                msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhuma competidora do arquivo foi inscrita na CF-OBI.
                         <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
            return render(request,
                      'restrito/compet_feminina_inscreve_lote_resp.html',
                      context={'msg': msg, 'errors': errors,
                      })
    else:
        form = CompetInscreveLoteForm()
    return render(request, 'restrito/compet_feminina_inscreve_lote.html', {'form': form, 'pagetitle': 'Inscreve Competidoras CF-OBI por Lote', 'pagetype': 'batch'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_recupera_elegivel_inscricao_cfobi(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    response = HttpResponse(
        content_type='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename="competidoras_obi_elegiveis_inscricao_cfobi.csv"'},
    )

    writer = csv.writer(response)
    writer.writerow(['Num. Inscr.', 'Nível OBI', 'Nível CF-OBI', 'Nome', 'Nascimento', 'Gênero', 'Ano Escola', 'Turma Escolar', 'Email'])

    for compet_type in LEVEL_INI + LEVEL_CFOBI:
        compets=Compet.objects.filter(compet_school_id=school.school_id, compet_sex__in=(x[0] for x in SEX_CHOICES_CFOBI), compet_type=compet_type).order_by('compet_name')
        for c in compets:
            if getattr(c, 'competcfobi', None) is not None: # Already registered for CF-OBI.
                continue
            birthdate = c.compet_birth_date.strftime("%d/%m/%Y")
            level_cfobi = LEVEL_NAME[c.compet_type] if c.compet_type in LEVEL_CFOBI else ''
            writer.writerow([c.compet_id_full, LEVEL_NAME[c.compet_type], level_cfobi, c.compet_name, birthdate, c.compet_sex, c.compet_year, c.compet_class, c.compet_email])

    return response


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_inscreve_lote_senha(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    if request.method == 'POST':
        form = CompetInscreveLoteForm(request.POST, request.FILES)
        if form.is_valid():
            file_path, disregard = write_school_uploaded_file(school_id=school_id,
                                                   modality='',phase_name='',fwhy='inscricao',
                                                   f=request.FILES['data'],fname=request.FILES['data'].name)
            msg,errors,validated_compets,school_passwords = check_compet_batch_password(request.FILES['data'],school)
            if len(errors)==0 and len(msg)==0:
                res_msg = Compet.objects.bulk_create(validated_compets)
                k = 0
                for c in validated_compets:
                    # create user for compet and send email
                    #c.compet_id_full = format_compet_id(c.compet_id)
                    compet_create_user(request,c,c.compet_type,school,school_passwords[k])
                    compet_send_email(request,c,school,reason="fazer sua inscrição",queue=True)
                    compet_authorize_default_exams(request,c,school)
                    k += 1
                msg = '<p>O arquivo foi processado corretamente. Foram encontrados {} competidores no arquivo. Todos os competidores foram inseridos no sistema.</p>'.format(len(validated_compets))
            else:
                msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhum competidor do arquivo foi inserido no sistema.
                <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
            return render(request,
                      'restrito/compet_inscreve_lote_resp.html',
                      context={'msg': msg, 'errors': errors,
                      })
    else:
        form = CompetInscreveLoteForm()
    return render(request, 'restrito/compet_inscreve_lote.html', {'form': form, 'pagetitle': 'Inscreve Competidores por Lote com Senha'})


EMAIL_MSG_COMPET_PASSWD = '''{greeting} competidor{sex_suffix},

você está recebendo esta mensagem porque seu professor informou este endereço de
email ao {reason} na OBI (Olimpíada Brasileira de Informática),
com os seguinte dados

Nome: {name}
Modalidade: {modal}
Escola: {school}
Cidade: {city}
Estado: {state}

Seu número de inscrição na OBI{year} é {compet_id}.

Para acessar sua página pessoal na OBI, onde serão disponibilizadas as
datas e os resultados das provas, utilize o link "ACESSO COMPETIDORES"
no menu  da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/compet"):

usuário: {compet_id}
senha: {password}

Boa OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

EMAIL_MSG_COLAB = '''{greeting} Colaborador{sex_suffix},

você está recebendo esta mensagem porque o Coordenador Local da OBI na
sua escola informou este endereço de email ao {reason} na
OBI (Olimpíada Brasileira de Informática) como "Colaborador", com
os seguintes dados:

Nome: {name}
Escola: {school}
Cidade: {city}
Estado: {state}

Como Colaborador, você terá acesso ao sistema da OBI para
gerenciar competidores (inserir/editar/excluir) e inserir
notas.

Para acessar o sistema da OBI utilize o link "ACESSO ESCOLAS" no menu
da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/restrito"):

usuário: {user}
senha: {password}

Obrigado por seu trabalho pela OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''
EMAIL_MSG_COLAB_FULL = '''{greeting} Colaborador{sex_suffix},

você está recebendo esta mensagem porque o Coordenador Local da OBI na
sua escola informou este endereço de email ao {reason} na
OBI (Olimpíada Brasileira de Informática) como "Colaborador", com
os seguintes dados:

Nome: {name}
Escola: {school}
Cidade: {city}
Estado: {state}

Como Colaborador, você terá acesso ao sistema da OBI para
gerenciar competidores (inserir/editar/excluir), inserir
notas e acessar as provas para impressão.

Para acessar o sistema da OBI utilize o link "ACESSO ESCOLAS" no menu
da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/restrito"):

usuário: {user}
senha: {password}

Obrigado por seu trabalho pela OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_atualiza_senhas_lote(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    if request.method == 'POST':
        form = CompetInscreveLoteForm(request.POST, request.FILES)
        if form.is_valid():
            file_path, disregard = write_school_uploaded_file(school_id=school_id,
                                                   modality='',phase_name='',fwhy='inscricao',
                                                   f=request.FILES['data'],fname=request.FILES['data'].name)
            msg,errors,validated_compets = check_compet_batch_update_password(request.FILES['data'],school)
            if len(errors)==0 and len(msg)==0:
                k = 0
                for c,password in validated_compets:
                    u = c.user
                    u.set_password(password)
                    u.save()
                    # store only contestants passwords
                    pw = Password(user_id=u.id,password=password)
                    pw.save()
                    c.compet_conf = password
                    c.save()
                    # update password in CMS db
                    if c.compet_type in LEVEL_PROG:
                        pass
                        #cms_update_password(u.username, c.compet_type, u.password)
                    k += 1

                msg = '<p>O arquivo foi processado corretamente. Foram encontrados {} competidores no arquivo, as senhas foram alteradas no sistema.</p>'.format(len(validated_compets))
            else:
                msg = '''<p>Foram encontrados alguns erros durante o processamento do arquivo. Nenhuma senha foi alterada no sistema.
                <p>Por favor corrija os erros abaixo e re-submeta o arquivo.</p><p>{}</p>'''.format(msg)
            return render(request,
                      'restrito/compet_inscreve_lote_resp.html',
                      context={'msg': msg, 'errors': errors,
                      })
    else:
        form = CompetInscreveLoteForm()
    return render(request, 'restrito/compet_inscreve_lote.html', {'form': form, 'pagetitle': 'Atualiza Senhas por Lote', 'pagetype': 'update'})


EMAIL_MSG_COMPET_PASSWD = '''{greeting} competidor{sex_suffix},

você está recebendo esta mensagem porque seu professor informou este endereço de
email ao {reason} na OBI (Olimpíada Brasileira de Informática),
com os seguinte dados

Nome: {name}
Modalidade: {modal}
Escola: {school}
Cidade: {city}
Estado: {state}

Seu número de inscrição na OBI{year} é {compet_id}.

Para acessar sua página pessoal na OBI, onde serão disponibilizadas as
datas e os resultados das provas, utilize o link "ACESSO COMPETIDORES"
no menu  da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/compet"):

usuário: {compet_id}
senha: {password}

Boa OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

EMAIL_MSG_COLAB = '''{greeting} Colaborador{sex_suffix},

você está recebendo esta mensagem porque o Coordenador Local da OBI na
sua escola informou este endereço de email ao {reason} na
OBI (Olimpíada Brasileira de Informática) como "Colaborador", com
os seguintes dados:

Nome: {name}
Escola: {school}
Cidade: {city}
Estado: {state}

Como Colaborador, você terá acesso ao sistema da OBI para
gerenciar competidores (inserir/editar/excluir) e inserir
notas.

Para acessar o sistema da OBI utilize o link "ACESSO ESCOLAS" no menu
da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/restrito"):

usuário: {user}
senha: {password}

Obrigado por seu trabalho pela OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''
EMAIL_MSG_COLAB_FULL = '''{greeting} Colaborador{sex_suffix},

você está recebendo esta mensagem porque o Coordenador Local da OBI na 
sua escola informou este endereço de email ao {reason} na 
OBI (Olimpíada Brasileira de Informática) como "Colaborador", com
os seguintes dados:

Nome: {name}
Escola: {school}
Cidade: {city}
Estado: {state}

Como Colaborador, você terá acesso ao sistema da OBI para
gerenciar competidores (inserir/editar/excluir), inserir
notas e acessar as provas para impressão.

Para acessar o sistema da OBI utilize o link "ACESSO ESCOLAS" no menu
da página da OBI{year} com as seguintes credenciais (o link direto é
"https://olimpiada.ic.unicamp.br/restrito"):

usuário: {user}
senha: {password}

Obrigado por seu trabalho pela OBI{year}!
---
Olimpíada Brasileira de Informática
https://www.sbc.org.br/obi
'''

def send_email_colab_registered(request,c,colab_school,password,reason,group_name, queue=False):
    if c.colab_sex == 'F':
        greeting = 'Prezada'
        sex_suffix = 'a'
    else:
        greeting = 'Prezado'
        sex_suffix = ''
    if group_name == 'colab_full':
        msg = EMAIL_MSG_COLAB_FULL
    else:
        msg = EMAIL_MSG_COLAB

    body = msg.format(greeting=greeting,
                   sex_suffix=sex_suffix,
                   year=YEAR,
                   reason=reason,
                   name=c.colab_name,
                   school=colab_school.school_name,
                   city=colab_school.school_city,
                   state=colab_school.school_state,
                   user=c.colab_email,
                   password=password)

    if queue:
        queue_email(
            f'OBI{YEAR}, cadastro',
            body,
            DEFAULT_FROM_EMAIL,
            c.colab_email
        )
        logger.info("queued email to colab, user={}, colab={}, reason=cadastro".format(request.user,c,))

    else:
        try:
            send_mail(
                f'OBI{YEAR}, cadastro',
                body,
                DEFAULT_FROM_EMAIL,
                [c.colab_email]
            )

            logger.info("sent email to compet, user={}, colab={}, reason=cadastro".format(request.user,c,reason))
        except:
            messages.error(request, 'Envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
            logger.warning("send email to colab failed, user={}, colab={}, reason=cadastro".format(request.user,c))


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_inscreve(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    return aviso(request, msg)

    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    school_id = school.school_id

    #if school_id not in (1,557,566,563,562,564,561,558,565,2202,3330):
    #    msg = 'Período de inscrições terminou.'
    #    return aviso(request, msg)
    
    if request.method == 'POST':
        form = CompetInscreveForm(request.POST, request=request)
        if form.is_valid():
            f = form.cleaned_data
            c = Compet(compet_name=f['compet_name'], compet_type=int(f['compet_type']),
                       compet_year=f['compet_year'], compet_class=f['compet_class'], compet_email=f['compet_email'],
                       compet_birth_date=f['compet_birth_date'], compet_sex=f['compet_sex'],
                       compet_school=school)
            # create user for compet and send email
            c.save()
            c_extra = CompetExtra(c.compet_id)
            if f['compet_mother_name']:
                c_extra.compet_mother_name = f['compet_mother_name']
            if f['compet_cpf']:
                c_extra.compet_cpf = f['compet_cpf']
            if f['compet_nis']:
                c_extra.compet_nis = f['compet_nis']
            c_extra.save()
            #c.compet_id_full = format_compet_id(c.compet_id)
            #c.save()
            compet_create_user(request,c,c.compet_type,school)
            compet_send_email(request,c,school,reason="fazer sua inscrição", queue=True)
            compet_authorize_default_exams(request,c,school)
            logger.info("compet_inscreve, user={} compet={}".format(request.user,c))
            if c.compet_sex == 'F':
                messages.success(request, 'Competidora "{}" foi inscrita.'.format(c.compet_name))
            else:
                messages.success(request, 'Competidor "{}" foi inscrito.'.format(c.compet_name))
            if 'save_and_continue' in request.POST:
                form = CompetInscreveForm()
            else:
                return redirect('/restrito')
    else:
        form = CompetInscreveForm()

    return render(request, 'restrito/compet_inscreve.html', {'form': form, 'pagetitle': 'Inscreve Novo Competidor'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    #msg = 'Período de inscrições ainda não iniciou.'
    msg = 'Período de inscrições terminou.'
    return aviso(request, msg)

    return render(request, 'restrito/compet_feminina_inscreve.html', {})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_nova(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    #msg = 'Período de inscrições ainda não iniciou.'
    return aviso(request, msg)

    if request.method == 'POST':
        try:
            school = request.user.deleg.deleg_school
        except:
            school = request.user.colab.colab_school
        form = CompetFemininaInscreveForm(request.POST, request=request)
        if form.is_valid():
            f = form.cleaned_data

            try:
                school = request.user.deleg.deleg_school
            except:
                school = request.user.colab.colab_school

            c = Compet(compet_name=f['compet_name'], compet_type=CF,
                       compet_year=f['compet_year'], compet_class=f['compet_class'], compet_email=f['compet_email'],
                       compet_birth_date=f['compet_birth_date'], compet_sex=f['compet_sex'],
                       compet_school=school)
            c.save()

            c_extra = CompetExtra(c.compet_id)
            if f['compet_mother_name']:
                c_extra.compet_mother_name = f['compet_mother_name']
            if f['compet_cpf']:
                c_extra.compet_cpf = f['compet_cpf']
            if f['compet_nis']:
                c_extra.compet_nis = f['compet_nis']
            c_extra.save()

            c_cfobi = CompetCfObi(compet=c, compet_type=int(f['compet_type']))
            c_cfobi.save()

            compet_create_user(request, c, c_cfobi.compet_type, school, contest_id=DEFAULT_CONTEST_ID_CFOBI)
            compet_send_email(request, c, school, reason="fazer sua inscrição", queue=True)
            compet_feminina_authorize_default_exams(request, c, school)

            logger.info("compet_feminina_inscreve, user={} compet={}".format(request.user,c))

            messages.success(request, 'Competidora "{}" foi inscrita.'.format(c.compet_name))

            if 'save_and_continue' in request.POST:
                form = CompetFemininaInscreveForm()
            else:
                return redirect('/restrito')
    else:
        form = CompetFemininaInscreveForm()

    return render(request, 'restrito/compet_feminina_inscreve_nova.html', {'form': form, 'pagetitle': 'Inscreve Nova Competidora CF-OBI'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_prog(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    #msg = 'Período de inscrições ainda não iniciou.'
    return aviso(request, msg)

    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    compets = Compet.objects.filter(compet_sex__in=(x[0] for x in SEX_CHOICES_CFOBI), compet_type__in=LEVEL_CFOBI, compet_school_id=school_id, competcfobi__isnull=True)

    total = len(compets)
    if request.method == 'POST':
        form = CompetFemininaFiltroForm(request.POST)
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
        form = CompetFemininaFiltroForm(initial=instance)

    if compet_list_type:
        request.session['compet_list_type'] = int(compet_list_type)
        compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    try:
        compets = compets.order_by(compet_list_order)
    except:
        compets = compets.order_by('compet_name')

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

    return render(request, 'restrito/compet_feminina_inscreve_prog.html', {'items': partics, 'total':total, 'pagetitle':'Inscreve Competidoras da Programação OBI na CF-OBI', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_selecionadas_prog(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    registered = []
    if request.method == 'POST':
        register = request.POST.getlist('choices_set')
        registered = 0
        for r in register:
            compet_id = int(r)
            try:
                c = Compet.objects.get(compet_id=compet_id,compet_school=school)
            except:
                logger.info("compet_feminina_inscreve_selecionadas_prog falhou, competidora não existe, user={} compet_id={}".format(request.user,compet_id))
                continue

            c_cfobi = CompetCfObi(compet=c, compet_type=c.compet_type)
            c_cfobi.save()

            compet_feminina_authorize_default_exams(request, c, school)

            registered += 1

        if registered == 1:
            messages.success(request,f'Competidora {c} foi inscrita na CF-OBI.')
        else:
            messages.success(request,f'{registered} competidoras foram inscritas na CF-OBI.')
    logger.info("compet_feminina_inscreve_selecionadas_prog, user={} registered {}".format(request.user, register))
    return redirect('/restrito/compet_feminina_inscreve_prog')


# @user_passes_test(in_coord_colab_group, login_url='/contas/login/')
# def compet_feminina_inscreve_ini(request):
#     #msg = 'Sistema em manutenção, por favor aguarde'
#     #msg = 'Período de inscrições terminou.'
#     msg = 'Período de inscrições ainda não iniciou.'
#     return aviso(request, msg)

#     try:
#         school_id = request.user.deleg.deleg_school.pk
#     except:
#         school_id = request.user.colab.colab_school.pk

#     compets = Compet.objects.filter(compet_sex__in=(x[0] for x in SEX_CHOICES_CFOBI), compet_type__in=LEVEL_INI, compet_school_id=school_id, competcfobi__isnull=True)

#     total = len(compets)
#     if request.method == 'POST':
#         form = CompetFemininaFiltroForm(request.POST, compet_type_choices=LEVEL_CHOICES_FILTER_INI)
#         if form.is_valid():
#             f = form.cleaned_data
#             compet_list_order = f['compet_order']
#             compet_list_name = f['compet_name']
#             compet_list_type = f['compet_type']
#             request.session['compet_list_name'] = compet_list_name
#             request.session['compet_list_order'] = compet_list_order
#             request.session['compet_list_type'] = compet_list_type
#     else:
#         try:
#             compet_list_order = request.session['compet_list_order']
#         except:
#             compet_list_order = 'compet_name'
#         try:
#             compet_list_name = request.session['compet_list_name']
#         except:
#             compet_list_name = ''
#         try:
#             compet_list_type = request.session['compet_list_type']
#         except:
#             compet_list_type = None
#         instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
#         form = CompetFemininaFiltroForm(initial=instance, compet_type_choices=LEVEL_CHOICES_FILTER_INI)

#     if compet_list_type:
#         request.session['compet_list_type'] = int(compet_list_type)
#         compets = compets.filter(compet_type=compet_list_type)

#     tks = compet_list_name.split()
#     for tk in tks:
#         compets = compets.filter(compet_name__icontains = tk)

#     try:
#         compets = compets.order_by(compet_list_order)
#     except:
#         compets = compets.order_by('compet_name')

#     page = request.GET.get('page', 1)
#     page_size = calculate_page_size(len(compets), page)
#     try:
#         paginator = Paginator(compets, page_size)
#         try:
#             partics = paginator.page(page)
#         except PageNotAnInteger:
#             partics = paginator.page(1)
#         except EmptyPage:
#             partics = paginator.page(paginator.num_pages)
#     except:
#         partics = []

#     return render(request, 'restrito/compet_feminina_inscreve_ini.html', {'items': partics, 'total':total, 'pagetitle':'Inscreve Competidoras da Iniciação OBI na CF-OBI', 'form': form})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_ini(request):
    #msg = 'Sistema em manutenção, por favor aguarde'
    msg = 'Período de inscrições terminou.'
    #msg = 'Período de inscrições ainda não iniciou.'
    return aviso(request, msg)

    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    compets = Compet.objects.filter(compet_sex__in=(x[0] for x in SEX_CHOICES_CFOBI), compet_school_id=school_id, competcfobi__isnull=True)

    total = len(compets)
    if request.method == 'POST':
        form = CompetFemininaFiltroForm(request.POST, compet_type_choices=LEVEL_CHOICES_FILTER_INI + LEVEL_CHOICES_FILTER_CFOBI[1:])
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
        form = CompetFemininaFiltroForm(initial=instance, compet_type_choices=LEVEL_CHOICES_FILTER_INI+LEVEL_CHOICES_FILTER_CFOBI[1:])

    if compet_list_type:
        request.session['compet_list_type'] = int(compet_list_type)
        compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    try:
        compets = compets.order_by(compet_list_order)
    except:
        compets = compets.order_by('compet_name')

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

    return render(request, 'restrito/compet_feminina_inscreve_ini.html', {'items': partics, 'total':total, 'pagetitle':'Inscreve Competidoras da OBI na CF-OBI', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_inscreve_selecionadas_ini(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    registered = []
    if request.method == 'POST':
        register = request.POST.getlist('choices_set')
        compet_type = LEVEL[request.POST['level_cfobi']]
        registered = 0
        failed = 0
        for r in register:
            compet_id = int(r)
            try:
                c = Compet.objects.get(compet_id=compet_id,compet_school=school)
            except:
                logger.info("compet_feminina_inscreve_selecionadas_ini falhou, competidora não existe, user={} compet_id={}".format(request.user,compet_id))
                continue

            if c.compet_type == P1 and compet_type in (PJ,):
                failed += 1
                continue
            if c.compet_type == P2 and compet_type in (PJ,P1,):
                failed += 1
                continue
            c_cfobi = CompetCfObi(compet=c, compet_type=compet_type)
            c_cfobi.save()

            compet_feminina_authorize_default_exams(request, c, school)

            registered += 1

        message = ''
        if registered == 0:
            message += f'Nenhuma competidora foi inscrita na {LEVEL_NAME_FULL[compet_type]} da CF-OBI'
        elif registered == 1:
            message += f'Competidora {c} foi inscrita na {LEVEL_NAME_FULL[compet_type]} da CF-OBI'
        else:
            message += f'{registered} competidoras foram inscritas na {LEVEL_NAME_FULL[compet_type]} da CF-OBI'
        if failed == 0:
            message += '.'
            messages.success(request, message)
        elif failed == 1:
            message += f' (inscrição da competidora {c} falhou). Verifique a eligibilidade nas instruções.'
            messages.warning(request, message)
        else:
            message += f' (inscrições de {failed} competidoras falharam). Verifique a eligibilidade nas instruções.'
            messages.warning(request, message)
    logger.info(f"compet_feminina_inscreve_selecionadas_ini, user={request.user} registered {registered}, failed {failed}")
    return redirect('/restrito/compet_feminina_inscreve_ini')


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compets = Compet.objects.filter(compet_school_id=school_id, compet_type__in=LEVEL.values())
    total = len(compets)
    if request.method == 'POST':
        form = CompetFiltroForm(request.POST)
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
        form = CompetFiltroForm(initial=instance)

    print(compet_list_type, 'compet_list_type')
    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=LEVEL_INI)
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=LEVEL_PROG)
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    try:
        compets = compets.order_by(compet_list_order)
    except:
        compets = compets.order_by('compet_name')

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

    return render(request, 'restrito/compet_lista.html', {'items': partics, 'total':total, 'pagetitle':'Lista Competidores', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_lista(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    compets = Compet.objects.filter(compet_school_id=school_id, competcfobi__isnull=False)

    print(compets)
    
    total = len(compets)
    if request.method == 'POST':
        form = CompetFemininaFiltroForm(request.POST)
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
            # for compets, compet_list_type can be 'P' or 'I'
            compet_list_type = int(compet_list_type)
        except:
            compet_list_type = None
        instance = {'compet_order':compet_list_order, 'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetFemininaFiltroForm(initial=instance)

    if compet_list_type:
        request.session['compet_list_type'] = int(compet_list_type)
        compets = compets.filter(competcfobi__compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass
        
        
    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    try:
        compets = compets.order_by(compet_list_order)
    except:
        compets = compets.order_by('compet_name')

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

    return render(request, 'restrito/compet_feminina_lista.html', {'items': partics, 'total':total, 'pagetitle':'Lista Competidoras CF-OBI', 'form': form})


def compet_lista_rank(request,compet_level):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compet_type = LEVEL[compet_level]
    level_name = LEVEL_NAME_FULL[compet_type]
    num_compet_level = Compet.objects.filter(compet_type=compet_type).count()
    school  = School.objects.get(school_id=school_id)
    state = school.school_state
    num_compet_level_state = Compet.objects.filter(compet_type=compet_type,compet_school__school_state=state).count()

    compets = Compet.objects.filter(compet_school_id=school_id,compet_type=compet_type).order_by('compet_rank_final','compet_name')
    total = len(compets)

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
    return render(request, 'restrito/compet_lista_rank.html', {'items': partics, 'total':total, 'pagetitle': f'Classificação {level_name}', 'compet_level':compet_level, 'num_compet_level':num_compet_level,'num_compet_level_state':num_compet_level_state, 'level_name': level_name})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_remove(request, c, school):
    # must delete password first

    # 
    # if c.compet_type in (PJ, P1, P2, PS):
    #     try:
    #         p = PasswordCms.objects.get(compet_id=c.compet_id)
    #         print("p.compet_id",p.compet_id)
    #         p.delete()
    #     except:
    #         logger.info("compet_remove falhou remover PasswordCms, user={request.user} compet={c}")
            
    for exam in (ExamFase2,ExamFase1,TesteFase1):
        try:
            ex = exam(compet=c,school=school)
            ex.delete()
        except:
            logger.info("compet_remove falhou ao deautorizar {}, user={} compet={}".format(exam,request.user,c))

    if c.compet_type in LEVEL_PROG:
        try:
            compet_cms_remove_user(request,c.compet_id_full,c.compet_type)
        except:
            logger.info("compet_remove falhou para cms_remove_user, user={} compet={}".format(request.user,c))

    try:
        c.delete() # delete method override also deletes User
    except:
        logger.info("compet_remove falhou, user={} compet={}".format(request.user,c))
        return False

    logger.info("compet_remove, user={} compet={}".format(request.user,c))
    return True


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_remove(request, c, school):
    # If compet is only registered for CF-OBI
    if c.compet_type == CF:
        # must delete password first
        # DO NOT change PasswordCms, generated by admin, not coords (changed)
        # try:
        #     p = PasswordCms.objects.get(compet_id=c.compet_id)
        #     p.delete()
        # except:
        #    logger.info("compet_feminina_remove falhou remover PasswordCms, user={request.user} compet={c}")

        try:
            compet_cms_remove_user(request, c.compet_id_full, c.competcfobi.compet_type, DEFAULT_CONTEST_ID_CFOBI)
        except:
            logger.info("compet_feminina_remove falhou para cms_remove_user, user={} compet={}".format(request.user,c))

    # deauthorize test exams
    for exam in [ExamCfObi]:
        try:
            ex = exam(compet=c,school=school)
            ex.delete()
        except:
            logger.info("compet_feminina_remove falhou ao deautorizar {}, user={} compet={}".format(exam,request.user,c))

    try:
        c.competcfobi.delete()

        if c.compet_type == CF:
            c.delete() # delete method override also deletes User
    except:
        logger.info("compet_feminina_remove falhou, user={} compet={}".format(request.user,c))
        return False

    logger.info("compet_feminina_remove, user={} compet={}".format(request.user,c))
    return True


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_deleta_lote(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    delete = []
    if request.method == 'POST':
        delete = request.POST.getlist('choices_set')
        deleted = 0
        for d in delete:
            compet_id = int(d)
            try:
                c = Compet.objects.get(compet_id=compet_id,compet_school=school)
            except:
                logger.info("compet_deleta_lote falhou, competidor não existe, user={} compet_id={}".format(request.user,compet_id))
                continue
            if compet_remove(request, c, school):
                deleted += 1

        if deleted == 1:
            messages.success(request,f'Competidor {c} foi excluído.')
        else:
            messages.success(request,f'{deleted} competidores foram excluídos.')
    logger.info("compet_deleta_lote, user={} deleted {}".format(request.user,delete))
    return redirect('/restrito/compet_lista')


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_deleta_lote(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    delete = []

    if request.method == 'POST':
        delete = request.POST.getlist('choices_set')
        deleted = 0

        for d in delete:
            compet_id = int(d)
            try:
                c = Compet.objects.get(compet_id=compet_id,compet_school=school)
            except:
                logger.info("compet_feminina_deleta_lote falhou, competidor não existe, user={} compet_id={}".format(request.user,compet_id))
                continue
            if compet_feminina_remove(request, c, school):
                deleted += 1

        if deleted == 1:
            messages.success(request,f'Competidora {c} foi excluída da CF-OBI.')
        else:
            messages.success(request,f'{deleted} competidoras foram excluídas da CF-OBI.')

    logger.info("compet_feminina_deleta_lote, user={} deleted {}".format(request.user,delete))

    return redirect('/restrito/compet_feminina_lista')


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_deleta(request,compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    try:
        c = Compet.objects.get(compet_id=compet_id,compet_school=school)
    except:
        messages.error(request, 'Exclusão falhou, competidor não existe.')
        return redirect('/restrito/compet_lista')

    if not compet_remove(request, c, school):
        logger.info("compet_deleta falhou, user={} compet={}".format(request.user,c))
        return redirect('/restrito/compet_lista')

    if c.compet_sex == 'F':
        messages.success(request,'Competidora "{}" foi excluída.'.format(c))
    else:
        messages.success(request,'Competidor "{}" foi excluído.'.format(c))
    logger.info("compet_deleta, user={} compet={}".format(request.user,c))
    return redirect('/restrito/compet_lista')


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_deleta(request,compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    try:
        c = Compet.objects.get(compet_id=compet_id,compet_school=school)
    except:
        messages.error(request, 'Exclusão falhou, competidora não existe.')
        return redirect('/restrito/compet_feminina_lista')

    if not compet_feminina_remove(request, c, school):
        logger.info("compet_feminina_deleta falhou, user={} compet={}".format(request.user,c))
        return redirect('/restrito/compet_feminina_lista')

    messages.success(request,'Competidora "{}" foi excluída da CF-OBI.'.format(c))
    logger.info("compet_feminina_deleta, user={} compet={}".format(request.user,c))
    return redirect('/restrito/compet_feminina_lista')


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_edita(request,compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    try:
        c = Compet.objects.get(compet_id=compet_id,compet_school_id=school_id)
    except:
        messages.error(request, 'Competidor(a) não existente.')
        return redirect('/restrito/compet_lista')
    try:
        c_extra = CompetExtra.objects.get(id=c.compet_id)
    except:
        c_extra = CompetExtra()

    instance = {
        'compet_id_full': format_compet_id(c.compet_id),
        'compet_id': c.compet_id,
        'compet_name': c.compet_name,
        'compet_type': c.compet_type,
        'compet_year': c.compet_year,
        'compet_class': c.compet_class,
        'compet_email': c.compet_email,
        'compet_email_cur': c.compet_email,
        'compet_birth_date': c.compet_birth_date,
        'compet_sex': c.compet_sex,
        'compet_mother_name': c_extra.compet_mother_name,
        'compet_cpf': c_extra.compet_cpf,
        'compet_nis': c_extra.compet_nis,
    }
    if request.method == 'POST':
        logger.info("compet_edita, compet_edita start, user={} compet_id={}".format(request.user,compet_id))
        form = CompetEditaForm(request.POST, request=request)
        if form.is_valid():
            f = form.cleaned_data
            if 'delete' in request.POST:
                # confirm before deleting
                compet_deleta(request,c.compet_id)
            else:
                c.compet_name = f['compet_name']
                old_compet_type = c.compet_type
                c.compet_type = int(f['compet_type'])
                c.compet_year = f['compet_year']
                c.compet_class = f['compet_class']
                c.compet_birth_date = f['compet_birth_date']
                c.compet_sex = f['compet_sex']
                cur_compet_email = c.compet_email
                c.compet_email = f['compet_email']

                if c.compet_email != cur_compet_email:
                    c.user.email = c.compet_email
                    c.user.save()
                    logger.info("compet_edita send email, user={} compet_id={} compet={}".format(request.user,c.compet_id,c))
                    compet_send_email(request,c,school,reason="atualizar sua inscrição",queue=True)
                c.save()

                try:
                    c_extra = CompetExtra.objects.get(id=c.compet_id)
                except:
                    c_extra = CompetExtra(id=c.compet_id)

                if f['compet_mother_name']:
                    c_extra.compet_mother_name = f['compet_mother_name']
                else:
                    c_extra.compet_mother_name = ''
                if f['compet_cpf']:
                    c_extra.compet_cpf = f['compet_cpf']
                else:
                    c_extra.compet_cpf = ''
                if f['compet_nis']:
                    c_extra.compet_nis = f['compet_nis']
                else:
                    c_extra.compet_nis = ''
                c_extra.save()

                # if new compet_type is prog, need to add user to CMS db
                if c.compet_type in LEVEL_PROG and old_compet_type not in LEVEL_PROG:
                    compet_cms_add_user(request, c, c.compet_type)
                # if new compet_type is not prog, need to remove user from CMS db
                if c.compet_type not in LEVEL_PROG and old_compet_type in LEVEL_PROG:
                    compet_cms_remove_user(request, c.compet_id_full, old_compet_type)
                # if new compet_type is prog, but different level, must remove and recreate user
                if c.compet_type in LEVEL_PROG and old_compet_type in LEVEL_PROG and c.compet_type != old_compet_type:
                    compet_cms_remove_user(request, c.compet_id_full, old_compet_type)
                    compet_cms_add_user(request, c, c.compet_type)

                compet_authorize_default_exams(request,c,school)
                logger.info("compet_edita finish, user={} compet_id={} compet={}".format(request.user,c.compet_id,c))
                messages.success(request, 'Dados do(a) competidor(a) foram atualizados.')
            return redirect('/restrito/compet_lista')
    else:
        form = CompetEditaForm(initial=instance, request=request)
    return render(request, 'restrito/compet_edita.html', {'form': form, 'pagetitle': 'Edita Competidor'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_edita(request, compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id

    try:
        c = Compet.objects.get(compet_id=compet_id, compet_school_id=school_id)
    except:
        messages.error(request, 'Competidora não existente.')
        return redirect('/restrito/compet_feminina_lista')

    try:
        c_extra = CompetExtra.objects.get(id=c.compet_id)
    except:
        c_extra = CompetExtra(id=c.compet_id)

    try:
        c_cfobi = CompetCfObi.objects.get(compet=c)
    except:
        c_cfobi = CompetCfObi(compet=c)

    instance = {
        'compet_id_full': format_compet_id(c.compet_id),
        'compet_id': c.compet_id,
        'compet_name': c.compet_name,
        'compet_type': c_cfobi.compet_type,
        'compet_year': c.compet_year,
        'compet_class': c.compet_class,
        'compet_email': c.compet_email,
        'compet_email_cur': c.compet_email,
        'compet_birth_date': c.compet_birth_date,
        'compet_sex': c.compet_sex,
        'compet_mother_name': c_extra.compet_mother_name,
        'compet_cpf': c_extra.compet_cpf,
        'compet_nis': c_extra.compet_nis,
    }

    if request.method == 'POST':
        logger.info("compet_feminina_edita, compet_edita start, user={} compet_id={}".format(request.user, compet_id))
        form = CompetFemininaEditaForm(request.POST, request=request)
        if form.is_valid():
            f = form.cleaned_data
            if 'delete' in request.POST:
                # confirm before deleting
                compet_feminina_deleta(request,c.compet_id)
            else:
                c.compet_name = f['compet_name']
                old_compet_type = c_cfobi.compet_type
                c_cfobi.compet_type = int(f['compet_type'])
                c.compet_year = f['compet_year']
                c.compet_class = f['compet_class']
                c.compet_birth_date = f['compet_birth_date']
                c.compet_sex = f['compet_sex']
                cur_compet_email = c.compet_email
                c.compet_email = f['compet_email']

                if c.compet_email != cur_compet_email:
                    c.user.email = c.compet_email
                    c.user.save()
                    logger.info("compet_feminina_edita send email, user={} compet_id={} compet={}".format(request.user, c.compet_id, c))
                    compet_send_email(request, c, school, reason="atualizar sua inscrição", queue=True)
                c.save()
                c_cfobi.save()

                if f['compet_mother_name']:
                    c_extra.compet_mother_name = f['compet_mother_name']
                else:
                    c_extra.compet_mother_name = ''
                if f['compet_cpf']:
                    c_extra.compet_cpf = f['compet_cpf']
                else:
                    c_extra.compet_cpf = ''
                if f['compet_nis']:
                    c_extra.compet_nis = f['compet_nis']
                else:
                    c_extra.compet_nis = ''
                c_extra.save()

                # if new compet_type changed, must remove and recreate CMS user
                if c_cfobi.compet_type != old_compet_type:
                    compet_cms_remove_user(request, c.compet_id_full, old_compet_type, DEFAULT_CONTEST_ID_CFOBI)
                    compet_cms_add_user(request, c, c_cfobi.compet_type, DEFAULT_CONTEST_ID_CFOBI)

                compet_feminina_authorize_default_exams(request, c_cfobi, school)
                logger.info("compet_feminina_edita finish, user={} compet_id={} compet={}".format(request.user, c.compet_id, c))
                messages.success(request, 'Dados da competidora foram atualizados.')
            return redirect('/restrito/compet_feminina_lista')
    else:
        form = CompetFemininaEditaForm(initial=instance, request=request)

    return render(request, 'restrito/compet_feminina_edita.html', {'form': form, 'pagetitle': 'Edita Competidora CF-OBI'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def escola_edita(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    instance = {
        'school_name': school.school_name,
        'school_type': school.school_type,
        'school_inep_code': school.school_inep_code,
        'school_phone': school.school_phone,
        'school_zip': school.school_zip,
        'school_address': school.school_address,
        'school_address_number': school.school_address_number,
        'school_address_complement': school.school_address_complement,
        'school_address_district': school.school_address_district,
        'school_city': school.school_city,
        'school_state': school.school_state,
        'school_deleg_name': school.school_deleg_name,
        'school_deleg_phone': school.school_deleg_phone,
        'school_deleg_email': school.school_deleg_email,
        'school_deleg_email_conf': school.school_deleg_email,
        'school_address_building': school.school_address_building,
        'school_address_map': school.school_address_map,
        'school_address_other': school.school_address_other,
    }

    if request.method == 'POST':
        if school.school_type in [REGULAR_PUBLIC,REGULAR_PRIVATE]:
            form = EscolaEditaInepForm(request.POST)
        else:
            form = EscolaEditaForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            school.school_name = f['school_name']
            school.school_inep_code = int(f['school_inep_code'])
            school.school_type = int(f['school_type'])
            school.school_phone = f['school_phone']
            school.school_zip = f['school_zip']
            school.school_address = f['school_address']
            school.school_address_number = f['school_address_number']
            school.school_address_complement = f['school_address_complement']
            school.school_address_district = f['school_address_district']
            school.school_city = f['school_city']
            school.school_state = f['school_state']
            school.school_address_building = f['school_address_building']
            school.school_address_map = f['school_address_map']
            school.school_address_other = f['school_address_other']
            if school.school_type not in [REGULAR_PUBLIC,REGULAR_PRIVATE]:
                school.school_inep_code = 0
            school.save()
            logger.info("compet_edita, user={} school={}".format(request.user,school))
            messages.success(request, 'Dados da Escola foram atualizados.')
            return redirect('/restrito')
    else:
        if school.school_type in [REGULAR_PUBLIC,REGULAR_PRIVATE]:
            form = EscolaEditaInepForm(initial=instance)
        else:
            form = EscolaEditaForm(initial=instance)
    return render(request, 'restrito/escola_edita.html', {'form': form, 'pagetitle': 'Edita Escola'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def coord_edita(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    instance = {
        'school_deleg_name': school.school_deleg_name,
        'school_deleg_phone': school.school_deleg_phone,
        'school_deleg_email': school.school_deleg_email,
        'school_deleg_email_conf': school.school_deleg_email,
        'school_deleg_username': school.school_deleg_username,
    }

    if request.method == 'POST':
        form = CoordEditaForm(request.POST,user=request.user)
        if form.is_valid():
            f = form.cleaned_data
            school.school_deleg_name = f['school_deleg_name']
            school.school_deleg_phone = f['school_deleg_phone']
            school.school_deleg_email = f['school_deleg_email']
            request.user.last_name = school.school_deleg_name
            request.user.email = school.school_deleg_email
            request.user.save()
            school.save()
            logger.info("coord_edita, user={} school={}".format(request.user,school))
            messages.success(request, 'Dados de Coordenador foram atualizados.')
            # if needed, change password for user
            try:
                new_password = f['school_deleg_password']
            except:
                new_password = ""
            if new_password:
                request.user.set_password(new_password)
                request.user.save()
                logger.info("coord_edita change password, user={} school={}".format(request.user,school))
            return redirect('/restrito')
    else:
        form = CoordEditaForm(initial=instance,user=request.user)
    return render(request, 'restrito/coord_edita.html', {'form': form, 'pagetitle': 'Edita Coordenador'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def colab_lista(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    colabs = Colab.objects.filter(colab_school_id=school_id).order_by('colab_name')
    total = len(colabs)

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(colabs), page)
    paginator = Paginator(colabs, page_size)
    try:
        partics = paginator.page(page)
    except PageNotAnInteger:
        partics = paginator.page(1)
    except EmptyPage:
        partics = paginator.page(paginator.num_pages)

    return render(request, 'restrito/colab_lista.html', {'items': partics, 'total':total, 'pagetitle':'Lista Colaboradores'})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def colab_inscreve(request):
    if request.method == 'POST':
        form = ColabInscreveForm(request.POST, request=request)
        if form.is_valid():
            colab_school = request.user.deleg.deleg_school
            f = form.cleaned_data
            c = Colab(colab_name=f['colab_name'],
                       colab_email=f['colab_email'],
                       colab_sex=f['colab_sex'],
                       colab_school=colab_school)
            c.colab_admin = f['colab_admin']
            c.colab_admin_full = f['colab_admin_full']
            if c.colab_admin_full == 'S':
                c.colab_admin = 'S'

            # if is admin, create user
            if c.colab_admin == 'S' or c.colab_admin_full == 'S':
                # must have email
                password = make_password()
                user = User.objects.create_user(c.colab_email, c.colab_email, password)
                user.last_name = c.colab_name
                user.is_staff = False
                if c.colab_admin_full == 'S':
                    group_name = 'colab_full'
                else:
                    group_name = 'colab'
                g = Group.objects.get(name=group_name)
                g.user_set.add(user)
                user.save()
                c.user = user
            else:
                password = ''
            c.save()
            if c.colab_email:
                #print("send email")
                send_email_colab_registered(request,c,colab_school,password=password,reason="fazer seu cadastro",group_name=group_name,queue=True)
                try:
                    send_email_colab_registered(request,c,colab_school,password=password,reason="fazer seu cadastro",group_name=group_name,queue=True)
                except:
                    messages.error(request, 'Colaborador não foi inscrito pois o envio de email falhou; corrija o endereço de email informado" (email: {})'.format(c.colab_email))
                    if c.user:
                        c.user = None
                        c.colab_email = None
                        try:
                            c.user.delete()
                        except:
                            pass
                        c.delete
                    return redirect('/restrito')
            else:
                c.save()
            logger.info("colab_inscreve, user={} colab={}".format(request.user,c))
            if c.colab_sex == 'F':
                messages.success(request, 'Colaboradora "{}" foi inscrita.'.format(c))
            else:
                messages.success(request, 'Colaborador "{}" foi inscrito.'.format(c))
            if 'save_and_continue' in request.POST:
                form = ColabInscreveForm()
            else:
                return redirect('/restrito')
    else:
        form = ColabInscreveForm()
    return render(request, 'restrito/colab_inscreve.html', {'form': form, 'pagetitle': 'Inscreve Novo Colaborador'})


@user_passes_test(in_coord_group, login_url='/contas/login/')
def colab_remove(request,c):
    # if there is a user, remove it
    if c.user:
        c.user.delete()
        c.user = None
    try:
        c.delete()
    except:
        return False
    return True


@user_passes_test(in_coord_group, login_url='/contas/login/')
def colab_deleta_lote(request):
    # only coord can delete colab
    try:
        school = request.user.deleg.deleg_school
    except:
        logger.info("colab_deleta_lote falhou, usuário não autorizado, user={}".format(request.user))
        messages.error(request,'Apenas coordenadores podem excluir colaboradores.')
        return redirect('/restrito/compet_lista')

    delete = []
    if request.method == 'POST':
        delete = request.POST.getlist('choices_set')
        deleted = 0
        for d in delete:
            colab_id = int(d)
            try:
                c = Colab.objects.get(colab_id=colab_id,colab_school=school)
            except:
                logger.info("colab_remove falhou, colaborador não existe, user={} colab_id={}".format(request.user,colab_id))
                continue
            if colab_remove(request, c):
                deleted += 1

    if deleted == 1:
        messages.success(request,f'Colaborador {c.colab_name} foi excluído.')
    else:
        messages.success(request,f'{deleted} competidores foram excluídos.')
    logger.info("colab_deleta_lote, user={} deleted {}".format(request.user,delete))
    return redirect('/restrito/colab_lista')


@user_passes_test(in_coord_group, login_url='/contas/login/')
def colab_deleta(request,colab_id):
    # only coord can delete colab
    try:
        school_id = request.user.deleg.deleg_school
    except:
        logger.info("colab_deleta_lote falhou, usuário não autorizado, user={}".format(request.user))
        messages.error(request,'Apenas coordenadores podem excluir colaboradores.')
        return redirect('/restrito/compet_lista')
    try:
        c = Colab.objects.get(colab_id=colab_id,colab_school_id=school_id)
    except:
        messages.error(request, 'Exclusão falhou, colaborador(a) não existe.')
        return redirect('/restrito/colab_lista')
    if colab_remove(request, c):
        if c.colab_sex == 'F':
            messages.success(request,'Colaboradora "{}" foi excluída.'.format(c))
        else:
            messages.success(request,'Colaborador "{}" foi excluído.'.format(c))
    else:
        messages.error(request, 'Exclusão falhou.')
    return redirect('/restrito/colab_lista')


@user_passes_test(in_coord_group, login_url='/contas/login/')
def colab_edita(request,colab_id):
    school_id = request.user.deleg.deleg_school.school_id
    try:
        c = Colab.objects.get(colab_id=colab_id,colab_school_id=school_id)
    except:
        messages.error(request, 'Colaborador(a) não existente.')
        return redirect('/restrito/colab_lista')
    instance = {'colab_id': c.colab_id,
                'colab_name': c.colab_name,
                'colab_email': c.colab_email,
                'colab_email_cur': c.colab_email,
                'colab_sex': c.colab_sex,
                'colab_admin': c.colab_admin,
                'colab_admin_full': c.colab_admin_full,
    }
    if request.method == 'POST':
        form = ColabEditaForm(request.POST, request=request)
        if form.is_valid():
            colab_school = request.user.deleg.deleg_school
            f = form.cleaned_data
            if 'delete' in request.POST:
                # confirm before deleting
                colab_deleta(request,colab_id)
            else:
                c.colab_name = f['colab_name']
                c.colab_email = f['colab_email']
                c.colab_sex = f['colab_sex']
                c.colab_admin = f['colab_admin']
                c.colab_admin_full = f['colab_admin_full']
                if c.colab_admin_full == 'S':
                    c.colab_admin = 'S'
                # if there was a user and email changed, delete
                if c.colab_email != f['colab_email_cur']:
                    if c.user:
                        # will delete colab also!
                        c.user.delete()
                        c.user = None
                # if there is a user, and he/she is no more admin, remove it
                if c.colab_admin == 'N':
                    if c.user:
                        c.user.delete()
                        c.user = None
                # if colab is admin, create user if not already created
                elif c.colab_admin == 'S' or c.colab_admin_full == 'S':
                    if c.user:
                        # remove both groups and insert the correct group
                        g = Group.objects.get(name='colab')
                        g.user_set.remove(c.user)
                        g = Group.objects.get(name='colab_full')
                        g.user_set.remove(c.user)
                        if c.colab_admin_full == 'S':
                            group_name = 'colab_full'
                        else:
                            group_name = 'colab'
                        g = Group.objects.get(name=group_name)
                        g.user_set.add(c.user)
                        c.user.save()
                    # no user, create one
                    else:
                        password = make_password()
                        user = User.objects.create_user(c.colab_email, c.colab_email, password)
                        user.last_name = c.colab_name
                        user.is_staff = False
                        if c.colab_admin_full == 'S':
                            group_name = 'colab_full'
                        else:
                            group_name = 'colab'
                        g = Group.objects.get(name=group_name)
                        g.user_set.add(user)
                        user.save()
                        c.user = user

                        colab_school = request.user.deleg.deleg_school
                        send_email_colab_registered(request,c,colab_school,password=password,reason="editar seu cadastro",group_name=group_name,queue=True)
                c.save()
                logger.info("colab_edita, user={} colab={}".format(request.user,c))
                if c.colab_sex == 'F':
                    messages.success(request, 'Dados da colaboradora "{}" foram atualizados.'.format(c))
                else:
                    messages.success(request, 'Dados do colaborador "{}" foram atualizados.'.format(c))
            return redirect('/restrito/colab_lista')
    else:
        form = ColabEditaForm(initial=instance, request=request)
    return render(request, 'restrito/colab_edita.html', {'form': form, 'pagetitle': 'Edita Colaborador'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_pre_inscricao_lista(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compets = CompetAutoRegister.objects.filter(compet_school_id=school_id,compet_status="new")
    total = len(compets)
    if request.method == 'POST':
        form = CompetPreRegFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_list_name = f['compet_name']
            compet_list_type = f['compet_type']
            request.session['compet_list_name'] = compet_list_name
            request.session['compet_list_type'] = compet_list_type
    else:
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        instance = {'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetPreRegFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=LEVEL_INI)
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=LEVEL_PROG)
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    compets = compets.order_by('compet_name')

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    paginator = Paginator(compets, page_size)
    try:
        partics = paginator.page(page)
    except PageNotAnInteger:
        partics = paginator.page(1)
    except EmptyPage:
        partics = paginator.page(paginator.num_pages)

    return render(request, 'restrito/compet_pre_inscricao_lista.html', {'school_id': school_id,'items': partics, 'total':total, 'pagetitle':'Lista Competidores com Pré-Inscrição', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_pre_inscricao_lista(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk
    compets = CompetAutoRegister.objects.filter(compet_school_id=school_id,compet_status="new")
    total = len(compets)
    if request.method == 'POST':
        form = CompetPreRegFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_list_name = f['compet_name']
            compet_list_type = f['compet_type']
            request.session['compet_list_name'] = compet_list_name
            request.session['compet_list_type'] = compet_list_type
    else:
        try:
            compet_list_name = request.session['compet_list_name']
        except:
            compet_list_name = ''
        try:
            compet_list_type = request.session['compet_list_type']
        except:
            compet_list_type = None
        instance = {'compet_name':compet_list_name, 'compet_type':compet_list_type}
        form = CompetPreRegFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=LEVEL_INI)
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=LEVEL_PROG)
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)

    compets = compets.order_by('compet_name')

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(compets), page)
    paginator = Paginator(compets, page_size)
    try:
        partics = paginator.page(page)
    except PageNotAnInteger:
        partics = paginator.page(1)
    except EmptyPage:
        partics = paginator.page(paginator.num_pages)

    return render(request, 'restrito/compet_pre_inscricao_lista.html', {'school_id': school_id,'items': partics, 'total':total, 'pagetitle':'Lista Competidores com Pré-Inscrição', 'form': form})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_valida(request,id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.pk
    try:
        cpre = CompetAutoRegister.objects.get(id=id,compet_school_id=school_id,compet_status='new')
    except:
        messages.error(request, 'Competidor(a) não existente.')
        #compet_pre_inscricao_lista(request)
        return redirect('/restrito/compet_pre_inscricao_lista')

    instance = {
                'id': id,
                'compet_name': cpre.compet_name,
                'compet_type': cpre.compet_type,
                'compet_year': cpre.compet_year,
                'compet_class': cpre.compet_class,
                'compet_email': cpre.compet_email,
                'compet_email_cur': cpre.compet_email,
                'compet_birth_date': cpre.compet_birth_date,
                'compet_sex': cpre.compet_sex,
    }
    try:
        compet_exists = Compet.objects.filter(compet_name__iexact=cpre.compet_name,compet_school_id=school_id) # .exclude(id=id)
        c = compet_exists[0]
        registered = {
                'compet_id': c.compet_id,
                'compet_name': c.compet_name,
                'compet_type': c.compet_type,
                'compet_year': c.compet_year,
                'compet_class': c.compet_class,
                'compet_email': c.compet_email,
                'compet_birth_date': c.compet_birth_date,
                'compet_sex': c.compet_sex,
        }
    except:
        registered = None

    if request.method == 'POST':
        form = CompetValidaForm(request.POST, request=request)
        if form.is_valid():
            f = form.cleaned_data
            if 'delete' in request.POST:
                cpre.compet_status = 'excluded'
                cpre.save()
                if cpre.compet_sex == 'F':
                    messages.success(request, 'Pré-competidora "{}" excluída.'.format(cpre.compet_name))
                else:
                    messages.success(request, 'Pré-competidor "{}" excluído.'.format(cpre.compet_name))
                logger.info("compet_valida excluded: user={} compet={}".format(request.user,cpre))
            elif 'update' in request.POST:
                # update existing
                # name cannot be changed by form, informed by compet
                c.compet_name = cpre.compet_name
                # use compet_type informed by compet, but keep old compet_type
                old_compet_type = c.compet_type
                c.compet_type = int(f['compet_type'])
                c.compet_year = f['compet_year']
                c.compet_class = f['compet_class']
                c.compet_birth_date = f['compet_birth_date']
                c.compet_sex = f['compet_sex']
                #cur_compet_email = c.compet_email
                c.compet_email = f['compet_email']
                c.save()
                # don't need to change the user, username is registration number not email
                #if c.compet_email != cur_compet_email:
                #    # must update user
                #    remove_compet_user(request,c,school)
                #    if c.compet_email:
                #        create_compet_user(request,c,school,reason='atualizar sua inscrição')
                cpre.compet_status = 'updated'
                cpre.save()

                # if compet_type is prog, need to add user to CMS db
                if c.compet_type in LEVEL_PROG and old_compet_type not in LEVEL_PROG:
                    compet_cms_add_user(request, c, c.compet_type)
                # if compet_type is not prog, need to remove user from CMS db
                if c.compet_type not in LEVEL_PROG and old_compet_type in LEVEL_PROG:
                    compet_cms_remove_user(request, c.compet_id_full, old_compet_type)

                logger.info("compet_valida updated: user={} compet={}".format(request.user,compet_exists))
                if c.compet_sex == 'F':
                    messages.success(request, 'Dados da competidora "{}" foram atualizados.'.format(c.compet_name))
                else:
                    messages.success(request, 'Dados do competidor "{}" foram atualizados.'.format(c.compet_name))
            else:
                cnew = Compet(compet_name=f['compet_name'], compet_type=int(f['compet_type']),
                       compet_year=f['compet_year'], compet_class=f['compet_class'], compet_email=f['compet_email'],
                       compet_birth_date=f['compet_birth_date'], compet_sex=f['compet_sex'],
                              compet_school=school)
                cnew.save()
                cnew.compet_id_full = format_compet_id(cnew.compet_id)
                cnew.save()
                compet_create_user(request,cnew,cnew.compet_type,school)
                compet_send_email(request,cnew,school,reason="validar sua inscrição",queue=True)
                compet_authorize_default_exams(request,cnew,school)
                cpre.compet_status = 'validated'
                cpre.save()
                logger.info("compet_valida, user={} compet={}".format(request.user,cnew))
                if cnew.compet_sex == 'F':
                    messages.success(request, 'Competidora "{}" foi validada.'.format(cnew.compet_name))
                else:
                    messages.success(request, 'Competidor "{}" foi validado.'.format(cnew.compet_name))
            return redirect('/restrito/compet_pre_inscricao_lista')
    else:
        form = CompetValidaForm(initial=instance, request=request)
    return render(request, 'restrito/compet_valida.html', {'form': form, 'pagetitle': 'Valida Pré-inscrição de Competidor','registered': registered, 'instance':instance})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_aut_prova_online(request, exam_descr, turn):
    exam_title = EXAMS[exam_descr]['exam_title']
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    compets = select_turn_compets(request,exam_descr,turn,school)
    total = len(compets)
    if request.method == 'POST':
        form = CompetFiltroForm(request.POST)
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
        form = CompetFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=LEVEL_INI)
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=LEVEL_PROG)
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)
    compets = compets.order_by(compet_list_order)
    # now check existing authorizations for the exam
    if exam_descr == 'provaf1':
        authorized = ExamFase1.objects.filter(school=school).only('compet_id')
    else:
        authorized = None

    total_aut = 0
    if authorized:
        for c in compets:
            c.authorized = authorized.filter(compet_id=c.compet_id).exists()
            if c.authorized:
                total_aut += 1

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

    return render(request, 'restrito/compet_lista_aut_prova_online.html', {'items': partics, 'total':total, 'total_aut':total_aut, 'pagetitle':'Autoriza {} Online'.format(exam_title), 'form': form, 'exam_descr': exam_descr, 'turn':turn})


def select_turn_compets(request,exam_descr,turn,school):
    if exam_descr == 'testef1':
        compets = Compet.objects.filter(compet_school_id=school.school_id)
    elif exam_descr == 'provaf1':
        compets = Compet.objects.filter(compet_school_id=school.school_id)
    elif exam_descr == 'provaf2':
        compets = Compet.objects.filter(compet_school_id=school.school_id,compet_classif_fase1=True)
    elif exam_descr == 'provaf2b':
        compets = Compet.objects.filter(compet_school_id=school.school_id,compet_classif_fase1=True,compet_type__in=LEVEL_PROG)
    elif exam_descr == 'provaf3':
        compets = Compet.objects.filter(compet_school_id=school.school_id,compet_classif_fase2=True)
    else:
        #if school.school_turn_phase1_ini != turn and school.school_turn_phase1_prog != turn:
        #    msg = 'A escola optou pelo Turno {}'.format(school.school_turn_phase1_prog)
        #    return erro(request, msg)

        # query set cannot use union, the filter in page will try to filter the queryset, which is not allowed
        # so, construct a unique queryset
        if school.school_turn_phase1_ini == turn:
            if school.school_turn_phase1_prog == turn:
                compets = Compet.objects.filter(compet_school_id=school.school_id)
            else:
                compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=LEVEL_INI)
        elif school.school_turn_phase1_prog == turn:
            compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=LEVEL_PROG)
        else:
            compets = Compet.objects.filter(compet_id=-1) # empty queryset
    return compets


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_lista_status_prova_online(request, exam_descr, turn):
    if turn == 'B':
        exam_descr = exam_descr+'b'
    exam_title = EXAMS[exam_descr]['exam_title']
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    compets = select_turn_compets(request,exam_descr,turn,school)
    total = len(compets)
    if request.method == 'POST':
        form = CompetFiltroForm(request.POST)
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
            # could come from filter with compet points
            if compet_list_order == 'compet_points':
                compet_list_order = 'compet_name'
                request.session['compet_list_order'] = 'compet_name'
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
        form = CompetFiltroForm(initial=instance)

    if compet_list_type:
        if compet_list_type == 'I':
            compets = compets.filter(compet_type__in=LEVEL_INI)
        elif compet_list_type == 'P':
            compets = compets.filter(compet_type__in=LEVEL_PROG)
        else:
            request.session['compet_list_type'] = int(compet_list_type)
            compets = compets.filter(compet_type=compet_list_type)
    else:
        try:
            del(request.session['compet_list_type'])
        except:
            pass

    tks = compet_list_name.split()
    for tk in tks:
        compets = compets.filter(compet_name__icontains = tk)
    compets = compets.order_by(compet_list_order)
    # now check existing authorizations for the exam
    total_aut = 0
    total_started = 0
    total_finished = 0
    exam_object = EXAMS[exam_descr]['exam_object']
    for c in compets:
        try:
            c.authorized = exam_object.objects.filter(compet_id=c.compet_id).exists()
        except:
            c.authorized = False

        authorized,dummy,status,msg = check_exam_status(exam_descr,c)
        if status == 'not authorized':
            c.started = False
            c.finished = False
        elif status == 'running':
            c.started = True
            c.finished = False
            total_aut += 1
            total_started += 1
        elif status == 'done':
            c.started = True
            c.finished = True
            total_aut += 1
            total_started += 1
            total_finished += 1
        else:
            c.started = False
            c.finished = False
            total_aut += 1


    pagetitle = 'Status da {}'.format(exam_title)

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

    return render(request, 'restrito/compet_lista_status_prova_online.html',
                  {'items': partics, 'total':total, 'total_aut':total_aut,
                   'total_started':total_started, 'total_finished':total_finished,
                   'pagetitle': pagetitle, 'form': form, 'exam_descr': exam_descr, 'turn':turn})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_aut_prova_online(request, exam_descr, turn):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    compets = select_turn_compets(request,exam_descr,turn,school)
    # let all compets to be examined
    # but not deauthorized
    # compets = compets.filter(compet_type__in=LEVEL_INI)
    if exam_descr == 'provaf1':
        exam = ExamFase1
    else:
        exam = None
        messages.error(request, 'Ocorreu um erro, prova não reconhecida.'.format(c))
        return redirect('/restrito/compet_lista_aut_prova_online/{}/{}'.format(exam_descr,turn))
    exam_compets = exam.objects.filter(school=school)
    if request.method == 'POST':
        authorize = request.POST.getlist('choices_set')
        deauthorize = request.POST.getlist('choices_unset')
        changed = False
        for a in authorize:
            compet_id = int(a)
            try:
                c = compets.get(compet_id=compet_id)
                try:
                    # already authorized?
                    ex = exam_compets.get(compet=c,school=school)
                except:
                    # not authorized, then authorize
                    if c.user:
                        ex = exam(compet=c,school=school)
                        ex.save()
                        changed = True
                    else:
                        messages.error(request, 'Autorização falhou para {}, não tem usuário criado.'.format(c))
                        logger.info("Autorização para {} falhou, user={} compet={}".format(exam, request.user, c))
            except:
                print('could not find {} in school compets, disregarding'.format(compet_id))

        for d in deauthorize:
            compet_id=int(d)
            try:
                c = compets.get(compet_id=compet_id)
                if c.compet_type in LEVEL_PROG:
                    # programming contestants must do the exam online, cannot deauthorize
                    continue
                try:
                    ex = exam_compets.get(compet=c,school=school)
                    if not ex.time_start:
                        ex.delete()
                        changed = True
                    else:
                        messages.error(request, 'Remoção de autorização falhou para {}, prova já realizada online.'.format(c))
                        logger.info("Remoção de autorização para {} falhou, prova já realizada, user={} compet={}".format(exam, request.user, c))
                except:
                    pass
            except:
                pass
                #print('could not find {} in school compets, disregarding'.format(c))

        if changed:
            messages.success(request, 'Autorizações foram atualizadas.')
            logger.info("Autorizações atualizadas, user={} compet={}".format(exam, request.user,c))

    return redirect('/restrito/compet_lista_aut_prova_online/{}/{}'.format(exam_descr,turn))

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def partic_lista_status_semana(request):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    participants = Week.objects.filter(school=school)
    total = len(participants)
    if request.method == 'POST':
        form = ParticSemanaFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            partic_list_order = f['partic_order']
            partic_list_name = f['partic_name']
            partic_list_type = f['partic_type']
            request.session['partic_list_name'] = partic_list_name
            request.session['partic_list_order'] = partic_list_order
            request.session['partic_list_type'] = partic_list_type
    else:
        try:
            partic_list_order = request.session['partic_list_order']
        except:
            partic_list_order = 'compet_name'
        try:
            partic_list_name = request.session['partic_list_name']
        except:
            partic_list_name = ''
        try:
            partic_list_type = request.session['partic_list_type']
        except:
            partic_list_type = None

        instance = {'compet_order':partic_list_order, 'compet_name':partic_list_name, 'compet_type':partic_list_type}
        form = CompetFiltroForm(initial=instance)

    if partic_list_type:
        if partic_list_type == 'I':
            participants = participants.filter(compet__compet_type__in=LEVEL_INI)
        elif partic_list_type == 'P':
            participants = participants.filter(compet__compet_type__in=LEVEL_PROG)
        else:
            request.session['partic_list_type'] = int(partic_list_type)
            participants = participants.filter(compet__compet_type=partic_list_type)

    #tks = partic_list_name.split()
    #for tk in tks:
    #    participants = participants.filter(compet__compet_name__icontains = tk)

    participants = participants.order_by('compet__compet_name')

    # check confirmation of interest
    # if exam_descr == 'provaf1':
    #     authorized = ExamFase1.objects.filter(school=school).only('compet_id')
    # else:
    #     authorized = None

    # total_aut = 0
    # if authorized:
    #     for c in compets:
    #         c.authorized = authorized.filter(compet_id=c.compet_id).exists()
    #         if c.authorized:
    #             total_aut += 1

    page = request.GET.get('page', 1)
    page_size = calculate_page_size(len(participants), page)
    try:
        paginator = Paginator(participants, page_size)
        try:
            partics = paginator.page(page)
        except PageNotAnInteger:
            partics = paginator.page(1)
        except EmptyPage:
            partics = paginator.page(paginator.num_pages)
    except:
        partics = []

    return render(request, 'restrito/partic_lista_status_semana.html', {'items': partics, 'total':total, 'form': form})


def dowrite_card(label, width, height, data):
    #data = [['Num. Inscr.','Nome', 'Modalidade','Senha','Escola'],]
    i = 0
    label.add(shapes.String(15, height-25-i*15, data[1],
                                fontName="Helvetica-Bold", fontSize=11))
    i += 1
    label.add(shapes.String(15, height-25-i*15, 'Modalidade: '+data[2],
                                fontName="Helvetica", fontSize=11))
    i += 1
    label.add(shapes.String(15, height-35-i*15, 'Nome de usuário: '+data[0],
                                fontName="Helvetica", fontSize=11))
    i += 1
    label.add(shapes.String(15, height-35-i*15, 'Senha: '+data[3],
                                fontName="Helvetica", fontSize=11))
    i += 1
    label.add(shapes.String(15, height-55-i*15, 'Escola: '+data[4],
                                fontName="Helvetica", fontSize=8))
    i += 1


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_cartoes_senhas(request):
    if request.method == 'POST':
        form = CompetSenhasFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_type = f['compet_type']
            compet_order = f['compet_order']

            return compet_cartoes_senhas_exec(request, compet_type, compet_order)
    else:
        form = CompetSenhasFiltroForm()
    return render(request, 'restrito/compet_cartoes_senhas.html', {'form': form, 'pagetitle': 'Gera cartões com senhas'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_cartoes_senhas(request):
    try:
        school_id = request.user.deleg.deleg_school.pk
        usertype = 'coord'
    except:
        school_id = request.user.colab.colab_school.pk
        usertype = 'colab'

    s = School.objects.get(pk=school_id)
    school_name = s.school_name
    if usertype == 'coord':
        name = s.school_deleg_name
    else:
        colab = Colab.objects.get(user_id=request.user.id)
        name = colab.colab_name

    if request.method == 'POST':
        form = CompetFemininaSenhasFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_type = f['compet_type']
            compet_order = f['compet_order']

            return compet_cartoes_senhas_exec(request, compet_type, compet_order, is_cms=False, is_cf=True)
    else:
        form = CompetFemininaSenhasFiltroForm()
    
    return render(request, 'restrito/compet_cartoes_senhas_cms.html', {'form': form, 'pagetitle': 'Gera cartões com senhas para o CMS', 'school_name': school_name, 'name': name})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_feminina_cartoes_senhas_cms(request):

    #messages.error(request, 'Senhas ainda não disponíveis, serão disponibilizadas no dia anterior à prova.')
    #return redirect('/restrito/')
    
    try:
        school_id = request.user.deleg.deleg_school.pk
        usertype = 'coord'
    except:
        school_id = request.user.colab.colab_school.pk
        usertype = 'colab'

    s = School.objects.get(pk=school_id)
    school_name = s.school_name
    if usertype == 'coord':
        name = s.school_deleg_name
    else:
        colab = Colab.objects.get(user_id=request.user.id)
        name = colab.colab_name

    if request.method == 'POST':
        form = CompetFemininaSenhasFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_type = f['compet_type']
            compet_order = f['compet_order']

            return compet_cartoes_senhas_exec(request, compet_type, compet_order, is_cms=True, is_cf=True)
    else:
        form = CompetFemininaSenhasFiltroForm()
    
    return render(request, 'restrito/compet_cartoes_senhas_cms.html', {'form': form, 'pagetitle': 'Gera cartões com senhas para o CMS', 'school_name': school_name, 'name': name})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_cartoes_senhas_cms(request):
    #messages.error(request, 'Senhas ainda não disponíveis, serão disponibilizadas durante o período da Prova Teste.')
    #messages.error(request, 'Senhas ainda não disponíveis, serão disponibilizadas no dia anterior à prova.')
    #return redirect('/restrito/')

    try:
        school_id = request.user.deleg.deleg_school.pk
        usertype = 'coord'
    except:
        school_id = request.user.colab.colab_school.pk
        usertype = 'colab'

    s = School.objects.get(pk=school_id)
    school_name = s.school_name
    if usertype == 'coord':
        name = s.school_deleg_name
    else:
        colab = Colab.objects.get(user_id=request.user.id)
        name = colab.colab_name
        
    if request.method == 'POST':
        form = CompetSenhasCmsFiltroForm(request.POST)
        if form.is_valid():
            f = form.cleaned_data
            compet_type = f['compet_type']
            compet_order = f['compet_order']
            
            return compet_cartoes_senhas_exec(request, compet_type, compet_order, is_cms=True, is_cf=False)
    else:
        form = CompetSenhasCmsFiltroForm()
    return render(request, 'restrito/compet_cartoes_senhas_cms.html', {'form': form, 'pagetitle': 'Gera cartões com senhas para o CMS', 'school_name': school_name, 'name': name})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_cartoes_senhas_cms_prev(request):
    return render(request, 'restrito/compet_cartoes_senhas_prev.html', {'pagetitle': 'Gera cartões com senhas para o CMS'})


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def compet_cartoes_senhas_exec(request, compet_type, compet_order, is_cms=False, is_cf=False):
    # data: ('Num. Inscr.', 'Nome', 'Modalidade', 'Senha', 'Escola')

    #msg = 'Ainda não disponível.'
    #return aviso(request, msg)

    PHASE = 3
    
    def write_card(label, width, height, data):
        i = 0
        label.add(shapes.String(15, height-25-i*15,                       data[1], fontName="Helvetica-Bold", fontSize=11))
        i += 1
        label.add(shapes.String(15, height-25-i*15, 'Modalidade: '      + data[2], fontName="Helvetica", fontSize=11))
        i += 1
        label.add(shapes.String(15, height-35-i*15, 'Nome de usuário: ' + data[0], fontName="Helvetica", fontSize=11))
        i += 1
        label.add(shapes.String(15, height-35-i*15, 'Senha: '           + data[3], fontName="Helvetica", fontSize=11))
        i += 1
        label.add(shapes.String(15, height-55-i*15, 'Escola: '          + data[4], fontName="Helvetica", fontSize=8))
        i += 1
        try:
            label.add(shapes.String(15, height-55-i*15+4, 'Turma: '          + data[5], fontName="Helvetica", fontSize=8))
            i += 1
        except:
            pass

    if compet_type == '':
        list_type = LEVEL_ALL
    elif compet_type == 'I':
        list_type = LEVEL_INI
    elif compet_type == 'P':
        list_type = LEVEL_PROG
    else:
        list_type = (int(compet_type),)

    response = HttpResponse(content_type='application/pdf')

    if is_cf:
        if compet_type:
            fname = f"CartoesSenhasCMS_Competicao_Feminina_{LEVEL_NAME[int(compet_type)]}.pdf"
        else:
            fname = f"CartoesSenhasCMS_Competicao_Feminina.pdf"
    elif is_cms:
        if compet_type:
            fname = f"CartoesSenhasCMS_Fase{PHASE}_{LEVEL_NAME[int(compet_type)]}.pdf"
        else:
            fname = f"CartoesSenhasCMS_Fase{PHASE}_Prog.pdf"
    else:
        fname = f"CartoesSenhasPaginaPessoal.pdf"
            
    response['Content-Disposition'] = f'attachment; filename="{fname}"'
    
    try:
        school_id = request.user.deleg.deleg_school.pk
    except:
        school_id = request.user.colab.colab_school.pk

    s = School.objects.get(pk=school_id)

    from principal.utils.labels import Specification, Sheet

    specs = Specification(sheet_width=215.9, sheet_height=279.4, columns=2, rows=5,
                          label_width=101.6, label_height=50.8,
                          corner_radius=4,
                          left_margin=4, right_margin=4,
                          top_margin=12.7, bottom_margin=12.7,
                          column_gap=4.8, row_gap=0)

    mysheet = Sheet(specs, write_card, border=True)

    competsExist = False

    PHASE_3 = False

    for level_num in list_type:
        level = LEVEL_NAME[level_num]
        level_full = LEVEL_NAME_FULL[level_num]

        if is_cf:
            if level_num in (1,2,7):
                continue
            try:
                school_id = request.user.deleg.deleg_school.pk
            except:
                school_id = request.user.colab.colab_school.pk

            compets = []

            compets_obi = Compet.objects.filter(compet_school_id=school_id).order_by(compet_order)

            compets_cf = CompetCfObi.objects.filter(compet_type=level_num)
            compets = []
            for compet in compets_obi:
                try:
                    compet_cf = compets_cf.get(compet_id=compet.compet_id)
                except:
                    continue
                compets.append(compet)
                
        elif is_cms:
            if level_num in (1,2,7):
                continue
            # comment for phase 3!

            if PHASE == 1:
                compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num).order_by(compet_order,'compet_name')
            elif PHASE == 2:
                compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num, compet_classif_fase1=True).order_by(compet_order,'compet_name')
            elif PHASE == 3:
                compets = Compet.objects.filter(compet_school__school_site_phase3_prog=school_id,compet_classif_fase2=True,compet_type=level_num).order_by(compet_order)
                # or use this
                #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site().filter(compet_type=level_num).order_by(compet_order)
            else:
                # should not come here
                compets = None
                
            if compet_order == 'compet_class':
                compets = compets.order_by(compet_order,'compet_name')

            else:
                compets = compets.order_by(compet_order)

            # for fase 1
            # if compet_order == 'compet_class':
            #     compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num, compet_classif_fase1=True).order_by(compet_order,'compet_name')

            # else:
            #     compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num, compet_classif_fase1=True).order_by(compet_order)

            #compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num,compet_classif_fase1=True).order_by(compet_order)

            # this is valid only for phase 3!
            #compets = Compet.objects.filter(compet_school__school_site_phase3_prog=school_id,compet_classif_fase2=True,compet_type=level_num).order_by(compet_order)
            # or use this
            #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site().filter(compet_type=level_num).order_by(compet_order)
        else:
            compets = Compet.objects.filter(compet_school_id=school_id,compet_type=level_num).order_by(compet_order)

            # this is valid only for phase 3!
        #     compets = Compet.objects.filter(compet_school__school_site_phase3_prog=school_id,compet_classif_fase2=True,compet_type=level_num).order_by(compet_order)
        #     #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site().filter(compet_type=level_num).order_by(compet_order)
        # else:
        #     compets = Compet.objects.filter(compet_type=level_num,compet_school_id=school_id).order_by(compet_order)
        #     #compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site().filter(compet_type=level_num).order_by(compet_order)

        # if not PHASE_3:
        #     if not is_cfobi:
        #         compets = Compet.objects.filter(compet_school_id=school_id, compet_type=level_num).order_by(compet_order)
        #     else:
        #         compets = Compet.objects.filter(compet_school_id=school_id, competcfobi__compet_type=level_num).order_by(compet_order)
        # else: # this is valid only for phase 3!
        #      if level_num in LEVEL_INI:
        #          compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_ini_in_this_site().filter(compet_type=level_num).order_by(compet_order)
        #      elif level_num in LEVEL_PROG:
        #          compets = SchoolPhase3.objects.get(school_id=school_id).get_compets_prog_in_this_site().filter(compet_type=level_num).order_by(compet_order)
        #      # extra compets
        #      #compets = compets | Compet.objects.filter(compet_type=level_num,compet_school_id_fase3=school_id,compet_classif_fase2=True)

        if len(compets) == 0:
            continue

        competsExist = True

        for c in compets:
            if is_cf:
                compet = Compet.objects.get(compet_id=c.compet_id)
                p = PasswordCms.objects.get(compet=compet)
                password = p.password
            elif is_cms:
                #print(c.compet_id)
                try:
                    p = PasswordCms.objects.get(compet=c)
                    password = p.password
                except:
                    password = ''
            else:
                password = c.compet_conf

            # data: ('Num. Inscr.', 'Nome', 'Modalidade', 'Senha', 'Escola')
            data = ((c.compet_id_full, c.compet_name, level_full, password, c.compet_school.school_name, c.compet_class))
            mysheet.add_label(data)

    if competsExist:
        from io import BytesIO
        pdf = BytesIO()

        mysheet.save(pdf)
        #report = PrintPresenceList(subtitle1)
        #pdf = report.print_list(data, title, subtitle1, subtitle2)

        response.write(pdf.getbuffer())
    else:
        msg = 'Não há competidores com o filtro selecionado.'
        return erro(request, msg)

    return response


@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def consulta_sede_fase3(request,hash,reply_type):
    # get hash
    try:
        site = School.objects.get(school_hash=hash)
    except:
        msg = 'Erro: solicitação inválida.'
        logger.info(f'consulta_escola_fase3 failed, wrong hash: {hash}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Consulta Sobre Sede Fase 3'})
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school

    if school.school_id != site.school_id:
        msg = 'Erro: solicitação inválida.'
        logger.info(f'consulta_sede_fase3 failed, {school.school_id} trying to reply {site.school_id}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Consulta Sobre Sede Fase 3'})

    logger.info(f'consulta_escola_fase3 reply {reply_type}, school_id: {school.school_id}, school_name: {school.school_name}')
    
    try:
        school_extra = SchoolExtra.objects.get(school=school)
    except:
        school_extra = SchoolExtra(school=school)
    try:
        school_extra.save()
    except:
        msg = 'Erro: contate a coordenação da OBI.'
        logger.info(f'consulta_sede_fase3 failed, {school.school_id} trying to reply {site.school_id}, school_extra could not be saved')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Consulta Sobre Sede Fase 3'})
        
    msg = 'A seguinte informação foi registrada: <p><em>A escola <strong>' + school.school_name + '</strong> '

    # 0: not site, 1: site ini, 2: site prog, 3: site both

    school_extra.school_answer_consulta_fase3 = reply_type
    if reply_type == 1: # SIM TODOS Iniciação + Programação
        msg += 'tem disponibilidade para ser sede da Fase 3 das modalidades Iniciação e Programação para todos os alunos da cidade/região.'
    elif reply_type == 2: # SIM TODOS Iniciação
        msg += 'tem disponibilidade para ser sede da Fase 3 da modalidade Iniciação para todos os alunos da cidade/região.'
    elif reply_type == 3: # SIM TODOS Programação
        msg += 'tem disponibilidade para ser sede da Fase 3 da modalidade Programação para todos os alunos da cidade/região.'
    elif reply_type == 4: # SIM apenas seus alunos
        msg += 'tem disponibilidade para ser sede da Fase 3 apenas para seus próprios alunos.'
    elif reply_type == 5: # NAO Iniciacao
        msg += 'NÃO tem disponibilidade para ser sede da Fase 3.'
    else:
        msg = 'Erro: solicitação inválida.'
        logger.info(f'consulta_sede_fase3 failed, wrong reply_type: {reply_type}')
        return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Consulta Sobre Sede Fase 3'})

    try:
        school_extra.user_answer_consulta_fase3 = request.user.id
        school_extra.save()
    except:
        logger.info(f'consulta_sede_fase3 failed to save user: {request.user}')
    
    msg += '</em><p>Obrigado pela informação. Se desejar modificá-la, basta clicar novamente nos links enviados (a última informação é a que vale).'
    return render(request, 'principal/pagina_com_mensagem.html', {'msg': msg, 'pagetitle':'Consulta Sobre Sede Fase 3'})

