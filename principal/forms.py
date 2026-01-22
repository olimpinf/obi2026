import string

from django import forms
from django.contrib import messages
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# begin - implementation of fieldsets
from django.forms.models import ModelFormOptions

from restrito.forms import (COMPET_LEVEL_CHOICES, SCHOOL_YEAR_CHOICES_FORM)
from serpro.utils import verifica_nome_cpf

from .models import (LEVEL_CHOICES_FORM, PARTIC_TYPE_CHOICES_FORM, 
                     REGULAR_PUBLIC, REGULAR_PRIVATE, HIGHER_PUBLIC, HIGHER_PRIVATE, SPECIAL,
                     SCHOOL_TYPE_CHOICES, SEX_CHOICES, SEX_F, SEX_M,
                     STATE_CHOICES, Compet, School, Colab, SubWWW, capitalize_name,
                     validate_compet_level, validate_username, CompetAutoRegister)
from .utils.utils import format_compet_id, validate_cpf_cnpj, validate_only_cpf
from obi.settings import YEAR

_old_init = ModelFormOptions.__init__
def _new_init(self, options=None):
    _old_init(self, options)
    self.fieldsets = getattr(options, 'fieldsets', None)
ModelFormOptions.__init__ = _new_init

class Fieldset(object):
  def __init__(self, form, title, fields, classes, single_field):
    self.form = form
    self.title = title
    self.fields = fields
    self.classes = classes
    self.single_field = single_field
  
  def __iter__(self):
      # Similar to how a form can iterate through its fields...
      if self.single_field:
          yield self.fields
      else:
          for field in self.fields:
              yield field

def fieldsets(self):
    meta = getattr(self, '_meta', None)
    if not meta:
        meta = getattr(self, 'Meta', None)
  
    if not meta or not meta.fieldsets:
        return
  
    for name, data in meta.fieldsets:
        if str(type(data['fields'])) != "<class 'tuple'>":
            single = True
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[data.get('fields',())]),
                classes=data.get('classes', ''),
                single_field = single
                )
        else:
            single = False
            yield Fieldset(
                form=self,
                title=name,
                fields=(self[f] for f in data.get('fields',())),
                classes=data.get('classes', ''),
                single_field = single
                )

forms.BaseForm.fieldsets = fieldsets
# end implementation fieldsets


class RegisterEmailForm(forms.Form):
    deleg_email = forms.EmailField(
        label = 'Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = True,
        help_text = 'Utilize preferencialmente um endereço de email institucional, pois isso agilizará a validação do cadastro da escola.',
        )
    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('deleg_email')}),
        )


class RegisterSchoolForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        school_type = int(cleaned_data.get('school_type'))
        try:
            school_inep_code = int(cleaned_data.get('school_inep_code'))
        except:
            school_inep_code = 0
            self.cleaned_data['school_inep_code'] = 0
        if school_type in [REGULAR_PUBLIC,REGULAR_PRIVATE] and school_inep_code == 0:
            self.add_error('school_inep_code','Informe o Código INEP da Escola')
        if School.objects.filter(school_inep_code=school_inep_code, school_ok=True).exists():
            self.add_error('school_inep_code','Escola com esse código INEP já está cadastrada.')

        # check document and name are OK
        name = cleaned_data.get('school_deleg_name')
        validated = cleaned_data.get('school_deleg_cpf')
        print("will call verifica_nome_cpf", name, validated)
        if not verifica_nome_cpf(name, validated):
            self.add_error("school_deleg_cpf", "Nome não confere com o CPF nos registros da Receita Federal. Por favor informe o nome completo, como consta do CPF.")

        return self.cleaned_data

    def clean_school_deleg_cpf(self):
        document = self.cleaned_data.get('school_deleg_cpf')
        validated = validate_only_cpf(document)
        if not validated:
            self.add_error("school_deleg_cpf", "Documento inválido")
        return validated
    
    school_type = forms.ChoiceField(
        label='Tipo da Escola',
        required=True,
        choices= (SCHOOL_TYPE_CHOICES ),
        widget=forms.Select(attrs={'class':'form-select'}), # 'onchange':'_showHideSchoolType("id_school_inep_code")'}),
        )
    school_inep_code = forms.IntegerField(
        label='Código INEP da Escola',
        help_text='Obrigatório para escolas do Ensino Básico. Informe o código INEP e pressione a tecla TAB no seu teclado; os dados da escola serão preenchidos automaticamente. Se você não sabe o código INEP de sua escola, <a href="http://www.buscacep.correios.com.br/sistemas/buscacep/" target="_blank">consulte aqui</a>.',
        required=False,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    school_name = forms.CharField(
        label='Nome da Escola', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        )
    school_phone = forms.CharField(
        label='Telefone da Escola, com DDD',
        max_length=16,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Para contato com a Escola durante o processo de verificação de dados. Não informe telefone pessoal.',
        )
    school_zip = forms.CharField(
        label='CEP da Escola',
        max_length=10,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        help_text='Informe o CEP e pressione a tecla TAB no seu teclado; os campos Logradouro, Bairro, Cidade e Estado serão completados automaticamente. Se você não sabe o CEP, <a href="http://www.buscacep.correios.com.br/sistemas/buscacep/" target="_blank">consulte aqui</a>.'
        )
    school_address = forms.CharField(
        label='Logradouro',
        max_length=256,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        required=False,
        )
    school_address_number = forms.CharField(
        label='Número',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=16,
        required=False,
        )
    school_address_complement = forms.CharField(
        label='Complemento',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=128,
        required=False,
        )
    school_address_district = forms.CharField(
        label='Bairro/Distrito',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=32,
        )
    school_city = forms.CharField(
        label='Cidade',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=128,
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        #widget=forms.TextInput(attrs={'readonly':'readonly'})
        )
    school_deleg_name = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        help_text='Insira o nome completo, com a grafia correta, da pessoa que será o Coordenador Local da OBI na escola. O nome será utilizado durante a verificação de dados para habilitar a escola e também na emissão do Certificado de Participação.',
        )
    school_deleg_phone = forms.CharField(
        label='Telefone pessoal, com DDD',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=16,
        help_text='Para contato em caso de emergência.',
        required = True,
        )
    school_deleg_email = forms.EmailField(
        label = 'Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = True,
        help_text = 'Endereço para contato com a pessoa que será o Coordenador Local da OBI na escola.' 
        )
    school_deleg_cpf = forms.CharField(
        label='CPF',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=16,
        required = True,
        help_text='Informe o número de seu CPF.',
        )
    # school_deleg_username = forms.CharField(
    #     label='Nome de usuário',
    #     widget=forms.TextInput(attrs={'class':'form-control'}),
    #     max_length=64,
    #     help_text='Escolha um identificador para acessar o sistema da OBI como coordenador local. Utilize apenas letras, números e os caracteres hífen ("-"), sublinhado ("_"), ponto (".") e arroba ("@"). Quando a escola for habilitada, a senha será gerada automaticamente e enviada para o endereço de email informado.',
    #     validators = [validate_username]
    #     )

    school_change_coord = forms.ChoiceField(
        label='Informe se este cadastro está sendo feito porque a escola já está cadastrada e houve mudança de Coordenador Local da OBI na escola.',
        choices=((False,'Não houve mudança ou a escola não está cadastrada.'),(True,'Sim, houve mudança de coordenador em relação ao ano passado, e o coordenador anterior está ciente da alteração.')),
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=False,
        help_text='Antes de responder a esta pergunta, <a href="/consulta_escolas">consulte as escolas cadastradas</a>.'
    )
    first_school = forms.BooleanField(widget=forms.HiddenInput(),required=False)
    school_code = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    school_prev = forms.IntegerField(widget=forms.HiddenInput(),required=False)
    school_is_known = forms.BooleanField(widget=forms.HiddenInput(),required=False)
    class Meta:
        fieldsets = (
            ('Dados da Escola', {
                    'fields': ('school_type','school_inep_code','school_name','school_phone','school_zip','school_address','school_address_number','school_address_complement','school_address_district','school_city','school_state')}),
            ('Coordenador Local da OBI{}'.format(YEAR), {
                    'fields': ('school_deleg_name','school_deleg_phone','school_deleg_email', 'school_deleg_cpf')}),
            ('hidden', {
                    'fields': ('first_school','school_is_known','school_code','school_prev')}),
        )

class ConsultaEscolasForm(forms.Form):
    school_name = forms.CharField(
        label='Nome da Escola', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        )
#     school_type = forms.ChoiceField(
#         label='Tipo da Escola',
#         choices=( (None,'Todos'), (PUB,'Pública'), (PRI,'Privada') ),
#         widget=forms.Select(attrs={'class':'form-select'}),
#         required=False,
#         )
    school_city = forms.CharField(
        label='Cidade',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=128,
        required=False,
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )
    school_order = forms.ChoiceField(
        label='Ordena por',
        choices=( ('school_name','Nome da Escola'), ('school_city','Cidade'), ('school_state','Estado') ),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Dados para consulta', {
                    'fields': ('school_name','school_city','school_state')}),
            ('Visualização', {
                    'fields': ('school_order')}),
        )

class ConsultaCompetidoresForm(forms.Form):
    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        # avoid single quotes in names
        name = name.replace("'","’")
        return name
    
    compet_name = forms.CharField(
        label='Nome do(a) Competidor(a)', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        )
    compet_level = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )
    school_name = forms.CharField(
        label='Nome da Escola', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        )
    school_city = forms.CharField(
        label='Cidade',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=128,
        required=False,
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )
    list_order = forms.ChoiceField(
        label='Ordena por',
        choices=( ('compet_name','Nome do competidor'), ('compet_type','Modalidade'), ('school_name','Nome da Escola'), ('school_city','Cidade'), ('school_state','Estado') ),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Dados para consulta', {
                    'fields': ('compet_name','compet_level','school_name','school_city','school_state')}),
            ('Visualização', {
                    'fields': ('list_order')}),
        )

class RecuperaCadastroForm(forms.Form):
    def clean_old_username(self):
        current_year = int(YEAR)
        try:
            u = User.objects.using('obi{}'.format(current_year-1)).get(username=self.cleaned_data['old_username'])
        except:
            raise ValidationError(message='Usuário não existe no banco de dados da OBI{}'.format(current_year-1))
        return self.cleaned_data['old_username']

    def clean_old_password(self):
        current_year = int(YEAR)
        try:
            u = User.objects.using('obi{}'.format(current_year-1)).get(username=self.cleaned_data['old_username'])
        except:
            # clean_old_username will report this error
            return ''

        if not check_password(self.cleaned_data['old_password'], u.password):
            raise ValidationError(message='Password errada')
        return self.cleaned_data['old_password']

    old_username = forms.CharField(
        label='Nome de usuário',
        max_length=100,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    old_password = forms.CharField(
        label='Senha',
        max_length=128,
        widget=forms.PasswordInput(attrs={'class':'form-control'}),
        )

    class Meta:
        fieldsets = (
            ('Dados para acesso da OBI do ano passado (OBI{})'.format(int(YEAR)-1), {
                    'fields': ('old_username', 'old_password')}),
        )


class RelataErroForm(forms.Form):
    description = forms.CharField(
        label='Descrição:',
        required=True,
        widget=forms.Textarea(attrs={'class':'form-control'}),
        )

    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('description')}),
        )


############
# Results
#
class ConsultaResFase1IniForm(forms.Form):
    compet_id = forms.CharField(
        label='Número de Inscrição', 
        max_length=8,
        required=True,
        help_text='Não sabe o número de inscrição? <a href="/consulta_competidores">Consulte aqui</a>.'
        )

    class Meta:
        fieldsets = (
            ('Dados para consulta', {
                    'fields': ('compet_id')}),
        )


# used in certif
PARTIC_YEAR_FORM = (('',u'Selecione'),
                    ('2025',u'2025'),
                    ('2024',u'2024'),
                    ('2023',u'2023'),
                    ('2022',u'2022'),
                    ('2021',u'2021'),
                    ('2020',u'2020'),
                    ('2019',u'2019'),
                    ('2018',u'2018'),
                    ('2017',u'2017'),
                    ('2016',u'2016'),
                    ('2015',u'2015'),
                    ('2014',u'2014'),
                    ('2013',u'2013'),
                    ('2012',u'2012'),
                    ('2011',u'2011'),
                    ('2010',u'2010'),
                    ('2009',u'2009'),
                    ('2008',u'2008'),
                    ('2007',u'2007'),
                    ('2006',u'2006'),
                    ('2005',u'2005'),
                    )
class ConsultaParticipantesForm(forms.Form):
    competition = forms.ChoiceField(
        label='',
        choices=(('obi','OBI'),('cf','CF')),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text="É obrigatório selecionar a competição",
        )
    partic_year = forms.ChoiceField(
        label='',
        choices=PARTIC_YEAR_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text="É obrigatório selecionar o ano",
        )
    partic_type = forms.ChoiceField(
        label='Tipo de participação',
        choices=PARTIC_TYPE_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text="É obrigatório selecionar o tipo de participação",
        )
    partic_name = forms.CharField(
        label='Nome', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        )
    compet_level = forms.ChoiceField(
        label='Modalidade',
        choices=LEVEL_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-control'}),
        required=False,
        help_text='Apenas para competidores',
        )
    school_name = forms.CharField(
        label='Nome da Escola', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        )
    school_city = forms.CharField(
        label='Cidade',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=128,
        required=False,
        )
    school_state = forms.ChoiceField(
        label='Estado',
        choices=(STATE_CHOICES),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )
    list_order = forms.ChoiceField(
        label='Ordena por',
        choices=( ('partic_name','Nome'), ('compet_type','Modalidade'), ('school_name','Nome da Escola'), ('school_city','Cidade'), ('school_state','Estado') ),
        widget=forms.Select(attrs={'class':'form-select'}),
        required=False,
        )

    class Meta:
        fieldsets = (
            ('Competição', {
                    'fields': ('competition')}),
            ('Ano', {
                    'fields': ('partic_year')}),
            ('Dados do participante', {
                    'fields': ('partic_type', 'partic_name','compet_level')}),
            ('Dados da escola', {
                    'fields': ('school_name','school_city','school_state')}),
            ('Visualização', {
                    'fields': ('list_order')}),
        )

class PasswordResetForm(forms.Form):
    username = forms.CharField(
        label = 'Endereço de email',
        required = True,
        widget=forms.TextInput(attrs={'class':'form-control'}),
        )
    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('username')}),
        )

class PasswordResetCoordForm(forms.Form):
    username = forms.CharField(
        label = 'Nome de usuário ou endereço de email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required = True,
        )
    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('username')}),
        )

class PasswordResetCompetForm(forms.Form):
    username = forms.CharField(
        label = 'Número de Inscrição',
        widget=forms.TextInput(attrs={'class':'form-control-sm'}),
        required = True,
        )
    class Meta:
        fieldsets = (
            ('', {
                    'fields': ('username')}),
        )

class SubmeteSolucaoPratiqueForm(forms.Form):
    '''Used to upload submissions'''
    data = forms.FileField(
        label='Arquivo', 
        error_messages={'required': 'Escolha o arquivo'},
        )
    sub_lang = forms.ChoiceField(
        label='',
        choices=( (None,'Linguagem'), (1,'C'), (2,'C++'), (3,'Pascal'), (4,'Python2'), (7,'Python3'), (5,'Java'), (6,'Javascript'),),
        widget=forms.Select(attrs={'class':'form-select'}),
        )
    problem_name = forms.CharField(max_length=32,widget=forms.HiddenInput())
    problem_name_full = forms.CharField(max_length=128,widget=forms.HiddenInput())
    problem_request_path = forms.CharField(max_length=256,widget=forms.HiddenInput())

    class Meta:
        fields = (('data','sub_lang'))
        model = SubWWW

class AutoCadastroCompetForm(forms.Form):
    def clean(self):
        cleaned_data = super().clean()
        compet_type = cleaned_data.get('compet_type')
        compet_year = cleaned_data.get('compet_year')
        compet_class = cleaned_data.get('compet_class')
        compet_birth_date = cleaned_data.get('compet_birth_date')
        compet_name = cleaned_data.get('compet_name')
        compet_email = cleaned_data.get('compet_email')
        school_id = cleaned_data.get('school_id')
        school = School.objects.get(school_id=school_id)

        result = validate_compet_level(compet_type, compet_year, school.school_type)
        if result:
            self.add_error('compet_type', result)

        print(compet_name,school_id,
                                                          compet_type, compet_year,
                                                          compet_email,compet_birth_date)
        compet_exists = CompetAutoRegister.objects.filter(compet_name__iexact=compet_name,compet_school_id=school_id,
                                                          compet_type=compet_type, compet_year=compet_year,
                                                          compet_email=compet_email, compet_birth_date=compet_birth_date)

        if len(compet_exists) > 0:
            if compet_exists[0].compet_status == 'excluded':
                self.add_error('compet_email', "Competidor com exatamente esses dados informados já foi pré-inscrito anteriormente na OBI{} e foi excluído pelo Coordenador Local.".format(YEAR))
            else:
                self.add_error('compet_email', "Competidor com exatamente esses dados informados já foi pré-inscrito anteriormente na OBI{} e está aguardando validação pelo Coordenador Local.".format(YEAR))

        compet_exists = Compet.objects.filter(compet_name__iexact=compet_name,compet_school_id=school_id,
                                                          compet_type=compet_type, compet_year=compet_year,
                                                          compet_email=compet_email, compet_birth_date=compet_birth_date).exists()

        if compet_exists:
            self.add_error('compet_email', "Competidor com exatamente esses dados informados já está inscrito na OBI{}, com número de inscrição {}.".format(YEAR, format_compet_id(compet_id)))

        return self.cleaned_data

    def clean_compet_name(self):
        name = self.cleaned_data['compet_name']
        tks = name.split()
        if len(tks) < 2:
            raise forms.ValidationError("Informe o nome completo.")
        name = capitalize_name(name)
        # avoid single quotes in names
        name = name.replace("'","’")
        # leave check for clean()
        #school_id = self.cleaned_data['school_id']
        #compet_exists = Compet.objects.filter(compet_name__iexact=name,compet_school_id=school_id)
        #if len(compet_exists) > 0:
        #   raise forms.ValidationError("Competidor com esse nome já está inscrito.")
        return name

    school_id = forms.IntegerField(
        widget=forms.HiddenInput(),
    )
    compet_name = forms.CharField(
        label='Nome do(a) Competidor(a)', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=True,
        help_text='Insira o nome completo, com a grafia correta. O nome será utilizado na emissão do certificado de participação.',
    )
    compet_type = forms.ChoiceField(
        label='Modalidade',
        choices=COMPET_LEVEL_CHOICES,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
        help_text='<br>Cada competidor(a) pode ser inscrito(a) em uma única modalidade.',
    )
    compet_year = forms.ChoiceField(
        label='Ano Escolar',
        choices=SCHOOL_YEAR_CHOICES_FORM,
        widget=forms.Select(attrs={'class':'form-select'}),
        required=True,
    )
    compet_class = forms.CharField(
        label='Turma Escolar',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=8,
        required=True,
        initial='A',
    )
    compet_sex = forms.ChoiceField(
        label='Gênero',
        choices=SEX_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'horizontal'}),
        required=True,
    )
    compet_email = forms.EmailField(
        label='Email',
        widget=forms.TextInput(attrs={'class':'form-control'}),
        required=False,
    )
    compet_birth_date = forms.DateField(
        label='Data de Nascimento',
        widget=forms.SelectDateWidget(years=list(range(1980,2017))),
        required=True,
        initial='01/01/2000',
        )

    # extra information
    
    compet_mother_name = forms.CharField(
        label='Nome da mãe do(a) Competidor(a)', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        help_text='Insira o nome completo, com a grafia correta.',
    )
    compet_cpf = forms.CharField(
        label='CPF', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=200,
        required=False,
        help_text='Cadastro de pessoa física.'
    )
    compet_nis = forms.CharField(
        label='NIS', 
        widget=forms.TextInput(attrs={'class':'form-control'}),
        max_length=11,
        required=False,
        help_text='Número de identificação social.',
    )
    class Meta:
        fieldsets = (
            ('Dados Obrigatórios', {
                'fields': ('compet_name','compet_year','compet_class','compet_type','compet_sex','compet_birth_date')}
             ),
            ('Dados Opcionais', {
                'fields': ('compet_email', 'compet_mother_name', 'compet_cpf','compet_nis')}
             ),
            ('hidden', {
                'fields': ('school_id',)}
             ),
        )


