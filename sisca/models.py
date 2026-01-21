from django.core.validators import EmailValidator, FileExtensionValidator
from django.db import models

ALTERNATIVE_CHOICES = [
    ('A','A'),('B','B'),('C','C'),('D','D'),('E','E'),('X','Anulada')
    ]

NUM_ALTERNATIVE_CHOICES = (
    (3, u'3'),
    (4, u'4'),
    (5, u'5'),
    )

NUM_DIG_CHOICES = (
    (2, u'numérico, 2 dígitos'),
    (3, u'numérico, 3 dígitos'),
    (4, u'numérico, 4 dígitos'),
    (5, u'numérico, 5 dígitos'),
    (6, u'numérico, 6 dígitos'),
    (7, u'não numérico ou numérico maior do que 6 dígitos'),
    )
# NUM_QUESTION_CHOICES = (
#     (5, u'5'),
#     (10, u'10'),
#     (15, u'15'),
#     (20, u'20'),
#     (25, u'25'),
#     (30, u'30'),
#     (40, u'40'),
#     (50, u'50'),
#     (60, u'60'),
#     (70, u'70'),
#     (80, u'80'),
#     (90, u'90'),
#     (100, u'100'),
#     )
NUM_QUESTION_CHOICES = ((i,f'{i}') for i in range(1,101))

class GeraFolhasRespostas(models.Model):
    '''Generate blank pages'''
    label1 = models.CharField('Rótulo 1',max_length=100)
    label2 = models.CharField('Rótulo 2',max_length=100,blank=True)
    label3 = models.CharField('Rótulo 3',max_length=100,blank=True)
    label4 = models.CharField('Rótulo 4',max_length=100,blank=True)
    num_dig = models.IntegerField(
        'Formato da Identificação',
        choices = NUM_DIG_CHOICES,
        default = 5,
        )
    check_id = models.BooleanField('Incluir dígito de verificação',help_text='Apenas para identificação numérica com número de dígitos menor do que 7')
    num_questions = models.IntegerField(
        'Número de questões',
        choices = NUM_QUESTION_CHOICES,
        default = 20,
        )
    num_alternatives = models.IntegerField(
        'Número de alternativas',
        choices = NUM_ALTERNATIVE_CHOICES,
        help_text='Número de alternativas para cada questão',
        default = 5,
        )
    source_file = models.FileField('Arquivo de participantes',upload_to='sisca',blank=True)
    class Meta:
        db_table = 'generate_answer_sheet'
        verbose_name = u'Gerador de Folhas de Respostas'

class CorrigeFolhasRespostas(models.Model):
    '''Used to upload submission'''
    source_file = models.FileField('Arquivo de Folhas de Respostas', upload_to='sisca', validators=[FileExtensionValidator(['pdf','jpg','png'])])
    answer_file = models.FileField('Arquivo de gabarito', upload_to='sisca', validators=[FileExtensionValidator(['txt'])])
    num_questions = models.IntegerField(
        'Número de questões',
        choices =  ((i,f'{i}') for i in range(1,101)),
        default = 20,
        help_text='Número de questões (para verificar consistência do arquivo de gabarito)',
        )
    num_alternatives = models.IntegerField(
        'Número de alternativas',
        choices = NUM_ALTERNATIVE_CHOICES,
        help_text='Número de alternativas para cada questão (para verificar consistência do arquivo de gabarito)',
        default = 5,
        )
    reference = models.CharField('Referência',max_length=100)
    email = models.CharField('Email',max_length=100,validators = [EmailValidator(message=u'Por favor entre um endereço válido de email')])
    class Meta:
        verbose_name = u'Corretor de Folhas de Respostas'
        db_table = 'mark_answer_sheet'

class GeraGabarito(models.Model):
    '''Generate answer file'''

    num_questions = models.IntegerField(
        'Número de questões',
        choices =  ((i,f'{i}') for i in range(1,101)),
        default = 20,
        )
    num_alternatives = models.IntegerField(
        'Número de alternativas',
        choices = NUM_ALTERNATIVE_CHOICES,
        help_text='Número de alternativas para cada questão',
        default = 5,
        )
    comment = models.TextField(
        'Comentário',
        max_length=512,
        help_text='Se informado, o texto fornecido será copiado no início do arquivo gerado, como comentário',
        null=True,
        blank=True,
    )
    class Meta:
        db_table = 'generate_answer_file'
        verbose_name = u'Gerador de Gabarito'
