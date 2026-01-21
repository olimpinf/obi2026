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
from cms.models import LocalSubmissions,LocalSubmissionResults
from cms.utils import EXTENSIONS

logger = logging.getLogger(__name__)

BASE = '/tmp/submissions'

def extract_submissions(phase):
    count = 0
    try:
        shutil.rmtree(BASE)
    except:
        pass
    os.mkdir(BASE)
    for l in EXTENSIONS.keys():
        print(EXTENSIONS[l])
        os.mkdir(os.path.join(BASE,EXTENSIONS[l]))
        
    if phase == 1:
        contest_id = 1
    #for level in (PJ,P1,P2,):
    #    if level == PS and contest_id==1:
    #        contest_id=3

        local_submission_results = LocalSubmissionResults.objects.filter(score=100).order_by('submission_id')
        #compets = Compet.objects.filter(compet_type=level)
        for sub_res in local_submission_results:
            # keep only the last submission, overwrite older ones
            #filename = f'{sub.compet_id}-{sub.task_name}-{sub.submission_id}.{EXTENSIONS[sub.language]}'

            # group C and C++ together
            if sub_res.local_subm.language.find("C")==0:
                sub_res.local_subm.language = 'C++17 / g++'
            filename = f'{sub_res.compet_id}-{sub_res.local_subm.task_name}.{EXTENSIONS[sub_res.local_subm.language]}'
            dirname = os.path.join('/tmp/submissions',EXTENSIONS[sub_res.local_subm.language],sub_res.local_subm.task_name)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
            source = bytes(sub_res.local_subm.source)
            with open(os.path.join(dirname,filename),'wb') as f:
                f.write(source)
            count += 1

    return count

class Command(BaseCommand):
    help = 'Update cms passwords'

    def add_arguments(self, parser):
        parser.add_argument('phase', nargs='+', type=int)

    def handle(self, *args, **options):
        phase = options['phase'][0]
        count = extract_submissions(phase)
        self.stdout.write(self.style.SUCCESS(f'Copied {count} submissions.'))
