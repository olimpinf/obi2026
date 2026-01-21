import logging
import io
import os
import magic
import random
import json
from datetime import datetime, timedelta
from six import iteritems, itervalues

from io import StringIO
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponsePermanentRedirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.timezone import make_aware, timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.clickjacking import xframe_options_exempt

import time
import hmac
import hashlib
import base64
import secrets
from django.conf import settings
from django.views.decorators.http import require_GET


from principal.models import CompetCfObi,CompetCfObiDesclassif
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import cms_do_renew_participation
from principal.models import School, SchoolPhase3, Compet, CompetDesclassif, LEVEL_NAME, LEVEL_NAME_FULL, IJ, I1, I2, PJ, P1, P2, PS, CF, LANGUAGE_NAMES, SubWWW, ResWWW
from principal.forms import SubmeteSolucaoPratiqueForm
from principal.utils.utils import write_uploaded_file
from exams.models import ExamFase1, TesteFase1
from exams.models import Alternative, Question, Task
from cms.models import LocalFiles, LocalFsobjects



#from compet.views import in_compet_group
from .settings import EXAMS, TIMEZONE

logger = logging.getLogger(__name__)

def check_admin(user):
    return user.is_superuser

#######
# circular ref, copying from compet
def in_compet_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name='compet').exists()
#######
# circular ref, copying from restrito
def in_coord_colab_group(user):
    """Use with a ``user_passes_test`` decorator to restrict access to
    authenticated users who are in the "coord" group."""
    return user.is_authenticated and user.groups.filter(name__in=['local_coord', 'colab', 'colab_full']).exists()

class Dummy:
    '''dummy class to facilite passing parameters in rendertask'''
    pass

## from cms

def task_score(submissions, results, task, public=False, only_tokened=False):

    submissions = [s for s in participation.submissions
                   if s.task is task and s.official]
    if len(submissions) == 0:
        return 0.0, False

    submissions_and_results = [
        (s, s.get_result(task.active_dataset))
        for s in sorted(submissions, key=lambda s: s.timestamp)]

    score_details_tokened = []
    partial = False
    for s, sr in submissions_and_results:
        if sr is None or not sr.scored():
            partial = True
            score, score_details = None, None
        elif public:
            score, score_details = sr.public_score, sr.public_score_details
        elif only_tokened and not s.tokened():
            # If the caller wants the only_tokened score and this submission is
            # not tokened, the score mode should ignore its score. To do so, we
            # send to the score mode what we would send if it wasn't already
            # scored.
            score, score_details = None, None
        else:
            score, score_details = sr.score, sr.score_details
        score_details_tokened.append((score, score_details, s.tokened()))

    if task.score_mode == SCORE_MODE_MAX:
        return _task_score_max(score_details_tokened), partial
    if task.score_mode == SCORE_MODE_MAX_SUBTASK:
        return _task_score_max_subtask(score_details_tokened), partial
    elif task.score_mode == SCORE_MODE_MAX_TOKENED_LAST:
        return _task_score_max_tokened_last(score_details_tokened), partial
    else:
        raise ValueError("Unknown score mode '%s'" % task.score_mode)

def _task_score_max_subtask(score_details_tokened):
    """Compute score using the "max subtask" score mode.

    This has been used in IOI since 2017. The score of a participant on a
    task is the sum, over the subtasks, of the maximum score amongst all
    submissions for that subtask (not yet computed scores count as 0.0).

    If this score mode is selected, all tasks should be children of
    ScoreTypeGroup, or follow the same format for their score details. If
    this is not true, the score mode will work as if the task had a single
    subtask.

    score_details_tokened ([(float|None, object|None, bool)]): a tuple for each
        submission of the user in the task, containing score, score details
        (each None if not scored yet) and if the submission was tokened.

    return (float): the score.

    """
    # Maximum score for each subtask (not yet computed scores count as 0.0).
    max_scores = {}

    for score, details, _ in score_details_tokened:
        if score is None:
            continue

        if details == [] and score == 0.0:
            # Submission did not compile, ignore it.
            continue

        try:
            subtask_scores = dict(
                (subtask["idx"],
                 subtask["score_fraction"] * subtask["max_score"])
                for subtask in details)
        except Exception:
            subtask_scores = None

        if subtask_scores is None or len(subtask_scores) == 0:
            # Task's score type is not group, assume a single subtask.
            subtask_scores = {1: score}

        for idx, score in iteritems(subtask_scores):
            max_scores[idx] = max(max_scores.get(idx, 0.0), score)


    max_score = sum(itervalues(max_scores))
    #print('max_score',max_score)
    
    # original command:
    # subtask_full_score = max([sum([subtask["max_score"] for subtask in details]) for score, details, _ in score_details_tokened])
    try:
        subtask_full_score = max([sum([subtask.get("max_score", 0) for subtask in details]) for score, details, _ in score_details_tokened])
    except:
        subtask_full_score = 100

    #print('subtask_full_score',subtask_full_score)
    # for some, details == None, rewrite to avoid error:
    # maxpoints = 0
    # for score, details, _ in score_details_tokened:
    #     if details != None:
    #         subtask_sum = 0
    #         for subtask in details:
    #             subtask_sum += subtask.get("max_score", 0)
    #         if subtask_sum > maxpoints:
    #             subtask_sum = maxpoints
    # subtask_full_score = maxpoints

    #print(max_score,subtask_full_score)
    # original command:
    #return max_score if max_score <= subtask_full_score else subtask_full_score
    #print('max_score <= subtask_full_score',float(max_score) <= float(subtask_full_score))
    #print(type(max_score),type(subtask_full_score))
    if max_score <= subtask_full_score:
        return max_score
    else:
        return subtask_full_score

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def show_result_details_prog_coord(request, exam_descriptor, subm_id, compet_id):
    compet = Compet.objects.get(compet_id=compet_id)
    user = request.user
    try:
        # try coord
        # check if submission is from a compet in this school
        school = user.deleg.deleg_school
        if compet.compet_school_id != school.school_id:
            return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})
    except:
        try:
        # try colab
            # check if submission is from a compet in this school
            school = user.colab.colab_school
            if compet.compet_school_id != school.school_id:
                return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})
        except:
            return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})

    return do_show_result_details_prog(request, exam_descriptor, subm_id, compet)

@user_passes_test(in_compet_group, login_url='/contas/login/')
def show_result_details_prog(request, exam_descriptor, subm_id):
    compet = request.user.compet
    return do_show_result_details_prog(request, exam_descriptor, subm_id, compet)

def do_show_result_details_prog(request, exam_descriptor, subm_id, compet):
    user = request.user
    if not user.is_authenticated:
        return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})

    sr = LocalSubmissionResults.objects.get(local_subm=subm_id)

    try:
        # check if submission is from this compet
        if compet.compet_id != sr.compet_id:
            return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})
    except:
        return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})

    details = sr.score_details
    msg = "<p>Corpo do modal</p>"
    FEEDBACK_LEVEL_FULL = "full"
    feedback_level = FEEDBACK_LEVEL_FULL
    return render(request,'exams/submission_details.html',
                  {'sr':sr, 'feedback_level': feedback_level, 'FEEDBACK_LEVEL_FULL': FEEDBACK_LEVEL_FULL})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def save_exam_answer(request, exam_descriptor, task_name):
    if request.method != 'POST':
        return HttpResponse(status=404)
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    if not ok:
        logger.info("save_exam_answer not ok, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
        return HttpResponse(status=404)
    if status != 'running':
        logger.info("save_exam_answer not running, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
        return HttpResponse(status=404)
    # no need to do this
    # request_csrf_token = request.POST.get('csrfmiddlewaretoken', '')
    logger.info("save_exam_answer begin, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    data=json.loads(request.body.decode('UTF-8'))
    qnum = data['question']
    anum = data['answer']
    logger.info("save_exam_answer, {}, compet {}, level {}, question {}, answer {}".format(exam_title,compet.compet_id,level_name,qnum,anum))
    task_descriptor = f'{exam_descriptor}{level_name}_{task_name}'
    answers = eval(exam.answers)
    answers[task_descriptor][qnum] = int(anum)
    exam.answers = str(answers)
    exam.save()
    # now calculate new task status to show to the compet
    answered,questions = 0,0
    for num in answers[task_descriptor].keys():
        questions += 1
        if answers[task_descriptor][num] != -1:
            answered += 1
    total_answered,total_questions = 0,0
    for task in answers.keys():
        for num in answers[task].keys():
            total_questions += 1
            if answers[task][num] != -1:
                total_answered += 1
    if answered == questions:
        task_status = f'{answered}/{questions}'
    else:
        task_status = f'<font color="red">{answered}</font>/{questions}'
    if total_answered == total_questions:
        total_status = f'0 sem resposta'
    else:
        total_status = f'<font color="red">{total_questions-total_answered} sem resposta</font>'
    data = {'task_status': task_status, 'total_status': total_status}
    logger.info("save_exam_answer end, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    return JsonResponse(data)

def get_exam_start(exam_descriptor, compet):
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    try:
        exam = exam_obj.objects.get(compet_id=compet.compet_id)
    except:
        return None
    return exam.time_start

def get_exam_finish(exam_descriptor, compet):
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    try:
        exam = exam_obj.objects.get(compet_id=compet.compet_id)
    except:
        return None
    return exam.time_finish + timedelta(minutes=exam.time_extra)

def check_exam_finished(exam_descriptor, exam, compet):
    #print('check_exam_finished', compet)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    exam_title = EXAMS[exam_descriptor]['exam_title']
    if compet in EXAMS[exam_descriptor]['exam_superusers']:
        return False,"",""

    do_finish = False
    now = make_aware(datetime.now())

    #print(exam_descriptor)
    #print(EXAMS[exam_descriptor])
    #print(EXAMS[exam_descriptor]['exam_date_finish'])

    # give extra seconds to check finished
    extra = 10
    if now > exam.time_start + timedelta(minutes=exam.time_extra) + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + timedelta(seconds=extra):
        #print('time finished')
        do_finish = True

    if now > EXAMS[exam_descriptor]['exam_date_finish'][level_name[0]]:
        #print('now',now, EXAMS[exam_descriptor]['exam_date_finish'][level_name[0]])
        do_finish = True

    if do_finish:
        # finished
        exam.time_finish = exam.time_start + timedelta(minutes=exam.time_extra) + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name])
        exam.save()
        logger.info("check_exam_finished, time expired for {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        mark_exam(exam_descriptor,compet)
        exam_title = EXAMS[exam_descriptor]['exam_title']
        msg = 'A <em>{}</em> já foi realizada.'.format(exam_title)
        status = 'done'
        return True,status,msg
    else:
        return False,"",""

def check_exam_status(exam_descriptor, compet):
    print("compet.compet_type",compet.compet_type)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    msg = ''
    status = 'X'
    superusers = EXAMS[exam_descriptor]['exam_superusers']
    is_superuser = compet.compet_id in superusers

    # using only for prog, CMS
    if compet.compet_type not in (PJ,P1,P2,PS):
        #msg = 'Falta autorização para você realizar a <em>{}</em>.'.format(exam_title)
        #status = 'not authorized'
        if exam_descriptor == 'provaf1' or exam_descriptor == 'provaf2':
            if compet.compet_points_fase1:
                msg = 'A <em>{}</em> já foi realizada.'.format(exam_title)
                status = 'done'
        return False, None, status, msg

    #print('check_exam_status',compet.compet_id)
    logger.info("check_exam_status exam_obj={}".format(exam_obj))
    #######
    # only for turns in phase 1
    #######
    # if level_name[0] == 'i':
    #     turn = compet.compet_school.school_turn_phase1_ini
    # else:
    #     turn = compet.compet_school.school_turn_phase1_prog
    # if exam_descriptor == 'provaf1b' and turn == 'A':
    #     msg = 'A sua escola optou por realizar a {} no <em>Turno A</em>. Esta prova é relativa ao <em>Turno B</em>, você não tem permissão de acesso.'.format(exam_title)
    #     status = 'not authorized'
    #     return False, None, status, msg
    # elif exam_descriptor == 'provaf1' and turn == 'B':
    #     msg = 'A sua escola optou por realizar a {} no <em>Turno B</em>. Esta prova é relativa ao <em>Turno A</em>, você não tem permissão de acesso.'.format(exam_title)
    #     status = 'not authorized'
    #     return False, None, status, msg

    # moved after date check
    # try:
    #     exam = exam_obj.objects.get(compet_id=compet.compet_id)
    # except:
    #     msg = 'Falta autorização do Coordenador Local da OBI na sua escola para você realizar a <em>{}</em> online.'.format(exam_title)
    #     status = 'not authorized'
    #     return False, None, status, msg
    try:
        exam = exam_obj.objects.get(compet_id=compet.compet_id)
    except:
        #msg = 'Falta autorização para você realizar a  <em>{}</em> online. Para obter autorização, contate o professor Coordenador Local da sua escola.'.format(exam_title)
        msg = 'Falta autorização para você realizar a  <em>{}</em> online. '.format(exam_title)
        status = 'not authorized'
        return False, None, status, msg

    if is_superuser:
        msg = 'A <em>{}</em> está em andamento.'.format(exam_title)
        status = 'running'
        return True, exam, status, msg

    # para sabadistas
    # if compet.compet_id not in (55333,59696):
    #     msg = 'Período de realização da <em>{}</em> terminou.'.format(exam_title)
    #     status = 'too late'
    #     return False, None, status, msg
    if (not is_superuser) and make_aware(datetime.now()) < EXAMS[exam_descriptor]['exam_date_start'][level_name[0]]:
        #print('now < start',compet.compet_id)
        msg = 'Link para a <em>{}</em> estará disponível no período da prova.'.format(exam_title)
        status = 'too soon'
        return False, None, status, msg

    if exam.time_finish:
        #print('time_finish',compet.compet_id)
        msg = 'A <em>{}</em> já foi realizada.'.format(exam_title)
        status = 'done'
        return False, exam, status, msg
    print("OK1")
    if exam.time_start:
        # started, could have finished
        finished,status,msg = check_exam_finished(exam_descriptor, exam, compet)
        if finished:
            #print('started, failed by check_finish',compet)
            return False, None, status, msg
        else:
            msg = 'A <em>{}</em> está em andamento.'.format(exam_title)
            status = 'running'
            return True, exam, status, msg
    print("OK2")
    if make_aware(datetime.now()) > EXAMS[exam_descriptor]['exam_date_finish'][level_name[0]] + \
                                    timedelta(minutes=(exam.time_extra if exam.time_extra != None else 0)):
        msg = 'Período de realização da <em>{}</em> terminou.'.format(exam_title)
        status = 'too late'
        return False, None, status, msg
    # authorized, not started
    status = 'not started'
    msg =  'A <em>{}</em> ainda não foi realizada.'.format(exam_title)
    return True, exam, status, msg

@user_passes_test(in_compet_group, login_url='/contas/login/')
def index(request):
    return render(request,'restrito/erro.html', {})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def start_exam(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_descriptor = EXAMS[exam_descriptor]['exam_descriptor']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    f.compet = compet
    f.status = status
    f.exam_subm_max = exam_subm_max
    #print('in start',exam_subm_max)
    logger.info("start_exam page, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
    if not ok:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})
    if status == 'not started':
        #exam.subm_remaining = exam_subm_max
        exam.time_duration = EXAMS[exam_descriptor]['exam_duration'][level_name]  # minutes
        if mod == 'i':
            answers = {}
            tasks = Task.objects.filter(exam=exam_descriptor,level=compet.compet_type)
            for task in tasks:
                questions = Question.objects.filter(task=task)
                answers[task.descriptor] = {}
                for q in questions:
                    answers[task.descriptor][q.num] = -1
            exam.answers = str(answers)
            f.answers = answers
            f.answers_task = {} # at beginning
            shuffle_pattern = [1,2,3,4,5]
            random.shuffle(shuffle_pattern)
            exam.shuffle_pattern = str(shuffle_pattern)
        exam.save()
        logger.info("start_exam page, exam prepared {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    else:
        # exam is running
        if mod == 'i':
            f.answers = eval(exam.answers)
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            #f.answers_task = {}
    f.mod = mod
    f.exam_title = mark_safe(exam_title)
    f.exam_descriptor = exam_descriptor
    #f.subm_remaining = exam.subm_remaining
    f.time_remaining = check_remaining_time(compet,exam_descriptor,level_name)
    return render(request, 'exams/start_exam.html', {'f': f, 'pagetitle': f.exam_title})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def restart_exam(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    if exam_descriptor != 'testef1':
        #if (exam_descriptor == 'cfobif1' and compet.compet_id in (51024, 51025)):
        #    pass
        #else:
            return render(request, 'exams/nao_autorizado.html', {'msg': 'Você não tem permissão para acessar esta página.', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': ''})
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    exam_descriptor = EXAMS[exam_descriptor]['exam_descriptor']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    if not ok and status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})

    #exam.answers = None
    #exam.correct_answers = None
    #exam.num_correct_answers = None
    #exam.shuffle_pattern = None
    #exam.subm_remaining = None
    exam.time_start = None
    exam.time_finish = None
    exam.completed = None
    exam.save()
    ### 
    if mod == 'p':
        # remove cms_participation and local submissions
        local_submissions = LocalSubmissions.objects.filter(compet_type=compet.compet_type,contest_id=exam_contest_id)
        for subm in local_submissions:
            subm.delete()
        local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet.compet_type,contest_id=exam_contest_id)
        for subm in local_submission_results:
            subm.delete()
        # remove cms participation and add new cms participation
        cms_do_renew_participation(compet.compet_id_full, compet.compet_type, exam_contest_id)


        # remove submissions and result
        # submissions judged
        # results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
        # for r in results_judged:
        #     logger.info("Removing result, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        #     r.delete()
        # submissions_judged = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(team_id=compet.compet_id).order_by('problem_name','sub_id').using(EXAMS[exam_descriptor]['exam_db'])
        # for s in submissions_judged:
        #     logger.info("Removing submission, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        #     s.delete()

        # # all submissions during the exam
        # results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
        # for r in results:
        #     logger.info("Removing result all submissions, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        #     r.delete()
        # submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(team_id=compet.compet_id).order_by('problem_name','sub_id').using(EXAMS[exam_descriptor]['exam_db'])
        # for s in submissions:
        #     logger.info("Removing submission all submissions, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        #     s.delete()

    messages.success(request,"A {} foi reinicializada. Você pode refazer a prova.".format(exam_title))
    logger.info("Exam reset, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    return redirect('/compet/')

@user_passes_test(in_compet_group, login_url='/contas/login/')
def show_submissions(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    if not ok:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})
    answers = ''
    submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(team_id=compet.compet_id).order_by('problem_name','sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    for s in submissions:
        #s.sub_time = s.sub_time + timedelta(hours=TIMEZONE)
        s.sub_lang = LANGUAGE_NAMES[int(s.sub_lang)]
    results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
    id_results = []
    for r in results:
        id_results.append(r.sub_id)
    res_results = {}
    for r in results:
        res_results[r.sub_id] = (r.num_correct_tests > 0 and r.num_correct_tests == r.num_total_tests)
    f.compet = compet
    f.status = status
    f.level = level_name
    f.exam_title = mark_safe(exam_title)
    f.exam_descriptor = exam_descriptor
    #f.subm_remaining = exam.subm_remaining
    f.id_results = id_results
    f.res_results = res_results
    f.mod = mod
    f.exam_subm_max = exam_subm_max
    return render(request, 'exams/show_submissions.html', {'f': f, 'pagetitle': 'Resultado das submissões', 'submissions': submissions})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def exam(request,exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    logger.info("exam_ page, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
    if not ok:
        logger.info("exam page, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name, status))
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})
    #if exam_descriptor == 'f1':
    #    exam = ExamFase1.objects.get(compet_id=compet.compet_id)
    #else:
    #    exam = None
    if not exam.time_start:
        status = 'running' # started
        exam.time_start = make_aware(datetime.now())
        # exam.subm_remaining = exam_subm_max
        # exam.time_duration = EXAMS[exam_descriptor]['exam_duration'][level_name]  # minutes
        # if mod == 'i':
        #     answers = {}
        #     tasks = Task.objects.filter(exam=exam_descriptor,level=compet.compet_type)
        #     for task in tasks:
        #         questions = Question.objects.filter(task=task)
        #         answers[task.descriptor] = {}
        #         for q in questions:
        #             answers[task.descriptor][q.num] = -1
        #     exam.answers = str(answers)
        #     f.answers = answers
        #     f.answers_task = {}
        #     shuffle_pattern = [1,2,3,4,5]
        #     random.shuffle(shuffle_pattern)
        #     print('exam',shuffle_pattern)
        #     exam.shuffle_pattern = str(shuffle_pattern)
        exam.save()
        logger.info("Exam started {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    #else:
    if mod == 'i':
            f.answers = eval(exam.answers)
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.answers_task = {}
    f.compet = compet
    f.mod = mod
    f.status = status
    f.level = level_name
    f.exam_title = mark_safe(exam_title)
    f.exam_descriptor = exam_descriptor
    #f.subm_remaining = exam.subm_remaining
    #f.exam_subm_max = exam_subm_max
    t = Dummy() # dummy task, use the same template as rendertask
    t.title = mark_safe(exam_title)
    t.statement = None
    f.time_remaining = check_remaining_time(compet,exam_descriptor,level_name)
    if mod == 'i':
        template = 'exams/tarefa_iniciacao.html'
    else:
        template = 'exams/tarefa_programacao.html'
    return render(request, template, {'task': t, 'f': f, 'pagetitle': f.exam_title })
    #return render(request, 'exams/provas/{}/{}.html'.format(exam_descriptor,level), {'compet': compet, 'exam_title': exam_title, 'exam_descriptor': exam_descriptor, 'level': level, 'exam_answers': answers})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def exam_task(request,exam_descriptor,task_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    logger.info("exam_task page, {}, compet {}, level {}, status {}, task {}".format(exam_title,compet.compet_id,level_name,status,task_descriptor))
    if not ok:
        logger.info("Não autorizado, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})

    f.compet = compet
    f.status = status
    f.mod = mod
    f.exam_descriptor = exam_descriptor
    #f.descriptor = '{}{}_{}'.format(exam_descriptor,level_name,task_descriptor)
    #############
    # for turn b
    #############
    #if exam_descriptor[-1] == 'b':
    #    descr = exam_descriptor[:-1]
    #else:
    #    descr = exam_descriptor
    descr = exam_descriptor
    f.descriptor = '{}{}_{}'.format(descr,level_name,task_descriptor)
    f.exam_title = exam_title
    if request.method == 'POST':
        task = Task.objects.get(exam=exam_descriptor, descriptor=f.descriptor, level=compet.compet_type)
        if exam.subm_remaining <= 0:
            f.subm_remaining = 0
            messages.error(request,"Número de submissões excedido.")
            logger.info("Número de submissões excedido, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
            #return rendertask(request,'{}{}_{}'.format(exam_descriptor,level_name,task_descriptor), f)
            # for turn b
            return rendertask(request,'{}{}_{}'.format(descr,level_name,task_descriptor), f)
        else:
            exam.subm_remaining -= 1
            exam.save()
        if mod == 'i':
            questions = Question.objects.filter(task=task)
            answers = eval(exam.answers)
            num_valid = 0
            for q in questions:
                if str(q.num) in request.POST.keys():
                    answers[f.descriptor][q.num] = int(request.POST[str(q.num)])
                    num_valid += 1
                else:
                    answers[f.descriptor][q.num] = -1
            exam.answers = str(answers)
            exam.save()
            if num_valid > 0:
                messages.success(request,"As respostas foram atualizadas.")
                logger.info("As respostas foram atualizadas, {}, {}, compet {}, level {}, answers {}".format(exam_title,request.path, compet.compet_id,level_name,answers))
            else:
                messages.error(request,"Escolha a resposta para ao menos uma questão antes de salvar.")
                logger.info("Escolha a resposta para ao menos uma questão antes de salvar, {}, compet {}, level {}, answers {}".format(exam_title,compet.compet_id,level_name,answers))
            f.answers = answers
            f.answers_task = answers[f.descriptor]
            f.shuffle_pattern = eval(exam.shuffle_pattern)
        else:
            form = SubmeteSolucaoPratiqueForm(request.POST,request.FILES)
            # check whether it is valid:
            if form.is_valid():
                sub_file_name = request.FILES['data'].name
                source_path = write_uploaded_file(request.FILES['data'],request.FILES['data'].name,'sub_www')
                guess = magic.from_file(source_path,mime=True)
                if guess[:4] != 'text':
                    messages.error(request,"Houve um erro na submissão, arquivo não é de tipo texto.")
                    logger.info("Houve um erro na submissão, arquivo não é de tipo texto, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
                    # for turn b
                    #return rendertask(request,'{}{}_{}'.format(exam_descriptor,level_name,task_descriptor), f)
                    return rendertask(request,'{}{}_{}'.format(descr,level_name,task_descriptor), f)
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
                        messages.error(request,"Houve um erro na submissão, arquivo não é de tipo texto.")
                        logger.info("Houve um erro na submissão, arquivo não é de tipo texto, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
                        # for turn b
                        #return rendertask(request,'{}{}_{}'.format(exam_descriptor,level_name,task_descriptor), f)
                        return rendertask(request,'{}{}_{}'.format(descriptor,level_name,task_descriptor), f)
                os.remove(source_path)
                submission = EXAMS[exam_descriptor]['exam_table_submissions'](sub_source=source,sub_lang=form.cleaned_data['sub_lang'],problem_name=form.cleaned_data['problem_name'],problem_name_full=form.cleaned_data['problem_name_full'],team_id=compet.compet_id,sub_file=sub_file_name)
                submission.save(using=EXAMS[exam_descriptor]['exam_db'])
                # save the submission data in session
                request.session['submission_sub_id']=submission.sub_id
                request.session['submission_problem_name_full']=form.cleaned_data['problem_name_full'],
                request.session['problem_request_path']=form.cleaned_data['problem_request_path'],
                messages.success(request,"A solução foi submetida, aguarde o resultado.")
                logger.info("Solução submetida, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    else:
        if mod == 'i':
            f.answers = eval(exam.answers)
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.answers_task = f.answers[f.descriptor]
    f.subm_remaining = exam.subm_remaining
    f.exam_subm_max = exam_subm_max
    f.time_remaining = check_remaining_time(compet,exam_descriptor,level_name)
    #return rendertask(request,'{}{}_{}'.format(descr,level_name,task_descriptor), f)
    # for turn_b
    return rendertask(request,'{}{}_{}'.format(descr,level_name,task_descriptor), f)

def rendertask(request, descriptor, f):
    """
    Models: `tasks.tasks`
    Templates: Uses the template defined by the ``template_name`` field,
        or :template:`tasks/default.html` if template_name is not defined.
    Context:
        task
            `tasks.tasks` object
    """
    try:
        t = get_object_or_404(Task, descriptor=descriptor)
    except Http404:
        raise
    if f.mod != 'i':
        return render_task(request, t, f)
    questions = Question.objects.filter(task=t).order_by('num')
    for q in questions:
        alternatives = Alternative.objects.filter(question=q).order_by('num')
        q.alternatives = alternatives
    t.questions = questions
    return render_task(request, t, f)

@csrf_protect
def render_task(request, t, f):
    """
    Internal interface to the task page view.
    """
    # If registration is required for accessing this page, and the user isn't
    # logged in, redirect to the login page.
    if t.registration_required and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.path)
#     if f.template_name:
#         template = loader.select_template((f.template_name, DEFAULT_TEMPLATE))
#     else:
#         template = loader.get_template(DEFAULT_TEMPLATE)

    if f.is_review:
        if t.template_name.find('programacao') > 0:
            template = loader.get_template('exams/review_programacao.html')
        else:
            template = loader.get_template('exams/review_iniciacao.html')
    else:
        template = loader.get_template(t.template_name)

    # To avoid having to always use the "|safe" filter in task templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    t.title = mark_safe(t.title)
    t.statement = mark_safe(t.statement)
    context = {'task': t, 'f': f, 'pagetitle':t.title}
    response = HttpResponse(template.render(context, request))
    return response

def check_remaining_time(compet,exam_descriptor,level_name):
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    duration = EXAMS[exam_descriptor]['exam_duration'][level_name]
    exam = exam_obj.objects.get(compet_id=compet.compet_id)
    if exam.time_finish:
        # finished
        tempo = timedelta(0)
    elif exam.time_start:
        # running
        extra = 5
        tempo = exam.time_start + timedelta(minutes=exam.time_extra) + timedelta(minutes=duration) - make_aware(datetime.now())
        if tempo + timedelta(extra) < timedelta(0):
            tempo = timedelta(0)
            #exam.time_finish = make_aware(datetime.now())
            exam.time_finish = exam.time_start + timedelta(minutes=exam.time_extra) + timedelta(minutes=duration)
            logger.info("check_remaining_time, time expired for compet {}, {}".format(compet.compet_id,level_name))
            exam.save()
            mark_exam(exam_descriptor,compet)
    else:
        # not started
        tempo = timedelta(minutes=duration) + timedelta(minutes=exam.time_extra)
    return round(tempo.total_seconds())

######
# TODO
@user_passes_test(in_compet_group, login_url='/contas/login/')
def finish_review_exam(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    exam_descriptor = EXAMS[exam_descriptor]['exam_descriptor']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = False
    f.compet = compet
    f.status = status
    f.exam_subm_max = exam_subm_max
    logger.info("finish_review_exam page, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
    if not ok:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    if mod == 'i':
        f.answers = eval(exam.answers)
        f.shuffle_pattern = eval(exam.shuffle_pattern)
    f.mod = mod
    f.exam_title = mark_safe(exam_title)
    f.exam_descriptor = exam_descriptor
    f.subm_remaining = exam.subm_remaining
    f.time_remaining = check_remaining_time(compet,exam_descriptor,level_name)
    return render(request, 'exams/finish_review_exam.html', {'f': f, 'pagetitle': f.exam_title})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def finish_exam(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    level_name = LEVEL_NAME[compet.compet_type].lower()
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    logger.info("finish_exam page, {}, compet {}, level {}, status {}".format(exam_title,compet.compet_id,level_name,status))
    if ok and not exam.time_finish:
        exam.time_finish = make_aware(datetime.now())
        exam.save()
        mark_exam(exam_descriptor,compet)
        messages.success(request,"A {} foi finalizada.".format(exam_title))
    elif status == 'done':
        messages.success(request,"A {} foi finalizada.".format(exam_title))
    else:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    return redirect('/compet/')

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def retrieve_submission_coord(request,exam_descriptor,compet_id,sub_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    try:
        compet = Compet.objects.get(compet_id=compet_id,compet_school_id=school_id)
        ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    except:
        try:
            compet = CompetDesclassif.objects.get(compet_id=compet_id,compet_school_id=school_id)
            status = 'done'
        except:
            messages.error(request, 'Competidor(a) não existente.')
            return redirect('/restrito')
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    return do_retrieve_submission(request,exam_descriptor,compet,sub_id)

@user_passes_test(in_compet_group, login_url='/contas/login/')
def retrieve_submission(request,exam_descriptor,sub_id):
    compet = Compet.objects.get(user_id=request.user.pk)
    return do_retrieve_submission(request,exam_descriptor,compet,sub_id)

def do_retrieve_submission(request,exam_descriptor,compet,sub_id):
    level_name = LEVEL_NAME[compet.compet_type].lower()
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])

    try:
        submission = LocalSubmissions.objects.get(id=sub_id,compet_id=compet.compet_id)
    except:
        logger.info("do_retrieve_submission  {}, compet {}, level {} failed".format(exam_title,compet.compet_id,level_name))
        msg = "Você não tem acesso a esse arquivo."
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})

    language = submission.language
    filename = submission.filename
    source = bytes(submission.source)
    response = FileResponse(io.BytesIO(source),content_type='text/plain')
    response["Content-Disposition"] = "attachment; filename={}".format(filename)
    return response

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def retrieve_res_log_coord(request,exam_descriptor,compet_id,sub_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    try:
        compet = Compet.objects.get(compet_id=compet_id,compet_school_id=school_id)
    except:
        messages.error(request, 'Competidor(a) não existente.')
        return redirect('/restrito')
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    return do_retrieve_res_log(request,exam_descriptor,compet,sub_id)

@user_passes_test(in_compet_group, login_url='/contas/login/')
def retrieve_res_log(request,exam_descriptor,sub_id):
    compet = Compet.objects.get(user_id=request.user.pk)
    return do_retrieve_res_log(request,exam_descriptor,compet,sub_id)

def do_retrieve_res_log(request,exam_descriptor,compet,sub_id):
    level_name = LEVEL_NAME[compet.compet_type].lower()
    exam_title = EXAMS[exam_descriptor]['exam_title']
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    if not ok and status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    submission = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id,sub_id=sub_id).using(EXAMS[exam_descriptor]['exam_db']).get()
    source = submission.result_log
    return render(request, 'exams/raw.html', {'source': source})

@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def retrieve_res_log_judge_coord(request,exam_descriptor,compet_id,sub_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id
    try:
        compet = Compet.objects.get(compet_id=compet_id,compet_school_id=school_id)
    except:
        messages.error(request, 'Competidor(a) não existente.')
        return redirect('/restrito')
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    if status != 'done' or not EXAMS[exam_descriptor]['exam_show_results_coord'][level_name[0]]:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})
    return do_retrieve_res_log_judge(request,exam_descriptor,compet,sub_id)

def do_retrieve_res_log_judge(request,exam_descriptor,compet,sub_id):
    level_name = LEVEL_NAME[compet.compet_type].lower()
    exam_title = EXAMS[exam_descriptor]['exam_title']
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    submission = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id,sub_id=sub_id).using(EXAMS[exam_descriptor]['exam_db']).get()
    source = submission.result_log
    return render(request, 'exams/raw.html', {'source': source})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def retrieve_res_log_judge(request,exam_descriptor,sub_id):
    compet = Compet.objects.get(user_id=request.user.pk)
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    if status != 'done' or not EXAMS[exam_descriptor]['exam_show_results'][level_name[0]]:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': EXAMS[exam_descriptor]['exam_title']})
    return do_retrieve_res_log_judge(request,exam_descriptor,compet,sub_id)

def show_results_all(request, exam_descriptor,compet_id):
    try:
        compet = Compet.objects.get(compet_id=compet_id)
    except:
        messages.error(request, 'Competidor(a) não existente.')
        return redirect('/fase1/')
    school = School.objects.get(school_id=compet.compet_school_id)
    if compet.compet_type in (I1,I2,IJ):
        return show_results_ini(request, exam_descriptor,school,compet,'all')
    else:
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': EXAMS[exam_descriptor]['exam_title']})
        

    
    
@user_passes_test(in_coord_colab_group, login_url='/contas/login/')
def show_results_coord(request, exam_descriptor,compet_id):
    try:
        school = request.user.deleg.deleg_school
    except:
        school = request.user.colab.colab_school
    school_id = school.school_id

    if exam_descriptor == 'provaf1':
        compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type__in=(PJ,P1,P2,PS))
    elif exam_descriptor == 'provaf2':
        compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase1=True, compet_type__in=(PJ,P1,P2,PS))
    elif exam_descriptor == 'provaf2b':
        compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase1=True, compet_type__in=(PJ,P1,P2,PS))
    elif exam_descriptor == 'cfobif1':
        compets = CompetCfObi.objects.filter(compet__compet_school_id=school.school_id, compet_type__in=(PJ,P1,P2))
        compets_cf_desclassif = CompetCfObiDesclassif.objects.filter(compet__compet_school_id=school.school_id, compet_type__in=(PJ,P1,P2))
    elif exam_descriptor == 'provaf3':
        if school.school_is_site_phase3:
            compets = SchoolPhase3.objects.get(school_id=school.school_id).get_compets_prog_in_this_site()
        else:
            compets = Compet.objects.filter(compet_school_id=school.school_id, compet_classif_fase2=True, compet_type__in=(PJ,P1,P2,PS))
    else:
        messages.error(request, 'Prova não existente.')
        return redirect('/restrito')

    if exam_descriptor == 'cfobif1':
        try:
            compet = compets.get(compet_id=compet_id)
            ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
        except:
            try:
                compet = compets_cf_desclassif.get(compet_id=compet_id)
                status = 'done'
            except:
                messages.error(request, 'Competidor(a) não existente.')
                return redirect('/restrito')
    else:
        try:
            compet = compets.get(compet_id=compet_id)
            ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
        except:
            try:
                compet = CompetDesclassif.objects.get(compet_id=compet_id)
                status = 'done'
            except:
                messages.error(request, 'Competidor(a) não existente.')
                return redirect('/restrito')

    #ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': EXAMS[exam_descriptor]['exam_title']})
    if compet.compet_type in (I1,I2,IJ):
        return show_results_ini(request, exam_descriptor,school,compet,'coord')
    else:
        return do_show_results_compet_prog(request,exam_descriptor,compet,'coord')

def show_results_ini(request, exam_descriptor,school,compet,user_type):
    ALTERNATIVE_LETTER = "XABCDEX"
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]

    f = Dummy() # use a dummy class to facilitate passing values to rendertask

    ONLINE = False
    if ONLINE:
        ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
        if not exam:
            messages.error(request, 'Competidor(a) não fez a {}.'.format(exam_title))
            return redirect('/fase1/ini/consulta_res')
        f.exam = exam
    else:
        status = 'done'
        msg =''
        ok = True

    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.compet = compet
    f.status = status
    f.mod = mod
    f.level = level_name
    f.exam_descriptor = exam_descriptor
    f.exam_title = exam_title

    # if request.method == 'POST':
    #########################
    # do not show results unless specified in settings
    #########################
    if user_type == 'coord':
        f.show_results = EXAMS[exam_descriptor]['exam_show_results_coord'][level_name[0]]
        f.show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']
        template = 'exams/show_results_ini_coord.html'
    elif user_type == 'all':
        f.show_results = EXAMS[exam_descriptor]['exam_show_results_all'][level_name[0]]
        f.show_classif = EXAMS[exam_descriptor]['exam_show_classif_all']
        template = 'exams/show_results_ini_all.html'
    else:
        f.show_results = False
        f.show_classif = False
    if exam_descriptor.find('provaf1') >= 0:
        f.phase = 1
        f.next_phase = 'Fase Estadual'
    elif exam_descriptor.find('provaf2') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('provaf2b') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    else:
        f.phase = 3
        f.next_phase = ''

    if ONLINE and exam.answers:
        # compet participated online
        if f.show_results:
            f.answers = eval(exam.answers)
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.correct_answers = eval(exam.correct_answers)
            f.num_correct_answers = eval(exam.num_correct_answers)
            f.total_points = 0
            for k in f.num_correct_answers.keys():
                f.total_points += f.num_correct_answers[k]
        else:
            f.answers = eval(exam.answers)
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.correct_answers = eval(exam.correct_answers)
            f.num_correct_answers = eval(exam.num_correct_answers)
            f.total_points = '?'
            for k in f.num_correct_answers.keys():
                f.num_correct_answers[k] = '?'
    else:
        # compet participated not online
        f.answers = None
        if f.show_results:
            if exam_descriptor.find('provaf1') >= 0:
                f.total_points = compet.compet_points_fase1
            elif exam_descriptor.find('provaf2') >= 0:
                f.total_points = compet.compet_points_fase2
            elif exam_descriptor.find('provaf3') >= 0:
                f.total_points = compet.compet_points_fase3
            else:
                f.total_points = None
        else:
            f.total_points = '?'

    if f.show_classif:
        if exam_descriptor.find('provaf1') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase1 else 'Não'
        elif exam_descriptor.find('provaf2') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase2 else 'Não'
        else:
            f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'
    else:
        #f.classif_next_phase = '?'
        f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'

    if f.answers:
        tasks = Task.objects.filter(exam=exam_descriptor,level=compet.compet_type).order_by('order')
        ans = StringIO()
        qnum = 1
        for t in tasks:
            questions = Question.objects.filter(task=t).order_by('num')
            #print('# {}'.format(t.title))
            print('# {}'.format(t.title),file=ans)
            for q in questions:
                correct_mark = ''
                if f.show_results:
                    correct = Alternative.objects.filter(question=q,correct=True).only('num')
                    is_correct = False
                    for i in range(len(correct)):
                        if (correct[i].num == f.answers[t.descriptor][q.num]):
                            is_correct = True
                            break
                    if is_correct:
                        correct_mark = ' +'
                print("{}. {}{}".format(qnum,ALTERNATIVE_LETTER[f.answers[t.descriptor][q.num]],correct_mark),file=ans)
                qnum += 1

        print("\nA letra 'X' indica que o competidor deixou a questão sem resposta.",file=ans)
        if f.show_results:
            print("O símbolo '+' indica resposta correta.",file=ans)
        f.answer_list = ans.getvalue()
        f.subm_remaining = exam.subm_remaining
        f.exam_subm_max = exam_subm_max
    f.school_turn = school.school_turn_phase1_ini
    return render(request, template, {'f': f, 'pagetitle': f.exam_title})

@user_passes_test(in_compet_group, login_url='/contas/login/')
def show_results_prog(request, exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    print("in show_results_prog, compet=", compet)
    return do_show_results_compet_prog(request,exam_descriptor,compet,'compet')

def do_show_results_compet_prog(request,exam_descriptor,compet,user_type):

    if exam_descriptor == 'cfobif1':
        try:
            competcf = CompetCfObi.objects.get(compet_id=compet.compet_id)
            compet.compet_type = competcf.compet_type
        except:
            competcf = CompetCfObiDesclassif.objects.get(compet_id=compet.compet_id)
            compet.compet_type = competcf.compet_type
            
    level_name = LEVEL_NAME[compet.compet_type].lower()        
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    
    ###############################
    #
    # NEED FIX!!!!
    exam_contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]

    # doing this because of compet desclassif
    if user_type == 'coord':
        try:
            school = request.user.deleg.deleg_school
        except:
            school = request.user.colab.colab_school
        school_id = school.school_id
        status = ''
        msg = "Você não tem autorização para ver este resultado."

        try:
            if compet.compet_school_id == school_id:
                status = 'done'
                msg = ''
        except:
            # CF 
            if compet.compet.compet_school_id == school_id:
                status = 'done'
                msg = ''
            
    else:
        ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
        
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam_descriptor = exam_descriptor
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Resultado não disponível', 'exam_header': f.exam_header})

    #########################
    # do not show results unless specified in settings
    #########################
    if user_type == 'compet':
        f.show_results = EXAMS[exam_descriptor]['exam_show_results'][level_name[0]]
        f.show_classif = EXAMS[exam_descriptor]['exam_show_classif']
    elif user_type == 'coord':
        f.show_results = EXAMS[exam_descriptor]['exam_show_results_coord'][level_name[0]]
        f.show_classif = EXAMS[exam_descriptor]['exam_show_classif_coord']
    else:
        f.show_results = EXAMS[exam_descriptor]['exam_show_results_all'][level_name[0]]
        f.show_classif = EXAMS[exam_descriptor]['exam_show_classif_all']

    f.user_type = user_type
    if exam_descriptor.find('provaf1') >= 0:
        f.phase = 1
        f.next_phase = 'Fase Estadual'
    elif exam_descriptor.find('provaf2') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('provaf2b') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('fcobif1') >= 0:
        f.phase = 2
        f.next_phase = ''
    else:
        f.phase = 3
        f.next_phase = ''

    if f.show_classif:
        if exam_descriptor.find('provaf1') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase1 else 'Não'
        elif exam_descriptor.find('provaf2') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase2 else 'Não'
        else:
            #f.classif_next_phase = '?'
            f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'
            
    else:
        #f.classif_next_phase = '?'
        f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'

    f.task_points = {}
    f.total_points = 0
    local_submission_results = {}

    if f.show_results:
        local_submission_results = LocalSubmissionResults.objects.filter(compet_id=compet.compet_id,compet_type=compet.compet_type,contest_id=exam_contest_id).order_by("-submission_id")
        scores = {}
        task_titles = {}
        for s in local_submission_results:
            task = s.local_subm.task_name
            if task in scores.keys():
                scores[task].append((s.public_score,s.public_score_details,False))
                f.total_points += _task_score_max_subtask(scores[task])
            else:
                scores[task] = [(s.public_score,s.public_score_details,False)]
                task_titles[task] = s.local_subm.task_title

        f.total_points = 0
        for task in scores.keys():
            f.total_points += _task_score_max_subtask(scores[task])
        f.total_points = int(f.total_points)
        for task in task_titles.keys():
            task_title = task_titles[task]
            f.task_points[task_title] = int(_task_score_max_subtask(scores[task]))

        #results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
        #print('results_judged:',results_judged)
    #else:

        #id_results_judged = []
        #for r in results_judged:
        #    id_results_judged.append(r.sub_id)
        #res_results_judged = {}
        #f.num_correct_tests = {}
    #for r in results_judged:
    #    res_results_judged[r.sub_id] = r.num_correct_tests
    #    f.total_points += r.num_correct_tests
    #    f.num_correct_tests[r.problem_name] = r.num_correct_tests

    # all submissions during the exam
    local_submissions = LocalSubmissions.objects.filter(compet_id=compet.compet_id,contest_id=exam_contest_id).order_by('task_title','-submission_id')
    #submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(team_id=compet.compet_id).order_by('problem_name','sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    #for s in submissions:
    #    s.sub_lang = LANGUAGE_NAMES[int(s.sub_lang)]
    #results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
    #id_results = []
    #for r in results:
    #    id_results.append(r.sub_id)
    #res_results = {}
    #for r in results:
    #    res_results[r.sub_id] = (r.num_correct_tests > 0 and r.num_correct_tests == r.num_total_tests)

    f.compet = compet
    f.status = status
    f.level = level_name
    f.exam_title = mark_safe(exam_title)
    f.exam_descriptor = exam_descriptor
    #f.subm_remaining = exam.subm_remaining
    #f.id_results = id_results
    #f.res_results = res_results
    #f.id_results_judged = id_results_judged
    #f.res_results_judged = res_results_judged
    f.mod = mod
    f.exam_subm_max = exam_subm_max
    if user_type == 'compet':
        if f.exam_descriptor == 'provaf3':
            #template = 'exams/show_results_prog_fase3.html'
            template = 'exams/show_results_prog.html'
        else:
            template = 'exams/show_results_prog.html'
    elif user_type == 'coord':
        if f.exam_descriptor == 'provaf3':
            #template = 'exams/show_results_prog_coord_fase3.html'
            template = 'exams/show_results_prog.html'
        else:
            template = 'exams/show_results_prog.html'
    else:
        if f.exam_descriptor == 'provaf3':
            template = 'exams/show_results_prog_all_fase3.html'
        else:
            template = 'exams/show_results_prog_all.html'

    #print("local_submissions",local_submissions)
    return render(request, template, {'f': f, 'pagetitle': 'Resultado da correção', 'submissions': local_submissions, 'submission_results': local_submission_results})

def exam_task_review(request,exam_descriptor,task_descriptor):
    exam_title = EXAMS[exam_descriptor]['exam_title']
    user = request.user
    if not user.is_authenticated:
        return render(request, 'exams/nao_autorizado.html', {'msg': '', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_title})
    if user.groups.filter(name='compet').exists():
        compet = Compet.objects.get(user_id=request.user.pk)
    elif user.groups.filter(name__in=['local_coord', 'colab', 'colab_full']).exists():
        try:
            school = request.user.deleg.deleg_school
        except:
            school = request.user.colab.colab_school
        school_id = school.school_id
        try:
            compet = Compet.objects.get(compet_id=compet_id,compet_school_id=school_id)
        except:
            messages.error(request, 'Competidor(a) não existente.')
            return redirect('/restrito')
    else:
        return render(request, 'exams/nao_autorizado.html', {'msg': '', 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_title})

    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': exam_header})

    level_name = LEVEL_NAME[compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = True
    if status != 'done':
        logger.info("Não autorizado, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})

    f.compet = compet
    f.status = status
    f.mod = mod
    f.exam_descriptor = exam_descriptor
    #f.descriptor = '{}{}_{}'.format(exam_descriptor,level_name,task_descriptor)
    #############
    # for turn b
    #############
    if exam_descriptor[-1] == 'b':
        descr = exam_descriptor[:-1]
    else:
        descr = exam_descriptor
    f.descriptor = '{}{}_{}'.format(descr,level_name,task_descriptor)

    f.exam_title = exam_title
    if exam_descriptor.find('provaf1') >= 0:
        f.phase = 1
        f.next_phase = 'Fase Estadual'
    elif exam_descriptor.find('provaf2') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('provaf2b') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    else:
        f.phase = 3
        f.next_phase = ''

    # if request.method == 'POST':
    #########################
    # do not show results unless specified in settings
    #########################
    f.show_results = EXAMS[exam_descriptor]['exam_show_results'][level_name[0]]
    f.show_classif = EXAMS[exam_descriptor]['exam_show_classif']
    if f.show_results:
        if mod == 'i':
            f.answers = eval(exam.answers)
            f.answers_task = f.answers[f.descriptor]
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.correct_answers = eval(exam.correct_answers)
            f.correct_answers_task = f.correct_answers[f.descriptor]
            f.num_correct_answers = eval(exam.num_correct_answers)
            f.num_correct_tests = {}
            f.total_points = 0
            for k in f.num_correct_answers.keys():
                f.total_points += f.num_correct_answers[k]
        else:
            results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
            f.num_correct_tests = {}
            f.total_points = 0
            for r in results_judged:
                f.total_points += r.num_correct_tests
                f.num_correct_tests[r.problem_name] = r.num_correct_tests
    else:
        if mod == 'i':
            f.answers = eval(exam.answers)
            f.answers_task = f.answers[f.descriptor]
            f.shuffle_pattern = eval(exam.shuffle_pattern)
            f.correct_answers = eval(exam.correct_answers)
            f.correct_answers_task = f.correct_answers[f.descriptor]
            f.num_correct_answers = eval(exam.num_correct_answers)
            f.num_correct_tests = {}
            f.total_points = '?'
            for k in f.num_correct_answers.keys():
                f.num_correct_answers[k] = '?'
        else:
            results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
            f.num_correct_tests = {}
            f.total_points = 0
            for r in results_judged:
                f.total_points += r.num_correct_tests
                f.num_correct_tests[r.problem_name] = r.num_correct_tests

    if exam_descriptor.find('provaf1') >= 0:
        f.phase = 1
        f.next_phase = 'Fase Estadual'
    elif exam_descriptor.find('provaf2') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('provaf2b') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    else:
        f.phase = 3
        f.next_phase = ''
    if f.show_classif:
        if exam_descriptor.find('provaf1') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase1 else 'Não'
        elif exam_descriptor.find('provaf2') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase2 else 'Não'
        else:
            #f.classif_next_phase = '?'
            f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'
    else:
        #f.classif_next_phase = '?'
        f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'


    f.subm_remaining = exam.subm_remaining
    f.exam_subm_max = exam_subm_max
    # for turn b
    #return rendertask(request,'{}{}_{}'.format(exam_descriptor,level_name,task_descriptor), f)
    return rendertask(request,'{}{}_{}'.format(descr,level_name,task_descriptor), f)

def calc_total_correct_answers(report):
    total = 0
    for t in report.keys():
        for q in report[t].keys():
            if report[t][q]:
                total += 1
            #print('t',t,'report[t][q]',report[t][q],'total',total)
    return total

def mark_exam(exam_descriptor,compet):
    tasks = Task.objects.filter(exam=exam_descriptor,level=compet.compet_type).order_by('order')
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    exam_title = EXAMS[exam_descriptor]['exam_title']
    level_name = LEVEL_NAME[compet.compet_type].lower()
    logger.info("mark_exam begin, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    if compet.compet_type in (IJ,I1,I2):
        correct_answers = {}
        exam = exam_obj.objects.get(compet_id=compet.compet_id)
        num_correct_answers = {}
        answers = eval(exam.answers)
        for task in tasks:
            questions = Question.objects.filter(task=task)
            correct_answers[task.descriptor] = {}
            num_correct_answers[task.descriptor] = 0
            for q in questions:
                correct_answers[task.descriptor][q.num] = False
                alternatives = Alternative.objects.filter(question=q).order_by('num')
                for a in alternatives:
                    if a.correct and int(answers[task.descriptor][q.num]) == a.num:
                        num_correct_answers[task.descriptor] += 1
                        correct_answers[task.descriptor][q.num] = True

        #print(exam.correct_answers)
        #total_old = calc_total_correct_answers(eval(exam.correct_answers))
        exam.correct_answers=str(correct_answers)
        #total_new = calc_total_correct_answers(correct_answers)
        #if total_old != total_new:
        #    print(f'compet: {compet.compet_id}, old: {total_old}, new: {total_new}')
        exam.num_correct_answers=str(num_correct_answers)
        exam.save()
    # else:
    #     # move accepted solutions to be judged
    #     exam_obj = EXAMS[exam_descriptor]['exam_object']
    #     exam_db = EXAMS[exam_descriptor]['exam_db']
    #     results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id,num_correct_tests=1).only('sub_id').order_by('problem_name','-sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    #     accepted = []
    #     for r in results:
    #         accepted.append(r.sub_id)
    #     submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(sub_id__in=accepted).order_by('problem_name','-sub_id').using(EXAMS[exam_descriptor]['exam_db'])
    #     seen = set()
    #     for sub in submissions:
    #         if sub.problem_name not in seen:
    #             logger.info("Copying submission, {}, compet {}, level {}, {}, {}".format(exam_title,compet.compet_id,level_name, sub.sub_id, sub.problem_name))
    #             seen.add(sub.problem_name)
    #             # when re-marking, remove previous accepted solution
    #             try:
    #                 old = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(problem_name=sub.problem_name,team_id=compet.compet_id).using(EXAMS[exam_descriptor]['exam_db'])
    #                 if len(old) == 1:
    #                     print('found old submission, removing')
    #                     old[0].delete()
    #             except:
    #                 pass
    #             s = EXAMS[exam_descriptor]['exam_table_submissions_judge']()
    #             s.pk = sub.pk
    #             s.sub_id = sub.sub_id
    #             s.sub_lang = sub.sub_lang
    #             s.sub_source = sub.sub_source
    #             s.team_id = sub.team_id
    #             s.sub_file = sub.sub_file
    #             s.sub_time = sub.sub_time
    #             s.problem_name = sub.problem_name
    #             s.problem_name_full = sub.problem_name_full
    #             s.sub_lock = 0
    #             s.sub_marked = 0
    #             s.save(using=(EXAMS[exam_descriptor]['exam_db']))
    #             #print('saved',s.problem_name,s.sub_id,'using',EXAMS[exam_descriptor]['exam_db'])
    logger.info("mark_exam end, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))

# used only manually
def re_mark_exam(exam_descriptor,exam,compet):
    tasks = Task.objects.filter(exam=exam_descriptor,level=compet.compet_type).order_by('order')
    exam_title = EXAMS[exam_descriptor]['exam_title']
    level_name = LEVEL_NAME[compet.compet_type].lower()
    logger.info("re_mark_exam begin, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
    if compet.compet_type in (IJ,I1,I2):
        correct_answers = {}
        num_correct_answers = {}
        if exam.answers:
            answers = eval(exam.answers)
        else:
            logger.info("re_mark_exam end, no answers {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))
            return 0
        for task in tasks:
            questions = Question.objects.filter(task=task)
            correct_answers[task.descriptor] = {}
            num_correct_answers[task.descriptor] = 0
            #print(task.descriptor)
            for q in questions:
                #print('q.num',q.num,type(q.num))
                correct_answers[task.descriptor][q.num] = False
                alternatives = Alternative.objects.filter(question=q).order_by('num')
                for a in alternatives:
                    #print('a',a,a.correct)
                    if a.correct and int(answers[task.descriptor][q.num]) == a.num:
                        num_correct_answers[task.descriptor] += 1
                        correct_answers[task.descriptor][q.num] = True
        #print(num_correct_answers)
        #print(exam.correct_answers)
        try:
            total_old = calc_total_correct_answers(eval(exam.correct_answers))
            total_new = calc_total_correct_answers(correct_answers)
            #print('totals:',total_old, total_new)
            if total_old > total_new:
                print('update to smaller total_old:', total_old, 'total_new:', total_new)
            #elif total_old < total_new:
            #    print('update to greater total_old:', total_old, 'total_new:', total_new)
        except:
            print('bad...')
            pass

        exam.correct_answers=str(correct_answers)
        #total_new = calc_total_correct_answers(correct_answers)
        #if total_old != total_new:
        #    print(f'compet: {compet.compet_id}, old: {total_old}, new: {total_new}')
        exam.num_correct_answers=str(num_correct_answers)
        exam.save()
        return 1
    # else:
    #     # move accepted solutions to be judged
    #     exam_obj = EXAMS[exam_descriptor]['exam_object']
    #     exam_db = EXAMS[exam_descriptor]['exam_db']
    #     # instead of using accepted, use best score
    #     results = EXAMS[exam_descriptor]['exam_table_results'].objects.filter(team_id=compet.compet_id).only('sub_id').order_by('-num_correct_tests').using(EXAMS[exam_descriptor]['exam_db'])
    #     accepted = []
    #     seen = set()
    #     for r in results:
    #         if r.problem_name not in seen:
    #             accepted.append(r.sub_id)
    #             seen.add(r.problem_name)
    #             if r.problem_name.find('torre2') > 0:
    #                 seen.add(r.problem_name[:-1]) # seen torre also
    #             elif r.problem_name.find('torre') > 0:
    #                 seen.add(r.problem_name+'2')
    #         else:
    #             continue
    #     submissions = EXAMS[exam_descriptor]['exam_table_submissions'].objects.filter(sub_id__in=accepted).order_by('problem_name').using(EXAMS[exam_descriptor]['exam_db'])
    #     for sub_id in accepted:
    #         #print('sub_id',sub_id)
    #         sub = submissions.get(sub_id=sub_id)
    #         #print('sub',sub)
    #         logger.info("Copying submission, {}, compet {}, level {}, {}, {}".format(exam_title,compet.compet_id,level_name, sub.sub_id, sub.problem_name))
    #         # when re-marking, remove previous accepted solution
    #         try:
    #             old = EXAMS[exam_descriptor]['exam_table_submissions_judge'].objects.filter(problem_name=sub.problem_name,team_id=compet.compet_id).using(EXAMS[exam_descriptor]['exam_db'])
    #             if len(old) == 1:
    #                 print('found old submission, removing',old[0])
    #                 old[0].delete()
    #         except:
    #             pass
    #         s = EXAMS[exam_descriptor]['exam_table_submissions_judge']()
    #         s.pk = sub.pk
    #         s.sub_id = sub.sub_id
    #         s.sub_lang = sub.sub_lang
    #         s.sub_source = sub.sub_source
    #         s.team_id = sub.team_id
    #         s.sub_file = sub.sub_file
    #         s.sub_time = sub.sub_time
    #         s.problem_name = sub.problem_name
    #         s.problem_name_full = sub.problem_name_full
    #         s.sub_lock = 0
    #         s.sub_marked = 0
    #         s.save(using=(EXAMS[exam_descriptor]['exam_db']))
    #         #print('saved',s.problem_name,s.sub_id,'using',EXAMS[exam_descriptor]['exam_db'])
    logger.info("re_mark_exam end, {}, compet {}, level {}".format(exam_title,compet.compet_id,level_name))

def exam_review(request,exam_descriptor):
    compet = Compet.objects.get(user_id=request.user.pk)
    level_name = LEVEL_NAME[compet.compet_type].lower()
    mod = level_name[0]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_subm_max = EXAMS[exam_descriptor]['exam_submissions'][level_name]
    ok,exam,status,msg = check_exam_status(exam_descriptor, compet)
    f = Dummy() # use a dummy class to facilitate passing values to rendertask
    f.exam = exam
    f.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet.compet_type])
    f.is_review = True
    if status != 'done':
        return render(request, 'exams/nao_autorizado.html', {'msg': msg, 'pagetitle': 'Acesso Não Autorizado', 'exam_header': f.exam_header})

    f.compet = compet
    f.status = status
    f.mod = mod
    f.exam_descriptor = exam_descriptor
    f.exam_title = exam_title


    #########################
    # do not show results unless specified in settings
    #########################
    if EXAMS[exam_descriptor]['exam_show_results'][level_name[0]]:
        f.show_results= True
        if mod == 'i':
            if exam.answers:
                f.answers = eval(exam.answers)
                f.shuffle_pattern = eval(exam.shuffle_pattern)
                f.correct_answers = eval(exam.correct_answers)
                f.num_correct_answers = eval(exam.num_correct_answers)
                f.total_points = 0
                for k in f.num_correct_answers.keys():
                    f.total_points += f.num_correct_answers[k]
            else:
                f.answers = None
                # compet participated not online
                if exam_descriptor.find('provaf1') >= 0:
                    f.total_points = compet.compet_points_fase1
                elif exam_descriptor.find('provaf2') >= 0:
                    f.total_points = compet.compet_points_fase2
                elif exam_descriptor.find('provaf3') >= 0:
                    f.total_points = compet.compet_points_fase3
                else:
                    f.total_points = None
        else:
            results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
            f.num_correct_tests = {}
            f.total_points = 0
            for r in results_judged:
                f.total_points += r.num_correct_tests
                f.num_correct_tests[r.problem_name] = r.num_correct_tests
    else:
        f.show_results= False
        if mod == 'i':
            if exam_answers:
                f.answers = eval(exam.answers)
                f.shuffle_pattern = eval(exam.shuffle_pattern)
                f.correct_answers = eval(exam.correct_answers)
                f.num_correct_answers = eval(exam.num_correct_answers)
                for k in f.num_correct_answers.keys():
                    f.num_correct_answers[k] = '?'
                f.total_points = '?'
            else:
                f.answers = None
                f.total_points = '?'

        else:
            results_judged = EXAMS[exam_descriptor]['exam_table_results_judge'].objects.filter(team_id=compet.compet_id).only('sub_id','num_correct_tests','num_total_tests').using(EXAMS[exam_descriptor]['exam_db'])
            f.num_correct_tests = {}
            f.total_points = 0
            for r in results_judged:
                f.total_points += r.num_correct_tests
                f.num_correct_tests[r.problem_name] = r.num_correct_tests


    if EXAMS[exam_descriptor]['exam_show_classif']:
        f.show_classif= True
    else:
        f.show_classif= False

    if exam_descriptor.find('provaf1') >= 0:
        f.phase = 1
        f.next_phase = 'Fase Estadual'
    elif exam_descriptor.find('provaf2') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    elif exam_descriptor.find('provaf2b') >= 0:
        f.phase = 2
        f.next_phase = 'Fase Nacional'
    else:
        f.phase = 3
        f.next_phase = ''

    if f.show_classif:
        if exam_descriptor.find('provaf1') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase1 else 'Não'
        elif exam_descriptor.find('provaf2') >= 0:
            f.classif_next_phase = 'Sim' if compet.compet_classif_fase2 else 'Não'
        else:
            #f.classif_next_phase = '?'
            f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'
            
    else:
        #f.classif_next_phase = '?'
        f.classif_next_phase = 'classificação ainda não computada, será computada quanto todos os recursos de recorreção tiverem sido processados.'

    f.subm_remaining = exam.subm_remaining
    f.exam_subm_max = exam_subm_max

    f.level = level_name
    t = Dummy() # dummy task, use the same template as rendertask
    t.title = mark_safe(exam_title)
    t.statement = None
    if mod == 'i':
        if f.answers:
            template = 'exams/review_iniciacao.html'
        else:
            # not online exam
            template = 'exams/show_results_ini_all.html'
    else:
        template = 'exams/review_programacao.html'
    return render(request, template, {'task': t, 'f': f, 'pagetitle': f.exam_title })
    #return render(request, 'exams/provas/{}/{}.html'.format(exam_descriptor,level), {'compet': compet, 'exam_title': exam_title, 'exam_descriptor': exam_descriptor, 'level': level, 'exam_answers': answers})

@user_passes_test(check_admin)
def show_ranking_prog(request,exam_descriptor,compet_type):
    level_name = LEVEL_NAME_FULL[compet_type]
    exam_title = EXAMS[exam_descriptor]['exam_title']
    exam_contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    exam_obj = EXAMS[exam_descriptor]['exam_object']

    page_info =  Dummy() # use a dummy class to facilitate passing values to rendertask
    page_info.exam_header = "{} - {}".format(exam_title,LEVEL_NAME_FULL[compet_type])
    page_info.pagetitle = 'Ranking'
    page_info.level_name = level_name

    compet_type_ids = Compet.objects.filter(compet_type=compet_type).values_list('compet_id', flat=True)
    exam_ids = exam_obj.objects.filter(time_start__isnull=False,compet_id__in=compet_type_ids).values_list('compet_id', flat=True)

    f_list = []

    task_names = LocalSubmissions.objects.filter(compet_type=compet_type,contest_id=exam_contest_id).distinct('task_name').values_list('task_name', flat=True)

    for compet in Compet.objects.filter(compet_id__in=exam_ids):
        local_submission_results = LocalSubmissionResults.objects.filter(compet_id=compet.compet_id,compet_type=compet.compet_type,contest_id=exam_contest_id).order_by("-submission_id")
        scores = {}

        for s in local_submission_results:
            task = s.local_subm.task_name
            if task in scores.keys():
                scores[task].append((s.public_score,s.public_score_details,False))
            else:
                scores[task] = [(s.public_score,s.public_score_details,False)]

        f = Dummy() # use a dummy class to facilitate passing values to rendertask

        f.total_points = 0
        for task in scores.keys():
            f.total_points += _task_score_max_subtask(scores[task])
        f.total_points = int(f.total_points)

        f.task_points = {}
        for task in task_names:
            f.task_points[task] = int(_task_score_max_subtask(scores[task])) if task in scores.keys() else 0

        f.compet = compet
        f.school = School.objects.get(school_id=compet.compet_school_id)

        f_list.append(f)

    f_list = sorted(f_list, key=lambda f: (-f.total_points, f.compet.compet_name))

    return render(request, 'exams/show_ranking_prog.html', {'f_list': f_list, 'task_names': task_names, 'page_info': page_info})

