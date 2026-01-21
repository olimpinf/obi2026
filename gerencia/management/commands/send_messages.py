import os
import sys

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
from principal.models import School

DO_SEND = True

def send_messages(msg_subject,msg_template,msg_to_addresses):
    # send explicitly
    #connection = mail.get_connection()
    # when testing, the connection is not the debug port, fix this here
    # run
    # python -m smtpd -n -c DebuggingServer localhost:1025
    #connection.localhost = 'localhost'
    #connection.port = 1025

    # do not send to registered schools
    registered = School.objects.all()
    registered_emails = set()
    for r in registered:
        registered_emails.add(r.school_deleg_email)
    print("registered:", len(registered), file=sys.stderr)

    # do not send if sent already
    sent_file = os.path.join(BASE_DIR,"attic","mensagens","invitations_sent.csv")
    sent_emails = set()
    with open(sent_file,"r") as sfile:
        line = sfile.readline()
        while line:
            email = line.split(';')[0].strip()
            if email:
                sent_emails.add(email)
            line = sfile.readline()
    print("sent_emails:", len(sent_emails), file=sys.stderr)

    # do not send if sent and failed
    failed_file = os.path.join(BASE_DIR,"attic","mensagens","invitations_failed.csv")
    failed_emails = set()
    with open(failed_file,"r") as ffile:
        line = ffile.readline()
        while line:
            email = line.split(';')[0].strip()
            if email:
                failed_emails.add(email)
            line = ffile.readline()
    print("failed_emails:", len(failed_emails), file=sys.stderr)

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))
    with open(msg_to_addresses,'r') as f:
        lines = f.readlines()

    delimiter = ''
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line[0] == "#":
            continue
        for d in (';',',','|'):
            if line.find(d) > 0:
                delimiter = d
                break
        # only first line
        break
    print(f"using '{delimiter}' as delimiter", file=sys.stderr)

    template = loader.get_template(os.path.join(BASE_DIR,"gerencia","templates","gerencia",msg_template))
    
    count,failed,skipped = 0,0,0
    for line in lines:
        line = line.strip()
        if line == "":
            continue
        if line[0] == "#":
            continue
        try:
            tokens = line.split(delimiter)
            if tokens[0].find('@') > 0:
                to_address = tokens[0].strip().lower()
                school_name = tokens[1].strip()
            else:
                to_address = tokens[1].strip().lower()
                school_name = tokens[0].strip()
        except:
            print('\nto_address {}, school_name {} *********** failed'.format(to_address, school_name), file=sys.stderr)
            failed += 1
            continue

        if to_address == '' or to_address == 'none':
            print('\nto_address {}, school_name {} is empty'.format(to_address, school_name), file=sys.stderr)
            print('{};{} - no email'.format(to_address, school_name))
            continue

        if to_address in registered_emails:
            print('\nto_address {}, school_name {} is registered'.format(to_address, school_name), file=sys.stderr)
            skipped += 1
            continue
        if to_address in sent_emails:
            print('\nto_address {}, school_name {} already sent'.format(to_address, school_name), file=sys.stderr)
            skipped += 1
            continue
        context = {'school_name': school_name}
        body = template.render(context)
        if DO_SEND:
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
                print('{};{} - sent'.format(to_address, school_name))
                print('{};{} - sent'.format(to_address, school_name),file=sys.stderr)
                #print('.', file=sys.stderr, end='')
                sys.stderr.flush()
                with open(sent_file,"a") as sfile:
                    print(f'{to_address};{school_name}', file=sfile)
                count += 1
            except:
                print('\nto_address {}, school_name {} *********** failed'.format(to_address, school_name), file=sys.stderr)
                with open(failed_file,"a") as ffile:
                    print(f'{to_address};{school_name}', file=ffile)
            connection.close()
            #if count % 5 == 0:
            sleep(2)
        else:
            print('\n****************** send to_address {}, school_name {}'.format(to_address, school_name), file=sys.stderr)
            count += 1
            
    #connection.close()
    return count


class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('msg_subject', nargs='+', type=str)
        parser.add_argument('msg_template', nargs='+', type=str)
        parser.add_argument('msg_to_addresses', nargs='+', type=str)

    def handle(self, *args, **options):
        msg_subject = options['msg_subject'][0]
        msg_template = options['msg_template'][0]
        msg_to_addresses = options['msg_to_addresses'][0]
        count = send_messages(msg_subject, msg_template, msg_to_addresses)
        self.stderr.write(self.style.SUCCESS('Sent {} messages.'.format(count)))
