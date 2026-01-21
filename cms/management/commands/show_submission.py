import base64
import logging
import os
import re
import shutil
import sys
from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetCfObi, LEVEL, PJ, P1, P2, PS, CF
#from cfobi.models import CompetCfObi
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS
from cms.check_duplicates import check_duplicates
from obi.settings import BASE_DIR

logger = logging.getLogger(__name__)

#BASE = '/ext/submissions'
LANG = ["c", "cpp", "java", "js", "py"]
JLANG = ["c/c++", "c/c++", "java19", "text", "text", "python3"]
COMPET_LEVEL = {3:"P1", 4:"P2", 5:"PJ", 6:"PS", 8:"CF"}

#EXCEPT_TASKS = ["festa","pizzaria","leite","dieta"] 
EXCEPT_TASKS = []
PHASE = 1

problem_names = set()

def get_submission(contest_id, submission_id):
    print("get submission")    
    local_submission = LocalSubmissions.objects.filter(contest_id=contest_id, id=submission_id)
    print('len(local_submission)',len(local_submission))
    compet_id = 'not found'
    task_name = ''
    source = ''
    for sub in local_submission:
        # keep only the last submission, overwrite older ones
        #filename = f'{sub.compet_id}-{sub.task_name}-{sub.submission_id}.{EXTENSIONS[sub.language]}'
        short_filename = f'{sub.compet_id}-{sub.task_name}.{EXTENSIONS[sub.language]}'
        
        if sub.compet_id <= 1:
            # test users
            continue

        #print(sub.task_name, end=' ')
        if sub.task_name in EXCEPT_TASKS:
            continue
        # group C and C++ together
        if sub.language.find("C")==0:
            sub.language = 'C++20 / g++'
        compet_id = sub.compet_id
        task_name = f'{sub.task_name}.{EXTENSIONS[sub.language]}'
        source = bytes(sub.source).decode("utf-8")

    return compet_id, task_name, source

    
class Command(BaseCommand):
    help = 'Check exact copy'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)
        parser.add_argument('submission_id', nargs='+', type=int)

    def handle(self, *args, **options):
        contest_id = options['contest_id'][0]
        submission_id = options['submission_id'][0]

        compet_id, task_name, source = get_submission(contest_id, submission_id)
        print(compet_id, task_name)
        print(source)
        print()
