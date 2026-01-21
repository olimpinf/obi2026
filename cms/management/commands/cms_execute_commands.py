import os
import sys
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
from cms.utils import (cms_do_add_user, cms_do_update_password, cms_do_remove_user)
from cms.models import CMScommand

    
def cms_execute_commands(self):
    commands = CMScommand.objects.filter(done=False).order_by('id')
    self.stdout.write(self.style.SUCCESS('Found {} commands to execute.'.format(len(commands))))

    #########
    #########
    for cmd in commands:
        if cmd.command == 'add':
            ######### will only update passwords in Fase 2
            #pass
            cms_do_add_user(username=cmd.username, first_name=cmd.first_name, last_name=cmd.last_name, compet_type=cmd.compet_type, password=cmd.password)
        elif cmd.command == 'update':
            cms_do_update_password(username=cms.username, compet_type=cmd.compet_type, password=cmd.password)
        elif cmd.command == 'remove':
            pass
            #cms_do_remove_user(username=cmd.username, compet_type=cmd.compet_type)
        else:
            print(cmd)
            raise boom
        cmd.done = True
        cmd.save()
        
class Command(BaseCommand):
    help = 'Add CMS users'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('compet_type', nargs='+', type=str)

    def handle(self, *args, **options):
        #compet_type = options['compet_type'][0].upper()
        #compet_type = LEVEL[compet_type]
        cms_execute_commands(self)
        #self.stdout.write(self.style.SUCCESS('Added {} cms users.'.format(count)))
