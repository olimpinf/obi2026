import sys
import logging

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, LEVEL_NAME
from exams.models import TesteFase1
from restrito.views import compet_send_email_admin
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def fix_compet_password(modality):
    if modality == 'i':
        compets = Compet.objects.filter(compet_type__in=(1,2,7))
    elif modality == 'p':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    else:
        print('wrong modality')
        return 0
    count = 0

    #compets = compets.filter(compet_email__isnull=False,user__isnull=True)
    #compets = compets.filter(compet_conf='',compet_school_id=1).order_by('compet_id')
    compets = compets.filter(compet_conf='').order_by('compet_id')
    print(f'found {len(compets)} to fix)')
    for c in compets:
        if c.compet_email:
            email = c.compet_email.strip()
        
            if email != c.compet_email:
                print('******* strip diff',end=' ')
            if email=="":
                print('blank space email {},{}'.format(c.compet_name,LEVEL_NAME[c.compet_type]))
                #sys.exit(-1)
                #continue
        else:
            email = ""
            
        logger.info('fixing compet_id:{} - {}, user:{}, password:{} email:{}'.format(c.compet_id, c.compet_name, c.compet_conf, c.user, email))
        print('-----')
        print('fixing {} - {}, user:{}, password:{}'.format(c.compet_id_full, c.compet_name, c.user, c.compet_conf))
        try:
            user = User.objects.get(username=c.compet_id_full)
        except:
            print('user does not exist??? Should not', c.compet_id_full)
            sys.exit(1)

        password = make_password()
        c.compet_conf = password
        c.save()
        user.set_password(password)
        user.save()

        try:
            g = Group.objects.get(name='compet')
            g.user_set.add(user)
        except:
            logger.info("falha ao inserir em grupo compet,  user={} compet={}".format(user,c))
            print("falha ao inserir em grupo compet,  user={} compet={}".format(user,c))

        school = c.compet_school
        try:
            compet_send_email_admin(c,school,reason="atualizar sua inscrição",queue=True)
        except:
           logger.info('Dados foram atualizados mas envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
           print('Dados foram atualizados mas envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
           break
        count += 1
    
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        modality = options['modality'][0]
        count = fix_compet_password(modality)
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
