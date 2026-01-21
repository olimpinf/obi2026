import base64
import logging
import os
import re
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

def check_plagiarism(directory):
    count = 0

    compets = Compet.objects.filter(compet_type__in=(PJ,P1,P2,PS))
    schools = School.objects.filter(school_ok=True)
    pat = re.compile(r"(?P<task>\w+)\/(?P<compet_id>\w+)-(?P<language>\w+)\.(?P<lang>\w+)")
    suspect = set()
    for root, dirs, files in os.walk(directory, topdown = False):
        for name in files:
            base,ext = os.path.splitext(name)
            if ext == '.csv':
                with open(os.path.join(root, name),"r") as f:
                    data = f.readlines()
                for line in data:
                    items = line.strip().split(';')
                    match = re.search(pat,items[0])
                    compet_a = int(match.group('compet_id'))
                    match = re.search(pat,items[2])
                    compet_b = int(match.group('compet_id'))
                    try:
                        compet_a = compets.get(compet_id=compet_a)
                        school_a = schools.get(school_id=compet_a.compet_school_id)
                    except:
                        print("no compet?",compet_a)
                        print(line)
                        continue
                    try:
                        compet_b = compets.get(compet_id=compet_b)
                        school_b = schools.get(school_id=compet_b.compet_school_id)
                    except:
                        print("no compet?",compet_b)
                        print(line)
                        continue
                    if school_a.school_id == school_b.school_id:
                        suspect.add((school_a.school_id,school_a.school_name,school_a.school_deleg_name,school_a.school_deleg_email,compet_a.compet_id_full,compet_a.compet_name,compet_b.compet_id_full,compet_b.compet_name,f"{match.group('task')}.{match.group('lang')}"))
    suspect = list(suspect)
    suspect.sort()
    with open('suspect.csv',"w") as f:
        for s in suspect:
            print(','.join(['"'+str(i)+'"' for i in s]),file=f)
    return len(suspect)
    #for l in EXTENSIONS.keys():
    #    print(EXTENSIONS[l])
    #    os.mkdir(os.path.join(BASE,EXTENSIONS[l]))
        
class Command(BaseCommand):
    help = 'Update cms passwords'

    def add_arguments(self, parser):
        parser.add_argument('directory', nargs='+', type=str)

    def handle(self, *args, **options):
        directory = options['directory'][0]
        count = check_plagiarism(directory)
        self.stdout.write(self.style.SUCCESS(f'Got {count} suspect submissions.'))
