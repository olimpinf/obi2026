import getopt
import os
import re
import sys
from datetime import datetime, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import make_aware, timezone

from principal.models import LEVEL, Compet, School
from exams.models import Alternative, Question, Task
from exams.views import mark_exam
from exams.settings import EXAMS

def authorize_exam_compet(exam,compet,school):
    if not compet.compet_classif_fase2:
        print('compet not classif',compet.compet_id)
        return 0
    
    if exam.objects.filter(compet=compet,school=school).exists():
        #print('compet already authorized',compet.compet_id)
        return 0
    try:
        ex = exam(compet=compet,school=school)
        ex.save()
        print('authorized compet', compet.compet_id,compet,school)
        return 1
    except:
        print('error when authorizing compet', compet.compet_id,compet,school)
    return 0

def authorize_exam_school(exam, level,  school):
    compet_type = LEVEL[level.upper()]
    compets = Compet.objects.filter(compet_school_id=school.school_id, compet_type=compet_type, compet_classif_fase2=True)
    count = 0
    for compet in compets:
        count += authorize_exam_compet(exam,compet,school)
    return count

def authorize_exams(descriptor,level,school_id,compet_id):
    count = 0
    exam = EXAMS[descriptor]['exam_object']
    if school_id != 0:
        print('school_id',school_id)
        school = School.objects.get(pk=school_id)
        print('school',school)
        if compet_id != 0:
            # authorize one compet
            compet_type = LEVEL[level.upper()]
            try:
                compet = Compet.objects.get(pk=compet_id,compet_type=compet_type,compet_school_id=school_id,compet_classif_fase2=True)
                count += authorize_exam_compet(exam,compet,school)
            except:
                print('no such compet in school',compet_id,school)
        else:
            # authorize all compets in school
            count += authorize_exam_school(exam,level,school)
    else:
        if level[0] == 'i':
            schools = School.objects.filter()
        elif level[0] == 'p':
            schools = School.objects.filter()
        else:
            raise('Error in level',level)
        print('schools',schools)
        for s in schools:
            count += authorize_exam_school(exam, level,  s)
    return count

class Command(BaseCommand):
    help = 'Authorize exam in phase 2'

    def add_arguments(self, parser):
        parser.add_argument('descriptor', nargs='+', type=str)
        parser.add_argument('level', nargs='+', type=str)
        parser.add_argument('school_id', nargs='+', type=int)
        parser.add_argument('compet_id', nargs='+', type=int)

    def handle(self, *args, **options):
        descriptor = options['descriptor'][0]
        level = options['level'][0]
        school_id = int(options['school_id'][0])
        compet_id = int(options['compet_id'][0])
        authorized = authorize_exams(descriptor,level,school_id,compet_id)
        self.stdout.write(self.style.SUCCESS('Authorized {} exams.'.format(authorized)))
