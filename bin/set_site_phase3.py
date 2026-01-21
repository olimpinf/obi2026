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
        parser.add_argument('school_city', nargs='+', type=str)
        parser.add_argument('school_state', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=int)
        parser.add_argument('site_id', nargs='+', type=int)

    def handle(self, *args, **options):
        school_city = options['school_city'][0]
        school_state = options['school_state'][0]
        level = options['level'][0]
        school_id = options['school_id'][0]
        tmp = School.objects.filter(school_ok=True,school_city=school_city,school_state=school_state)
        print(tmp, "  - y/n?")
        go = input()
        if go != 'y':
            print(self.stdout.write(self.style.SUCCESS('No change')))
            return
        self.stdout.write(self.style.SUCCESS('OK'))
