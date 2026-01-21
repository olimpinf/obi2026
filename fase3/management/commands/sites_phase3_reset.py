import sys

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from principal.models import Compet, School

        
class Command(BaseCommand):
    help = 'build sites phase 3 from csv file'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        print("Are you sure you want to reset all sites for phase3? (y/n)", end=' ')
        resp = input()
        if resp != 'y':
            return
        schools = School.objects.all()
        for s in schools:
            s.school_is_site_phase3 = False            
            s.school_site_phase3_show = False
            s.school_site_phase3_type = 0
            s.school_site_phase3 = 0
            s.school_site_phase3_ini = 0
            s.school_site_phase3_prog = 0
            s.save()
