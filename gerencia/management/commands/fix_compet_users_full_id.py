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

#def fix_compet_users(modality):
def fix_compet_users():
    # if modality == 'i':
    #     compets = Compet.objects.filter(compet_type__in=(1,2,7))
    # elif modality == 'p':
    #     compets = Compet.objects.filter(compet_type__in=(3,4,5,6))
    # else:
    #     print('wrong modality')
    #     return 0
    #compets = compets.filter(compet_id_full='')
    compets = Compet.objects.filter(compet_id_full='')
    count = 0
    print('len(compets)',len(compets))

    for c in compets:
        print(f"{c.user}")
        c.compet_id_full = format_compet_id(c.compet_id)
        #c.save()
        if c.user == None or c.user == "":
            print('******* user is None', c)

        email = c.compet_email
        if c.compet_email:
            email = c.compet_email.strip()
        if email != c.compet_email:
            print('******* strip diff', c)
            sys.exit(-1)
        if email=="":
            print('blank space email {},{}'.format(c.compet_name,LEVEL_NAME[c.compet_type]))
            #sys.exit(-1)
            #continue
                
        print('fixing {} - {}, user:{}'.format(c.compet_id_full, c.compet_name, c.user))
        password = make_password()
        c.compet_conf = password
        c.compet_id_full = format_compet_id(c.compet_id)
        try:
             user = User.objects.get(username=c.compet_id_full)
             print('user exists!')
        except:
            print('create user')
            try:
                user = User.objects.create_user(c.compet_id_full,c.compet_email,password)
            except Exception as ex:
                print('*********** error creating user!!!', c.compet_id_full)
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print(message)
                return count
        print('user',user)
        g = Group.objects.get(name='compet')
        try:
            g.user_set.add(user)
        except:
            print("user exists in group")

        user.username=c.compet_id_full
        user.last_name = c.compet_name
        user.is_staff = False
        user.save()
        c.user = user
        c.save()
        print("OK")
        #try:
        #     c.save() # must save to send email
        # except:
        #     logger.info('duplicate user.id: {}'.format(user.id))
        #     print('duplicate user.id: {}'.format(user.id))
        #     continue
        # school = c.compet_school
        # # authorize TesteFase1
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
        pass
        #parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        #modality = options['modality'][0]
        #count = fix_compet_users(modality)
        count = fix_compet_users()
        self.stdout.write(self.style.SUCCESS('Fixed {} compets.'.format(count)))
