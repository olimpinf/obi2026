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

from obi.settings import BASE_DIR, DEFAULT_FROM_EMAIL, DEFAULT_REPLY_TO_EMAIL
from principal.utils.utils import obi_year
from principal.models import School, Colab, Compet, IJ, I1, I2, PJ, P1, P2, PS

DO_SEND = True

def send_messages(filename):
    year = '2022'
    msg_subject = 'OBI' + year + ' - importante - plágio'
    msg_template = 'mensagem_coord_avisa_plagio.html'

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia", msg_template))
    with open(filename,'r') as f:
        lines = f.readlines()

    line = lines[0].strip().split(',')
    line[2] = line[2].strip('"')
    school_data = {'school_id':line[1], 'school_name':line[2], 'coord_name': line[3], 'email': line[4],
                   'item':[{'compet_id_full_1': line[5], 'compet_name_1': line[6],
                            'compet_id_full_2': line[7], 'compet_name_2': line[8], 'source_name':line[9]}]}

    count = 0
    for line in lines:
        line = line.strip().split(',')
        if line[0] != 'sim':
            continue
        line[2] = line[2].strip('"')
        if line[1] == school_data['school_id']:
            school_data['item'].append({'compet_id_full_1': line[5], 'compet_name_1': line[6],
                            'compet_id_full_2': line[7], 'compet_name_2': line[8], 'source_name':line[9]})
        else:
            to_address = school_data['email']
            context = {"greetings": "Caro(a) Prof(a).",'school_data': school_data, 'year': year}
            body = template.render(context)

            connection = mail.get_connection()
            connection.open()
            email = mail.EmailMessage(
                msg_subject,
                body,
                DEFAULT_FROM_EMAIL,
                [to_address],
                reply_to=[DEFAULT_REPLY_TO_EMAIL],
                connection=connection
            )
            #if attachment_data:
            #    email.attach('arquivo', attachment_data, 'image/png')
            try:
                email.send()
                print('{};{} - sent'.format(to_address, school_data['school_name']),file=sys.stderr)
                sys.stderr.flush()
                count += 1
                sleep(1)
            except:
                print('\nto_address {}, {} *********** failed'.format(to_address, coord.school_deleg_name), file=sys.stderr)
                failed += 1
            school_data = {'school_id':line[1], 'school_name':line[2], 'coord_name': line[3], 'email': line[4],
                   'item':[{'compet_id_full_1': line[5], 'compet_name_1': line[6],
                            'compet_id_full_2': line[7], 'compet_name_2': line[8], 'source_name':line[9]}]}

            connection.close()

    #connection.close()
    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs='+', type=str)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        count = send_messages(filename)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
