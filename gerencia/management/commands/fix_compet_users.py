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
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

EMAIL_FROM="Coordenação da OBI <olimpinf@ic.unicamp.br>"

def fix_compet_users(modality):
    if modality == 'i':
        compets = Compet.objects.filter(compet_type__in=(1,2,7))
    elif modality == 'p':
        compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    else:
        print('wrong modality')
        return 0
    count = 0

    #compets = compets.filter(compet_email__isnull=False,user__isnull=True)
    compets = compets.filter(user__isnull=True).order_by('compet_id')
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
            
        logger.info('fixing compet_id:{} - {}, user:{}, email:{}'.format(c.compet_id, c.compet_name, c.user, email))
        print('-----')
        print('fixing {} - {}, user:{}'.format(c.compet_id_full, c.compet_name, c.user))
        try:
            user = User.objects.get(username=c.compet_id_full)
        except:
            password = make_password()
            c.compet_conf = password
            try:
                user = User.objects.create_user(c.compet_id_full,c.compet_email,password)
            except:
                print('user exists??? Should not', c.compet_id_full)
                sys.exit(1)
        g = Group.objects.get(name='compet')
        g.user_set.add(user)
        user.last_name = c.compet_name
        user.is_staff = False
        user.save()
        c.user = user
        try:
            c.save() # must save to send email
        except:
            logger.info('duplicate user.id: {}'.format(user.id))
            print('duplicate user.id: {}'.format(user.id))
            continue

        # school = c.compet_school
        # authorize TesteFase1
        # try:
        #     ex = TesteFase1.objects.get(compet_id=c.compet_id)
        # except:
        #     try:
        #         ex = TesteFase1(compet=c,school=school)
        #         ex.save()
        #     except:
        #         logger.info("compet_inscreve falhou ao autorizar TesteFase1, user={} compet={}".format(user,c))
        #         print("compet_inscreve falhou ao autorizar TesteFase1, user={} compet={}".format(user,c))
        #try:
        #    send_email_compet_registered(c,school,password=password, reason="atualizar sua inscrição")
        #except:
        #    logger.info('Dados foram atualizados mas envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
        #    print('Dados foram atualizados mas envio de email falhou, corrija o endereço de email informado" (email: {})'.format(c.compet_email))
        #    user.delete()
        #    continue
        count += 1
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        modality = options['modality'][0]
        count = fix_compet_users(modality)
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
