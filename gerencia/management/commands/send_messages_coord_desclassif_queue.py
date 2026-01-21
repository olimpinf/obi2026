import os
import sys
from itertools import chain

from time import sleep
from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.template import loader

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, YEAR
from principal.utils.utils import obi_year
from principal.models import School, SchoolPhase3, Colab, Compet, CompetDesclassif, IJ, I1, I2, PJ, P1, P2, PS, LEVEL_NAME_FULL
from week.models import Week
from restrito.views import queue_email

DO_SEND = True

def send_messages(filename):

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia","mensagem_coord_desclassif_compet.html"))
    with open(filename, "r") as f:
        lines = f.readlines()
    count,failed = 0,0
    for line in lines:
        tokens = line.split(";")
        school = School.objects.get(school_id=int(tokens[0]))
        try:
            to_address = school.school_deleg_email
            to_name = school.school_deleg_name
            to_school_name = school.school_name
            username = school.school_deleg_username
            greetings = "Caro(a) Prof(a)."
        except:
            failed += 1
            print('\nfailed *********** {} failed'.format(coord), file=sys.stderr)
            continue

        tmp = tokens[1:]
        compets = []
        for t in tmp:
            t = t.translate({ord(i): None for i in '()""\''})
            c = [i.strip() for i in t.split(',')]
            if c[3] == 'fase-1':
                c[3] = 'Fase 1'
            elif c[3] == 'fase-2':
                c[3] = 'Fase 2'
            elif c[3] == 'fase-2b':
                c[3] = 'Fase 2 Turno B'
            elif c[3] == 'fase-3':
                c[3] = 'Fase 3'
            elif c[3] == 'fase-cf':
                c[3] = 'Competição Feminina'
            compets.append(tuple(c))

        #compets = CompetDesclassif.objects.filter(compet_id__in=compets)
        context = {"greetings": greetings,'school_name': to_school_name, 'coord_name': to_name, 'username': username, 'compets': compets, 'year': YEAR}
        body = template.render(context)
        subject = f'OBI{YEAR} - IMPORTANTE'
        priority = 1

        if DO_SEND:
            queue_email(
                subject,
                body,
                DEFAULT_FROM_EMAIL,
                to_address,
                priority
            )
        else:
            print()
            print(to_address)
            print(subject)
            print(body)
            print('-------------------------\n')
            print()
        count += 1

    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        count = send_messages(filename)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
