import getopt
import os
import re
import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from cadastro.models import LEVEL, Compet, School
from principal.utils.check_solutions_file import Error, check_solutions_file


class Command(BaseCommand):
    help = 'Compute compets that are promoted to next phase'

    def add_arguments(self, parser):
        parser.add_argument('archive', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('phase', nargs='+', type=int)
        parser.add_argument('school_id', nargs='+', type=int)

    def handle(self, *args, **options):
        level = options['level'][0]
        level_num = LEVEL[level.upper()]
        archive = options['archive'][0]
        phase = options['phase'][0]
        school_id = options['school_id'][0]
        result = check_solutions_file(archive, level_num, phase, school_id)
        print('result msg',result[0])
        for error in result[1]:
            print(error.compet, error.program, error.comment)
        self.stdout.write(self.style.SUCCESS('OK'))
