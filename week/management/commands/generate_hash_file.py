import getopt
import os
import re
import sys

import magic
import hashlib

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from week.models import Week
from week.views import gen_hash
from principal.models import School

from obi.settings import YEAR

class Command(BaseCommand):
    help = 'Create receipt hash file'

    def add_arguments(self, parser):
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('file_path', nargs='+', type=str)

    def handle(self, *args, **options):
        school_id = options['school_id'][0]
        file_path = options['file_path'][0]
        try:
            week = Week.objects.filter(school_id=school_id)
        except:
            self.stdout.write(self.style.ERROR('School not in Week'))
            self.stdout.write(self.style.ERROR('No change'))
            return

        school = School.objects.get(school_id=school_id)

        guess = magic.from_file(file_path,mime=True)

        if guess == 'application/pdf':
            print('is pdf')
            os.system(f'convert {file_path} {file_path}.png')
            if os.path.exists(f'{file_path}-0.png'):
                os.system(f'cp {file_path}-0.png {file_path}.png')
            imgpath = file_path + '.png'
        elif guess == 'image/png':
            os.system(f'cp {file_path} {file_path}.png')
            imgpath = file_path + '.png'
        elif guess == 'image/jpeg':
            os.system(f'cp {file_path} {file_path}.jpg')
            imgpath = file_path + '.jpg'

        try:
            os.system(f'chgrp www-data {imgpath}')
        except:
            pass

        file_number = os.path.basename(file_path).split('_')

        name_hash = gen_hash(school.school_id, school.school_name) + ('_' + file_number[1] if len(file_number) > 1 else '')

        static_imgpath = os.path.join(f'extras/obi{YEAR}/semana/pagamentos', name_hash)

        local_static_imgpath = os.path.join('static', static_imgpath)
        os.system(f'cp {imgpath} {local_static_imgpath}')
