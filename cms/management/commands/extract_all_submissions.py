import base64
import logging
import os
import shutil
from time import sleep

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL, PJ, P1, P2, PS
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions
from cms.utils import EXTENSIONS

logger = logging.getLogger(__name__)

BASE = '/ext/submissions/fase1'
EXCLUDE = ['ogro','bacterias']

problem_names = set()

def extract_submissions(contest_id):
    count = 0

    shutil.rmtree(BASE)

    try:
        os.mkdir(BASE)
    except:
        pass

    for l in EXTENSIONS.keys():
        if l == 'c':
            continue
        os.mkdir(os.path.join(BASE,EXTENSIONS[l]))

    local_submissions = LocalSubmissions.objects.filter(contest_id=contest_id).order_by('submission_id')
    #compets = Compet.objects.filter(compet_type=level)
    for sub in local_submissions:
        # keep only the last submission, overwrite older ones
        #filename = f'{sub.compet_id}-{sub.task_name}-{sub.submission_id}.{EXTENSIONS[sub.language]}'
        
        # group C and C++ together
        if sub.language.find("C")==0:
            sub.language = 'C++17 / g++'
        filename = f'{sub.compet_id}-{sub.task_name}.{EXTENSIONS[sub.language]}'
        dirname = os.path.join(BASE,EXTENSIONS[sub.language],sub.task_name)
        if sub.task_name in EXCLUDE:
            continue
        problem_names.add(sub.task_name)
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        source = bytes(sub.source)
        with open(os.path.join(dirname,filename),'wb') as f:
            f.write(source)
            count += 1
    print(problem_names)
    return count

class Command(BaseCommand):
    help = 'Extract cms submissions'

    def add_arguments(self, parser):
        parser.add_argument('contest_id', nargs='+', type=int)

    def handle(self, *args, **options):
        contest_id = options['contest_id'][0]
        count = extract_submissions(contest_id)
        self.stdout.write(self.style.SUCCESS(f'Copied {count} submissions.'))
