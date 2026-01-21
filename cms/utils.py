import logging
import os
import sys
from pytz import timezone
import pytz
from datetime import datetime, timedelta

from django.db import connection, connections
from django.utils.timezone import make_aware
from exams.settings import EXAMS, DEFAULT_CONTEST_ID
from principal.utils.utils import (make_password)
from principal.models import PJ, P1, P2, PS, LEVEL_NAME, Compet, PasswordCms
from obi.settings import DEBUG, CMS_HOST
from cms.models import (CMSuser, CMSparticipation, CMScommand, CMSsubmissions, CMSsubmissionResults, CMSdataset,
                        CMSFiles, CMSFsobjects, CMStask,
                        LocalSubmissions, LocalSubmissionResults, ExtraLocalSubmissions,
                        LocalFiles, LocalFsobjects)

logger = logging.getLogger(__name__)

CMS_DB = {PJ: 'cms_pj', P1: 'cms_p1', P2: 'cms_p2', PS: 'cms_ps'}

EXTENSIONS = {'C11 / gcc': 'c', 'C++20 / g++': 'cpp', 'Javascript': 'js',
              'Python 3 / CPython': 'py', 'Java / JDK': 'java', 'Pascal / fpc': 'pas'}

##################################
#### functions for CMS integration


def cms_check_participation(compet,contest_id=DEFAULT_CONTEST_ID):
    print("in cms_check_participation",compet.compet_id_full, contest_id)
    DB = CMS_DB[compet.compet_type]
    cms_user = CMSuser.objects.filter(username=compet.compet_id_full).using(DB).first()
    if cms_user:
        participation = CMSparticipation.objects.filter(user_id=cms_user.pk).using(DB).first()
    if participation:
        starting_time = participation.starting_time
    else:
        starting_time = None
    print("in cms_check_participation starting_time", starting_time)
    return starting_time
    
def cms_do_add_user(username,first_name,last_name,compet_type,password,contest_id=DEFAULT_CONTEST_ID):
    CMD = '''ssh -q -tt cms@{} <<'EOF'
cms
cmsAddUser -p '{}' '{}' '{}' {}
cmsAddParticipation -c {} -p {} {}
logout
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], password, first_name, last_name, username, contest_id, password, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms add  username=%s, compet_type=%s, contest_id=%d', username, compet_type, contest_id)
    try:
        os.system(cmd)
        return 1
    except:
        return 0


def cms_do_add_user_encrypted(username,first_name,last_name,compet_type,password,contest_id=DEFAULT_CONTEST_ID):
    CMD = '''ssh -T cms@{} <<'EOF'
cmsAddUser -H '{}' -- '{}' '{}' {}
cmsAddParticipation -c {} {}
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], password, first_name, last_name, username, contest_id, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms add  username=%s, compet_type=%s, contest_id=%d', username, compet_type, contest_id)
    try:
        os.system(cmd)
        return 1
    except:
        return 0

# version for CF-OBI
# do not use normally, see below
# def cms_do_update_password(username,compet_type,password):
#     ''' Will not update participation password!
#     '''

#     CMD = '''ssh -T cms@{} <<'EOF'
# cmsUpdatePassword -H '{}' --pbkdf2 '{}'
# EOF'''

#     if compet_type in (PJ,P1,P2):
#         try:
#             c = Compet.object.get(compet_id_full=username)
#         except:
#             print('failed for compet', compet_id_full)
#             return 0
#         if c.compet_sex=='F' or c.compet_sex=='O':
#             if c.compet_type == PJ:
#                 cmd = CMD.format(CMS_HOST[PJ], password, username)
#             elif c.compet_id < 25600:
#                 cmd = CMD.format(CMS_HOST[P2], password, username)
#             elif c.compet_id < 37000:
#                 cmd = CMD.format(CMS_HOST[P1], password, username)
#             else:
#                 cmd = CMD.format(CMS_HOST[PS], password, username)
#     else:
#         return 0

#     print(f'\n****************\n{cmd}\n****************\n')
#     logger.info('cms update username=%s, compet_type=%s', username, compet_type)
#     try:
#         os.system(cmd)
#         return 1
#     except:
#         return 0

# working version
def cms_do_update_password(username,compet_type,password):
    ''' Will not update participation password!
    '''

    CMD = '''ssh -q -tt cms@{} <<'EOF'
cms
cmsUpdatePassword -p '{}' '{}'
logout
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], password, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms update username=%s, compet_type=%s', username, compet_type)
    try:
        os.system(cmd)
        return 1
    except:
        return 0

def cms_do_update_password_encrypted(username,compet_type,password):
    ''' Will not update participation password!
    '''

    CMD = '''ssh -T cms@{} <<'EOF'
cmsUpdatePassword -H '{}' --pbkdf2 '{}'
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], password, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms update username=%s, compet_type=%s', username, compet_type)
    try:
        os.system(cmd)
        return 1
    except:
        return 0

def cms_do_update_password_using_db(compet):
    #password = compet.user.password
    password = "plaintext:"+compet.compet_conf
    username = compet.user.username
    # get does not work
    cms_users = CMSuser.objects.filter(username=username).using(CMS_DB[compet.compet_type])
    for c in cms_users:
        if c.username == username:
            c.password = password
            c.save()
            # get does not work
            participations = CMSParticipation.objects.filter(user_id=c.id).using(CMS_DB[c.compet_type])
            for p in participations:
                if p.user_id == c.id:
                    p.password = password
                    return 1
            return 0
    return 0


def cms_do_remove_user(username, compet_type, contest_id=DEFAULT_CONTEST_ID):
    # remove local files
    try:
        compet_id = int(username.split('-')[0])
    except:
        logger.info('cms do remove user failed  username=%s, compet_type=%s', username, compet_type)
        return 0

    subm = LocalSubmissions.objects.filter(contest_id=contest_id, compet_id=compet_id)
    for s in subm:
        s.delete()

    CMD = '''ssh -q -tt cms@{} <<'EOF'
cms
cmsRemoveUser {}
logout
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms remove user username=%s, compet_type=%s', username, compet_type)
    try:
        os.system(cmd)
        return 1
    except:
        return 0


def cms_remove_user(username, compet_type, contest_id=DEFAULT_CONTEST_ID):
    '''create a remove user command to be done later
    '''
    #cmd = CMScommand(command='remove',username=username, compet_type=compet_type, contest_id=contest_id)
    #cmd.save()
    try:
        p = PasswordCms.objects.get(compet_id=compet.compet_id)
        p.delete()
        #return
    except:
        #print("creating password")
        pass


def cms_do_add_submission(username,first_name,last_name,compet_type,password,contest_id=DEFAULT_CONTEST_ID):
    CMD = '''ssh -q -tt cms@{} <<'EOF'
cms
cmsAddParticipation -c {} -p {} {}
logout
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], password, first_name, last_name, username, contest_id, password, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms add  username=%s, compet_type=%s, contest_id=%d', username, compet_type, contest_id)
    try:
        os.system(cmd)
        return 1
    except:
        return 0


def cms_do_renew_participation(username, compet_type, contest_id=DEFAULT_CONTEST_ID):
    CMD = '''ssh -T cms@{} <<'EOF'
cmsRemoveParticipation -c {} {}
cmsAddParticipation -c {} {}
EOF'''
    cmd = CMD.format(CMS_HOST[compet_type], contest_id, username, contest_id, username, contest_id, username)
    print(f'\n****************\n{cmd}\n****************\n')
    logger.info('cms renew participation user username=%s, compet_type=%s, contest_id=%d', username, compet_type, contest_id)
    try:
        os.system(cmd)
        return 1
    except:
        return 0

def cms_update_password(username, compet_type, password):
    '''create a update password command to be done later
    '''

    # USING QUEUE
    #cmd = CMScommand(command='update',username=username, compet_type=compet_type, password=password)
    #cmd.save()

    # update now
    cms_do_update_password(username,compet_type,password)

def cms_add_user_encrypted(compet, compet_type, contest_id=DEFAULT_CONTEST_ID):
    '''create a update password command to be done later
    '''

    cmd = CMScommand(command='add',username=compet.compet_id_full, compet_type=compet_type,
                     first_name=compet.user.first_name, last_name=compet.user.last_name,
                     contest_id=contest_id, password=compet.user.password)
    cmd.save()


def cms_add_user(compet, compet_type, contest_id=DEFAULT_CONTEST_ID):
    '''create password command to be done later
    '''
    try:
        p = PasswordCms.objects.get(compet_id=compet.compet_id)
        #print("password exists for user")
        #return
    except:
        #print("creating password")
        pass
    names = compet.compet_name.split(" ")
    first_name = names[0]
    last_name = " ".join(names[1:])
    password = make_password(separator='.')
    # for fase 0:
    try:
        p = PasswordCms()
        p.password = password
        #p.password = compet.compet_conf
        p.compet = compet
        p.save()
    
        #cmd = CMScommand(command='add',username=compet.compet_id_full, compet_type=compet_type,
           # first_name=first_name, last_name=last_name,
           # contest_id=contest_id, password=password)
        #cmd.save()
    except:
        pass

def get_source_file(compet_type,submission):
    cms_file = CMSFiles.objects.filter(submission=submission).using(CMS_DB[compet_type])[0]
    filename = cms_file.filename
    ext = EXTENSIONS[submission.language]
    filename = filename.replace('%l',ext)
    cms_fsobjects = CMSFsobjects.objects.filter(digest=cms_file.digest).using(CMS_DB[compet_type])

    source = b''
    with connections[CMS_DB[compet_type]].cursor() as cms_cursor:
        for sub in cms_fsobjects:
            cms_cursor.execute("select * from pg_largeobject where loid=%s",[sub.loid]) # WHERE loid = %s", [sub.loid])
            columns = [col[0] for col in cms_cursor.description]
            result =  [dict(zip(columns, row)) for row in cms_cursor.fetchall()]
            for res in result:
                # print('loid',res['loid'])
                # print('pageno',res['pageno'])
                # print('data',res['data'])
                # print('data',bytes(res['data']))
                # print()
                source += bytes(res['data'])
    return filename,source

def cms_sync_submissions(exam_descriptor):
    SYNC_SUBMISSIONS = True
    SYNC_SUBMISSION_RESULTS = True
    SYNC_PARTICIPATIONS = True
    RE_SYNC_SUBMISSION_RESULTS = False
    count_subm = 0

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    for compet_type in (PJ,P1,P2,PS):

        # only PS
        if compet_type != PS:
            continue

        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)

        DB = CMS_DB[compet_type]
        cms_users = CMSuser.objects.all().using(DB)
        cms_participation = CMSparticipation.objects.all().using(DB)

        if SYNC_SUBMISSIONS:
            ## sync submissions
            print('sync submissions')
            cms_submissions = CMSsubmissions.objects.all().order_by('id').using(DB)
            local_submissions = LocalSubmissions.objects.filter(compet_type=compet_type,contest_id=contest_id)
            print('current cms_submissions:', len(cms_submissions))
            print('current local_submissions:', len(local_submissions))
            if len(cms_submissions) > len(local_submissions):
              for sub in cms_submissions:
                cms_user_id = sub.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                print('.', end='')
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                if not local_submissions.filter(compet_id=compet_id,submission_id=sub.id, contest_id=contest_id).exists():
                    # make timestamp zone aware
                    timestamp = utc.localize(sub.timestamp)
                    timestamp = timestamp.astimezone(brasilia)
                    filename,source = get_source_file(compet_type,sub)
                    local_sub = LocalSubmissions(
                        compet_id = compet_id,
                        compet_type = compet_type,
                        submission_id = sub.id,
                        contest_id = contest_id,
                        task_name = sub.task.name,
                        task_title = sub.task.title,
                        timestamp = timestamp,
                        language = sub.language,
                        source = source,
                        filename = filename,
                        comment = sub.comment,
                        official = sub.official)
                    # print(f'compet_id={compet_id}, submission_id={local_sub.submission_id}, language={local_sub.language}, contes_id={local_sub.contest_id}')
                    print('+', end='')
                    local_sub.save()
                    count_subm += 1
              print('\n  retrieved', count_subm, 'new submissions')

            # for sub in local_submissions:
            #     #if not cms_submissions.filter(id=sub.submission_id).exists():
            #     tmp = cms_submissions.filter(id=sub.submission_id)
            #     if len(tmp) > 1:
            #         print('extra local submission', sub.submission_id, sub.compet_id, sub.task_name)
            #         extra = ExtraLocalSubmissions(
            #             compet_id = sub.compet_id,
            #             compet_type = sub.compet_type,
            #             submission_id = sub.submission_id,
            #             contest_id = sub.contest_id,
            #             task_name = sub.task_name,
            #             task_title = sub.task_title,
            #             timestamp = sub.timestamp,
            #             language = sub.language,
            #             comment = sub.comment,
            #             official = sub.official,
            #             source = sub.source,
            #             filename = sub.filename
            #             )
            #         #extra.save()
            #         #sub.delete()

        if SYNC_SUBMISSION_RESULTS:
            #sync submission_results
            print('sync submission_results')
            cms_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(DB)
            local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet_type,contest_id=contest_id).order_by('id')
            print('current cms_submission_results:', len(cms_submission_results))
            print('current local_submission_results:', len(local_submission_results))
            count_subm_results = 0
            if RE_SYNC_SUBMISSION_RESULTS or len(cms_submission_results) != len(local_submission_results):

              for cms_res in cms_submission_results:
                cms_user_id = cms_res.submission.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue

                #if cms_user.username not in ('24077-I','26082-J','26118-E','26130-E','26135-J','26141-J','26142-C','36041-B','38653-J','53831-H','73458-E','100504-G','13572-D','13574-J','14623-J','26115-F','53832-A'):
                #    continue
                compet_id = int(cms_user.username.split('-')[0])

                if local_submission_results.filter(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id).exists() and not RE_SYNC_SUBMISSION_RESULTS:
                    continue

                try:
                    #print(f'get local sub compet_id={compet_id}')
                    print('.', end='')
                    local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id)
                except:
                    print('\n********** local_sub get failed, got results but not submission?')
                    print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                    continue

                if RE_SYNC_SUBMISSION_RESULTS:
                    print(f'get local sub result compet_id={compet_id}')
                    try:
                        # reusing db entry
                        print("resync reusing entry")
                        local_sub_result = LocalSubmissionResults.objects.get(submission_id=cms_res.submission_id,compet_id=compet_id,contest_id=contest_id)
                        local_sub_result.local_subm = local_sub
                        local_sub_result.compet_id = compet_id
                        local_sub_result.compilation_text = cms_res.compilation_text
                        local_sub_result.compilation_stdout = cms_res.compilation_stdout
                        local_sub_result.compilation_stderr = cms_res.compilation_stderr
                        local_sub_result.score = cms_res.score
                        local_sub_result.score_details = cms_res.score_details
                        local_sub_result.public_score = cms_res.public_score
                        local_sub_result.public_score_details = cms_res.public_score_details
                    except:
                        print('********** local_sub_result get failed')
                        print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                        continue
                else:
                    local_sub_result = LocalSubmissionResults(
                    local_subm = local_sub,
                    compet_id = compet_id,
                    compet_type = compet_type,
                    submission_id = cms_res.submission.id,
                    contest_id = contest_id,
                    compilation_text = cms_res.compilation_text,
                    compilation_stdout = cms_res.compilation_stdout,
                    compilation_stderr = cms_res.compilation_stderr,
                    score = cms_res.score,
                    score_details = cms_res.score_details,
                    public_score = cms_res.public_score,
                    public_score_details = cms_res.public_score_details)

                local_sub_result.save()
                count_subm_results += 1
                print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

            print('  retrieved', count_subm_results, "results")
            for local_res in local_submission_results:
                if not cms_submission_results.filter(submission_id=local_res.submission_id).exists():
                    print('extra local submission', local_res.submission_id, local_res.compet_id, local_res.public_score)


        if SYNC_PARTICIPATIONS:
            # sync participations, setting the exam status for the compet/contest
            print('sync participations', len(cms_participation))
            for partic in cms_participation:
                if partic.starting_time is None:
                    continue
                cms_user_id = partic.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])

                print('partic started',cms_user.username)
                # make starting_time zone aware
                starting_time = utc.localize(partic.starting_time)
                starting_time = starting_time.astimezone(brasilia)
                if partic.delay_time is not None:
                    delay_time = partic.delay_time
                else:
                    delay_time = timedelta(0)
                if partic.extra_time is not None:
                    extra_time = partic.extra_time
                else:
                    extra_time = timedelta(0)

                try:
                    exam = exam_obj.objects.get(compet_id=compet_id)
                except:
                    print('not in exam db', compet_id)
                    continue

                print('in exam db')
                changed = False
                fix_timezone = timedelta(hours=0)
                
                if exam.time_start is None:
                    # check exam started
                    print('cms exam start not recorded locally',cms_user.username,compet_type)
                    exam.time_start = starting_time - fix_timezone
                    logger.info('cms exam started for username=%s, compet_type=%s', cms_user.username, compet_type)
                    changed = True

                # check exam finished
                if exam.time_finish is None:
                    # print('exam finished not marked',cms_user.username,compet_type)
                    # print('starting_time:',starting_time)
                    # print('duration',timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]))
                    # print('delay_time',delay_time)
                    # print('extra_time',extra_time)
                    # print('now',make_aware(datetime.now()))
                    # print(starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0))
                    # print()


                    #if starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0):

                    exam.time_finish = starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - fix_timezone
                    logger.info('cms exam finished for username=%s, compet_type=%s', cms_user.username, compet_type)
                    print('cms exam finished for',cms_user.username,compet_type)
                    changed = True

                if changed:
                    pass
                    exam.save()



    return 0

def cms_sync_compet_submissions(exam_descriptor, compet_type, compet_id_full):
    SYNC_SUBMISSIONS = True
    SYNC_SUBMISSION_RESULTS = True
    SYNC_PARTICIPATIONS = False
    RE_SYNC_SUBMISSION_RESULTS = True
    count_subm = 0

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    compet_id = int(compet_id_full.split('-')[0])
    print(compet_id)
    import sys

    for compet_type in (compet_type,):
        #if compet_type == P2:
        #    contest_id=3

        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)

        DB = CMS_DB[compet_type]
        print('\n**********\nDB', DB)
        cms_users = CMSuser.objects.all().using(DB)
        cms_participations = CMSparticipation.objects.all().using(DB)

        cms_user = cms_users.get(username=compet_id_full)
        print("id",cms_user.id)
        cms_participation = cms_participations.get(user_id=cms_user.id)

        print(cms_participation)
        
        if SYNC_SUBMISSIONS:
            ## sync submissions
            print('sync submissions')
            cms_submissions = CMSsubmissions.objects.filter(participation_id=cms_participation.id).order_by('id').using(DB)
            local_submissions = LocalSubmissions.objects.filter(compet_id=compet_id,contest_id=contest_id)
            print('current cms_submissions:', len(cms_submissions))
            print('current local_submissions:', len(local_submissions))
            if len(cms_submissions) > len(local_submissions):
              for sub in cms_submissions:
                cms_user_id = sub.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                if not local_submissions.filter(compet_id=compet_id,submission_id=sub.id, contest_id=contest_id).exists():
                    # make timestamp zone aware
                    timestamp = utc.localize(sub.timestamp)
                    timestamp = timestamp.astimezone(brasilia)
                    filename,source = get_source_file(compet_type,sub)
                    local_sub = LocalSubmissions(
                        compet_id = compet_id,
                        compet_type = compet_type,
                        submission_id = sub.id,
                        contest_id = contest_id,
                        task_name = sub.task.name,
                        task_title = sub.task.title,
                        timestamp = timestamp,
                        language = sub.language,
                        source = source,
                        filename = filename,
                        comment = sub.comment,
                        official = sub.official)
                    print(f'compet_id={compet_id}, submission_id={local_sub.submission_id}, language={local_sub.language}, contes_id={local_sub.contest_id}')
                    local_sub.save()
                    count_subm += 1
              print('  retrieved', count_subm, 'new submissions')

        if SYNC_SUBMISSION_RESULTS:
            #sync submission_results
            print('sync submission_results')
            cms_submission_ids = cms_submissions.only("id")
            print(cms_submission_ids)
            compet_subm_ids = []
            for id in cms_submission_ids:
                compet_subm_ids.append(id.id)
            #cms_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(DB)
            cms_submission_results = CMSsubmissionResults.objects.filter(submission_id__in=compet_subm_ids).order_by('submission_id').using(DB)
            print(cms_submission_results)            
            local_submission_results = LocalSubmissionResults.objects.filter(compet_id=compet_id,contest_id=contest_id).order_by('id')
            print('current cms_submission_results:', len(cms_submission_results))
            print('current local_submission_results:', len(local_submission_results))
            count_subm_results = 0
            if RE_SYNC_SUBMISSION_RESULTS or len(cms_submission_results) != len(local_submission_results):
                
              for cms_res in cms_submission_results:
                print("==============",cms_res.score, cms_res.submission_id)
                cms_user_id = cms_res.submission.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                if local_submission_results.filter(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id).exists() and not RE_SYNC_SUBMISSION_RESULTS:
                    continue
                    
                try:
                    print(f'get local sub compet_id={compet_id}')
                    local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id)
                except:
                    print('********** local_sub get failed, got results but not submission?')
                    print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                    continue

                try:
                    local_sub_result = LocalSubmissionResults.objects.get(submission_id=cms_res.submission_id,compet_id=compet_id,contest_id=contest_id)
                except:
                    print('********** local_sub_result get failed')
                    print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                    local_sub_result = LocalSubmissionResults()

                local_sub_result.submission_id=cms_res.submission_id
                local_sub_result.compet_id = compet_id
                local_sub_result.compet_type = compet_type
                local_sub_result.local_subm = local_sub
                local_sub_result.contest_id = contest_id
                local_sub_result.compilation_text = cms_res.compilation_text
                local_sub_result.compilation_stdout = cms_res.compilation_stdout
                local_sub_result.compilation_stderr = cms_res.compilation_stderr
                local_sub_result.score = cms_res.score
                local_sub_result.score_details = cms_res.score_details
                local_sub_result.public_score = cms_res.public_score
                local_sub_result.public_score_details = cms_res.public_score_details

                local_sub_result.save()
                count_subm_results += 1
                print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

            print('  retrieved', count_subm_results, "results")
            for local_res in local_submission_results:
                if not cms_submission_results.filter(submission_id=local_res.submission_id).exists():
                    print('extra local submission', local_res.submission_id, local_res.compet_id, local_res.public_score)


        if SYNC_PARTICIPATIONS:
            # sync participations, setting the exam status for the compet/contest
            print('sync participations')
            for partic in cms_participation:
                if partic.starting_time is None:
                    continue
                cms_user_id = partic.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])

                #print('partic started',cms_user.username)
                # make starting_time zone aware
                starting_time = utc.localize(partic.starting_time)
                starting_time = starting_time.astimezone(brasilia)
                if partic.delay_time is not None:
                    delay_time = partic.delay_time
                else:
                    delay_time = timedelta(0)
                if partic.extra_time is not None:
                    extra_time = partic.extra_time
                else:
                    extra_time = timedelta(0)

                try:
                    exam = exam_obj.objects.get(compet_id=compet_id)
                except:
                    print('not in exam db', compet_id)
                    continue

                changed = False
                fix_timezone = timedelta(hours=0)
                if exam.time_start is None:
                    # check exam started
                    print('cms exam start not recorded locally',cms_user.username,compet_type)
                    exam.time_start = starting_time - fix_timezone
                    logger.info('cms exam started for username=%s, compet_type=%s', cms_user.username, compet_type)
                    changed = True

                # check exam finished
                if exam.time_finish is None:
                    # print('exam finished not marked',cms_user.username,compet_type)
                    # print('starting_time:',starting_time)
                    # print('duration',timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]))
                    # print('delay_time',delay_time)
                    # print('extra_time',extra_time)
                    # print('now',make_aware(datetime.now()))
                    # print(starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0))
                    # print()
                    if starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0):
                        exam.time_finish = starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - fix_timezone
                        logger.info('cms exam finished for username=%s, compet_type=%s', cms_user.username, compet_type)
                        print('cms exam finished for',cms_user.username,compet_type)
                        changed = True
                if changed:
                    exam.save()



    return 0

def cms_sync_all_autojudge_submissions(exam_descriptor):
    SYNC_SUBMISSIONS = True
    SYNC_SUBMISSION_RESULTS = True
    SYNC_PARTICIPATIONS = True

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    for compet_type in (PJ,P1,P2):
        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)

        DB = CMS_DB[compet_type]
        cms_users = CMSuser.objects.all().using(DB)
        cms_special_users = [user.id for user in cms_users.filter(username__in=['00000-J','00001-C','00000-A','00000-B'])]

        if SYNC_SUBMISSIONS:
            ## sync submissions
            print('sync submissions')
            cms_submissions = CMSsubmissions.objects.all().exclude(participation__user_id__in=cms_special_users).order_by('id').using(DB)
            local_submissions = LocalSubmissions.objects.filter(compet_type=compet_type,contest_id=contest_id)

            print('current cms_submissions:', len(cms_submissions))
            print('current local_submissions:', len(local_submissions))

            count_subm = 0
            if len(cms_submissions) > len(local_submissions):
                for cms_sub in cms_submissions:
                    cms_user = cms_users.get(id=cms_sub.participation.user_id)
                    compet_id = int(cms_user.username.split('-')[0])

                    if not local_submissions.filter(compet_id=compet_id,submission_id=cms_sub.id, contest_id=contest_id).exists():
                        # make timestamp zone aware
                        timestamp = utc.localize(cms_sub.timestamp)
                        timestamp = timestamp.astimezone(brasilia)
                        filename,source = get_source_file(compet_type,cms_sub)
                        local_sub = LocalSubmissions(
                            compet_id = compet_id,
                            compet_type = compet_type,
                            submission_id = cms_sub.id,
                            contest_id = contest_id,
                            task_name = cms_sub.task.name,
                            task_title = cms_sub.task.title,
                            timestamp = timestamp,
                            language = cms_sub.language,
                            source = source,
                            filename = filename,
                            comment = cms_sub.comment,
                            official = cms_sub.official)
                        print(f'compet_id={compet_id}, submission_id={local_sub.submission_id}, language={local_sub.language}, contest_id={local_sub.contest_id}')
                        local_sub.save()
                        count_subm += 1
            print('  retrieved', count_subm, 'new submissions')

        if SYNC_SUBMISSION_RESULTS:
            #sync submission_results
            print('sync submission_results')
            cms_all_autojudge_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(DB)

            task_ids = set(cms_all_autojudge_submission_results.values_list('dataset__task_id',flat=True))
            datasets = CMSdataset.objects.filter(id__in=set(cms_all_autojudge_submission_results.values_list('dataset',flat=True))).using(DB)

            for task_id in task_ids:
                task_datasets = datasets.filter(task_id=task_id).order_by('id')

                if len(task_datasets) > 1:
                    # If a task has multiple datasets, only keeps the ones where autojudge is enabled
                    task_datasets_autojudge_disabled = task_datasets.filter(autojudge=False)
                    cms_all_autojudge_submission_results = cms_all_autojudge_submission_results.exclude(dataset__in=task_datasets_autojudge_disabled)
                    task_datasets = task_datasets.filter(autojudge=True)

                    score_details_first = CMSsubmissionResults.objects.filter(dataset=task_datasets.first()).using(DB).first().score_details
                    score_details_last = CMSsubmissionResults.objects.filter(dataset=task_datasets.last()).using(DB).first().score_details

                    max_scores_first = [sd['max_score'] for sd in score_details_first]
                    max_scores_last = [sd['max_score'] for sd in score_details_last]

                    # If max scores have changed, keep only latest dataset
                    if max_scores_first !=  max_scores_last:
                        excluded_datasets = task_datasets.exclude(id=task_datasets.last().id)
                        cms_all_autojudge_submission_results = cms_all_autojudge_submission_results.exclude(dataset__in=excluded_datasets)

            cms_submissions = CMSsubmissions.objects.all().exclude(participation__user_id__in=cms_special_users).order_by('id').using(DB)

            # Use all autojudge datasets to find the best result
            cms_submission_results = [cms_all_autojudge_submission_results.filter(submission=cms_sub).order_by('-score', '-dataset__id').using(DB).first() for cms_sub in cms_submissions]

            local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet_type,contest_id=contest_id).order_by('id')

            print('current cms_submission_results:', len(cms_submission_results))
            print('current local_submission_results:', len(local_submission_results))

            count_subm_results = 0
            if len(cms_submission_results) != len(local_submission_results):
                for cms_sub_result in cms_submission_results:
                    cms_sub = cms_sub_result.submission
                    cms_user = cms_users.get(id=cms_sub.participation.user_id)
                    compet_id = int(cms_user.username.split('-')[0])

                    if local_submission_results.filter(compet_id=compet_id,submission_id=cms_sub.id,dataset_id=cms_sub_result.dataset_id,contest_id=contest_id).exists():
                        continue

                    try:
                        local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=cms_sub.id,contest_id=contest_id)
                    except:
                        print('********** local_sub get failed, got results but not submission?')
                        print("compet_id = ", compet_id, 'submission_id =',cms_sub.id, 'contest_id =', contest_id)
                        continue

                    local_sub_result = LocalSubmissionResults(
                        local_subm = local_sub,
                        compet_id = compet_id,
                        compet_type = compet_type,
                        submission_id = cms_sub.id,
                        dataset_id = cms_sub_result.dataset.id,
                        contest_id = contest_id,
                        compilation_text = cms_sub_result.compilation_text,
                        compilation_stdout = cms_sub_result.compilation_stdout,
                        compilation_stderr = cms_sub_result.compilation_stderr,
                        score = cms_sub_result.score,
                        score_details = cms_sub_result.score_details,
                        public_score = cms_sub_result.public_score,
                        public_score_details = cms_sub_result.public_score_details)

                    local_sub_result.save()
                    count_subm_results += 1
                    print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

            print('  retrieved', count_subm_results, "results")

            cms_sub_res = [(csr.submission_id, csr.dataset_id) for csr in cms_submission_results]
            for local_sub_result in local_submission_results:
                #if not cms_submission_results.filter(submission_id=local_sub_result.submission_id).exists():
                if not (local_sub_result.submission_id, local_sub_result.dataset_id) in cms_sub_res:
                    print('extra local submission', local_sub_result.submission_id, local_sub_result.compet_id, local_sub_result.public_score)

        if SYNC_PARTICIPATIONS:
            # sync participations, setting the exam status for the compet/contest
            print('sync participations')
            cms_participation = CMSparticipation.objects.all().exclude(user_id__in=cms_special_users).using(DB)

            for partic in cms_participation:
                if partic.starting_time is None:
                    continue
                cms_user = cms_users.get(id=partic.user_id)
                compet_id = int(cms_user.username.split('-')[0])

                # make starting_time zone aware
                starting_time = utc.localize(partic.starting_time)
                starting_time = starting_time.astimezone(brasilia)
                if partic.delay_time is not None:
                    delay_time = partic.delay_time
                else:
                    delay_time = timedelta(0)
                if partic.extra_time is not None:
                    extra_time = partic.extra_time
                else:
                    extra_time = timedelta(0)

                try:
                    exam = exam_obj.objects.get(compet_id=compet_id)
                except:
                    print('not in exam db', compet_id)
                    continue

                changed = False
                fix_timezone = timedelta(hours=0)
                if exam.time_start is None:
                    # check exam started
                    print('cms exam start not recorded locally',cms_user.username,compet_type)
                    exam.time_start = starting_time - fix_timezone
                    logger.info('cms exam started for username=%s, compet_type=%s', cms_user.username, compet_type)
                    changed = True

                # check exam finished
                if exam.time_finish is None:
                    if starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0):
                        exam.time_finish = starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - fix_timezone
                        logger.info('cms exam finished for username=%s, compet_type=%s', cms_user.username, compet_type)
                        print('cms exam finished for',cms_user.username,compet_type)
                        changed = True
                if changed:
                    exam.save()

    return 0

def cms_test():
    '''Test
    '''
    compet_type=3
    submissions = CMSsubmissions.objects.all().using(DB)
    #print(submissions)
    for s in submissions:
        #print(s)
        print(s.id)
        filename,source = get_source_file(compet_type=compet_type,submission=s)
        print(filename)
        print(source)
        print()

def cms_update_submissions(exam_descriptor):
    SYNC_SUBMISSIONS = False
    SYNC_SUBMISSION_RESULTS = True
    SYNC_PARTICIPATIONS = False

    USERNAMES = ('37116-D','04773-H', '26443-I')
    count_subm = 0

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    for compet_type in (P2,):

        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)

        DB = CMS_DB[compet_type]
        cms_users = CMSuser.objects.all().using(DB)
        cms_participation = CMSparticipation.objects.all().using(DB)

        if SYNC_SUBMISSIONS:
            ## sync submissions
            print('sync submissions')
            cms_submissions = CMSsubmissions.objects.all().order_by('id').using(DB)
            local_submissions = LocalSubmissions.objects.filter(compet_type=compet_type,contest_id=contest_id)
            print('current cms_submissions:', len(cms_submissions))
            print('current local_submissions:', len(local_submissions))
            #if len(cms_submissions) > len(local_submissions):
            if True:
              for sub in cms_submissions:
                cms_user_id = sub.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                if cms_user.username not in USERNAMES:
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                if not local_submissions.filter(compet_id=compet_id,submission_id=sub.id, contest_id=contest_id).exists():
                    # make timestamp zone aware
                    timestamp = utc.localize(sub.timestamp)
                    timestamp = timestamp.astimezone(brasilia)
                    filename,source = get_source_file(compet_type,sub)
                    local_sub = LocalSubmissions(
                        compet_id = compet_id,
                        compet_type = compet_type,
                        submission_id = sub.id,
                        contest_id = contest_id,
                        task_name = sub.task.name,
                        task_title = sub.task.title,
                        timestamp = timestamp,
                        language = sub.language,
                        source = source,
                        filename = filename,
                        comment = sub.comment,
                        official = sub.official)
                    print(f'compet_id={compet_id}, submission_id={local_sub.submission_id}, language={local_sub.language}, contes_id={local_sub.contest_id}')
                    local_sub.save()
                    count_subm += 1
                else:
                    timestamp = utc.localize(sub.timestamp)
                    timestamp = timestamp.astimezone(brasilia)
                    filename,source = get_source_file(compet_type,sub)
                    local_sub = local_submissions.get(compet_id=compet_id,submission_id=sub.id, contest_id=contest_id)
                    local_sub.compet_type = compet_type
                    local_sub.submission_id = sub.id
                    local_sub.contest_id = contest_id
                    local_sub.task_name = sub.task.name
                    local_sub.task_title = sub.task.title
                    local_sub.timestamp = timestamp
                    local_sub.language = sub.language
                    local_sub.source = source
                    local_sub.filename = filename
                    local_sub.comment = sub.comment
                    local_sub.official = sub.official
                    print(f'compet_id={compet_id}, submission_id={local_sub.submission_id}, language={local_sub.language}, contes_id={local_sub.contest_id}')
                    local_sub.save()
                    count_subm += 1

              print('  retrieved', count_subm, 'new submissions')


            # for sub in local_submissions:
            #     #if not cms_submissions.filter(id=sub.submission_id).exists():
            #     tmp = cms_submissions.filter(id=sub.submission_id)
            #     if len(tmp) > 1:
            #         print('extra local submission', sub.submission_id, sub.compet_id, sub.task_name)
            #         extra = ExtraLocalSubmissions(
            #             compet_id = sub.compet_id,
            #             compet_type = sub.compet_type,
            #             submission_id = sub.submission_id,
            #             contest_id = sub.contest_id,
            #             task_name = sub.task_name,
            #             task_title = sub.task_title,
            #             timestamp = sub.timestamp,
            #             language = sub.language,
            #             comment = sub.comment,
            #             official = sub.official,
            #             source = sub.source,
            #             filename = sub.filename
            #             )
            #         #extra.save()
            #         #sub.delete()

        if SYNC_SUBMISSION_RESULTS:
            #sync submission_results
            print('sync submission_results')
            cms_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(DB)
            local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet_type,contest_id=contest_id).order_by('id')
            print('current cms_submission_results:', len(cms_submission_results))
            print('current local_submission_results:', len(local_submission_results))
            count_subm_results = 0
            #if len(cms_submission_results) != len(local_submission_results):
            if True:
              for sub in cms_submission_results:
                cms_user_id = sub.submission.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                if cms_user.username not in USERNAMES:
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                print('compet_id:',compet_id, 'submission_id:',sub.submission_id, 'contest_id', contest_id)

                try:
                    local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id)
                except:
                    print('********** local_sub get failed, got results but not submission?')
                    print(cms_user.username, 'submission_id =',sub.submission_id, 'contest_id =', contest_id)
                    continue

                if local_submission_results.filter(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id).exists():
                    # update
                    local_sub_result = local_submission_results.get(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id)
                    local_sub_result.local_subm = local_sub
                    local_sub_result.compet_id = compet_id
                    local_sub_result.compet_type = compet_type
                    local_sub_result.submission_id = sub.submission.id
                    local_sub_result.contest_id = contest_id
                    local_sub_result.compilation_text = sub.compilation_text
                    local_sub_result.compilation_stdout = sub.compilation_stdout
                    local_sub_result.compilation_stderr = sub.compilation_stderr
                    local_sub_result.score = sub.score
                    local_sub_result.score_details = sub.score_details
                    local_sub_result.public_score = sub.public_score
                    local_sub_result.public_score_details = sub.public_score_details
                    local_sub_result.save()
                    count_subm_results += 1
                    print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

                else:
                    local_sub_result = LocalSubmissionResults(
                        local_subm = local_sub,
                        compet_id = compet_id,
                        compet_type = compet_type,
                        submission_id = sub.submission.id,
                        contest_id = contest_id,
                        compilation_text = sub.compilation_text,
                        compilation_stdout = sub.compilation_stdout,
                        compilation_stderr = sub.compilation_stderr,
                        score = sub.score,
                        score_details = sub.score_details,
                        public_score = sub.public_score,
                        public_score_details = sub.public_score_details)
                    local_sub_result.save()
                    count_subm_results += 1
                    print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

            print('  retrieved', count_subm_results, "results")
            for sub in local_submission_results:
                if not cms_submission_results.filter(submission_id=sub.submission_id).exists():
                    print('extra local submission', sub.submission_id, sub.compet_id, sub.public_score)


        if SYNC_PARTICIPATIONS:
            # sync participations, setting the exam status for the compet/contest
            print('sync participations')
            for partic in cms_participation:
                if partic.starting_time is None:
                    continue
                cms_user_id = partic.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                if cms_user.username not in USERNAMES:
                    continue
                compet_id = int(cms_user.username.split('-')[0])

                #print('partic started',cms_user.username)
                # make starting_time zone aware
                starting_time = utc.localize(partic.starting_time)
                starting_time = starting_time.astimezone(brasilia)
                if partic.delay_time is not None:
                    delay_time = partic.delay_time
                else:
                    delay_time = timedelta(0)
                if partic.extra_time is not None:
                    extra_time = partic.extra_time
                else:
                    extra_time = timedelta(0)

                exam = exam_obj.objects.get(compet_id=compet_id)
                if exam.time_start is not None:
                    continue

                changed = False
                # check exam started
                fix_timezone = timedelta(hours=0)

                print('cms exam start not recorded locally',cms_user.username,compet_type)
                exam.time_start = starting_time - fix_timezone
                logger.info('cms exam started for username=%s, compet_type=%s', cms_user.username, compet_type)
                changed = True

                # check exam finished
                #print(cms_user.username, exam.time_finish)
                #
                if exam.time_finish is not None:
                    continue

                # print('exam finished not marked',cms_user.username,compet_type)
                # print('starting_time:',starting_time)
                # print('duration',timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]))
                # print('delay_time',delay_time)
                # print('extra_time',extra_time)
                # print('now',make_aware(datetime.now()))
                # print(starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0))
                # print()
                if starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0):
                    exam.time_finish = starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - fix_timezone
                    logger.info('cms exam finished for username=%s, compet_type=%s', cms_user.username, compet_type)
                    print('cms exam finished for',cms_user.username,compet_type)
                    changed = True
                if changed:
                    exam.save()
    return 0


def cms_modify_submissions(exam_descriptor):
    TASK_NAME = 'var'
    NEW_TASK_NAME = 'video'
    LANGUAGE = 'Java / JDK'
    USERNAMES = () #('18428-A',)
    count_subm = 0

    #task = CMStask.objects.get(name=TASK_NAME)

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    for compet_type in (P1,):
        try:
            os.mkdir(str(compet_type))
        except:
            pass
        level_name = LEVEL_NAME[compet_type].lower()

        DB = CMS_DB[compet_type]
        cms_users = CMSuser.objects.all().using(DB)
        cms_participation = CMSparticipation.objects.all().using(DB)

        tasks = CMStask.objects.all().using(DB)
        task = tasks.get(name=TASK_NAME)

        print('submissions')
        cms_submissions = CMSsubmissions.objects.filter(task_id=task.id).order_by('id').using(DB)
        cms_submission_results = CMSsubmissionResults.objects.filter(submission__task_id=task.id, submission__language=LANGUAGE).order_by('submission_id').using(DB)
        print('current cms_submissions:', len(cms_submissions))
        print('current cms_submission_results:', len(cms_submission_results))

        for cms_submission_result in cms_submission_results:
            if cms_submission_result.score and cms_submission_result.score > 0:
                continue
            sub = cms_submission_result.submission
            cms_user_id = sub.participation.user_id
            cms_user = cms_users.get(id=cms_user_id)
            if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                continue
            compet_id = int(cms_user.username.split('-')[0])
            filename,source = get_source_file(compet_type,sub)
            print(f'compet_id={compet_id}, sub.id={sub.id}, language={sub.language}')
            #print(source)
            try:
                os.mkdir(os.path.join(str(compet_type), cms_user.username))
            except:
                pass
            if not os.path.exists(os.path.join(str(compet_type), cms_user.username, f'{NEW_TASK_NAME}.java')):
                with open(os.path.join(str(compet_type), cms_user.username, f'{NEW_TASK_NAME}.java'),"wb") as f:
                    f.write(source)
            else:
                for i in range(1,50):
                    if not os.path.exists(os.path.join(str(compet_type), cms_user.username, f'{NEW_TASK_NAME}_{i}.java')):
                        with open(os.path.join(str(compet_type), cms_user.username, f'{NEW_TASK_NAME}_{i}.java'),"wb") as f:
                            f.write(source)
                        break
            count_subm += 1
        print(count_subm)
    return 0


def cms_resync_submissions(contest_id):
    count_subm = 0

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    EXAM_NAMES = {1: 'provaf1'}
    exam_descriptor = EXAM_NAMES[contest_id]
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)

    for compet_type in (PS,):
        if compet_type == P2:
            contest_id=3

        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)
        cms_users = CMSuser.objects.all().using(CMS_DB[compet_type])
        cms_participation = CMSparticipation.objects.all().using(CMS_DB[compet_type])

        ## sync submission_results
        print('sync submission_results')
        cms_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(CMS_DB[compet_type])
        local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet_type,contest_id=contest_id).order_by('id')
        print('current cms_submission_results:', len(cms_submission_results))
        print('current local_submission_results:', len(local_submission_results))
        count_subm_results = 0
        for sub in cms_submission_results:
            if sub.dataset_id != 5:
                continue
            cms_user_id = sub.submission.participation.user_id
            cms_user = cms_users.get(id=cms_user_id)
            compet_id = int(cms_user.username.split('-')[0])
            #print('compet_id:',compet_id, 'submission_id:',sub.submission_id, 'contest_id', contest_id, 'dataset_id', sub.dataset_id)

            try:
                local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id)
            except:
                local_sub = LocalSubmissions.objects.filter(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id)
                print('********** local_sub get failed, got results but not submission?')
                print(cms_user.username, 'submission_id =',sub.submission_id, 'contest_id =', contest_id)
                continue

            try:
                local_sub_results = LocalSubmissionResults.objects.get(compet_id=compet_id,submission_id=sub.submission_id, contest_id=contest_id)
            except:
                print('********** local_sub_results get failed, no results for this submission?')
                print(cms_user.username, 'submission_id =',sub.submission_id, 'contest_id =', contest_id)
                continue

            if sub.score == None:
                print('********** cms sub.score is null, no results for this submission?\n  ',
                      cms_user.username, 'submission_id =',sub.submission_id, 'contest_id =', contest_id)
                if local_sub_results.score == None:
                    print('********** local sub.score is not null!', local_sub_results.score,'\n  ',
                          cms_user.username, 'submission_id =',sub.submission_id, 'contest_id =', contest_id)
                continue

            # update if score is greater
            if sub.score > local_sub_results.score:
                print(cms_user.username,'submission_id =',sub.submission_id,local_sub_results.score,'->',sub.score)
                local_sub_results.compilation_text = sub.compilation_text
                local_sub_results.compilation_stdout = sub.compilation_stdout
                local_sub_results.compilation_stderr = sub.compilation_stderr
                local_sub_results.score = sub.score
                local_sub_results.score_details = sub.score_details
                local_sub_results.public_score = sub.public_score
                local_sub_results.public_score_details = sub.public_score_details


                local_sub_results.save()
                count_subm_results += 1

        print('  updated', count_subm_results, "results")
        for sub in local_submission_results:
            if not cms_submission_results.filter(submission_id=sub.submission_id).exists():
                print('extra local submission', sub.submission_id, sub.compet_id, sub.public_score)


    return 0


def cms_check_synched_submissions(exam_descriptor):
    SYNC_SUBMISSIONS = True
    SYNC_SUBMISSION_RESULTS = False
    SYNC_PARTICIPATIONS = False
    RE_SYNC_SUBMISSION_RESULTS = False
    count_subm = 0
    count_test_subm = 0

    # to localize times
    utc = timezone('utc')
    brasilia = timezone('America/Sao_Paulo')

    # to check end of contest time for participants
    print('exam_descriptor',exam_descriptor)
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    print('exam_obj',exam_obj)
    contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    print('contest_id',contest_id)

    
    for compet_type in (PJ,P1,P2,PS):

        if compet_type != PJ:
            continue

        level_name = LEVEL_NAME[compet_type].lower()
        print('\n**********\ncompet_type', compet_type, level_name)

        DB = CMS_DB[compet_type]
        cms_users = CMSuser.objects.all().using(DB)
        cms_participation = CMSparticipation.objects.all().using(DB)

        if SYNC_SUBMISSIONS:
            ## sync submissions
            print('sync submissions')
            cms_submissions = CMSsubmissions.objects.all().order_by('id').using(DB)
            local_submissions = LocalSubmissions.objects.filter(compet_type=compet_type,contest_id=contest_id)
            print('current cms_submissions:', len(cms_submissions))
            print('current local_submissions:', len(local_submissions))
            for sub in cms_submissions:
                cms_user_id = sub.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    count_test_subm += 1
                    continue
                compet_id = int(cms_user.username.split('-')[0])
                if not local_submissions.filter(compet_id=compet_id,submission_id=sub.id, contest_id=contest_id).exists():
                    print(f'missing submission for compet_id {compet_id}, submission {sub.id}, language={sub.language}')
                    filename,source = get_source_file(compet_type,sub)    
                    count_subm += 1
            if count_subm > 0:
                print(f'missing {count_subm} submissions')
            print('current cms_submissions without test users:', len(cms_submissions)-count_test_subm)
            print('current local_submissions:', len(local_submissions))

                
            # for sub in local_submissions:
            #     #if not cms_submissions.filter(id=sub.submission_id).exists():
            #     tmp = cms_submissions.filter(id=sub.submission_id)
            #     if len(tmp) > 1:
            #         print('extra local submission', sub.submission_id, sub.compet_id, sub.task_name)
            #         extra = ExtraLocalSubmissions(
            #             compet_id = sub.compet_id,
            #             compet_type = sub.compet_type,
            #             submission_id = sub.submission_id,
            #             contest_id = sub.contest_id,
            #             task_name = sub.task_name,
            #             task_title = sub.task_title,
            #             timestamp = sub.timestamp,
            #             language = sub.language,
            #             comment = sub.comment,
            #             official = sub.official,
            #             source = sub.source,
            #             filename = sub.filename
            #             )
            #         #extra.save()
            #         #sub.delete()

        if SYNC_SUBMISSION_RESULTS:
            #sync submission_results
            print('sync submission_results')
            cms_submission_results = CMSsubmissionResults.objects.all().order_by('submission_id').using(DB)
            local_submission_results = LocalSubmissionResults.objects.filter(compet_type=compet_type,contest_id=contest_id).order_by('id')
            print('current cms_submission_results:', len(cms_submission_results))
            print('current local_submission_results:', len(local_submission_results))
            count_subm_results = 0
            if RE_SYNC_SUBMISSION_RESULTS or len(cms_submission_results) != len(local_submission_results):

              for cms_res in cms_submission_results:
                cms_user_id = cms_res.submission.participation.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue

                #if cms_user.username not in ('24077-I','26082-J','26118-E','26130-E','26135-J','26141-J','26142-C','36041-B','38653-J','53831-H','73458-E','100504-G','13572-D','13574-J','14623-J','26115-F','53832-A'):
                #    continue
                compet_id = int(cms_user.username.split('-')[0])

                if local_submission_results.filter(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id).exists() and not RE_SYNC_SUBMISSION_RESULTS:
                    continue

                try:
                    #print(f'get local sub compet_id={compet_id}')
                    print('.', end='')
                    local_sub = LocalSubmissions.objects.get(compet_id=compet_id,submission_id=cms_res.submission_id, contest_id=contest_id)
                except:
                    print('\n********** local_sub get failed, got results but not submission?')
                    print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                    continue

                if RE_SYNC_SUBMISSION_RESULTS:
                    print(f'get local sub result compet_id={compet_id}')
                    try:
                        # reusing db entry
                        print("resync reusing entry")
                        local_sub_result = LocalSubmissionResults.objects.get(submission_id=cms_res.submission_id,compet_id=compet_id,contest_id=contest_id)
                        local_sub_result.local_subm = local_sub
                        local_sub_result.compet_id = compet_id
                        local_sub_result.compilation_text = cms_res.compilation_text
                        local_sub_result.compilation_stdout = cms_res.compilation_stdout
                        local_sub_result.compilation_stderr = cms_res.compilation_stderr
                        local_sub_result.score = cms_res.score
                        local_sub_result.score_details = cms_res.score_details
                        local_sub_result.public_score = cms_res.public_score
                        local_sub_result.public_score_details = cms_res.public_score_details
                    except:
                        print('********** local_sub_result get failed')
                        print("compet_id = ", compet_id, 'submission_id =',cms_res.submission_id, 'contest_id =', contest_id)
                        continue
                else:
                    local_sub_result = LocalSubmissionResults(
                    local_subm = local_sub,
                    compet_id = compet_id,
                    compet_type = compet_type,
                    submission_id = cms_res.submission.id,
                    contest_id = contest_id,
                    compilation_text = cms_res.compilation_text,
                    compilation_stdout = cms_res.compilation_stdout,
                    compilation_stderr = cms_res.compilation_stderr,
                    score = cms_res.score,
                    score_details = cms_res.score_details,
                    public_score = cms_res.public_score,
                    public_score_details = cms_res.public_score_details)

                local_sub_result.save()
                count_subm_results += 1
                print(f'compet_id={compet_id}, submission_id={local_sub_result.submission_id}, score={local_sub_result.score}')

            print('  retrieved', count_subm_results, "results")
            for local_res in local_submission_results:
                if not cms_submission_results.filter(submission_id=local_res.submission_id).exists():
                    print('extra local submission', local_res.submission_id, local_res.compet_id, local_res.public_score)


        if SYNC_PARTICIPATIONS:
            # sync participations, setting the exam status for the compet/contest
            print('sync participations', len(cms_participation))
            for partic in cms_participation:
                if partic.starting_time is None:
                    continue
                cms_user_id = partic.user_id
                cms_user = cms_users.get(id=cms_user_id)
                if cms_user.username in ('00000-J','00001-C','00000-A','00000-B'):
                    continue
                compet_id = int(cms_user.username.split('-')[0])

                print('partic started',cms_user.username)
                # make starting_time zone aware
                starting_time = utc.localize(partic.starting_time)
                starting_time = starting_time.astimezone(brasilia)
                if partic.delay_time is not None:
                    delay_time = partic.delay_time
                else:
                    delay_time = timedelta(0)
                if partic.extra_time is not None:
                    extra_time = partic.extra_time
                else:
                    extra_time = timedelta(0)

                try:
                    exam = exam_obj.objects.get(compet_id=compet_id)
                except:
                    print('not in exam db', compet_id)
                    continue

                print('in exam db')
                changed = False
                fix_timezone = timedelta(hours=0)
                
                if exam.time_start is None:
                    # check exam started
                    print('cms exam start not recorded locally',cms_user.username,compet_type)
                    exam.time_start = starting_time - fix_timezone
                    logger.info('cms exam started for username=%s, compet_type=%s', cms_user.username, compet_type)
                    changed = True

                # check exam finished
                if exam.time_finish is None:
                    # print('exam finished not marked',cms_user.username,compet_type)
                    # print('starting_time:',starting_time)
                    # print('duration',timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]))
                    # print('delay_time',delay_time)
                    # print('extra_time',extra_time)
                    # print('now',make_aware(datetime.now()))
                    # print(starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0))
                    # print()


                    #if starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - make_aware(datetime.now()) < timedelta(0):

                    exam.time_finish = starting_time + timedelta(minutes=EXAMS[exam_descriptor]['exam_duration'][level_name]) + delay_time + extra_time - fix_timezone
                    logger.info('cms exam finished for username=%s, compet_type=%s', cms_user.username, compet_type)
                    print('cms exam finished for',cms_user.username,compet_type)
                    changed = True

                if changed:
                    pass
                    exam.save()



    return 0
