import logging
import os
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
from cms.utils import (cms_do_add_user, cms_do_remove_user)
from cms.models import CMSuser, CMSparticipation

logger = logging.getLogger(__name__)


def cms_report_participation(self, compet_type, contest_id):

    from exams.models import ExamFase1, ExamFase2, ExamCfObi, ExamFase3

    if contest_id == 1:
        exam = ExamFase1
    elif contest_id == 2:
        exam = ExamFase2
    elif contest_id == 3:
        exam = ExamCfObi
    elif contest_id == 4:
        exam = ExamFase3
    else:
        print('???')
        raise Boom
        
    starts = exam.objects.filter(compet__compet_type = compet_type).order_by('time_start').only('time_start')
    finishes = exam.objects.filter(compet__compet_type = compet_type).order_by('time_finish').only('time_finish')

    events = []
    count = 0
    for t in starts:
        if t.time_start:
            events.append((t.time_start,'s'))
            count += 1
    for f in finishes:
        if f.time_finish:
            events.append((f.time_finish,'f'))

    events.sort()

    max_participants = 0
    participants = 0
    max_time = events[0][0]
    for e in events:
        if e[1] == 's':
            participants += 1
            #print('+',end='')
            if participants > max_participants:
                max_participants = participants
                max_time = e[0]
            
        else:
            #print('-',end='')
            participants -= 1

    print('inscritos',len(finishes))
    print("participantes", count)
    print('pico',max_participants, max_time)
    print()
    return max_participants


        
class Command(BaseCommand):
    help = 'report participation'

    def add_arguments(self, parser):
        parser.add_argument('compet_type', nargs='+', type=int)
        parser.add_argument('contest_id', nargs='+', type=int)

    def handle(self, *args, **options):
        compet_type = options['compet_type'][0]
        contest_id = options['contest_id'][0]
        #compet_type = LEVEL[compet_type]
        pico = 0
        if compet_type == 0:
            compet_types = (PJ,P1,P2,PS)
        else:
            compet_types = (compet_type,)
        for t in compet_types:
            print(f'\n************ compet_type={t}\n')
            pico += cms_report_participation(self, t, contest_id)
        self.stdout.write(self.style.SUCCESS('total pico {} cms users.\n'.format(pico)))
        
