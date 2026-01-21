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

BASE = '/tmp/user_submissions'

problem_names = set()

def extract_submissions(level, compets):
    count = 0
    try:
        shutil.rmtree(os.path.join(BASE, level))
    except:
        print('did not remove',os.path.join(BASE, level))
        pass
    try:
        os.mkdir(BASE)
    except:
        pass
    os.mkdir(os.path.join(BASE, level))
    for c in compets:
        with open(os.path.join(BASE, level, c.compet_id_full),'w') as f:
            for contest_id in (1,2,3,5):
                local_submissions = LocalSubmissions.objects.filter(contest_id=contest_id,compet_id=c.compet_id).order_by('submission_id')
                for sub in local_submissions:
                    print('*********************', file=f)
                    print(f'{c.compet_id_full}, submission {sub.submission_id}', file=f)
                    print(f'{sub.task_name}.{EXTENSIONS[sub.language]}', file=f)
                    # group C and C++ together
                    if sub.language.find("C")==0:
                        sub.language = 'C++17 / g++'
                    try:
                        source = bytes(sub.source).decode("utf-8")
                    except:
                        source = bytes(sub.source).decode("latin1")
                        
                    print(source, file=f)
                    count += 1

    return count

class Command(BaseCommand):
    help = 'Extract cms submissions'

    def add_arguments(self, parser):
        parser.add_argument('compet_level', nargs='+', type=str)
        parser.add_argument('compet_points_fase3', nargs='+', type=int)

    def handle(self, *args, **options):
        compet_level = options['compet_level'][0].upper()
        compet_type = LEVEL[compet_level]
        compet_points_fase3 = options['compet_points_fase3'][0]
        compets = Compet.objects.filter(compet_type=compet_type, compet_points_fase3__gte=compet_points_fase3)
        count = len(compets)
        count = extract_submissions(compet_level, compets)
        self.stdout.write(self.style.SUCCESS(f'Copied {count} submissions.'))
