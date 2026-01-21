import sys
import logging
import unidecode

import string
from django import forms
from django.apps import apps
from django.contrib.auth.management import _get_all_permissions
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.core.validators import EmailValidator, RegexValidator
from django.db import models
from django.utils.encoding import smart_str
from django.utils import timezone

from .utils.utils import capitalize_name, format_compet_id, obi_year

logger = logging.getLogger('obi')

###################
# To fix bug in permissions for proxy model, https://gist.github.com/magopian/7543724
# have to run migrate everytime a new permission is needed


def proxy_perm_create(**kwargs):
    for model in apps.get_models():
        opts = model._meta
        #sys.stdout.write('{}-{}\n'.format(opts.app_label, opts.object_name.lower()))
        ctype, created = ContentType.objects.get_or_create(
            app_label=opts.app_label,
            model=opts.object_name.lower())

        for codename, name in _get_all_permissions(opts):
            #sys.stdout.write('  --{}\n'.format(codename))
            p, created = Permission.objects.get_or_create(
                codename=codename,
                content_type=ctype,
                defaults={'name': name})
            if created:
                #sys.stdout.write('Adding permission {}\n'.format(p))
                pass

models.signals.post_migrate.connect(proxy_perm_create)

LANG_SUFFIXES = {"cc":2, "cpp":2, "c++":2, "c":1, "pas":3, "p":3, "py2":4, "java":5, "js":6, "py3":7}
LANG_SUFFIXES_NAMES = {2:".cpp", 1:".c", 3:".pas", 4:"_py2.py", 5:".java", 6:".js", 7:"_py3.py"}

NO_CHOICE = 0
REGULAR_PUBLIC = 1
REGULAR_PRIVATE = 2
HIGHER_PUBLIC = 3
HIGHER_PRIVATE = 4
SPECIAL = 5
SCHOOL_TYPE_CHOICES = (
    ('', u'Selecione'),
    (REGULAR_PUBLIC, u'Ensino Básico Pública'),
    (REGULAR_PRIVATE, u'Ensino Básico Privada'),
    (HIGHER_PUBLIC, u'Ensino Superior Pública'),
    (HIGHER_PRIVATE, u'Ensino Superior Privada'),
#    (SPECIAL, u'Ensino de Programação'),
)
#     )
# 2019
# PUB = 1
# PRI = 2
# SCHOOL_TYPE_CHOICES = (
#     (PUB, u'Pública'),
#     (PRI, u'Privada'),
#     )

SEX_M = 'M'
SEX_F = 'F'
SEX_O = 'O'
SEX_CHOICES = (
    (SEX_F,'Feminino'), (SEX_M,'Masculino'), (SEX_O,'Outro')
)
SEX_CHOICES_CFOBI = (
    (SEX_F,'Feminino'), (SEX_O,'Outro')
)


COMPET_SORT_CHOICES = [('compet_name','Nome'),('compet_id','Num. Inscr.')]
COMPET_SORT_CHOICES_CLASS = [('compet_name','Nome'),('compet_id','Num. Inscr.'),('compet_class','Turma')]

IJ = 7
I1 = 1
I2 = 2
PJ = 5
P1 = 3
P2 = 4
PS = 6
CF = 8

LEVEL_ALL = (IJ, I1, I2, PJ, P1, P2, PS)
LEVEL_INI = (IJ, I1, I2)
LEVEL_PROG = (PJ, P1, P2, PS)
LEVEL_CFOBI = (PJ, P1, P2)

LEVEL_CHOICES_INI = (
    (IJ, u'Iniciação Nível Júnior'),
    (I1, u'Iniciação Nível 1'),
    (I2, u'Iniciação Nível 2'),
)
LEVEL_CHOICES_PROG = (
    (PJ, u'Programação Nível Júnior'),
    (P1, u'Programação Nível 1'),
    (P2, u'Programação Nível 2'),
    (PS, u'Programação Nível Sênior'),
)
LEVEL_CHOICES_CFOBI = (
    (PJ, u'Programação Nível Júnior'),
    (P1, u'Programação Nível 1'),
    (P2, u'Programação Nível 2'),
)
LEVEL_CHOICES = LEVEL_CHOICES_INI + LEVEL_CHOICES_PROG
LEVEL_CHOICES_FORM = (('',u'Todas'),) + LEVEL_CHOICES
LEVEL_CHOICES_FILTER = (('',u'Todas'),) + (('I',u'Iniciação'),) + (('P',u'Programação'),) + LEVEL_CHOICES
LEVEL_CHOICES_FILTER_INI = (('',u'Todas'),) + LEVEL_CHOICES_INI
LEVEL_CHOICES_FILTER_PROG = (('',u'Todas'),) + LEVEL_CHOICES_PROG
LEVEL_CHOICES_FILTER_CFOBI = (('',u'Todas'),) + LEVEL_CHOICES_CFOBI
LEVEL_NAME = {IJ:'IJ',I1:'I1',I2:'I2',PJ:'PJ',P1:'P1',P2:'P2',PS:'PS',CF:'CF'}
LEVEL_NAME_FULL = {IJ:'Iniciação Nível Júnior',I1:'Iniciação Nível 1',I2:'Iniciação Nível 2',
                   PJ:'Programação Nível Júnior',P1:'Programação Nível 1',P2:'Programação Nível 2',PS:'Programação Nível Sênior',CF:'Competição Feminina'}
LEVEL={'IJ':IJ,'I1':I1,'I2':I2,'PJ':PJ, 'P1':P1,'P2':P2,'PS':PS,'PU':PS}

LANG_C = 1
LANG_CPP = 2
LANG_PASCAL = 3
LANG_PYTHON2 = 4
LANG_JAVA = 5
LANG_JAVASCRIPT = 6
LANG_PYTHON3 = 7
LANGUAGE_CHOICES = (
    (LANG_C,'C'),
    (LANG_CPP,'C++'),
    (LANG_PASCAL,'Pascal'),
    (LANG_PYTHON2,'Python2'),
    (LANG_PYTHON3,'Python3'),
    (LANG_JAVA,'Java'),
    (LANG_JAVASCRIPT,'Javascript'),
)
LANGUAGE_NAMES = {LANG_C: 'C', LANG_CPP: 'C++', LANG_PASCAL: 'Pascal', LANG_PYTHON2: 'Python2',
                  LANG_JAVA: 'Java', LANG_JAVASCRIPT: 'Javascript', LANG_PYTHON3: 'Python3'}
STATE_CHOICES = (('','Todos'),
    ('AC','AC'),
    ('AL','AL'),
    ('AM','AM'),
    ('AP','AP'),
    ('BA','BA'),
    ('CE','CE'),
    ('DF','DF'),
    ('ES','ES'),
    ('GO','GO'),
    ('MA','MA'),
    ('MG','MG'),
    ('MS','MS'),
    ('MT','MT'),
    ('PA','PA'),
    ('PB','PB'),
    ('PE','PE'),
    ('PI','PI'),
    ('PR','PR'),
    ('SC','SC'),
    ('SE','SE'),
    ('SP','SP'),
    ('RJ','RJ'),
    ('RN','RN'),
    ('RO','RO'),
    ('RR','RR'),
    ('RS','RS'),
    ('TO','TO')
)

PARTIC_TYPE_CHOICES_FORM = (('',u'Selecione'),
                            ('compet',u'Competidor'),
                            ('deleg',u'Coordenador'),
                            ('colab',u'Colaborador'),
                            )

FUND4 = 'F4'
FUND5 = 'F5'
FUND6 = 'F6'
FUND7 = 'F7'
FUND8 = 'F8'
FUND9 = 'F9'
MED1 = 'M1'
MED2 = 'M2'
MED3 = 'M3'
TEC4 = 'T4'
UNI1 = 'U1'
SCHOOL_YEAR_CHOICES = (
    (FUND4, u'Fundamental, quarto ano'),
    (FUND5, u'Fundamental, quinto ano'),
    (FUND6, u'Fundamental, sexto ano'),
    (FUND7, u'Fundamental, sétimo ano'),
    (FUND8, u'Fundamental, oitavo ano'),
    (FUND9, u'Fundamental, nono ano'),
    (MED1, u'Médio, primeiro ano'),
    (MED2, u'Médio, segundo ano'),
    (MED3, u'Médio, terceiro ano'),
    (TEC4, u'Técnico, quarto ano'),
    (UNI1, u'Universitário, primeiro ano'),
)
SCHOOL_YEAR_CHOICES_CFOBI = (
    (FUND4, u'Fundamental, quarto ano'),
    (FUND5, u'Fundamental, quinto ano'),
    (FUND6, u'Fundamental, sexto ano'),
    (FUND7, u'Fundamental, sétimo ano'),
    (FUND8, u'Fundamental, oitavo ano'),
    (FUND9, u'Fundamental, nono ano'),
    (MED1, u'Médio, primeiro ano'),
    (MED2, u'Médio, segundo ano'),
    (MED3, u'Médio, terceiro ano'),
)

SCHOOL_YEARS = (FUND4,FUND5,FUND6,FUND7,FUND8,FUND9,MED1,MED2,MED3,TEC4,UNI1)
SCHOOL_YEARS_CFOBI = (FUND4,FUND5,FUND6,FUND7,FUND8,FUND9,MED1,MED2,MED3)

SCHOOL_YEAR_FULL = {
    FUND4: u'Fundamental, quarto ano',
    FUND5: u'Fundamental, quinto ano',
    FUND6: u'Fundamental, sexto ano',
    FUND7: u'Fundamental, sétimo ano',
    FUND8: u'Fundamental, oitavo ano',
    FUND9: u'Fundamental, nono ano',
    MED1: u'Médio, primeiro ano',
    MED2: u'Médio, segundo ano',
    MED3: u'Médio, terceiro ano',
    TEC4: u'Técnico, quarto ano',
    UNI1: u'Universitário, primeiro ano',
}

def remove_accents(s):
    return unidecode.unidecode(s)

def validate_compet_level(compet_type, compet_year, school_type):
    '''returns non-empty message if finds an error '''
    error_message = ''
    compet_type = int(compet_type)
    school_type = int(school_type)
    if school_type == SPECIAL and compet_type in [IJ,I1,I2]:
        error_message = "Alunos de escolas não regulares podem participar somente da modalidade Programação"
        # not a regular school
    #elif compet_type in (PJ,P1,P2,PS):
        #pass
        #error_message = "Inscrições encerradas para a modalidade Programação"
    elif compet_type in [PJ] and compet_year in [MED1,MED2,MED3,TEC4,UNI1]:
        error_message = "Alunos da modalidade Programação Júnior devem estar no Ensino Fundamental"
    elif compet_type in [P1] and compet_year in [MED2,MED3,TEC4,UNI1]:
        error_message = "Alunos da modalidade Programação 1 devem estar no Ensino Fundamental ou no primeiro ano do Ensino Médio"
    elif compet_type == P2 and compet_year in [TEC4,UNI1]:
        error_message = "Alunos da modalidade Programação 2 devem estar cursando no máximo o terceiro ano do Ensino Médio"
    elif compet_type == PS and compet_year not in [TEC4,UNI1]:
        error_message = "Alunos da modalidade Programação Sênior devem estar cursando o quarto ano do Ensino Técnico/Médio ou primeiro ano do Ensino Superior"
    elif compet_type == IJ and compet_year not in [FUND4, FUND5]:
        error_message = "Alunos da modalidade Iniciação Júnior devem estar no quarto ou quinto ano do Ensino Fundamental"
    elif compet_type == I1 and compet_year not in [FUND6, FUND7]:
        error_message = "Alunos da modalidade Iniciação 1 devem estar no sexto ou sétimo ano do Ensino Fundamental"
    elif compet_type == I2 and compet_year not in [FUND8, FUND9]:
        error_message = "Alunos da modalidade Iniciação 2 devem estar no oitavo ou nono ano do Ensino Fundamental"
    return error_message


def validate_email_colab(email, show_which=False):
    if not email:
        return
    # email_exists = Compet.objects.filter(compet_email=email)
    # if len(email_exists) > 0:
    #     if show_which:
    #         return 'Este email já está registrado para outro competidor: {}'.format(email_exists[0])
    #     else:
    #         return 'Este email já está registrado para outro participante da OBI.'

    # email_exists = School.objects.filter(school_deleg_email=email)
    # if len(email_exists) > 0:
    #     if show_which:
    #         return 'Este email já está registrado para um Coordenador da OBI: {}'.format(email_exists[0])
    #     else:
    #         return 'Este email já está registrado para outro participante da OBI.'

    email_exists = Colab.objects.filter(colab_email=email)
    if len(email_exists) > 0:
        if show_which:
            return 'Este email já está registrado para um Colaborador da OBI: {}'.format(email_exists[0])
        else:
            return 'Este email já está registrado para um Colaborador da OBI.'



def validate_username(username):
    for c in username:
        if c not in string.ascii_letters+string.digits+'_-@.':
            raise forms.ValidationError(
                '"%(username)s" é um nome de usuário inválido, favor escolha outro nome de usuário.',
                params={'username': username},
                )
    if User.objects.filter(username=username).exists():
        raise forms.ValidationError(
            '"%(username)s" já está sendo utilizado, por favor escolha outro nome de usuário.',
            params={'username': username},
            )
    # do not need this anymore
    if School.objects.filter(school_deleg_username=username).exists():
        raise forms.ValidationError(
            '"%(username)s" já está sendo utilizado, por favor escolha outro nome de usuário.',
            params={'username': username},
            )
    # if Compet.objects.filter(compet_email=username).exists():
    #     raise forms.ValidationError(
    #         '"%(username)s" já está sendo utilizado, por favor escolha outro nome de usuário.',
    #         params={'username': username},
    #         )

    if Colab.objects.filter(colab_email=username).exists():
        raise forms.ValidationError(
            '"%(username)s" já está sendo utilizado, por favor use outro endereço de email.',
            params={'username': username},
            )

def validate_username_colab(username):
    # in future, merge with validate username
    if User.objects.filter(username=username).exists():
        return 'endereço de email já está sendo utilizado para outro colaborador, por favor utilize outro'


def validate_username_compet(username):
    # in future, merge with validate username
    for c in username:
        if c not in string.ascii_letters+string.digits+'_-@.':
            return 'nome de usuário inválido'
    if len(username) < 4:
        return 'nome de usuário muito curto, deve ter ao menos quatro caracteres'
    if User.objects.filter(username=username).exists():
        return 'nome de usuário já está sendo utilizado'


class School(models.Model):
    def __str__(self):
        return self.school_name

    school_id = models.AutoField('ID',primary_key=True)
    school_inep_code = models.IntegerField('Código INEP da Escola',default=0,blank=True)
    school_code = models.IntegerField('Código da Escola (id do ano anterior)',default=0,blank=True)
    school_name = models.CharField('Nome da Escola',max_length=100)
    school_type = models.IntegerField(
        'Tipo da escola',
        choices = SCHOOL_TYPE_CHOICES,
        blank=False,
        )
    school_deleg_name = models.CharField('Coordenador local',max_length=100)
    school_deleg_email = models.CharField('Email',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')])
    school_deleg_username = models.CharField('Nome de usuário',max_length=100)
    school_change_coord = models.BooleanField("Novo coord",null=True,blank=True) 

    school_ok = models.BooleanField(default=False) 
    school_is_known = models.BooleanField('Prev',default=False)
    school_state = models.CharField(
        'Estado',
        max_length=2,
        choices = STATE_CHOICES)
    school_city = models.CharField('Cidade',max_length=150)
    school_zip = models.CharField('CEP',max_length=10)
    school_address = models.CharField('Logradouro',max_length=256)
    school_address_number = models.CharField('Número',max_length=16)
    school_address_complement = models.CharField('Complemento',max_length=256,null=True,blank=True)
    school_address_district = models.CharField('Bairro',max_length=128,null=True,blank=True)
    school_phone = models.CharField('Telefone da Escola',max_length=20)
    school_deleg_phone = models.CharField('Telefone Pessoal',max_length=20)
    # old school fields
    school_deleg_login = models.CharField('Nome de usuário',max_length=100,null=True)
    school_ddd = models.CharField('DDD',max_length=4,null=True)
    school_prev = models.IntegerField('',default=0,blank=True,null=True)
    # school for phase 3
    school_is_site_phase3 = models.BooleanField('Sede Fase3',default=False)
    school_site_phase3_show = models.BooleanField(default=False)
    school_site_phase3_type = models.IntegerField(default=0) # 0: not site, 1: site ini, 2: site prog, 3: site both
    school_site_phase3 = models.IntegerField(default=0)
    school_site_phase3_ini = models.IntegerField(default=0)
    school_site_phase3_prog = models.IntegerField(default=0)
    school_address_building = models.CharField('Local da prova',max_length=1024,null=True,blank=True)
    school_address_map = models.CharField('Link para mapa',max_length=512,null=True,blank=True)
    school_address_other = models.CharField('Outras informações',max_length=1024,null=True,blank=True)
    school_has_medal = models.BooleanField(default=False)
    school_hash = models.CharField('Hash para recuperação',max_length=256,null=True,blank=True)
    school_turn_phase1_prog = models.CharField('Turno Fase 1 Programação',max_length=1,null=True,blank=True)
    school_turn_phase1_ini = models.CharField('Turno Fase 1 Iniciação',max_length=1,null=True,blank=True)

    def num_inscr(self):
        "Returns number of students registered by school"
        try:
            num = Compet.objects.filter(compet_school=self.pk).count()
        except:
            num = 0
        return num

    class Meta:
        db_table = 'school'
        verbose_name = 'Escola'
        verbose_name_plural = 'Escolas'
        ordering = ['school_name']

class SchoolExtra(models.Model):
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    school_answer_consulta_fase3 = models.IntegerField('Resposta a consulta sede Fase3)',default=0,blank=True)
    user_answer_consulta_fase3 = models.IntegerField('Quem respondeu consulta sede Fase3)',default=0,blank=True)
    date_answer_consulta_fase3 = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'school_extra'
    

class SchoolDesclassif(models.Model):
    def __str__(self):
        return self.school_name

    school_id = models.AutoField('ID',primary_key=True)
    school_inep_code = models.IntegerField('Código INEP da Escola',default=0,blank=True)
    school_code = models.IntegerField('Código da Escola (id do ano anterior)',default=0,blank=True)
    school_name = models.CharField('Nome da Escola',max_length=100)
    school_type = models.IntegerField(
        'Tipo da escola',
        choices = SCHOOL_TYPE_CHOICES,
        )
    school_deleg_name = models.CharField('Coordenador local',max_length=100)
    school_deleg_email = models.CharField('Email',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')])
    school_deleg_username = models.CharField('Nome de usuário',max_length=100)
    school_ok = models.BooleanField(default=False) 
    school_is_known = models.BooleanField('Prev',default=False)
    school_state = models.CharField(
        'Estado',
        max_length=2,
        choices = STATE_CHOICES)
    school_city = models.CharField('Cidade',max_length=64)
    school_zip = models.CharField('CEP',max_length=10)
    school_address = models.CharField('Logradouro',max_length=256)
    school_address_number = models.CharField('Número',max_length=16)
    school_address_complement = models.CharField('Complemento',max_length=256,null=True,blank=True)
    school_address_district = models.CharField('Bairro',max_length=128,null=True,blank=True)
    school_phone = models.CharField('Telefone da Escola',max_length=20)
    school_deleg_phone = models.CharField('Telefone Pessoal',max_length=20)
    # old school fields
    school_deleg_login = models.CharField('Nome de usuário',max_length=100,null=True)
    school_ddd = models.CharField('DDD',max_length=4,null=True)
    school_prev = models.IntegerField('',default=0,blank=True,null=True)
    # school for phase 3
    school_is_site_phase3 = models.BooleanField(default=False)
    school_site_phase3_show = models.BooleanField(default=False)
    school_site_phase3_type = models.IntegerField(default=0) # 0: not site, 1: site ini, 2: site prog, 3: site both
    school_site_phase3 = models.IntegerField(default=0)
    school_site_phase3_ini = models.IntegerField(default=0)
    school_site_phase3_prog = models.IntegerField(default=0)
    school_address_building = models.CharField('Local da prova',max_length=1024,null=True,blank=True)
    school_address_map = models.CharField('Link para mapa',max_length=512,null=True,blank=True)
    school_address_other = models.CharField('Outras informações',max_length=1024,null=True,blank=True)
    school_has_medal = models.BooleanField(default=False)
    school_hash = models.CharField('Hash para recuperação',max_length=256,null=True,blank=True)
    school_turn_phase1_prog = models.CharField('Turno Fase 1 Programação',max_length=1,null=True,blank=True)
    school_turn_phase1_ini = models.CharField('Turno Fase 1 Iniciação',max_length=1,null=True,blank=True)

    def num_inscr(self):
        "Returns number of students registered by school"
        try:
            num = Compet.objects.filter(compet_school=self.pk).count()
        except:
            num = 0
        return num

    class Meta:
        db_table = 'school_desclassif'
        verbose_name = 'Escola Desclassificada'
        verbose_name_plural = 'Escolas Desclassificadas'
        ordering = ['school_name']

class SchoolRejected(models.Model):
    def __str__(self):
        return self.school_name

    school_id = models.AutoField('ID',primary_key=True)
    school_inep_code = models.IntegerField('Código INEP da Escola',default=0,blank=True)
    school_code = models.IntegerField('Código da Escola (id do ano anterior)',default=0,blank=True)
    school_name = models.CharField('Nome da Escola',max_length=100)
    school_type = models.IntegerField(
        'Tipo da escola',
        choices = SCHOOL_TYPE_CHOICES,
        )
    school_deleg_name = models.CharField('Coordenador local',max_length=100)
    school_deleg_email = models.CharField('Email',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')])
    school_deleg_username = models.CharField('Nome de usuário',max_length=100)
    school_ok = models.BooleanField(default=False) 
    school_is_known = models.BooleanField('Prev',default=False)
    school_state = models.CharField(
        'Estado',
        max_length=2,
        choices = STATE_CHOICES)
    school_city = models.CharField('Cidade',max_length=64)
    school_zip = models.CharField('CEP',max_length=10)
    school_address = models.CharField('Logradouro',max_length=256)
    school_address_number = models.CharField('Número',max_length=16)
    school_address_complement = models.CharField('Complemento',max_length=256,null=True,blank=True)
    school_address_district = models.CharField('Bairro',max_length=128,null=True,blank=True)
    school_phone = models.CharField('Telefone da Escola',max_length=20)
    school_deleg_phone = models.CharField('Telefone Pessoal',max_length=20)
    school_reason = models.CharField('Razão',max_length=256)

    class Meta:
        db_table = 'school_rejected'
        verbose_name = 'Escola Rejeitada'
        verbose_name_plural = 'Escolas Rejeitadas'

class SchoolRemoved(models.Model):
    def __str__(self):
        return self.school_name

    school_id = models.AutoField('ID',primary_key=True)
    school_inep_code = models.IntegerField('Código INEP da Escola',default=0,blank=True)
    school_code = models.IntegerField('Código da Escola (id do ano anterior)',default=0,blank=True)
    school_name = models.CharField('Nome da Escola',max_length=100)
    school_type = models.IntegerField(
        'Tipo da escola',
        choices = SCHOOL_TYPE_CHOICES,
        )
    school_deleg_name = models.CharField('Coordenador local',max_length=100)
    school_deleg_email = models.CharField('Email',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')])
    school_deleg_username = models.CharField('Nome de usuário',max_length=100)
    school_ok = models.BooleanField(default=False) 
    school_is_known = models.BooleanField('Prev',default=False)
    school_state = models.CharField(
        'Estado',
        max_length=2,
        choices = STATE_CHOICES)
    school_city = models.CharField('Cidade',max_length=64)
    school_zip = models.CharField('CEP',max_length=10)
    school_address = models.CharField('Logradouro',max_length=256)
    school_address_number = models.CharField('Número',max_length=16)
    school_address_complement = models.CharField('Complemento',max_length=256,null=True,blank=True)
    school_address_district = models.CharField('Bairro',max_length=128,null=True,blank=True)
    school_phone = models.CharField('Telefone da Escola',max_length=20)
    school_deleg_phone = models.CharField('Telefone Pessoal',max_length=20)

    class Meta:
        db_table = 'school_removed'
        verbose_name = 'Escola Removida'
        verbose_name_plural = 'Escolas Removidas'
        


class SchoolUnregistered(School):
    def school_email_prev(self):
        "Returns True if email was used the previous year"
        prev_year = obi_year(as_int=True) - 1
        is_known1 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_deleg_email__iexact=self.school_deleg_email).exists()
        prev_year = obi_year(as_int=True) - 2
        is_known2 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_deleg_email__iexact=self.school_deleg_email).exists()
        return is_known1 or is_known2

    def school_email_cur(self):
        "Returns True if email is used the current year"
        is_known = School.objects.exclude(school_id=self.pk).filter(school_deleg_email__iexact=self.school_deleg_email).exists()
        return is_known


    def school_name_prev(self):
        "Returns True if school name was used the previous year"
        prev_year = obi_year(as_int=True) - 1
        is_known1 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_name__iexact=self.school_name).exists()
        prev_year = obi_year(as_int=True) - 2
        is_known2 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_name__iexact=self.school_name).exists()
        return is_known1 or is_known2


    def school_name_prev_full(self):
        "Returns True if school name was used the previous year"
        prev_year = obi_year(as_int=True) - 1
        is_known1 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_name__iexact=self.school_name).exists()
        prev_year = obi_year(as_int=True) - 2
        is_known2 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_name__iexact=self.school_name).exists()
        return is_known1 or is_known2

    def school_deleg_name_prev(self):
        "Returns True if school deleg name was used the previous year"
        prev_year = obi_year(as_int=True) - 1
        is_known1 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_deleg_name__iexact=self.school_deleg_name).exists()
        prev_year = obi_year(as_int=True) - 2
        is_known2 = School.objects.using('obi{}'.format(prev_year)).filter(school_ok=True,school_deleg_name__iexact=self.school_deleg_name).exists()
        return is_known1 or is_known2

    def school_name_repeated(self):
        "Returns True if school name appears already in the DB"
        try:
            #query = School.objects.filter(school_city__iexact=self.school_city).exclude(school_id=self.pk)
            query = School.objects.all().exclude(school_id=self.pk)
            query = query.only('school_name')
            school_names = []
            for s in query:
                school_names.append(remove_accents(s.school_name).lower())
            return remove_accents(self.school_name.strip()).lower() in school_names
        except:
            return False

    def school_name_city_repeated(self):
        "Returns True if school name appears already in the DB"
        #query = School.objects.filter(school_city__iexact=self.school_city).exclude(school_id=self.pk)
        query = School.objects.all().exclude(school_id=self.pk)
        name = remove_accents(self.school_name.strip()).lower()
        city = remove_accents(self.school_city.strip()).lower()
        for s in query:
            if remove_accents(s.school_name).lower() == name and remove_accents(s.school_city).lower() == city:
                return True
        return False

        
    school_email_cur.boolean = True
    school_email_cur.short_description = u'Cur Email'
    school_email_prev.boolean = True
    school_email_prev.short_description = u'Prev Email'
    school_name_prev.boolean = True
    school_name_prev.short_description = u'Prev Nome'
    school_deleg_name_prev.boolean = True
    school_deleg_name_prev.short_description = u'Prev Deleg'
    school_name_repeated.boolean = True
    school_name_repeated.short_description = u'Repet'
    school_name_city_repeated.boolean = True
    school_name_city_repeated.short_description = u'CityRepet'

    school_name_prev.short_description = u'Prev Escola'

    class Meta:
        proxy = True
        verbose_name = 'Escola Pendente'
        verbose_name_plural = 'Escolas Pendentes'

class SchoolDeleg(School):
    class Meta:
        proxy = True
        verbose_name = 'Minha Escola'
        verbose_name_plural = 'Minha Escola'


class SchoolPhase3(School):
    class Meta:
        proxy = True
        verbose_name = 'Escola Fase Nacional'
        verbose_name_plural = 'Escolas Fase Nacional'

    def get_compets_ini_in_this_site(self):
        if not self.school_is_site_phase3:
            # should return something
            return Compet.objects.none()

        compet_ids_override_yes = Compet.objects.filter(compet_school_id_fase3=self.school_id,compet_type__in=(IJ,I1,I2)).values_list('compet_id', flat=True)
        compet_ids_override_no = Compet.objects.filter(compet_school_id_fase3__isnull=False,compet_type__in=(IJ,I1,I2)).exclude(compet_id__in=compet_ids_override_yes).values_list('compet_id', flat=True)

        schools_in_this_site = School.objects.filter(school_site_phase3_ini=self.school_id).values_list('school_id', flat=True)
        compet_ids_in_this_site = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(IJ,I1,I2),
                                                        compet_school_id__in=schools_in_this_site).exclude(compet_id__in=compet_ids_override_no).values_list('compet_id', flat=True)
        
        return Compet.objects.filter(compet_id__in=list(compet_ids_in_this_site) + list(compet_ids_override_yes))

    def get_compets_prog_in_this_site(self):
        if not self.school_is_site_phase3:
            # should return something
            return Compet.objects.none()

        compet_ids_override_yes = Compet.objects.filter(compet_school_id_fase3=self.school_id,compet_type__in=(PJ,P1,P2,PS)).values_list('compet_id', flat=True)
        compet_ids_override_no = Compet.objects.filter(compet_school_id_fase3__isnull=False,compet_type__in=(PJ,P1,P2,PS)).exclude(compet_id__in=compet_ids_override_yes).values_list('compet_id', flat=True)

        schools_in_this_site = School.objects.filter(school_site_phase3_prog=self.school_id).values_list('school_id', flat=True)
        compet_ids_in_this_site = Compet.objects.filter(compet_classif_fase2=True,compet_type__in=(PJ,P1,P2,PS),
                                                        compet_school_id__in=schools_in_this_site).exclude(compet_id__in=compet_ids_override_no).values_list('compet_id', flat=True)

        return Compet.objects.filter(compet_id__in=list(compet_ids_in_this_site) + list(compet_ids_override_yes))


#######################
# last access
#######################
class LastAccess(models.Model):
    def __str__(self):
        return self.user.date

    last_access_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'last_access'
        verbose_name = 'Último acesso'
        verbose_name_plural = 'Últimos acessos'

#######################
# deleg
#######################
class Deleg(models.Model):
    def __str__(self):
        return self.user.first_name

    deleg_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    deleg_school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE)
    class Meta:
        db_table = 'deleg'
        verbose_name = 'Coordenador'
        verbose_name_plural = 'Coordenador'

    def get_school_name(self):
        """Return the name of the school associated."""
        return self.first_name


#######################
# colab
#######################
class Colab(models.Model):
    def __str__(self):
        return self.colab_name

    colab_id = models.AutoField(primary_key=True)
    colab_name = models.CharField('Nome',max_length=100)
    colab_school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.PROTECT)
    colab_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        )
    colab_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    colab_admin = models.CharField(
        'Pode gerenciar competidores',
        max_length=1,
        choices = (('S','Sim'),('N','Não'),),
        null = False,
        blank = False,
    )
    colab_admin_full = models.CharField(
        'Pode gerenciar competidores e provas',
        max_length=1,
        choices = (('S','Sim'),('N','Não'),),
        null = False,
        blank = False,
    )

    class Meta:
        db_table = 'colab'
        verbose_name = 'Colaborador'
        verbose_name_plural = 'Colaboradores'



#######################
# compet
#######################
class Compet(models.Model):
    def __str__(self):
        return self.compet_name

    def delete(self, *args, **kwargs):
        res = super().delete(*args, **kwargs)
        # django does not cascade the delete, do it explicitly
        if self.user:
            User.objects.filter(id=self.user.id).delete()
        return res

    def _get_full_compet_id(self):
        "Returns the compet id formatted with checking char."
        return format_compet_id(self.pk)

    full_compet_id = property(_get_full_compet_id)
    _get_full_compet_id.short_description = u'Num. Inscrição'

    def _get_compet_type_short(self):
        "Returns the compet type formatted short."
        return LEVEL_NAME[self.compet_type]

    compet_type_short = property(_get_compet_type_short)
    _get_compet_type_short.short_description = u'Modalidade'

    def _get_school_city_phase3(self):
        "Returns the name of the school, used in phase 3."
        try:
            s = School.objects.get(pk=self.compet_school.pk)
            city = s.school_city
        except:
            city = 'Sede não encontrada'
        return city

    school_city_phase3 = property(_get_school_city_phase3)
    _get_school_city_phase3.short_description = u'Cidade'

    compet_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True)
    compet_name = models.CharField('Nome',max_length=100)
    compet_birth_date = models.DateField(u'Data de nascimento',default='01/01/2010',null=True,blank=True)
    #compet_birth_date = models.DateField(u'Data de nascimento',validators = [RegexValidator('\d\d/\d\d/\d\d\d\d')],null=True,blank=True)
    compet_school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.PROTECT)
    compet_type = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
        )
    compet_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        )
    #compet_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True,help_text='Para o(a) competidor(a) ter acesso aos <a href="/info/apoios/">benefícios AluraStart</a>, é necessário fornecer o email do(a) competidor(a).')
    compet_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True)
    compet_year = models.CharField(
        'Ano na escola',
        max_length=32,
        choices=SCHOOL_YEAR_CHOICES,
        )
    compet_class = models.CharField('Turma',default='A',max_length=8,null=True,blank=True)

    compet_points_fase1 = models.IntegerField('Pontos Fase 1',null=True,blank=True)
    compet_points_fase2 = models.IntegerField('Pontos Fase 2',null=True,blank=True)
    compet_points_fase3 = models.IntegerField('Pontos Fase 3',null=True)
    compet_points_fase2b = models.IntegerField('Pontos Fase Turno B',null=True)
    compet_points_final = models.IntegerField(null=True)
    compet_answers_fase1 = models.TextField(null=True)
    compet_answers_fase2 = models.TextField(null=True)
    compet_answers_fase3 = models.TextField(null=True)
    #compet_log_fase1 = models.TextField(null=True)
    #compet_log_fase2 = models.TextField(null=True)
    #compet_log_fase3 = models.TextField(null=True)
    compet_rank_fase1 = models.IntegerField(null=True)
    compet_rank_fase2 = models.IntegerField(null=True)
    compet_rank_fase3 = models.IntegerField(null=True)
    compet_rank_final = models.IntegerField(null=True)
    compet_rank_state = models.IntegerField(null=True)
    compet_medal = models.CharField(max_length=1,null=True)
    compet_classif_fase1 = models.BooleanField('Classificado',null=True)
    compet_classif_fase2 = models.BooleanField('Classificado',null=True)
    compet_classif_fase3 = models.BooleanField('Classificado',null=True)
    compet_classif_fase2a = models.BooleanField('Classificado',null=True)
    compet_classif_fase2b = models.BooleanField('Classificado',null=True)
    compet_school_id_fase3 = models.IntegerField('Sede Fase 3',null=True)
    compet_conf = models.CharField('Conferencia',max_length=16)
    compet_id_full = models.CharField('Número de inscrição',max_length=16)
    class Meta:
        db_table = 'compet'
        verbose_name = 'Competidor'
        verbose_name_plural = 'Competidores'
        unique_together = ("compet_name", "compet_school")


#######################
# compet
#######################
class CompetDesclassif(models.Model):
    def __str__(self):
        return self.compet_name

    # CompetDesclassif does not have a user
    # def delete(self, *args, **kwargs):
    #     res = super().delete(*args, **kwargs)
    #     # django does not cascade the delete, do it explicitly
    #     if self.user:
    #         User.objects.filter(id=self.user.id).delete()
    #     return res

    def _get_full_compet_id(self):
        "Returns the compet id formatted with checking char."
        return format_compet_id(self.pk)

    full_compet_id = property(_get_full_compet_id)
    _get_full_compet_id.short_description = u'Num. Inscrição'

    def _get_compet_type_short(self):
        "Returns the compet type formatted short."
        return LEVEL_NAME[self.compet_type]

    compet_type_short = property(_get_compet_type_short)
    _get_compet_type_short.short_description = u'Modalidade'

    def _get_school_city_phase3(self):
        "Returns the name of the school, used in phase 3."
        try:
            s = School.objects.get(pk=self.compet_school.pk)
            city = s.school_city
        except:
            city = 'Sede não encontrada'
        return city

    school_city_phase3 = property(_get_school_city_phase3)
    _get_school_city_phase3.short_description = u'Cidade'

    compet_id = models.AutoField(primary_key=True)
    compet_name = models.CharField('Nome',max_length=100)
    compet_birth_date = models.DateField(u'Data de nascimento',default='01/01/2000',null=True,blank=True)
    #compet_birth_date = models.DateField(u'Data de nascimento',validators = [RegexValidator('\d\d/\d\d/\d\d\d\d')],null=True,blank=True)
    compet_school_id = models.IntegerField('School')
    compet_type = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
        )
    compet_type_cf = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
        null=True,blank=True)
    compet_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        )
    #compet_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True,help_text='Para o(a) competidor(a) ter acesso aos <a href="/info/apoios/">benefícios AluraStart</a>, é necessário fornecer o email do(a) competidor(a).')
    compet_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True)
    compet_year = models.CharField(
        'Ano na escola',
        max_length=32,
        choices=SCHOOL_YEAR_CHOICES,
        )
    compet_class = models.CharField('Turma',default='A',max_length=8,null=True,blank=True)

    compet_points_fase1 = models.IntegerField('Pontos Fase 1',null=True,blank=True)
    compet_points_fase2 = models.IntegerField('Pontos Fase 2',null=True,blank=True)
    compet_points_fase3 = models.IntegerField('Pontos Fase 3',null=True)
    compet_points_fase2b = models.IntegerField('Pontos Fase Turno B',null=True)
    compet_points_final = models.IntegerField(null=True)
    compet_answers_fase1 = models.TextField(null=True)
    compet_answers_fase2 = models.TextField(null=True)
    compet_answers_fase3 = models.TextField(null=True)
    #compet_log_fase1 = models.TextField(null=True)
    #compet_log_fase2 = models.TextField(null=True)
    #compet_log_fase3 = models.TextField(null=True)
    compet_rank_fase1 = models.IntegerField(null=True)
    compet_rank_fase2 = models.IntegerField(null=True)
    compet_rank_fase3 = models.IntegerField(null=True)
    compet_rank_final = models.IntegerField(null=True)
    compet_rank_state = models.IntegerField(null=True)
    compet_medal = models.CharField(max_length=1,null=True)
    compet_classif_fase1 = models.BooleanField('Classificado',null=True)
    compet_classif_fase2 = models.BooleanField('Classificado',null=True)
    compet_classif_fase3 = models.BooleanField('Classificado',null=True)
    compet_classif_fase2a = models.BooleanField('Classificado',null=True)
    compet_classif_fase2b = models.BooleanField('Classificado',null=True)
    compet_school_id_fase3 = models.IntegerField('Sede Fase 3',null=True)
    compet_conf = models.CharField('Conferencia',max_length=16)
    compet_id_full = models.CharField('Número de inscrição',max_length=16)
    user_id = models.BigIntegerField(null=True)

    compet_type_cf = models.IntegerField(null=True)
    compet_points_cf = models.IntegerField('Pontos CF',null=True,blank=True)
    compet_rank_cf = models.IntegerField('Rank CF',null=True)
    compet_medal_cf = models.CharField(max_length=1,null=True)
    compet_classif_cf = models.BooleanField('Classificada',null=True)
    desclassif_reason = models.CharField('Razão', max_length=512,null=True)
    desclassif_phase = models.IntegerField('Fase',null=True)
    
    class Meta:
        db_table = 'compet_desclassif'
        verbose_name = 'Competidor Desclassificado'
        verbose_name_plural = 'Competidores Desclassificados'



######################
# CF
######################

def validate_compet_feminina_level(compet_type, compet_feminina_type):
    '''returns non-empty message if finds an error '''
    error_message = ''
    compet_type = int(compet_type)
    compet_feminina_type = int(compet_feminina_type)

    if compet_feminina_type not in LEVEL_CFOBI:
        error_message = "Nível inválido para a CF-OBI"

    return error_message

class CompetCfObi(models.Model):
    def __str__(self):
        return self.compet.compet_name


    def _get_full_compet_id(self):
        "Returns the compet id formatted with checking char."
        return format_compet_id(self.pk)


    full_compet_id = property(_get_full_compet_id)
    _get_full_compet_id.short_description = u'Num. Inscrição'


    def _get_compet_type_short(self):
        "Returns the compet type formatted short."
        return LEVEL_NAME[self.compet_type]


    compet_type_short = property(_get_compet_type_short)
    _get_compet_type_short.short_description = u'Modalidade'


    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet, on_delete=models.CASCADE,null=True)
    compet_type = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
    )
    compet_points = models.IntegerField('Pontos CF-OBI',null=True,blank=True)
    compet_rank = models.IntegerField(null=True)
    compet_medal = models.CharField(max_length=1,null=True)
    compet_classif = models.BooleanField('Classificada',null=True)

    class Meta:
        db_table = 'compet_cfobi'
        verbose_name = 'Competidora'
        verbose_name_plural = 'Competidoras'

class CompetCfObiDesclassif(models.Model):
    def __str__(self):
        return self.compet.compet_name


    def _get_full_compet_id(self):
        "Returns the compet id formatted with checking char."
        return format_compet_id(self.pk)


    full_compet_id = property(_get_full_compet_id)
    _get_full_compet_id.short_description = u'Num. Inscrição'


    def _get_compet_type_short(self):
        "Returns the compet type formatted short."
        return LEVEL_NAME[self.compet_type]


    compet_type_short = property(_get_compet_type_short)
    _get_compet_type_short.short_description = u'Modalidade'


    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(CompetDesclassif, on_delete=models.CASCADE,null=True)
    compet_type = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
    )
    compet_points = models.IntegerField('Pontos CF-OBI',null=True,blank=True)
    compet_rank = models.IntegerField(null=True)
    compet_medal = models.CharField(max_length=1,null=True)
    compet_classif = models.BooleanField('Classificada',null=True)

    class Meta:
        db_table = 'compet_cfobi_desclassif'
        verbose_name = 'Competidora'
        verbose_name_plural = 'Competidoras'

        
#######################
# compet extra
#######################
class CompetExtra(models.Model):
    def __str__(self):
        return self.compet_name

    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet, on_delete=models.CASCADE,null=True)
    compet_mother_name = models.CharField('Nome da Mãe',max_length=100,null=True,blank=True)
    compet_cpf = models.CharField(max_length=20,null=True,blank=True)
    compet_nis = models.CharField(max_length=20,null=True,blank=True)
    compet_state_rank_fase2 = models.IntegerField(null=True,blank=True)
    compet_state_medal = models.BooleanField('Medalha Honra Estadual',blank=True,null=True)
    class Meta:
        db_table = 'compet_extra'
        verbose_name = 'Informações Adicionais Competidor'
        verbose_name_plural = 'Informações Adicionais Competidores'

#######################
# hash certifs
#######################
class CertifHash(models.Model):
    def __str__(self):
        return self.compet_name

    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet, on_delete=models.CASCADE,null=True)
    compet_cf = models.OneToOneField(CompetCfObi, on_delete=models.CASCADE,null=True)
    colab = models.OneToOneField(Colab, on_delete=models.CASCADE,null=True)
    school = models.OneToOneField(School, on_delete=models.CASCADE,null=True)
    hash = models.CharField('Hash',max_length=255,unique=True)
    class Meta:
        db_table = 'certif_hash'
        verbose_name = 'Hash certificados'
        verbose_name_plural = 'Hash certificados'

class PasswordCms(models.Model):
    id = models.AutoField(primary_key=True)
    compet = models.OneToOneField(Compet,verbose_name="Competidor",on_delete=models.CASCADE,unique=True)
    password = models.CharField('Senha',max_length=16)
    class Meta:
        db_table = 'password_cms'
        verbose_name = 'Senha CMS'


#######################
# compet auto register
#######################
class CompetAutoRegister(models.Model):
    def __str__(self):
        return self.compet_name

    def clean(self):
        result = validate_compet_level(self.compet_type, self.compet_year, self.compet_school.school_type)
        if result:
            raise ValidationError(result)

    def _get_compet_type_short(self):
        "Returns the compet type formatted short."
        return LEVEL_NAME[self.compet_type]

    compet_type_short = property(_get_compet_type_short)
    _get_compet_type_short.short_description = u'Modalidade'

    id = models.AutoField(primary_key=True)
    compet_status = models.CharField('Status',default='new',max_length=10,blank=True)
    compet_name = models.CharField('Nome',max_length=100)
    compet_birth_date = models.DateField(u'Data de nascimento',default='01/01/2000',null=True,blank=True)
    compet_school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.PROTECT)
    compet_type = models.IntegerField(
        'Modalidade',
        choices = LEVEL_CHOICES,
        )
    compet_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        )
    compet_email = models.CharField('Email',max_length=100,validators = [EmailValidator()])
    compet_year = models.CharField(
        'Ano na escola',
        max_length=32,
        choices=SCHOOL_YEAR_CHOICES,
        )
    compet_class = models.CharField('Turma',default='A',max_length=8,null=True,blank=True)

    # extra fields
    compet_mother_name = models.CharField('Nome da Mãe',max_length=100,null=True,blank=True)
    compet_cpf = models.CharField(max_length=20,null=True,blank=True)
    compet_nis = models.CharField(max_length=20,null=True,blank=True)
    class Meta:
        db_table = 'compet_auto_register'
        verbose_name = 'Competidor Auto Registrado'
        verbose_name_plural = 'Competidores Auto Registrados'
        unique_together = ("compet_name", "compet_birth_date", "compet_school", "compet_type", "compet_sex",
                           "compet_email", "compet_year")

# class InsertCompetBatch(Compet):
#     #form = CompetBatchForm
#     class Meta:
#         proxy = True
#         verbose_name = 'Insere Lote'
#         verbose_name_plural = 'Insere Lote'

# class InsertPointsPhase1Compet(Compet):
#     class Meta:
#         proxy = True
#         verbose_name = 'Pontos Fase 1 - Modalidade Iniciação'
#         verbose_name_plural = 'Pontos Fase 1 - Modalidade Iniciação'

class InsereLoteCompetidores(models.Model):
    '''Used for uploading a batch of compets'''
    data = models.FileField('Arquivo')
    class Meta:
        verbose_name = u'Competidores em lote'
        verbose_name_plural = 'Competidores em lote'


#######################
# SubWWW
#######################
class SubWWW(models.Model):
    sub_id = models.AutoField(primary_key=True)
    sub_source = models.TextField()
    sub_lang = models.IntegerField(
        'Linguagem',
        choices = LANGUAGE_CHOICES,
        )
    sub_lock = models.IntegerField(null=True,default=0)
    sub_marked = models.IntegerField(null=True,default=0)
    result_id = models.IntegerField(null=True) #models.ForeignKey(Res_www,on_delete=models.CASCADE,null=True)
    problem_name = models.CharField(max_length=32)
    problem_name_full = models.CharField(max_length=128)
    sub_file = models.FileField() 
    sub_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'sub_www'
        verbose_name = u'SubWWW'
        verbose_name_plural = u'SubWWW'


#######################
# res_www
#######################
class ResWWW(models.Model):
    result_id = models.AutoField(primary_key=True)
    result_log = models.TextField()
    sub = models.ForeignKey(SubWWW,on_delete=models.CASCADE)
    result_result = models.IntegerField()
    num_total_tests = models.IntegerField()
    num_correct_tests = models.IntegerField()
    problem_name = models.CharField(max_length=32)
    result_time = models.DateTimeField(auto_now_add=True)
    team_id = models.IntegerField(default=0)
    class Meta:
        db_table = 'res_www'

class ResIni(models.Model):
    res_ini_id = models.AutoField(primary_key=True)
    compet_id = models.IntegerField(unique=True)
    log_fase1 = models.TextField(null=True);
    log_fase2 = models.TextField(null=True);
    log_fase3 = models.TextField(null=True);
    answers_fase1 = models.TextField(null=True);
    answers_fase2 = models.TextField(null=True);
    answers_fase3 = models.TextField(null=True);
    class Meta:
        db_table = 'res_ini'


#######################
# linguagens de programação
#######################
class Language(models.Model):
    def __str__(self):
        return self.name

    @classmethod
    def from_db(cls, db, field_names, values):
        # Default implementation of from_db() (subject to change and could
        # be replaced with super()).
        if len(values) != len(cls._meta.concrete_fields):
            values = list(values)
            values.reverse()
            values = [
                values.pop() if f.attname in field_names else DEFERRED
                for f in cls._meta.concrete_fields
            ]
        instance = cls(*values)
        instance._state.adding = False
        instance._state.db = 'corretor'
        # customization to store the original field values on the instance
        instance._loaded_values = dict(zip(field_names, values))
        return instance

    id = models.AutoField(primary_key=True)
    name = models.CharField('Nome',max_length=32)
    class Meta:
        db_table = 'language'

#######################
# certificados
#######################
class GeraCertificados(Compet):
    class Meta:
        proxy = True
        verbose_name = 'Gera Certificados'
        verbose_name_plural = 'Gera Certificados'

#######################
# cities
#######################

class States(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField(primary_key=True)
    #ibge = models.CharField('IBGE',max_length=10)
    name = models.CharField('Nome',max_length=30)
    short_name = models.CharField('Nome',max_length=4)
    class Meta:
        db_table = 'states'

class Cities(models.Model):
    def __str__(self):
        return self.name

    id = models.AutoField(primary_key=True)
    ibge = models.CharField('IBGE',max_length=10)
    name = models.CharField('Nome',max_length=255)
    is_capital = models.BooleanField('Capital',default=False)
    lat = models.FloatField('Latitude')
    lng = models.FloatField('Longitude')
    state_id = models.IntegerField('Estado')
    
    class Meta:
        db_table = 'cities'

#######################
# inep
#######################

# class Inep(models.Model):
#     def __str__(self):
#         return self.name

#     id = models.AutoField(primary_key=True)
#     co_entidade = models.IntegerField('co_entidade')
#     no_entidade = models.CharField('Nome',max_length=255)
#     co_municipio = models.IntegerField('co_municipio')
#     co_uf = models.IntegerField('co_uf')
#     tp_dependencia = models.IntegerField('tp_dependencia')
#     class Meta:
#         db_table = 'inep'

#######################
# Password
#######################

class PasswordRequest(models.Model):
    def __str__(self):
        return f"user_id: {self.user_id}"

    # por alguma razão django está gerando duas requisições http para redefine_senha
    # por isso o campo first; se requisição não for first, desconsidera

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField('User ID')
    request_hash = models.CharField('Hash',max_length=255)
    request_time = models.DateTimeField('Horário',auto_now_add=True)
    first = models.BooleanField('Primeira',default=True)
    used = models.BooleanField('Usado',default=False)
    class Meta:
        db_table = 'password_request'

class Password(models.Model):
    def __str__(self):
        return f"user_id: {self.user_id}"

    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField('User ID')
    password = models.CharField('Password',max_length=32)
    request_time = models.DateTimeField('Horário',auto_now_add=True)
    class Meta:
        db_table = 'password'

#######################
# QueuedMail
#######################

class QueuedMail(models.Model):
    def __str__(self):
        return f"Message"

    id = models.AutoField(primary_key=True)
    subject = models.CharField('Subject',max_length=255)
    body = models.TextField('Body')
    body_html = models.TextField('Body',null=True,blank=True)
    from_addr = models.CharField('From',max_length=255)
    to_addr = models.CharField('To',max_length=255)
    sent = models.BooleanField('Sent',default=False)
    time_in = models.DateTimeField('Horário Entrada',default=timezone.now)
    time_out = models.DateTimeField('Horário Envio',null=True,blank=True)
    priority = models.IntegerField('Prioridade',default=0)
    status = models.CharField('Status',max_length=16)
    
    class Meta:
        db_table = 'queued_mail'

class Level(models.Model):
    def __str__(self):
        return f"Level"

    id = models.AutoField(primary_key=True)
    name = models.CharField('Subject',max_length=32)
    name_short = models.CharField('From',max_length=2)
    class Meta:
        db_table = 'level'

class EmailRequest(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.CharField('Email',max_length=255)
    hash = models.CharField('Hash',max_length=255)
    timestamp = models.DateTimeField('Horário',auto_now_add=True)
    class Meta:
        db_table = 'email_request'


