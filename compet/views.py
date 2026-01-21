import secrets
import logging
import time

import hmac
import hashlib
import base64

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.utils.timezone import make_aware
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.clickjacking import xframe_options_exempt
from principal.models import CompetCfObi, Compet, LEVEL_NAME, School, IJ, I1, I2, PJ, P1, P2, PS, LastAccess
from exams.models import ExamFase1
from exams.models import Alternative, Question, Task
from exams.views import check_exam_status
from exams.settings import EXAMS
from week.models import Week
from obi.settings import YEAR, UA_SECRET
from principal.utils.get_certif import get_week_certif_compet
from principal.utils.get_letter import get_letter_compet, get_letter_compet_camp
from cms.utils import cms_check_participation

logger = logging.getLogger('obi')

def in_compet_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to 
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='compet').exists()

@user_passes_test(in_compet_group, login_url='/contas/login/')
def emite_carta(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carta.pdf"'
    compets =  Compet.objects.filter(compet_type=compet.compet_type).count()
    num_compets = compets/1000
    file_data = get_letter_compet(compet.compet_id,YEAR,num_compets)
    response.write(file_data)
    return response

@user_passes_test(in_compet_group, login_url='/contas/login/')
def emite_carta_treinamento(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="carta.pdf"'
    file_data = get_letter_compet_camp(compet.compet_id,YEAR)
    response.write(file_data)
    return response

@user_passes_test(in_compet_group, login_url='/contas/login/')
def emite_certificado_semana(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    year = 2021
    ##################
    # semana olímpica
    week = None
    try:
        week = Week.objects.get(compet=compet)
        # not for P2 now
        if week.partic_level == 4:
            week = None
    except:
        return
    
    level = week.partic_level
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="certificado.pdf"'
    file_data = get_week_certif_compet(compet.compet_id,level,year)
    response.write(file_data)
    return response

@user_passes_test(in_compet_group, login_url='/contas/login/')
def compet_sede_fase3(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    school_compet = School.objects.get(pk=compet.compet_school_id)
    if compet.compet_type in (IJ, I1, I2):
        mod = 'ini'
    else:
        mod = 'prog'
    if compet.compet_school_id_fase3:
        schools = School.objects.filter(pk = compet.compet_school_id_fase3)
    elif compet.compet_type in (IJ, I1, I2):
        schools = School.objects.filter(pk = school_compet.school_site_phase3_ini)
        mod = 'ini'
    else:
        schools = School.objects.filter(pk = school_compet.school_site_phase3_prog)
        mod = 'prog'

    if len(schools) != 0:
        return render(request, 'fase3/mostra_sede_fase3.html', { 'school': schools[0], 'mod': mod })

    messages.error(request, 'Sede ainda não definida, por favor aguarde.')
    return redirect('/compet/')

@user_passes_test(in_compet_group, login_url='/contas/login/')
def index(request):
    compet = Compet.objects.get(user_id=request.user.pk)
    school  = School.objects.get(school_id=compet.compet_school_id)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    # add mod to compet object, used in template
    compet.mod = level_name[0]
    compet.level = level_name

    try:
        last_access = LastAccess.objects.get(user=request.user)
    except:
        last_access = LastAccess(user=request.user)
    last_access.save()
        
    
    ##################
    # semana olímpica
    week = None
    try:
        week = Week.objects.get(compet=compet)
        # not for P2 now
        #if week.partic_level == 4:
        #    week = None
    except:
        pass

    ##################
    # treinamento
    compets_invited = () # (29638, 29637,69235,38783,69300,64182)


    ##################
    # provas agendadas
    coming_exams = []

    #coming_exams.append(EXAMS['testef1'])
    #coming_exams.append(EXAMS['provaf1'])

    #if compet.compet_classif_fase1 and compet.compet_type in (P2,):
    #    coming_exams.append(EXAMS['provaf2b'])

    #if compet.compet_classif_fase1:
    #    coming_exams.append(EXAMS['provaf2'])

    #if compet.compet_classif_fase2:
    #    coming_exams.append(EXAMS['provaf3'])

    #if compet.compet_classif_fase1 and compet.compet_type in (PJ,P1,P2,PS):
    #    online_exams.append(EXAMS['provaf2b'])
    #if compet.compet_type in (3,4,5) and compet.compet_sex == 'F':
    #    online_exams.append(EXAMS['cfobif1'])

    # if hasattr(compet, 'competcfobi'):
    #     compet.mod = 'p'
    #     compet.level = LEVEL_NAME[compet.competcfobi.compet_type].lower()
    #     coming_exams.append(EXAMS['cfobif1'])

    # if compet.compet_classif_fase2:
    #    coming_exams.append(EXAMS['provaf3'])

    #if compet.compet_type in (I1,I2,IJ):
    #    online_exams.append(EXAMS['testef1'])

    # prova teste
    #if compet.compet_type in (PJ,P1,P2,PS):
    #    online_exams.append(EXAMS['testef1'])

    #if compet.compet_type in (PJ,P1,P2,PS):
    #    online_exams.append(EXAMS['provaf1'])


    ##################
    # provas passadas
    past_exams = []

    past_exams.append(EXAMS['provaf1'])
    ok,exam,status_provaf1,msg = check_exam_status('provaf1', compet)


    if compet.compet_classif_fase1:
        past_exams.append(EXAMS['provaf2'])
        ok,exam,status_provaf2,msg = check_exam_status('provaf2', compet)

    if compet.compet_classif_fase2:
        past_exams.append(EXAMS['provaf3'])
        ok,exam,status_provaf2,msg = check_exam_status('provaf3', compet)


    #if compet.compet_classif_fase1 and compet.compet_type == P2:
    #    past_exams.append(EXAMS['provaf2b'])
    #    ok,exam,status_provaf2b,msg = check_exam_status('provaf2b', compet)

    #past_exams.append(EXAMS['provaf2'])
    #ok,exam,status_provaf2,msg = check_exam_status('provaf2', compet)

    #if compet.compet_type in (PJ,P1,P2,PS):
    #    past_exams.append(EXAMS['provaf2b'])
    #    ok,exam,status_provaf2b,msg = check_exam_status('provaf2b', compet)


    #if compet.compet_classif_fase2:
    #    past_exams.append(EXAMS['provaf3'])
    #    ok,exam,status_provaf3,msg = check_exam_status('provaf3', compet)

    is_cf = False
    compet_cfobi = []
    try:
        compet_cfobi = CompetCfObi.objects.get(compet_id=compet.compet_id)
        is_cf = True
    except:
        pass
    if is_cf:
       past_exams.append(EXAMS['cfobif1'])
       import copy
       competcf_compet = copy.deepcopy(compet)
       competcf_compet.mod = 'p'
       competcf_compet.compet_type = compet_cfobi.compet_type
       competcf_compet.level = LEVEL_NAME[compet_cfobi.compet_type].lower()
       ok,exam,status_cfobi,msg = check_exam_status('cfobif1', competcf_compet)

    #    print("ok", ok)
    #    print("status_cfobi", status_cfobi)
    #    print("msg", msg)

    # prova teste

    #if compet.compet_type in (PJ,P1,P2,PS):
    #   ok,exam,status_testef1,msg = check_exam_status('testef1', compet)
    #   status_testef1 = 'done'
    #   if status_testef1 == 'done':
    #       past_exams.append(EXAMS['testef1'])


    # if compet.compet_type in (I1,I2,IJ):
    #     ok,exam,status_testef1,msg = check_exam_status('testef1', compet)
    #     if status_testef1 == 'done':
    #         past_exams.append(EXAMS['testef1'])
    # if compet.compet_classif_fase2:
    #     past_exams.append(EXAMS['provaf3'])
    # if compet.compet_classif_fase1:
    #     past_exams.append(EXAMS['provaf2'])
    # if compet.compet_type in (IJ,I1,I2):
    #     if school.school_turn_phase1_ini == 'A':
    #         past_exams.append(EXAMS['provaf1'])
    #     else:
    #         past_exams.append(EXAMS['provaf1b'])
    # else:
    #     if school.school_turn_phase1_prog == 'A':
    #         past_exams.append(EXAMS['provaf1'])
    #     else:
    #         past_exams.append(EXAMS['provaf1b'])
    #online_exams = [EXAMS['provaf1']]

    ##################
    # results
    # not used anymore
    # not used anymore
    # not used anymore
    
    exam_results = []

    #exam_results.append(EXAMS['testef1'])
    #ok,exam,status_provaf1,msg = check_exam_status('provaf1', compet)

    # ok,exam,status_provaf2,msg = check_exam_status('provaf2', compet)
    # ok,exam,status_provaf2b,msg = check_exam_status('provaf2b', compet)
    # ok,exam,status_provaf3,msg = check_exam_status('provaf3', compet)
    #if status_provaf1 == 'done':
    #    exam_results.append(EXAMS['provaf1'])
    # if status_provaf2 == 'done':
    #     exam_results.append(EXAMS['provaf2'])
    # if compet.compet_type in (PJ,P1,P2,PS) and status_provaf2b == 'done':
    #     exam_results.append(EXAMS['provaf2b'])

    # if compet.compet_type in (3,4,5) and compet.compet_sex == 'F':
    #     ok,exam,status_provacfobi,msg = check_exam_status('cfobif1', compet)
    #     if status_provacfobi == 'done':
    #         exam_results.append(EXAMS['cfobif1'])

    # if compet.compet_type in (PJ,P1,P2,PS) and status_provaf3 == 'done':
    #     exam_results.append(EXAMS['provaf3'])

    # if compet.compet_type in (IJ,I1,I2) and ((compet.compet_points_fase3 and compet.compet_points_fase3 >= 0) or (status_provaf3 and status_provaf3 == 'done')):
    #     exam_results.append(EXAMS['provaf3'])

    # prova teste
    # if compet.compet_type in (I1,I2,IJ):
    #     if status_testef1 == 'done':
    #         exam_results.append(EXAMS['testef1'])

    #if compet.compet_type in (PJ,P1,P2,PS):
        # status_testef1 = 'done'
        # if status_testef1 == 'done':
        #     exam_results.append(EXAMS['testef1'])

        #if status_provaf1 == 'done':
        #    exam_results.append(EXAMS['provaf1'])
        # if status_provaf2 == 'done':
        #     exam_results.append(EXAMS['provaf2'])
        # if status_provaf2b == 'done':
        #     exam_results.append(EXAMS['provaf2b'])
        # if status_provaf3 == 'done':
        #     exam_results.append(EXAMS['provaf3'])

    #if compet.compet_type in (IJ,I1,I2) and (compet.compet_classif_fase1 and compet.compet_points_fase2 and compet.compet_points_fase2 >= 0):
    #    exam_results.append(EXAMS['provaf2'])

    #if compet.compet_type in (IJ,I1,I2) and (compet.compet_classif_fase2 and compet.compet_points_fase3 and compet.compet_points_fase3 >= 0):
    #    exam_results.append(EXAMS['provaf3'])
        
    #if hasattr(compet, 'competcfobi'):
    #    exam_results.append(EXAMS['cfobif1'])

    level = LEVEL_NAME[compet.compet_type].lower()
    num_compet_level = Compet.objects.filter(compet_type=compet.compet_type).count()
    state = school.school_state
    #compets_with_problems = () # (55567,52909,53702,54938)
    compets_with_problems = () # (55567,52909,53702,54938)
    num_compet_level_state = Compet.objects.filter(compet_type=compet.compet_type,compet_school__school_state=state).count()

    return render(request, 'compet/index.html', {'compet': compet, 'level': level, 'mod': level[0], 'coming_exams': coming_exams, 'past_exams': past_exams, 'exam_results': exam_results, 'num_compet_level':num_compet_level,'num_compet_level_state':num_compet_level_state, 'week': week, 'compets_with_problems': compets_with_problems, 'compets_invited': compets_invited, 'compet_cfobi': compet_cfobi})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def erro(request,msg):
    data = {'pagetitle':'Erro', 'msg':msg}
    return render(request,'restrito/erro.html', data)


######
# get exam user-agent

# from django.utils import timezone
# from datetime import timedelta

def compareElapsedTime(starting_time, minutes=3):
    """
    Compares a starting_time (a DateTimeField value) to the current time.
    Returns True if the elapsed time is less than minutes,
    otherwise returns False.
    """
    
    if starting_time is None:
        return True
    from zoneinfo import ZoneInfo
    cms_tz = ZoneInfo("Europe/London")
    starting_time = make_aware(starting_time, timezone=cms_tz)
    print("starting_time", starting_time)
    # Get the current time (make sure it's timezone-aware)
    now = timezone.now()
    print("now", now)
    
    # Define your 3-minute duration
    delta_minutes = timedelta(minutes=minutes)

    # Calculate the elapsed time
    elapsed = now - starting_time
    print("elapsed", elapsed)
    # Return True if elapsed time is less than 3 minutes
    return elapsed < delta_minutes

def b64url_no_pad(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode("ascii")

@user_passes_test(in_compet_group)
def get_exam_ua(request):
    """
    Returns: plain text User-Agent string or JSON.
    """

    compet = Compet.objects.get(user_id=request.user.pk)
    logger.info(f'get_exam_ua, {compet.compet_id_full}')

    CONTEST_ID = 1

    starting_time = cms_check_participation(compet,contest_id=CONTEST_ID)
    logger.info(f'get_exam_ua, starting_time={starting_time}')

    if not compareElapsedTime(starting_time, minutes=3):
        return HttpResponse("exame encerrado", status=500)

    id = compet.compet_id_full
    level = compet.compet_type
    # timestamp (unix seconds)
    ts = int(time.time())
    # short random nonce
    nonce = secrets.token_urlsafe(12)  # 16-18 bytes url-safe
    # payload to sign
    payload = f"{id}|{ts}|{nonce}".encode("utf-8")
    if not UA_SECRET:
        return HttpResponse("server not configured", status=500)

    mac = hmac.new(UA_SECRET.encode("utf-8"), payload, hashlib.sha256).digest()
    sig = b64url_no_pad(mac)

    ua = f"level={level} ExamKit/1 id={id} ts={ts} nonce={nonce} sig={sig}"
    # Return as plain text for simplicity
    return HttpResponse(ua, content_type="text/plain")
