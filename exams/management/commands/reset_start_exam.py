import getopt
import os
import re
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware, timezone

from principal.models import LEVEL, Compet, School
from exams.models import Alternative, Question, Task
from exams.views import mark_exam
from exams.settings import EXAMS
from cms.models import (CMSuser, CMSparticipation, CMScommand, CMSsubmissions, CMSsubmissionResults,
                        CMSFiles, CMSFsobjects, 
                        LocalSubmissions, LocalSubmissionResults,
                        LocalFiles, LocalFsobjects)
from cms.utils import cms_do_renew_participation

def reset_start_exam(exam_descriptor,compet):
    exam_obj = EXAMS[exam_descriptor]['exam_object']
    exam = exam_obj.objects.get(compet_id=compet.compet_id)
    exam_contest_id = EXAMS[exam_descriptor]['exam_contest_id']
    if compet.compet_type == 4:
        exam_contest_id = 3
    else:
        exam_contest_id = 1
        
    exam.answers = None
    exam.correct_answers = None
    exam.num_correct_answers = None
    exam.shuffle_pattern = None
    exam.subm_remaining = None
    exam.time_start = None
    exam.time_finish = None
    exam.completed = None
    print('saving exam',file=sys.stderr)
    exam.save()
    ### TODO
    if compet.compet_type in (3,4,5,6):
        # remove cms_participation and local submissions
        local_submissions = LocalSubmissions.objects.filter(compet_id=compet.compet_id,compet_type=compet.compet_type,contest_id=exam_contest_id)
        for subm in local_submissions:
            subm.delete()
            print('cleaning submission',file=sys.stderr)
            subm.save()
        local_submission_results = LocalSubmissionResults.objects.filter(compet_id=compet.compet_id,compet_type=compet.compet_type,contest_id=exam_contest_id)
        for subm in local_submission_results:
            subm.delete()
            print('cleaning submission_results',file=sys.stderr)
            subm.save()
        # remove cms participation and add new cms participation
        print('renew participation',file=sys.stderr)
        cms_do_renew_participation(compet.compet_id_full, compet.compet_type, exam_contest_id)
        
    return 1

class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        exam_descriptor = options['descriptor'][0]
        level = options['level'][0]
        compet_id = int(options['compet_id'][0])
        compet_type = LEVEL[level.upper()]

        compet = Compet.objects.get(pk=compet_id,compet_type=compet_type)
        reset = reset_start_exam(exam_descriptor,compet)
        self.stdout.write(self.style.SUCCESS('Authorized {} exams.'.format(reset)))
