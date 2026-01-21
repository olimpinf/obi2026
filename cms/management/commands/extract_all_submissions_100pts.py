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

from principal.models import School, Compet, LEVEL_NAME, PJ, P1, P2, PS
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.models import LocalSubmissions, LocalSubmissionResults
from cms.utils import EXTENSIONS

logger = logging.getLogger(__name__)

BASE = '/tmp/submissions_100pts'

def extract_submissions(phase):
    count = 0
    try:
        shutil.rmtree(BASE)
    except:
        pass
    os.mkdir(BASE)
        
    if phase == 1:
        contest_id = 1
        for level in (P1,):
            os.mkdir(os.path.join(BASE,LEVEL_NAME[level]))

            local_submission_results = LocalSubmissionResults.objects.filter(score=100.0,compet_type=level).order_by('submission_id')
            local_submissions = LocalSubmissions.objects.filter(compet_type=level)
            #compets = Compet.objects.filter(compet_type=level)
            for sub_res in local_submission_results:
                # keep only the last submission, overwrite older ones
                #filename = f'{sub.compet_id}-{sub.task_name}-{sub.submission_id}.{EXTENSIONS[sub.language]}'
                sub = local_submissions.get(submission_id=sub_res.submission_id)
                filename = f'{sub.compet_id}-{sub.task_name}.{EXTENSIONS[sub.language]}'
                dirname = os.path.join(BASE,LEVEL_NAME[level],EXTENSIONS[sub.language])
                if not os.path.exists(dirname):
                    os.mkdir(dirname)
                source = bytes(sub.source)
                with open(os.path.join(dirname,filename),'wb') as f:
                    f.write(source)
                    count += 1
                        
    return count

class Command(BaseCommand):
    help = 'Extract all submissions 100pts'

    def add_arguments(self, parser):
        parser.add_argument('phase', nargs='+', type=int)

    def handle(self, *args, **options):
        phase = options['phase'][0]
        count = extract_submissions(phase)
        self.stdout.write(self.style.SUCCESS(f'Copied {count} submissions.'))
