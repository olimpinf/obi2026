import sys
import logging

from django.conf import settings
from django.contrib import messages
from django.core import mail
from django.utils.text import slugify
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User, Group, UserManager

from principal.models import School, Compet, CompetExtra, LEVEL_NAME
from exams.models import TesteFase1
#from restrito.views import send_email_compet_registered
from principal.utils.utils import (make_password, obi_year,
                                   capitalize_name, remove_accents,
                                   write_uploaded_file,
                                   format_compet_id,)
#from restrito.views import compet_authorize_default_exams

logger = logging.getLogger(__name__)

NUM_POINTS_FASE_3 = {1: 40, 2: 40, 3: 400, 4:500, 5:400, 6: 400, 7:30}
def calc_nota(c):
    if c.compet_points_fase3>0:
        nota_fase3 = round(100.0*c.compet_points_fase3/float(NUM_POINTS_FASE_3[c.compet_type]))
    else:
        nota_fase3 = 0
    return nota_fase3

def calc_faixa(c):
    if c.compet_year[0] == 'F':
        return 'Ens. Fundamental'
    else:
        return 'Ens. Médio'

def calc_nivel(c):
    NIVEL = {7:'Iniciação Nível Júnior',1:'Iniciação Nível 1',2:'Iniciação Nível 2',
             5:'Programação Nível Júnior',3:'Programação Nível 1',4:'Programação Nível 2'}
    return NIVEL[c.compet_type]
        
def calc_premio(c):
    if c.compet_medal == 'o':
        m = 'medalha de ouro'
    elif c.compet_medal == 'p':
        m = 'medalha de prata'
    elif c.compet_medal == 'b':
        m = 'medalha de bronze'
    elif c.compet_medal == 'h':
        m = 'honra ao mérito'
    else:
        m = 'mérito'
    return m

def print_header_row():
    print('Nome Competidor',end=',')
    print('Data Nasc.',end=',')
    print('Nota Final',end=',')
    print('Faixa',end=',')
    print('Nível',end=',')
    print('Premiação',end=',')
    print('Nome Mãe',end=',')
    print('CPF',end=',')
    print('NIS')
    
def print_row(c, cnew, extra):
    print(cnew.compet_name,end=',')
    print(cnew.compet_birth_date,end=',')
    print(calc_nota(c),end=',')
    print(calc_faixa(c),end=',')
    print(calc_nivel(c),end=',')
    print(calc_premio(c),end=',')
    print(extra.compet_mother_name,end=',')
    print(extra.compet_cpf,end=',')
    print(extra.compet_nis)
    
def gen_bic():
    count = 0
    all = Compet.objects.all()
    old = Compet.objects.all().using('obi2021')
    compets = CompetExtra.objects.filter(compet_id__compet_rank_final__lte=500).order_by('compet_id__compet_rank_final')

    print_header_row()
    for c in compets:
        compet = all.get(compet_id=c.compet_id)
        #print(compet.compet_name, compet.compet_rank_final, c.compet_nis, end=" ")
        try:
            compet_old = old.get(compet_name__iexact=compet.compet_name)
            #print("OK", compet_old.compet_rank_final)
            if compet_old.compet_points_fase3>0:
                print_row(compet_old, compet, c)
                count += 1
            else:
                pass

        except:
            pass
            #print("NO")

            
    return count

class Command(BaseCommand):
    help = 'Send message'

    def add_arguments(self, parser):
        pass
        #parser.add_argument('modality', nargs='+', type=str)

    def handle(self, *args, **options):
        #modality = options['modality'][0]
        count = gen_bic()
        self.stdout.write(self.style.SUCCESS('Found {} compets.'.format(count)))
