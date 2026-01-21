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

from principal.models import School, Compet, LEVEL, PJ, P1, P2, PS, PasswordCms
from principal.utils.utils import (obi_year,
                                   verify_compet_id,
                                   format_compet_id,)
from cms.utils import (cms_do_add_user, cms_do_remove_user)
from cms.models import CMSuser, CMSparticipation

logger = logging.getLogger(__name__)

CHECK = False
    
def cms_sync_passwords(self, compet_type, contest_id):
    cmsdb = {PJ: 'cms_pj', P1: 'cms_p1', P2: 'cms_p2', PS: 'cms_ps'}
    cms_users = CMSuser.objects.all().using(cmsdb[compet_type])
    cms_participations = CMSparticipation.objects.all().using(cmsdb[compet_type])
    cms_usernames = []
    cms_partic_usernames = []
    for u in cms_users:
        cms_usernames.append(u.username)
    compets = Compet.objects.filter(compet_type=compet_type)
    django_usernames = []
    for c in compets:
        django_usernames.append(c.compet_id_full)

    missing = []
    for d in django_usernames:
        if d not in cms_usernames:
            missing.append(d)
    print('missing users', len(missing))

    # add missing to cmsdb
    #for m in missing:
    #    compet = compets.get(compet_id_full=m)
    #    cms_pwd = PasswordCms.objects.get(compet=compet)
    #    password = cms_pwd.password
    #    cms_pwd.save()
    #    print('adding user',m)
    #    # cms_do_add_user(compet.compet_id_full, '', compet.compet_name, compet.compet_type, compet.user.password, contest_id)
    #    names = compet.compet_name.split(" ")
    #    first_name = names[0]
    #    last_name = " ".join(names[1:])
    #    cms_do_add_user(compet.compet_id_full, first_name, last_name, compet.compet_type, password, contest_id)

    # removing extras from cmsdb
    extra = []
    for c in cms_usernames:
        if c  not in django_usernames:
            extra.append(c)
    print('extra users', len(extra))

    # for e in extra:
    #     if e in ('00000-J','00001-C'):
    #         print("not removing", e)
    #         continue
    #     print('Removing user',e)
    #     cms_do_remove_user(e, compet_type)
            

    # print("check participations")
    # for c in cms_users:
    #     try:
    #         p = cms_participations.get(user_id=c.id)
    #     except:
    #         print('missing participation for user', c.username)
    #         compet = compets.get(compet_id_full=c.username)
    #         #cms_do_add_user(compet.compet_id_full, '', compet.compet_name, compet.compet_type, compet.user.password, contest_id)
    #         names = compet.compet_name.split(" ")
    #         first_name = names[0]
    #         last_name = " ".join(names[1:])
    #         cms_pwd = PasswordCms.objects.get(compet=compet)
    #         password = cms_pwd.password
    #         cms_do_add_user(compet.compet_id_full, first_name, last_name, compet.compet_type, password, contest_id)

    if CHECK:
        for d in django_usernames:
            compet = compets.get(compet_id_full=d)
            cms_pwd = PasswordCms.objects.get(compet=compet)
            password = cms_pwd.password
            cms_user = cms_users.get(username=d)
            participation = cms_participations.get(user_id=cms_user.id, contest_id=contest_id)
            #if "pbkdf2:"+compet.user.password != cms_user.password:
            if "plaintext:"+password != cms_user.password:
                print('django and cms passwords are different!')
                print(compet.compet_id_full)
                print(password)
                print(cms_user.password)
                print()
            #if participation.password and "pbkdf2:"+compet.user.password != participation.password:
            if participation.password and "plaintext:"+password != participation.password:
                print('participation password exists and is different!')
                print(compet.compet_id_full)
                print(password)
                print(participation.password)
                print()
    count = 0
    return count


        
class Command(BaseCommand):
    help = 'Add CMS users'

    def add_arguments(self, parser):
        parser.add_argument('compet_type', nargs='+', type=int)
        parser.add_argument('contest_id', nargs='+', type=int)

    def handle(self, *args, **options):
        compet_type = options['compet_type'][0]
        contest_id = options['contest_id'][0]
        #compet_type = LEVEL[compet_type]
        if compet_type == 0:
            compet_types = (PJ,P1,P2,PS)
        else:
            compet_types = (compet_type,)
        for t in compet_types:
            print(f'\n************ compet_type={t}\n')
            cms_sync_passwords(self, t, contest_id)
        #self.stdout.write(self.style.SUCCESS('Added {} cms users.'.format(count)))
