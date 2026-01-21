import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from cadastro.models import LEVEL, Compet, School
from fase3.utils.check_solutions_file import Error, check_solutions_file

PHASE = 3

class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('archive', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        archive = options['archive'][0]
        archive = os.path.abspath(archive)
        phase = PHASE
        school_id = options['school_id'][0]
        school_compets=Compet.objects.filter(compet_type=level_num,compet_school_id=school_id)
        result = check_solutions_file(archive, level_num, phase, school_compets)
        print('result msg',result[0])
        for error in result[1]:
            print(error.compet, error.program, error.comment)
        self.stdout.write(self.style.SUCCESS('OK'))
