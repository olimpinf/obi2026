from django.db import models
from django.core.validators import EmailValidator, RegexValidator

from principal.models import (LEVEL_CHOICES, Colab, Compet, Deleg,
                              School, SEX_CHOICES)
from principal.utils.utils import format_compet_id

INDEFINIDO =  u'Indefinido'
AEROPORTO = u'Aeroporto'
HOTEL = u'Hotel'
RODOVIARIA = u'Rodoviária'
PLACE_TYPE_CHOICES = (
    (INDEFINIDO, u'Indefinido'),
    (AEROPORTO, u'Aeroporto'),
    (HOTEL, u'Hotel'),
    (RODOVIARIA, u'Rodoviária'),
    )

#P = 'P'
#M = 'M'
#G = 'G'
#XG = 'XG'
#XXG = 'XXG'
#SHIRT_SIZE_CHOICES = [
#    (P, P),
#    (M, M),
#    (G, G),
#    (XG, XG),
#    (XXG, XXG),
#    ]

SHIRT_SIZE_CHOICES = [
    ('T_PP',   'Tradicional PP - 67,0 x 45,0'),
    ('T_P',    'Tradicional P - 70,0 x 49,0'),
    ('T_M',    'Tradicional M - 74,0 x 52,0'),
    ('T_G',    'Tradicional G - 78,0 x 57,0'),
    ('T_GG',   'Tradicional GG - 82,0 x 61,0'),
    ('T_EGG',  'Tradicional EGG - 86,0 x 65,0'),
    ('T_EEGG', 'Tradicional EEGG - 94,0 x 69,0'),
    ('B_PP',   'Baby Look PP - 56,0 x 38,0'),
    ('B_P',    'Baby Look P - 58,5 x 41,0'),
    ('B_M',    'Baby Look M - 61,0 x 43,5'),
    ('B_G',    'Baby Look G - 63,5 x 47,0'),
    ('B_GG',   'Baby Look GG - 66,0 x 50,0'),
    ('B_EGG',  'Baby Look EGG - 67,0 x 53,0')
 ]

COMPET = 'Competidor'
COORD = 'Coordenador'
COLAB = 'Colaborador'
CHAPERONE = 'Acompanhante'
WEEK_PARTIC_CHOICES = (
    (COMPET, COMPET),
    (COORD, COORD),
    (COLAB, COLAB),
    (CHAPERONE, CHAPERONE),
    )

PARENT_FATHER = 'P'
PARENT_MOTHER = 'M'
PARENT_OTHER = 'R'
PARENT_TYPE_CHOICES = [
    (PARENT_FATHER,'Pai'), (PARENT_MOTHER,'Mãe'),  (PARENT_OTHER,'Responsável Legal') 
    ]

STATUS = {
    'confirm': 'Participação Pendente',
    'deny': 'Não Participará',
    'no_reply': 'Não Respondeu',
}

#######################
# Chaperone
#######################
class Chaperone2(models.Model):
    def __str__(self):
        return self.chaperone_name

    chaperone_id = models.AutoField(primary_key=True)
    chaperone_name = models.CharField('Nome',max_length=100,null=True,blank=True)
    chaperone_school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.PROTECT,blank=True,null=True)
    chaperone_sex = models.CharField(
        'Gênero',
        max_length=1,
        choices = SEX_CHOICES,
        )
    chaperone_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True)
    class Meta:
        db_table = 'chaperone2'
        verbose_name = 'Acompanhante'
        verbose_name_plural = 'Acompanhante'

#######################
# Pai, Mãe ou Responsável Legal
#######################
class Parent(models.Model):
    def __str__(self):
        return self.parent_name

    parent_id = models.AutoField(primary_key=True)
    parent_compet = models.OneToOneField(Compet, on_delete=models.CASCADE,null=True,unique=True)
    parent_name = models.CharField('Nome',max_length=100,null=True,blank=True)
    parent_type = models.CharField(
        'Responsável Legal',
        max_length=1,
        choices = PARENT_TYPE_CHOICES,
        )
    parent_email = models.CharField('Email',max_length=100,validators = [EmailValidator()],null=True,blank=True)
    parent_phone = models.CharField('Telefone',max_length=20)
    class Meta:
        db_table = 'parent'
        verbose_name = 'Pai ou responsável'
        verbose_name_plural = 'Pais ou responsáveis'


#######################
# Pagamento
#######################
class Payment(models.Model):
    def __str__(self):
        # if self.payment_school:
        #     return self.payment_school
        # elif self.payment_parent:
        #     return self.payment_parent
        # elif self.payment_compet:
        #     return self.payment_compet
        return str(self.id)

    id = models.AutoField(primary_key=True)
    value = models.FloatField('Valor')
    data = models.TextField('Dados do pagamento',null=True,blank=True)
    receipt_file = models.CharField('Arquivo', max_length=512, blank=True,null=True)
    ignored = models.BooleanField('Ignorado',default=False,null=True)
    confirmed = models.BooleanField('Confirmado',default=False,null=True)
    confirmed_sbc = models.BooleanField('Confirmado SBC',default=False,null=True)
    doc_name = models.CharField('CPF ou CNPJ', max_length=512, blank=True,null=True)
    doc_number = models.CharField('CPF ou CNPJ', max_length=32, blank=True,null=True)
    doc_email = models.CharField('Email', max_length=128, blank=True,null=True)
    doc_address = models.TextField('Email', blank=True,null=True)
    time_informed = models.DateTimeField(auto_now_add=True)
    time_confirmed = models.DateTimeField(blank=True,null=True)
    time_ignored = models.DateTimeField(blank=True,null=True)

    class Meta:
        db_table = 'payment'
        verbose_name = 'Pagamento de taxa'
        verbose_name_plural = 'Pagamentos de taxa'

        
class Week(models.Model):
#     def __str__(self):
#         if self.compet:
#             return self.compet.compet_name
#         elif self.colab:
#             return 'Colab'
#             return self.colab.colab_name
#         else:
#             return 'Delegado'
#             return self.deleg.deleg_name

    def _get_full_compet_id(self):
        "Returns the compet id formatted with checking char."
        if self.compet:
            return format_compet_id(self.compet)
        else:
            return "-"
    full_compet_id = property(_get_full_compet_id)
    _get_full_compet_id.short_description = u'Num. Inscrição'

    def _get_participant_name(self):
        "Returns the participant name."
        if self.compet:
            return self.compet.compet_name
        elif self.colab:
            return self.colab.colab_name
        elif self.colab:
            return self.colab.colab_name
        elif self.chaperone:
            return self.chaperone.chaperone_name
        else:
            return self.school.deleg_name

    participant_name = property(_get_participant_name)
    _get_participant_name.short_description = u'Participante'


    week_id = models.AutoField(primary_key=True)
    partic_level = models.IntegerField(
        'Nível do participante',
        choices = LEVEL_CHOICES,blank=True,null=True)
    partic_type = models.CharField(
        'Tipo de participante',
        max_length=32,
        choices = WEEK_PARTIC_CHOICES,blank=True,null=True)
    compet = models.OneToOneField(Compet, on_delete=models.CASCADE,null=True,unique=True)
    #compet = models.ForeignKey(Compet,verbose_name="Competidor",on_delete=models.CASCADE,blank=True,null=True,unique=True)
    #colab = models.ForeignKey(Colab,verbose_name="Acompanhante (colab.)",on_delete=models.CASCADE,blank=True,null=True,unique=True)
    colab = models.OneToOneField(Colab,verbose_name="Acompanhante (colab.)",on_delete=models.CASCADE,blank=True,null=True,unique=True)
    #chaperone = models.ForeignKey(Chaperone,verbose_name="Acompanhante",on_delete=models.CASCADE,blank=True,null=True,unique=True)
    chaperone = models.OneToOneField(Chaperone2,verbose_name="Acompanhante",on_delete=models.CASCADE,blank=True,null=True,unique=True)
    school = models.ForeignKey(School,verbose_name="Escola",on_delete=models.CASCADE,blank=True,null=True)
    payment = models.ForeignKey(Payment,verbose_name="Pagamento",on_delete=models.CASCADE,blank=True,null=True)
    paying = models.BooleanField('Pagante',default=False,null=True)
    tax_paid = models.BooleanField('Pagamento Informado',default=False,null=True)
    tax_confirmed = models.BooleanField('Pagamento Confirmado',default=False,null=True)
    tax_value = models.DecimalField('Taxa',decimal_places=2,max_digits=10,blank=True,null=True)
    form_info = models.BooleanField('Formulário Informações',default=False,blank=True,null=True)
    form_arrival = models.BooleanField('Formulário Chegada/Partida',default=False,blank=True,null=True)
    arrival_place = models.CharField(
        'Local de Chegada',
        max_length=32,
        choices = PLACE_TYPE_CHOICES,blank=True,null=True)
    arrival_from = models.CharField(
        'Origem',
        max_length=64,blank=True,null=True)
    arrival_info = models.CharField(
        'Vôo',
        max_length=32,blank=True,null=True)
    arrival_time = models.DateTimeField(blank=True,null=True)
    van_arrival_time = models.DateTimeField(blank=True,null=True)
    departure_place = models.CharField(
        'Local de Partida',
        max_length=32,
        choices = PLACE_TYPE_CHOICES,blank=True,null=True)
    departure_to = models.CharField(
        'Destino',
        max_length=64,blank=True,null=True)
    departure_info = models.CharField(
        'Vôo',
        max_length=32,blank=True,null=True)
    departure_time = models.DateTimeField(blank=True,null=True)
    van_departure_time = models.DateTimeField(blank=True,null=True)

    phone = models.CharField('Telefone Pessoal',max_length=20,blank=True,null=True)
    document = models.CharField(
        'Documento',
        max_length=32,
        blank=True,null=True)
    shirt_size = models.CharField(
        'Camiseta',
        max_length=6,
        choices = SHIRT_SIZE_CHOICES,blank=True,null=True)
    allergies = models.CharField(
        'Alergias',
        max_length=256,
        blank=True,null=True)
    status = models.CharField(
        'Status',
        max_length=32,blank=True,null=True)

    class Meta:
        db_table = 'week'


